from django.db import models
from django.urls import reverse
from django.utils import timezone

class CollectionReport(models.Model):
    report_items = models.ManyToManyField(
        'CollectionReportItem',
        related_name='collection_reports'
    )

    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)

    # Certification fields
    certification_text = models.TextField(null=True, blank=True)
    collecting_officer_name = models.CharField(max_length=255, null=True, blank=True)
    # collecting_officer_signature = models.CharField(max_length=255, null=True, blank=True)  # Or ImageField if you want to store actual signatures
    special_collecting_officer = models.CharField(max_length=255, null=True, blank=True)
    special_collecting_officer_date = models.DateField(null=True, blank=True)
    official_designation = models.CharField(max_length=255, null=True, blank=True)
    
    # # Summary fields
    undeposited_collections = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_collections = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def date_range_display(self):
        """Return a readable date range, preferring stored dates over calculated ones."""
        # Use stored date range if available
        if self.date_from and self.date_to:
            if self.date_from == self.date_to:
                return self.date_from.strftime("%b %d, %Y")
            else:
                return f"{self.date_from.strftime('%b %d, %Y')} - {self.date_to.strftime('%b %d, %Y')}"
        
        # Fall back to calculating from report items
        dates = self.report_items.values_list('date', flat=True)
        if not dates:
            return "No dates"

        first_date = min(dates)
        last_date = max(dates)

        if first_date == last_date:
            return first_date.strftime("%b %d, %Y")
        else:
            return f"{first_date.strftime('%b %d, %Y')} - {last_date.strftime('%b %d, %Y')}"

    def __str__(self):
        return f"Report ({self.date_range_display()})"

    def delete(self, *args, **kwargs):
        # Delete all associated report items first
        self.report_items.all().delete()
        # Then delete the report itself
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("collection-report", args=[self.pk])


class CollectionReportItem(models.Model):
    # General information
    date = models.DateField(default=timezone.now)
    number = models.CharField(max_length=50, blank=True, null=True, help_text='Official Receipt Number')
    rc_code = models.CharField(max_length=50, blank=True, null=True)
    payor = models.CharField(max_length=255, blank=True, null=True)
    particulars = models.CharField(max_length=255, blank=True, null=True)

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
        return f"{self.payor} - {self.number or 'No OR'}"
    
    def get_absolute_url(self):
        return reverse("collection-report-item", args=[self.pk]) 
