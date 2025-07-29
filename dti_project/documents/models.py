from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from .model_choices import APPLICATION_OR_ACTIVITY_CHOICES, OFFICE_SHOP_CHOICES, SERVICE_CATEGORY_CHOICES, YES_NO_CHOICES
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class BaseApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_filed = models.DateField(default=timezone.now)

    class Meta:
        abstract = True

class PeriodModel(models.Model):
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['start_date']

class YesNoField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 3)
        kwargs.setdefault('choices', [('Yes', 'Yes'), ('No', 'No')])
        kwargs.setdefault('default', 'No')
        kwargs.setdefault('blank', True)
        super().__init__(*args, **kwargs)

class SalesPromotionPermitApplication(BaseApplication):
    promo_title = models.CharField(max_length=255)

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
        return f"{self.first_name} {self.middle_name if self.middle_name else None} {self.last_name}"

class EmployeeBackground(PeriodModel):
    personal_data_sheet = models.ForeignKey(PersonalDataSheet, related_name='employee_backgrounds', on_delete=models.CASCADE)
    employer = models.CharField(max_length=255)
    position = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.position} - {self.employer}"
    
class TrainingsAttended(PeriodModel):
    personal_data_sheet = models.ForeignKey(PersonalDataSheet, related_name='trainings_attended', on_delete=models.CASCADE)
    training_course = models.CharField(max_length=255)
    conducted_by = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Trainings Attended'

    def __str__(self):
        return self.training_course
    
class EducationalAttainment(PeriodModel):
    personal_data_sheet = models.ForeignKey(PersonalDataSheet, related_name='educational_attainment', on_delete=models.CASCADE)
    school = models.CharField(max_length=255)
    course = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.school} - {self.course}"
    
class CharacterReference(models.Model):
    personal_data_sheet = models.ForeignKey(PersonalDataSheet, related_name='character_references', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    company = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    def clean(self):
        if not self.email and not self.contact_number:
            raise ValidationError("At least one of 'email' or 'contact number' must be provided.")

    def __str__(self):
        return f"{self.name} ({self.company})"

class ServiceRepairAccreditationApplication(models.Model):
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

    STAR_RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5')
    ]

    application_type = models.CharField(max_length=10, choices=APPLICATION_TYPES)
    category = models.CharField(max_length=100, choices=CATEGORIES)
    star_rating = models.PositiveSmallIntegerField(choices=STAR_RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])

    name_of_business = models.CharField(max_length=255)

    # Business Address Fields
    building_name_or_number = models.CharField(max_length=50)
    street_name = models.CharField(max_length=50)
    barangay = models.CharField(max_length=50)
    city_or_municipality = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

    telephone_number = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)
    fax_number = models.CharField(max_length=20, blank=True)
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

    annual_gross_service_revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text="As of 31 December 20__")
    capital_investment = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    tax_identification_number = models.CharField(max_length=20)
    date_established = models.DateField(blank=True, null=True)
    total_employees = models.PositiveIntegerField()

    warranty_period = models.PositiveIntegerField(
        help_text="Number of days warranty is valid", 
        default=0,
    )

    def get_warranty_text(self):
        """Generate the warranty/undertaking text with the warranty period filled in"""
        warranty_template = """
        {name_of_business} Warrants the quality of workmanship and process undertaken by the shop for a period of {warranty_period} ({warranty_period_words}) 
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
            return str(number)  # For larger numbers, just return the digit
        
class OrderOfPayment(models.Model):
    name = models.CharField(max_length=55)
    date = models.DateField(default=timezone.now)
    address = models.TextField(max_length=255)

    account_officer_date = models.DateField(null=True, blank=True)
    account_officer_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    special_collecting_officer_date = models.DateField(null=True, blank=True)
    special_collecting_officer_or_number = models.CharField(max_length=50, blank=True)
    special_collecting_officer_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Orders of Payment'

    def __str__(self):
        return f"{self.name} {self.address}"
    
class PermitFee(models.Model):
    PERMIT_CHOICES = [
        ('discount', 'Discount'),
        ('premium', 'Premium'),
        ('raffle', 'Raffle'),
        ('contest', 'Contest'),
        ('redemption', 'Redemption'),
        ('games', 'Games'),
        ('beauty_contest', 'Beauty Contest'),
        ('home_solicitation', 'Home Solicitation'),
        ('amendments', 'Amendments'),
        ('doc_stamp', 'DocStamp'),
    ]

    REMARK_CHOICES = [
        ('R', 'Several provinces/cities within a region'),
        ('P', 'Single province/city/municipality'),
        ('X', '2 or more regions excluding Metro Manila'),
        ('A', 'Additional fees due to reassessment of premium and prizes')
    ]

    permit = models.ForeignKey(SalesPromotionPermitApplication, related_name='fees', on_delete=models.CASCADE)
    fee_type = models.CharField(max_length=20, choices=PERMIT_CHOICES)
    remarks = models.CharField(max_length=64, choices=REMARK_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Automatically set amount to ₱30 if fee_type is doc_stamp and amount wasn't set
        if self.fee_type == 'doc_stamp' and self.amount != 30:
            self.amount == 30
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.permit} ({self.fee_type}): ₱{self.amount}"
    
class InspectionValidationReport(models.Model):
    # Basic Information
    name_of_business = models.CharField(max_length=255)
    address = models.TextField()
    date = models.DateField(default=timezone.now)
    type_of_application_activity = models.CharField(max_length=50, choices=APPLICATION_OR_ACTIVITY_CHOICES)

    # Basic Info Section
    years_in_service = models.PositiveIntegerField(null=True, blank=True)
    types_of_office_shop = models.CharField(max_length=30, choices=OFFICE_SHOP_CHOICES, default='Main', help_text='Type of Office/Shop')

    business_name_cert = YesNoField(help_text='Business Name Certificates')
    business_name_cert_remarks = models.TextField(blank=True)

    accreditation_cert = YesNoField(help_text='Accreditation Certificate')
    accreditation_cert_remarks = models.TextField(blank=True)

    service_rates = YesNoField()
    service_rates_remarks = models.TextField(blank=True)

    # C. Tools and Equipment
    tools_equipment_complete = YesNoField()
    tools_equipment_serial_no = models.CharField(max_length=255, blank=True)
    racmac_sres_recovery_machine = YesNoField(help_text="For RAC/MAC SREs, with recovery machine")
    racmac_serial_no = models.CharField(max_length=255, blank=True)
    proof_acquisition_recovery_machine = models.CharField(max_length=255, blank=True, help_text="Proof of acquisition of recovery machine")

    # D. Competence of Technicians
    employed_technicians_count = models.PositiveIntegerField(null=True, blank=True)
    average_technician_experience = models.PositiveIntegerField(null=True, blank=True, help_text="Experience in years")
    tesda_certification_nc = models.CharField(max_length=255, blank=True)
    continuous_training_program = YesNoField()
    list_employees_past_2_years = YesNoField()
    refrigerant_storage_disposal_system = YesNoField()

    # E. Facilities
    office_work_area_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    working_stalls_count = models.PositiveIntegerField(null=True, blank=True)
    tool_equipment_storage_existing = YesNoField()
    tool_equipment_storage_adequate = YesNoField()
    existing_record_keeping_system = YesNoField()
    record_keeping_suitable = YesNoField()
    customers_reception_waiting_area_existing = YesNoField()
    customers_reception_waiting_area_adequate = YesNoField()

    # Safety Measures
    fire_extinguishers_count = models.PositiveIntegerField(null=True, blank=True)
    available_personal_protective_equipment = models.CharField(max_length=255, blank=True)
    security_personnel_count = models.PositiveIntegerField(null=True, blank=True)
    medical_kit_available = YesNoField()
    inflammable_areas = models.CharField(max_length=255, blank=True, help_text="Areas for inflammables such as gasoline, oil, paint, etc.")

    # F. Type of Insurance Coverage
    insurance_expiry_date = models.DateField(null=True, blank=True)
    insurance_coverage_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Amount in PHP")

    # G. Customer Satisfaction Feedback (CSF) and Complaint Handling
    complaints_handling_process_yes = YesNoField()
    complaints_handling_process_no = YesNoField()
    complaints_handling_documented = YesNoField()
    customer_satisfaction_feedback_form_yes = YesNoField()
    customer_satisfaction_feedback_form_no = YesNoField()

    # H. Findings/Remarks
    findings_remarks = models.TextField(blank=True)

    # I. Recommendation
    recommendation_approval = models.BooleanField(default=False)
    recommendation_disapproval = models.BooleanField(default=False)
    recommendation_monitoring_issuance_sco = models.BooleanField(default=False)
    recommendation_new_application = models.BooleanField(default=False)
    recommendation_renewal_application = models.BooleanField(default=False)
    recommendation_continuing_accreditation = models.BooleanField(default=False)

    # Inspection Details
    inspected_by_accreditation_officer = models.CharField(max_length=255, blank=True)
    inspected_by_member = models.CharField(max_length=255, blank=True)

    # Certification
    certification_text = models.TextField(
        default="This is to certify that the Accreditation Officer/s conducted the inspection in our premises today, and the information/data in this Inspection and Validation Report, gathered during the inspection are true and correct.",
        blank=True
    )
    authorized_signatory_name = models.CharField(max_length=255, blank=True)
    authorized_signatory_date = models.DateField(null=True, blank=True)

    # Add M2M if using services
    services_offered = models.ManyToManyField('Service', blank=True, related_name="inspection_reports")

    class Meta:
        verbose_name = "Inspection and Validation Report"
        verbose_name_plural = "Inspection and Validation Reports"
        ordering = ['-date']

    def __str__(self):
        return f"{self.name_of_business} - {self.date}"
        
    def get_recommendation_display(self):
        """Return a human-readable list of selected recommendations"""
        recommendations = []
        if self.recommendation_approval:
            recommendations.append("Approval")
        if self.recommendation_disapproval:
            recommendations.append("Disapproval")
        if self.recommendation_monitoring_issuance_sco:
            recommendations.append("Monitoring/Issuance of SCO")
        if self.recommendation_new_application:
            recommendations.append("New Application")
        if self.recommendation_renewal_application:
            recommendations.append("Renewal Application")
        if self.recommendation_continuing_accreditation:
            recommendations.append("Continuing Accreditation")
        return ", ".join(recommendations) if recommendations else "No recommendations selected"

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