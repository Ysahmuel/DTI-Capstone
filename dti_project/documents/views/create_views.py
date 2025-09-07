from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from ..mixins.context_mixins import PreviewContextMixin
from ..mixins.form_mixins import FormStepsMixin, FormSubmissionMixin, FormsetMixin, MessagesMixin
from ..mixins.service_mixins import ServiceCategoryMixin
from ..utils.form_helpers import get_certification_text
from ..constants import CHECKLIST_EVALUATION_DETAIL_GROUPS, CHECKLIST_EVALUATION_FIELD_GROUPS, INSPECTION_VALIDATION_DETAIL_GROUPS, INSPECTION_VALIDATION_REPORT_FIELD_GROUPS, ORDER_OF_PAYMENT_DETAIL_GROUPS, ORDER_OF_PAYMENT_FIELD_GROUPS, PERSONAL_DATA_SHEET_DETAIL_GROUPS, PERSONAL_DATA_SHEET_FIELD_GROUPS, SALES_PROMOTION_DETAIL_GROUPS, SALES_PROMOTION_FIELD_GROUPS, SERVICE_REPAIR_ACCREDITATION_DETAIL_GROUPS, SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS
from ..forms import FORMSET_CLASSES, ChecklistEvaluationSheetForm, InspectionValidationReportForm, OrderOfPaymentForm, PersonalDataSheetForm, SalesPromotionPermitApplicationForm, ServiceRepairAccreditationApplicationForm
from ..models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

from django.template.loader import render_to_string

class BaseCreateView(
    LoginRequiredMixin,
    PreviewContextMixin,
    MessagesMixin,
    FormSubmissionMixin,
    FormStepsMixin,
    FormsetMixin,
    CreateView
):
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        
        print(f"DEBUG: post() called with action: {action}")  # Debug print
        print(f"DEBUG: is_ajax: {request.headers.get('x-requested-with') == 'XMLHttpRequest'}")  # Debug print

        # Handle AJAX preview requests - bypass FormSubmissionMixin
        if request.headers.get("x-requested-with") == "XMLHttpRequest" and action == "preview":
            print("DEBUG: Handling AJAX preview")  # Debug print
            return self.handle_ajax_preview(request)
        
        # For all other cases, use FormSubmissionMixin's logic
        print("DEBUG: Using FormSubmissionMixin logic")  # Debug print
        return super().post(request, *args, **kwargs)
    
    def handle_ajax_preview(self, request):
        """Handle AJAX preview validation and response"""
        try:
            print("DEBUG: Starting handle_ajax_preview")  # Debug print
            
            self.object = None
            form = self.get_form(self.get_form_class())
            
            print(f"DEBUG: Form created, is_valid: {form.is_valid()}")  # Debug print
            if not form.is_valid():
                print(f"DEBUG: Form errors: {form.errors}")  # Debug print
            
            if form.is_valid():
                print("DEBUG: Form is valid, checking formsets")  # Debug print
                
                # Simple case - if no formsets, return preview directly  
                if not hasattr(self, 'formset_classes') or not self.formset_classes:
                    print("DEBUG: No formsets, returning preview")  # Debug print
                    context = self.get_preview_context(form)
                    print(f"DEBUG: Preview context: {context}")  # Debug print
                    return JsonResponse(context)
                
                # Handle formsets
                temp_obj = form.save(commit=False)
                temp_obj.user = request.user
                formsets = self.get_formsets(instance=temp_obj)
                formsets_valid = self.formsets_valid(formsets)
                
                print(f"DEBUG: Formsets valid: {formsets_valid}")  # Debug print
                
                if formsets_valid:
                    context = self.get_preview_context(form)
                    return JsonResponse(context)
                else:
                    print("DEBUG: Formsets invalid, calling form_invalid")  # Debug print
                    # Let form_invalid handle adding the formset errors to messages
                    self.form_invalid(form, action="preview", formsets=formsets)
            else:
                print("DEBUG: Form invalid, calling form_invalid")  # Debug print
                # Handle form validation errors
                self.form_invalid(form, action="preview")
            
            # Render messages HTML for AJAX response
            messages_html = render_to_string("documents/partials/alerts_container.html", {
                "messages": messages.get_messages(request)
            })
            
            response_data = {
                "errors": form.errors,
                "messages_html": messages_html
            }
            print(f"DEBUG: Returning error response")  # Debug print
            
            return JsonResponse(response_data, status=400)
            
        except Exception as e:
            print(f"DEBUG: Exception in handle_ajax_preview: {str(e)}")  # Debug print
            import traceback
            traceback.print_exc()  # This will print the full stack trace
            
            # Return simple error response
            return JsonResponse({
                "error": "Server error occurred",
                "message": str(e)
            }, status=500)
    
class CreateSalesPromotionView(BaseCreateView):
    template_name = 'documents/create_templates/create_sales_promotion.html'
    model = SalesPromotionPermitApplication
    context_object_name = 'sales_promo'
    form_class = SalesPromotionPermitApplicationForm
    formset_classes = {
        'product': FORMSET_CLASSES['product_covered']
    }

    FIELD_GROUPS = SALES_PROMOTION_FIELD_GROUPS
    detail_groups = SALES_PROMOTION_DETAIL_GROUPS
    additional_sections = ['coverage']

    def get_success_url(self):
        return reverse_lazy('sales-promotion-application', kwargs={'pk': self.object.pk})


class CreatePersonalDataSheetView(BaseCreateView):
    template_name = 'documents/create_templates/create_personal_data_sheet.html'
    model = PersonalDataSheet
    form_class = PersonalDataSheetForm
    formset_classes = {
        'employee_background': FORMSET_CLASSES['employee_background'],
        'trainings_attended': FORMSET_CLASSES['trainings_attended'],
        'educational_attainment': FORMSET_CLASSES['educational_attainment'],
        'character_references': FORMSET_CLASSES['character_references'],
    }
    context_object_name = 'personal_data'

    FIELD_GROUPS = PERSONAL_DATA_SHEET_FIELD_GROUPS
    detail_groups = PERSONAL_DATA_SHEET_DETAIL_GROUPS

    def get_success_url(self):
        return reverse_lazy('personal-data-sheet', kwargs={'pk': self.object.pk})


class CreateServiceRepairAccreditationApplicationView(BaseCreateView):
    template_name = 'documents/create_templates/create_service_repair.html'
    model = ServiceRepairAccreditationApplication
    form_class = ServiceRepairAccreditationApplicationForm

    FIELD_GROUPS = SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS
    detail_groups = SERVICE_REPAIR_ACCREDITATION_DETAIL_GROUPS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Example of adding computed field
        application = ServiceRepairAccreditationApplication(
            name_of_business=self.request.user,
            warranty_period=30
        )
        context['warranty_text'] = application.get_warranty_text()

        return context

    def get_success_url(self):
        return reverse_lazy('service-repair-accreditation', kwargs={'pk': self.object.pk})


class CreateInspectionValidationReportView(BaseCreateView, ServiceCategoryMixin):
    model = InspectionValidationReport
    template_name = 'documents/create_templates/create_inspection_validation_report.html'
    form_class = InspectionValidationReportForm

    FIELD_GROUPS = INSPECTION_VALIDATION_REPORT_FIELD_GROUPS
    detail_groups = INSPECTION_VALIDATION_DETAIL_GROUPS
    additional_sections = ['service_categories']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certification_text'] = get_certification_text()
        context['service_categories'] = self.get_service_categories_with_services()
        return context

    def get_success_url(self):
        return reverse_lazy('inspection-validation-report', kwargs={'pk': self.object.pk})


class CreateOrderOfPaymentView(BaseCreateView):
    model = OrderOfPayment
    template_name = 'documents/create_templates/create_order_of_payment.html'
    form_class = OrderOfPaymentForm
    
    FIELD_GROUPS = ORDER_OF_PAYMENT_FIELD_GROUPS
    detail_groups = ORDER_OF_PAYMENT_DETAIL_GROUPS

    def get_success_url(self):
        return reverse_lazy('order-of-payment', kwargs={'pk': self.object.pk})


class CreateChecklistEvaluationSheetView(BaseCreateView):
    model = ChecklistEvaluationSheet
    template_name = 'documents/create_templates/create_checklist_evaluation_sheet.html'
    form_class = ChecklistEvaluationSheetForm
    
    FIELD_GROUPS = CHECKLIST_EVALUATION_FIELD_GROUPS
    detail_groups = CHECKLIST_EVALUATION_DETAIL_GROUPS

    def get_success_url(self):
        return reverse_lazy('checklist-evaluation-sheet', kwargs={'pk': self.object.pk})
