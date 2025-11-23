from django.db import models
from documents.model_choices import BUSINESS_SCOPE_CHOICES, OTHER_BUSINESS_NAME_RELATED_FORM_CHOICES
from ..models.base_models import DraftModel
from users.models import User

class OtherBusinessNameRelatedFormModel(DraftModel, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name_of_business = models.CharField(max_length=255)
    certificate_number = models.CharField(max_length=20)
    date_registered = models.DateField()
    trn_ref_code = models.CharField(max_length=16, verbose_name='TRN/Reference Code')
    valid_id_presented = models.ImageField(upload_to="valid_ids", verbose_name="Valid Id Presented")

    # BN Certification
    bn_certification_purpose = models.TextField(verbose_name='State Purpose', blank=True, null=True)

    # Authentication
    no_of_copies = models.PositiveIntegerField(blank=True, null=True)

    # Change of Info - Territorial Scope
    change_territorial_scope = models.BooleanField(default=False)
    territorial_scope_from = models.CharField(max_length=255, blank=True, null=True, choices=BUSINESS_SCOPE_CHOICES)
    territorial_scope_to = models.CharField(max_length=255, blank=True, null=True, choices=BUSINESS_SCOPE_CHOICES)

    # Change of Info - Owner's Name
    change_owner_name = models.BooleanField(default=False)
    owner_name_from = models.CharField(max_length=255, blank=True, null=True)
    owner_name_to = models.CharField(max_length=255, blank=True, null=True)
    owner_name_proof_basis = models.FileField(upload_to="proof_documents", blank=True, null=True, verbose_name="Proof/Basis (Duplicate or Clear Certified Copy)")

    # Change of Info - Business Address
    change_business_address = models.BooleanField(default=False)
    business_address_from = models.CharField(max_length=255, blank=True, null=True)
    business_address_to = models.CharField(max_length=255, blank=True, null=True)

    # Change of Info - Owner's Address
    change_owner_address = models.BooleanField(default=False)
    owner_address_from = models.CharField(max_length=255, blank=True, null=True)
    owner_address_to = models.CharField(max_length=255, blank=True, null=True)

    # Cancellation
    cancellation_reason = models.CharField(max_length=100, blank=True, null=True, verbose_name="Basis/Reason for cancellation")

    class Meta:
        verbose_name = "Other Business Name Related Form"
        verbose_name_plural = "Other Business Name Related Forms"

    def __str__(self):
        return f"{self.name_of_business}"