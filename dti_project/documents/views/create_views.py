from django.urls import reverse_lazy

from ..mixins.form_mixins import FormStepsMixin, FormSubmissionMixin, FormsetMixin, MessagesMixin
from ..mixins.service_mixins import ServiceCategoryMixin
from ..utils.form_helpers import get_certification_text
from ..constants import CHECKLIST_EVALUATION_FIELD_GROUPS, INSPECTION_VALIDATION_REPORT_FIELD_GROUPS, ORDER_OF_PAYMENT_FIELD_GROUPS, PERSONAL_DATA_SHEET_FIELD_GROUPS, SALES_PROMOTION_FIELD_GROUPS, SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS
from ..forms import FORMSET_CLASSES, ChecklistEvaluationSheetForm, InspectionValidationReportForm, OrderOfPaymentForm, PersonalDataSheetForm, SalesPromotionPermitApplicationForm, ServiceRepairAccreditationApplicationForm
from ..models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

class CreateSalesPromotionView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, CreateView):
    template_name = 'documents/create_sales_promotion.html'
    model = SalesPromotionPermitApplication
    context_object_name = 'sales_promo'
    form_class = SalesPromotionPermitApplicationForm
    formset_classes = {
        'product': FORMSET_CLASSES['product_covered']
    }

    FIELD_GROUPS = SALES_PROMOTION_FIELD_GROUPS
    additional_sections = ['coverage']

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        context['field_groups'] = self.FIELD_GROUPS

        return context
    
    def get_success_url(self):
        return reverse_lazy('sales-promotion-application', kwargs={'pk': self.object.pk})
    
class CreatePersonalDataSheetView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, CreateView):
    template_name = 'documents/create_personal_data_sheet.html'
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = self.FIELD_GROUPS

        return context
    
    def get_success_url(self):
        return reverse_lazy('personal-data-sheet', kwargs={'pk': self.object.pk})
    
class CreateServiceRepairAccreditationApplicationView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, CreateView):
    template_name = 'documents/create_service_repair.html'
    model = ServiceRepairAccreditationApplication
    form_class = ServiceRepairAccreditationApplicationForm

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

class CreateInspectionValidationReportView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, ServiceCategoryMixin, CreateView):
    model = InspectionValidationReport
    template_name = 'documents/create_inspection_validation_report.html'
    form_class = InspectionValidationReportForm

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
    
class CreateOrderOfPaymentView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, CreateView):
    model = OrderOfPayment
    template_name = 'documents/create_order_of_payment.html'
    form_class = OrderOfPaymentForm
    
    FIELD_GROUPS = ORDER_OF_PAYMENT_FIELD_GROUPS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = self.FIELD_GROUPS
        return context

    def get_success_url(self):
        return reverse_lazy('order-of-payment', kwargs={'pk': self.object.pk})

class CreateChecklistEvaluationSheetView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, CreateView):
    model = ChecklistEvaluationSheet
    template_name = 'documents/create_checklist_evaluation_sheet.html'
    form_class = ChecklistEvaluationSheetForm
    
    FIELD_GROUPS = CHECKLIST_EVALUATION_FIELD_GROUPS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = self.FIELD_GROUPS
        return context

    def get_success_url(self):
        return reverse_lazy('checklist-evaluation-sheet', kwargs={'pk': self.object.pk})
