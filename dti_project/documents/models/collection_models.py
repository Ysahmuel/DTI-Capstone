from django.db import models
from django.utils import timezone


class CollectionReportItem(models.Model):
    # General information
    date = models.DateField(default=timezone.now)
    official_receipt_number = models.CharField(max_length=50)
    rc_code = models.CharField(max_length=50, blank=True, null=True)
    payor = models.CharField(max_length=255)
    particulars = models.CharField(max_length=255)

    # Core amounts
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    stamp_tax = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # BN Registration
    bn_original = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    bn_renewal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # Accreditation
    accreditation_original = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    accreditation_renewal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    accreditation_filing_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    truck_rebuilding_original = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    truck_rebuilding_renewal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # Sales Promo
    sales_promo_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sales_promo_revisions = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # Licensing and Certifications
    certification = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    bulk_sales = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    assessment_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    license_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # PETC and Miscellaneous
    petc_accreditation = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    bn_listings = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    confiscated_materials = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # Admin and Surcharge
    fines_penalties = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    surcharge_bn_reg = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    surcharge_accre = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    unserviceable = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # Miscellaneous income (678)
    misc_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.payor} - {self.official_receipt_number or 'No OR'}"
