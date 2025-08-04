import re
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from ..constants import PERSONAL_DATA_SHEET_FIELD_GROUPS, SALES_PROMOTION_FIELD_GROUPS, SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS
from ..mixins import FormStepsMixin, FormsetMixin
from ..forms import PersonalDataSheetForm, SalesPromotionPermitApplicationForm, FORMSET_CLASSES, ServiceRepairAccreditationApplicationForm
from ..models import PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date
from decimal import Decimal



# Create your views here.from your_app.models import InspectionValidationReport
from .create_views import (
    CreateSalesPromotionView,
    CreatePersonalDataSheetView,
    CreateServiceRepairAccreditationApplicationView,
    CreateInspectionValidationReportView,
    CreateOrderOfPaymentView,
    CreateChecklistEvaluationSheetView
)
from .detail_views import (
    SalesPromotionDetailView,
    PersonalDataSheetDetailView,
    InspectionValidationReportDetailView
)
