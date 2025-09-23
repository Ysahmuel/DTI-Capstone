from django.apps import apps
from .models.base_models import DraftModel
from .models import (
    ChecklistEvaluationSheet,
    InspectionValidationReport,
    OrderOfPayment,
    PersonalDataSheet,
    SalesPromotionPermitApplication,
    ServiceRepairAccreditationApplication,
)

MODEL_MAP = {
    model._meta.model_name: model
    for model in apps.get_models()
    if issubclass(model, DraftModel) and not model._meta.abstract
}

EXPORT_MODEL_MAP = {
    "salespromotionpermitapplication": SalesPromotionPermitApplication,
    "personaldatasheet": PersonalDataSheet,
    "servicerepairaccreditationapplication": ServiceRepairAccreditationApplication,
    "inspectionvalidationreport": InspectionValidationReport,
    "orderofpayment": OrderOfPayment,
    "checklistevaluationsheet": ChecklistEvaluationSheet,
}

UPLOAD_MODEL_MAP = {
    "accreditation of service and repair enterprises": ServiceRepairAccreditationApplication,
    "sales promotion permit applications": SalesPromotionPermitApplication,
    "personal data sheets": PersonalDataSheet,
    "orders of payment": OrderOfPayment,
    "checklist of requirements and evaluation sheets": ChecklistEvaluationSheet,
}