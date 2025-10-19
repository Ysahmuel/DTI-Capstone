from django.db import models
from django.utils import timezone

class CollectionReport(models.Model):
    report_items = models.ManyToManyField(
        'CollectionReportItem',
        related_name='collection_reports'
    )

    def date_range_display(self):
        """Return a readable date range for all report items."""
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
