from django.db import models

# Create your models here.
class SalesPromotionPermitApplication(models.Model):
    promo_title = models.CharField(max_length=255)
    date_filed = models.DateField(auto_now_add=True)

    sponsor_name = models.CharField(max_length=255)
    sponsor_address = models.TextField()
    sponsor_telephone = models.CharField(max_length=50, blank=True)
    sponsor_email = models.EmailField(blank=True)
    sponsor_authorized_rep = models.CharField(max_length=255)
    sponsor_designation = models.CharField(max_length=255)

    advertising_agency_name = models.CharField(max_length=255, blank=True)
    advertising_agency_address = models.TextField(blank=True)
    advertising_agency_telephone = models.CharField(max_length=50, blank=True)
    advertising_agency_email = models.EmailField(blank=True)
    advertising_agency_authorized_rep = models.CharField(max_length=255, blank=True)
    advertising_agency_designation = models.CharField(max_length=255, blank=True)

    promo_period_start = models.DateField(null=True, blank=True)
    promo_period_end = models.DateField(null=True, blank=True)

    COVERAGE_CHOICES = [
        ('NCR', 'NCR or several regions including Metro Manila'),
        ('2_REGIONS', '2 regions or more outside NCR'),
        ('1_REGION_2_PROVINCES', 'Single region covering 2 provinces or more'),
        ('1_PROVINCE', 'Single province')
    ]

    coverage = models.CharField(max_length=20, choices=COVERAGE_CHOICES)

    # Location-specific fields depending on coverage
    region_location_of_sponsor = models.CharField(max_length=255, blank=True)  # For '2_REGIONS'
    regions_covered = models.TextField(blank=True)                             # For '2_REGIONS'

    single_region = models.CharField(max_length=255, blank=True)               # For '1_REGION_2_PROVINCES'
    provinces_covered = models.TextField(blank=True)                           # For '1_REGION_2_PROVINCES'

    single_province = models.CharField(max_length=255, blank=True)             # For '1_PROVINCE'
    cities_or_municipalities_covered = models.TextField(blank=True)            # For '1_PROVINCE'

    def __str__(self):
        return self.promo_title
    
class ProductCovered(models.Model):
    permit_application = models.ForeignKey(SalesPromotionPermitApplication, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    specifications = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} {self.brand}"