from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from locations.models import Barangay, CityMunicipality, Province, Region
from ..models.base_models import BaseApplication, DraftModel, PeriodModel
from django.utils import timezone
from ..model_choices import REGION_CHOICES, SERVICE_CATEGORY_CHOICES, STAR_RATING_CHOICES
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import random
import string

class ServiceRepairAccreditationApplication(DraftModel, models.Model):
    class Meta:
        verbose_name = "Accreditation of Service and Repair Enterprise"
        verbose_name_plural = "Accreditation of Service and Repair Enterprises"
        
    APPLICATION_TYPES = [
        ('NEW', 'New'),
        ('RENEWAL', 'Renewal'),
    ]

    CATEGORIES = [
        ('MOTOR VEHICLES & HEAVY EQUIPMENT', 'Motor Vehicles & Heavy Equipment'),
        ('MEDICAL & DENTAL EQUIPMENT', 'Medical & Dental Equipment'),
        ('OFFICE MACHINE/DATA PROCESSING EQUIPMENT', 'Office Machine/Data Processing Equipment'),
        ('ENGINES & ENGINEERING WORKS (MACHINE SHOPS)', 'Engines & Engineering Works (Machine Shops)'),
        ('ELECTRONICS, ELECTRICAL, AIRCONDITIONING & REFRIGERATION', 'Electronics, Electrical, Airconditioning & Refrigeration'),
        ('OTHER CONSUMER MECHANICAL & INDUSTRIAL EQUIPMENT, APPLIANCES OR DEVICES', 'Other Consumer Mechanical & Industrial Equipment, Appliances or Devices'),
    ]

    SEX_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    ]

    SOCIAL_CLASSIFICATION_CHOICES = [
        ('ABLED', 'Abled'),
        ('PWD', 'Differently Abled'),
        ('IP', 'Indigenous Person'),
        ('SENIOR', 'Senior Citizen'),
        ('YOUTH', 'Youth'),
        ('OSY', 'Out-of-School Youth'),
    ]

    ASSET_SIZE_CHOICES = [
        ('MICRO', 'Micro (<Php3M)'),
        ('SMALL', 'Small (Php3M - <15M)'),
        ('MEDIUM', 'Medium (Php15M - 100M)'),
        ('LARGE', 'Large (>Php100M)'),
    ]

    FORM_OF_ORGANIZATION_CHOICES = [
        ('SP', 'Single Proprietorship'),
        ('CORP', 'Corporation'),
        ('PARTNERSHIP', 'Partnership'),
        ('COOP', 'Cooperative'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    application_type = models.CharField(max_length=10, choices=APPLICATION_TYPES)
    category = models.CharField(max_length=100, choices=CATEGORIES)
    star_rating = models.PositiveSmallIntegerField(choices=STAR_RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    date = models.DateTimeField(default=timezone.now)
    name_of_business = models.CharField(max_length=255)

    # Business Address Fields
    building_name_or_number = models.CharField(max_length=50)
    street_name = models.CharField(max_length=50)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True)
    city_or_municipality = models.ForeignKey(CityMunicipality, on_delete=models.SET_NULL, null=True, blank=True)
    barangay = models.ForeignKey(Barangay, on_delete=models.SET_NULL, null=True, blank=True)
    zip_code = models.CharField(max_length=10)

    telephone_number = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)
    fax_number = models.CharField(max_length=20, blank=True, null=True)
    email_address = models.EmailField(max_length=40)

    # Authorized Signatory
    title = models.CharField(max_length=20)
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30)
    suffix = models.CharField(max_length=10, blank=True)
    designation = models.CharField(max_length=255)

    
    # Additional Info
    sex = models.CharField(max_length=6, choices=SEX_CHOICES)
    social_classification = models.CharField(max_length=10, choices=SOCIAL_CLASSIFICATION_CHOICES)
    asset_size = models.CharField(max_length=10, choices=ASSET_SIZE_CHOICES)
    form_of_organization = models.CharField(max_length=20, choices=FORM_OF_ORGANIZATION_CHOICES)
    industry_classification = models.CharField(max_length=255, blank=True)

    annual_gross_service_revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text="Annual Gross Service Revenue (as of Dec 31, 20__)")
    capital_investment = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    tax_identification_number = models.CharField(max_length=12)
    mobile_number = models.CharField(max_length=11)
    telephone_number = models.CharField(max_length=15, blank=True, null=True)
    date_established = models.DateField(blank=True, null=True)
    total_employees = models.PositiveIntegerField()

    warranty_period = models.PositiveIntegerField(
        help_text="Number of days warranty is valid", 
        default=0,
        blank=True,
        null=True
    )
    
    # PAYMENT / OOP-LIKE FIELDS (fixed fees based on star rating / category)
    FILING_FEE = Decimal('50.00')
    ACCREDITATION_FEES = {
        1: Decimal('350.00'),
        2: Decimal('400.00'),
        3: Decimal('425.00'),
        4: Decimal('450.00'),
        5: Decimal('500.00'),
    }
    # For MEDICAL & DENTAL EQUIPMENT override to 350 (original & renewal)
    MEDICAL_CATEGORY_KEY = 'MEDICAL & DENTAL EQUIPMENT'

    reference_code = models.CharField(max_length=20, blank=True, null=True, unique=True)
    acknowledgment_generated_at = models.DateTimeField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    class PaymentStatus(models.TextChoices):
        AWAITING = 'awaiting', 'Awaiting Payment'
        PAID = 'paid', 'Paid'
        VERIFIED = 'verified', 'Verified'
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.AWAITING)

    def __str__(self):
        # show only the business name in lists/tables
        return self.get_str_display(self.name_of_business)

    def get_absolute_url(self):
        return reverse("service-repair-accreditation", args=[self.pk])
    
    def get_update_url(self):
        return reverse("update-service-repair-accreditation", args=[self.pk])

    def get_warranty_text(self):
        """Generate the warranty/undertaking text with the warranty period filled in"""
        warranty_template = """
        {name_of_business} warrants the quality of workmanship and process undertaken by the shop for a period of {warranty_period_words} ({warranty_period}) 
        days counted from the date of actual release and  delivery of each and/or job order to the respective customer.

        This warranty does not cover damage caused by misuse, accidents, or alteration of workmanship; in addition, 
        it is expressly understood that the shop management shall not be liable for any patent defect in the product and which is not included in the job contract.

        We further undertake to abide by the rules and regulations promulgated by DTI and the terms and conditions of this warranty. 
        In the event of violation on our part, our accreditation certificate may be cancelled at the discretion of the DTI.
        """
        
        # Convert number to words for the parentheses
        warranty_period_words = self.number_to_words(self.warranty_period)
        
        return warranty_template.format(
            name_of_business=self.name_of_business,
            warranty_period=self.warranty_period,
            warranty_period_words=warranty_period_words
        )

    def number_to_words(self, number):
        """Convert number to words for warranty period"""
        # Simple implementation - you might want to use a library like 'num2words' for more complex numbers
        ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        teens = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
        tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
        
        if number == 0:
            return 'zero'
        elif number < 10:
            return ones[number]
        elif number < 20:
            return teens[number - 10]
        elif number < 100:
            return tens[number // 10] + ('' if number % 10 == 0 else '-' + ones[number % 10])
        elif number < 1000:
            return ones[number // 100] + ' hundred' + ('' if number % 100 == 0 else ' ' + self.number_to_words(number % 100))
        else:
            return str(number)  
        
    def calculate_fee(self):
        """
        Calculate total: filing fee + accreditation fee based on star_rating and category.
        Medical/Dental equipment => fixed accreditation fee of 350.00
        """
        try:
            if self.category == self.MEDICAL_CATEGORY_KEY:
                accreditation_fee = Decimal('350.00')
            else:
                accreditation_fee = self.ACCREDITATION_FEES.get(int(self.star_rating), Decimal('0.00'))
        except Exception:
            accreditation_fee = Decimal('0.00')
        return (self.FILING_FEE + accreditation_fee).quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        try:
            self.total_amount = self.calculate_fee()
        except Exception:
            self.total_amount = Decimal('0.00')

        def _generate_reference():
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))

        if self.payment_status == self.PaymentStatus.VERIFIED and not self.reference_code:
            self.reference_code = _generate_reference()
            self.acknowledgment_generated_at = timezone.now()

        super().save(*args, **kwargs)

class ServiceCategory(models.Model):
    key = models.CharField(max_length=50, choices=SERVICE_CATEGORY_CHOICES, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Service Categories'

    def __str__(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('category', 'name')
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"