# models.py

# Explicit re-export of all models from the models folder
from .models import (
    # Base models
    BaseApplication,
    DraftModel,
    YesNoField,
    PeriodModel,
    
    # Checklist evaluation
    ChecklistEvaluationSheet,
    
    # Inspection validation
    InspectionValidationReport,
    
    # Order of payment
    OrderOfPayment,
    
    # Personal data sheet models
    PersonalDataSheet,
    EmployeeBackground,
    TrainingsAttended,
    EducationalAttainment,
    CharacterReference,
    
    # Sales promotion models
    SalesPromotionPermitApplication,
    ProductCovered,
    
    # Service repair accreditation models
    ServiceRepairAccreditationApplication,
    Service,
    ServiceCategory,
    
    # Change requests
    ChangeRequest,

    # Collection item
    CollectionReport,
    CollectionReportItem
)


# This makes all your models available when other files import from this module
# Example: from myapp.models import ChecklistEvaluationSheet will still work