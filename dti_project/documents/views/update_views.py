from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from ..mixins.service_mixins import ServiceCategoryMixin
from ..mixins.form_mixins import FormStepsMixin, FormSubmissionMixin, FormsetMixin, MessagesMixin
from ..mixins.permissions_mixins import OwnershipDraftMixin
from ..utils.form_helpers import get_certification_text
from ..constants import CHECKLIST_EVALUATION_FIELD_GROUPS, INSPECTION_VALIDATION_REPORT_FIELD_GROUPS, ORDER_OF_PAYMENT_FIELD_GROUPS, PERSONAL_DATA_SHEET_FIELD_GROUPS, SALES_PROMOTION_FIELD_GROUPS, SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS
from ..forms import FORMSET_CLASSES, ChecklistEvaluationSheetForm, InspectionValidationReportForm, OrderOfPaymentForm, PersonalDataSheetForm, SalesPromotionPermitApplicationForm, ServiceRepairAccreditationApplicationForm
from ..models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from ..models import ChangeRequest

class UpdateSalesPromotionView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, OwnershipDraftMixin, UpdateView):
    model = SalesPromotionPermitApplication
    template_name = 'documents/update_templates/update_sales_promo.html'
    context_object_name = 'sales_promo'
    form_class = SalesPromotionPermitApplicationForm
    formset_classes = {
        'product': FORMSET_CLASSES['product_covered']
    }

    FIELD_GROUPS = SALES_PROMOTION_FIELD_GROUPS
    additional_sections = ['coverage']
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        context['field_groups'] = self.FIELD_GROUPS

        return context

class UpdatePersonalDataSheetView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, OwnershipDraftMixin, UpdateView):
    template_name = 'documents/update_templates/update_personal_data_sheet.html'
    model = PersonalDataSheet
    form_class = PersonalDataSheetForm
    formset_classes = {
        'employee_background': FORMSET_CLASSES['employee_background'],
        'trainings_attended': FORMSET_CLASSES['trainings_attended'],
        'educational_attainment': FORMSET_CLASSES['educational_attainment'],
        'character_references': FORMSET_CLASSES['character_references'],
    }
    context_object_name = 'personal_data_sheet'

    FIELD_GROUPS = PERSONAL_DATA_SHEET_FIELD_GROUPS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = self.FIELD_GROUPS
        return context
    
    def get_success_url(self):
        return reverse_lazy('personal-data-sheet', kwargs={'pk': self.object.pk})

class UpdateServiceRepairAccreditationApplicationView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, OwnershipDraftMixin, UpdateView):
    template_name = 'documents/update_templates/update_service_repair_accreditation.html'
    model = ServiceRepairAccreditationApplication
    form_class = ServiceRepairAccreditationApplicationForm
    context_object_name = 'accreditation'

    FIELD_GROUPS = SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS
        
        # Create an unsaved instance with default values
        application = ServiceRepairAccreditationApplication(
            name_of_business=self.request.user,
            warranty_period=30  # Or whatever default
        )
        context['warranty_text'] = application.get_warranty_text()

        return context
    
    def get_success_url(self):
        return reverse_lazy('service-repair-accreditation', kwargs={'pk': self.object.pk})
    
class UpdateInspectionValidationReportView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, ServiceCategoryMixin, OwnershipDraftMixin, UpdateView):
    model = InspectionValidationReport
    template_name = 'documents/update_templates/update_inspection_validation_report.html'
    form_class = InspectionValidationReportForm
    context_object_name = 'report'
    FIELD_GROUPS = INSPECTION_VALIDATION_REPORT_FIELD_GROUPS
    additional_sections = ['service_categories']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = self.FIELD_GROUPS
        context['certification_text'] = get_certification_text()
        context['service_categories'] = self.get_service_categories_with_services()
        return context

    def get_success_url(self):
        return reverse_lazy('inspection-validation-report', kwargs={'pk': self.object.pk})

class UpdateOrderOfPaymentView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, OwnershipDraftMixin, UpdateView):
    model = OrderOfPayment
    template_name = 'documents/update_templates/update_order_of_payment.html'
    form_class = OrderOfPaymentForm
    context_object_name = 'order'
    
    FIELD_GROUPS = ORDER_OF_PAYMENT_FIELD_GROUPS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = self.FIELD_GROUPS
        return context

    def get_success_url(self):
        return reverse_lazy('order-of-payment', kwargs={'pk': self.object.pk})
    
class UpdateChecklistEvaluationSheetView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, OwnershipDraftMixin, UpdateView):
    model = ChecklistEvaluationSheet
    template_name = 'documents/update_templates/update_checklist_evaluation_sheet.html'
    form_class = ChecklistEvaluationSheetForm
    context_object_name = 'checklist'
    
    FIELD_GROUPS = CHECKLIST_EVALUATION_FIELD_GROUPS
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = self.FIELD_GROUPS
        return context

    def get_success_url(self):
        return reverse_lazy('checklist-evaluation-sheet', kwargs={'pk': self.object.pk})