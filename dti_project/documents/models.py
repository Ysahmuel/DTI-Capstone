from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from users.models import User

# Create your models here.
class BaseApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_filed = models.DateField(default=timezone.now)

    class Meta:
        abstract = True

class SalesPromotionPermitApplication(BaseApplication):
    promo_title = models.CharField(max_length=255)
    date_filed = models.DateField(default=timezone.now)

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

    region_location_of_sponsor = models.CharField(max_length=255, blank=True)
    regions_covered = models.TextField(blank=True)
    single_region = models.CharField(max_length=255, blank=True)
    provinces_covered = models.TextField(blank=True)
    single_province = models.CharField(max_length=255, blank=True)
    cities_or_municipalities_covered = models.TextField(blank=True)

    def __str__(self):
        return self.promo_title
    
class ProductCovered(models.Model):
    permit_application = models.ForeignKey(SalesPromotionPermitApplication, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    specifications = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} {self.brand}"
    
class PersonalDataSheet(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Non-Binary', 'Non-binary'),
        ('Prefer not to say', 'Prefer not to say'),
    ]

    CIVIL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated'),
        ('Divorced', 'Divorced')
    ]

    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="personal_data_images")
    position = models.CharField(max_length=50)
    sex = models.CharField(choices=GENDER_CHOICES, max_length=20)
    civil_status = models.CharField(choices=CIVIL_STATUS_CHOICES, max_length=30)
    nationality = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    current_address = models.TextField()
    contact_number = models.CharField(max_length=20)
    email_address = models.EmailField()

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class EmployeeBackground(models.Model):
    personal_data_sheet = models.ForeignKey(PersonalDataSheet, related_name='employee_backgrounds', on_delete=models.CASCADE)
    employer = models.CharField(max_length=255)
    position = models.CharField(max_length=255)

    # Period Covered 
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # in case it’s current/ongoing

    def __str__(self):
        return f"{self.position} - {self.employer}"