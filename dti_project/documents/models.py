from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

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
    
class TrainingsAttended(models.Model):
    personal_data_sheet = models.ForeignKey(PersonalDataSheet, related_name='trainings_attended', on_delete=models.CASCADE)
    training_course = models.CharField(max_length=255)
    conducted_by = models.CharField(max_length=255)

    # Training Period
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.training_course
    
class EducationalAttainment(models.Model):
    personal_data_sheet = models.ForeignKey(PersonalDataSheet, related_name='educational_attainment', on_delete=models.CASCADE)
    school = models.CharField(max_length=255)
    course = models.CharField(max_length=255)

    # Period
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.school} - {self.course}"
    
class CharacterReference(models.Model):
    personal_data_sheet = models.ForeignKey(PersonalDataSheet, related_name='character_references', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    company = models.CharField(max_length=50)
    email = models.EmailField()
    contact_number = models.CharField(max_length=20)

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

    annual_gross_service_revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
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
         WARRANTS THE QUALITY OF WORKMANSHIP AND PROCESS UNDERTAKEN BY THE SHOP FOR A PERIOD OF {warranty_period} ({warranty_period_words}) DAYS COUNTED FROM THE DATE OF ACTUAL RELEASE AND DELIVERY OF EACH AND/OR JOB ORDER TO THE RESPECTIVE CUSTOMER.

        This warranty does not cover damage caused by misuse, accidents, or alteration of workmanship; in addition, it is expressly understood that the shop management shall not be liable for any patent defect in the product and which is not included in the job contract.

        We further undertake to abide by the rules and regulations promulgated by DTI and the terms and conditions of this warranty. In the event of violation on our part, our accreditation certificate may be cancelled at the discretion of the DTI.
        """
        
        # Convert number to words for the parentheses
        warranty_period_words = self.number_to_words(self.warranty_period)
        
        return warranty_template.format(
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

class InspectionValidationReport(models.Model):
    """
    DTI-ALBAY Provincial Office Accreditation of Service & Repair Enterprises
    Inspection/Validation Report
    """
    
    # Header Information
    date = models.DateField()
    business_name = models.CharField(max_length=255)
    business_address = models.TextField()
    
    APPLICATION_TYPE_CHOICES = [
        ('new', 'New'),
        ('renewal', 'Renewal'),
        ('monitoring', 'Monitoring'),
    ]
    application_type = models.CharField(max_length=15, choices=APPLICATION_TYPE_CHOICES)
    
    # A. Basic Information
    years_in_service = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Number of years in service business"
    )
    
    OFFICE_TYPE_CHOICES = [
        ('main', 'Main'),
        ('branch', 'Branch'),
    ]
    office_type = models.CharField(max_length=10, choices=OFFICE_TYPE_CHOICES)
    validate_all_branches = models.BooleanField(default=False, help_text="Validate if all branches are accredited")
    
    # Display of Required Certificates/Documents
    business_name_certificate = models.BooleanField(default=False)
    business_name_certificate_remarks = models.TextField(blank=True)
    
    accreditation_certificate = models.BooleanField(default=False)
    accreditation_certificate_remarks = models.TextField(blank=True)
    
    service_rates = models.BooleanField(default=False)
    service_rates_remarks = models.TextField(blank=True)
    
    # Other services text field
    other_services = models.TextField(blank=True, help_text="Other services offered")
    
    # C. Tools and Equipment
    tools_equipment_complete = models.BooleanField(default=False)
    tools_equipment_serial_no = models.CharField(max_length=100, blank=True)
    has_recovery_machine = models.BooleanField(default=False)
    recovery_machine_proof = models.TextField(blank=True)
    
    # D. Competence of Technicians
    num_employed_technicians = models.PositiveIntegerField(default=0)
    avg_technician_experience = models.PositiveIntegerField(
        default=0,
        help_text="Average technician experience in years"
    )
    coc_certification = models.CharField(max_length=50, blank=True, help_text="COC certification")
    tesda_certification = models.CharField(max_length=50, blank=True, help_text="TESDA certification NC")
    
    has_training_program = models.BooleanField(default=False)
    has_training_list = models.BooleanField(default=False)
    refrigerant_recovery_disposal_consistent = models.BooleanField(default=False)
    
    # E. Facilities
    shop_area_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    working_stalls_bays = models.PositiveIntegerField(default=0)
    
    tool_equipment_storage_existing = models.BooleanField(default=False)
    tool_equipment_storage_adequate = models.BooleanField(default=False)
    
    record_keeping_system_existing = models.BooleanField(default=False)
    record_keeping_system_adequate = models.BooleanField(default=False)
    record_keeping_system_suitable = models.BooleanField(default=False)
    
    customer_reception_existing = models.BooleanField(default=False)
    customer_reception_adequate = models.BooleanField(default=False)
    customer_reception_suitable = models.BooleanField(default=False)
    
    # Safety Measures
    fire_extinguishers_count = models.PositiveIntegerField(default=0)
    medical_kit_available = models.BooleanField(default=False)
    security_personnel_count = models.PositiveIntegerField(default=0)
    flammable_areas_safe = models.BooleanField(default=False)
    
    # F. Type of Insurance Coverage
    insurance_type = models.CharField(max_length=100, blank=True)
    insurance_expiry_date = models.DateField(null=True, blank=True)
    insurance_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    insurance_currency = models.CharField(max_length=10, default='PHP')
    
    # G. Customer Satisfaction Feedback (CSF) and Complaint Handling
    has_complaints_process = models.BooleanField(default=False)
    complaints_process_documented = models.BooleanField(default=False)
    has_csf_form = models.BooleanField(default=False)
    
    # H. Findings/Remarks
    findings_remarks = models.TextField(blank=True)
    
    # Inspection Details
    inspector_name = models.CharField(max_length=100, blank=True)
    inspector_title = models.CharField(max_length=100, default='Accreditation Officer/Leader')
    member_name = models.CharField(max_length=100, blank=True)
    inspection_date = models.DateField(null=True, blank=True)
    
    # Certification
    authorized_signatory_name = models.CharField(max_length=100, blank=True)
    certification_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Inspection/Validation Report"
        verbose_name_plural = "Inspection/Validation Reports"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.business_name} - {self.date} - {self.get_application_type_display()}"
    
    @property
    def form_code(self):
        """Returns the form code from the document"""
        return "FM-SR-03"
    
    @property
    def revision(self):
        """Returns the revision number"""
        return "1"


class ServiceCategory(models.Model):
    """Master list of all service categories and subcategories"""
    
    MAIN_CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('electrical', 'Electrical'),
        ('aircon_refrigeration', 'Aircon/Refrigeration'),
        ('office_machine', 'Office Machine and Data Processing Equipment'),
        ('medical_dental', 'Medical/Dental'),
        ('motor_vehicles', 'Motor Vehicles and Heavy Equipment'),
        ('engines_engineering', 'Engines and Engineering Works (Machine Shops)'),
    ]
    
    CATEGORY_TYPE_CHOICES = [
        ('main', 'Main Category'),
        ('sub', 'Sub Category'),
        ('item', 'Service Item'),
    ]
    
    main_category = models.CharField(max_length=30, choices=MAIN_CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES, default='item')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_selectable = models.BooleanField(default=True, help_text="Can this category be selected in reports?")
    
    class Meta:
        verbose_name_plural = "Service Categories"
        unique_together = ['main_category', 'subcategory']
        ordering = ['main_category', 'subcategory']
    
    def __str__(self):
        return f"{self.get_main_category_display()} - {self.subcategory}"
    
    def get_full_path(self):
        """Returns the full hierarchical path of the category"""
        path = [self.subcategory]
        current = self.parent
        while current:
            path.insert(0, current.subcategory)
            current = current.parent
        return " > ".join(path)
    
    def get_children(self):
        """Returns all direct children of this category"""
        return ServiceCategory.objects.filter(parent=self)
    
    def get_all_descendants(self):
        """Returns all descendants of this category"""
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants


class ReportService(models.Model):
    """Services selected in the inspection report (B. Category of Services Offered)"""
    report = models.ForeignKey(
        InspectionValidationReport, 
        on_delete=models.CASCADE, 
        related_name='selected_services'
    )
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['report', 'service_category']
        verbose_name = "Report Service"
        verbose_name_plural = "Report Services"
    
    def __str__(self):
        return f"{self.report.business_name} - {self.service_category}"


class ReportRecommendation(models.Model):
    """Recommendations for the inspection report (I. Recommendation)"""
    
    RECOMMENDATION_CHOICES = [
        ('approval', 'Approval'),
        ('disapproval', 'Disapproval'),
        ('monitoring_sco', 'Monitoring/Issuance of SCO'),
        ('new_application', 'New Application'),
        ('renewal_application', 'Renewal Application'),
        ('continuing_accreditation', 'Continuing Accreditation'),
    ]
    
    report = models.ForeignKey(
        InspectionValidationReport, 
        on_delete=models.CASCADE, 
        related_name='recommendations'
    )
    recommendation = models.CharField(max_length=25, choices=RECOMMENDATION_CHOICES)
    
    class Meta:
        unique_together = ['report', 'recommendation']
        verbose_name = "Report Recommendation"
        verbose_name_plural = "Report Recommendations"
    
    def __str__(self):
        return f"{self.report.business_name} - {self.get_recommendation_display()}"


# Pre-populated service categories data for initial setup
SERVICE_CATEGORIES_DATA = [
    # Electronics - Main Category
    ('electronics', 'Electronics', 'ELEC_MAIN', 'main', None),
    ('electronics', 'Installation', 'ELEC_INSTALL', 'item', 'ELEC_MAIN'),
    ('electronics', 'Maintenance', 'ELEC_MAINT', 'item', 'ELEC_MAIN'),
    ('electronics', 'Service', 'ELEC_SERV', 'item', 'ELEC_MAIN'),
    ('electronics', 'Repair', 'ELEC_REPAIR', 'item', 'ELEC_MAIN'),
    ('electronics', 'Reconditioning', 'ELEC_RECON', 'item', 'ELEC_MAIN'),
    ('electronics', 'Reinstallation', 'ELEC_REINST', 'item', 'ELEC_MAIN'),
    
    # Electrical - Main Category
    ('electrical', 'Electrical', 'ELECT_MAIN', 'main', None),
    ('electrical', 'Assembly', 'ELECT_ASSEM', 'item', 'ELECT_MAIN'),
    ('electrical', 'Dis-assembly', 'ELECT_DISAS', 'item', 'ELECT_MAIN'),
    ('electrical', 'Repair', 'ELECT_REPAIR', 'item', 'ELECT_MAIN'),
    ('electrical', 'Rewinding', 'ELECT_REWIND', 'item', 'ELECT_MAIN'),
    ('electrical', 'Re-assembly', 'ELECT_REASS', 'item', 'ELECT_MAIN'),
    
    # Aircon/Refrigeration - Main Category
    ('aircon_refrigeration', 'Aircon/Refrigeration', 'RAC_MAIN', 'main', None),
    ('aircon_refrigeration', 'RAC Servicing (DomRac) (Type A)', 'RAC_DOMRAC_A', 'item', 'RAC_MAIN'),
    ('aircon_refrigeration', 'Commercial Air-Conditioning Installation and Servicing (Type B)', 'RAC_COMM_AC_B', 'item', 'RAC_MAIN'),
    ('aircon_refrigeration', 'Commercial Refrigeration Installation and Servicing (Type B)', 'RAC_COMM_REF_B', 'item', 'RAC_MAIN'),
    ('aircon_refrigeration', 'Land-Based Transport Mobile Air-Conditioning (MAC) (Type C)', 'RAC_LAND_MAC_C', 'item', 'RAC_MAIN'),
    
    # Office Machine and Data Processing Equipment - Main Category
    ('office_machine', 'Office Machine and Data Processing Equipment', 'OFFICE_MAIN', 'main', None),
    ('office_machine', 'Mechanical/Electromechanical Equipment Servicing', 'OFFICE_MECH_ELEC', 'item', 'OFFICE_MAIN'),
    ('office_machine', 'Electronic Office/Data Processing Equipment Servicing', 'OFFICE_ELEC_DATA', 'item', 'OFFICE_MAIN'),
    
    # Medical/Dental - Main Category
    ('medical_dental', 'Medical/Dental', 'MED_DENTAL_MAIN', 'main', None),
    ('medical_dental', 'Medical/Dental Equipment Servicing', 'MED_DENTAL', 'item', 'MED_DENTAL_MAIN'),
    
    # Motor Vehicles and Heavy Equipment - Main Category
    ('motor_vehicles', 'Motor Vehicles and Heavy Equipment', 'MV_MAIN', 'main', None),
    ('motor_vehicles', 'Painting', 'MV_PAINT', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Body Works', 'MV_BODY', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Brake System', 'MV_BRAKE', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Transmission-Standard', 'MV_TRANS_STD', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Transmission-Automatic', 'MV_TRANS_AUTO', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Hydraulic/Pneumatic/Air Systems', 'MV_HYDRAULIC', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Engine Overhauling', 'MV_ENGINE', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Front Suspension', 'MV_FRONT_SUSP', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Complete Wheel Alignment', 'MV_WHEEL_ALIGN', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Wheel Balancing', 'MV_WHEEL_BAL', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Overhaul Motorcycle/Small Engine', 'MV_MOTOR_OVER', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Lubricating System', 'MV_LUBRIC', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Glass Replacement & Door Repair', 'MV_GLASS', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Truck Rebuilding/Assembly', 'MV_TRUCK_REB', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Auto Electrical Repair', 'MV_AUTO_ELEC', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Steering Mechanism', 'MV_STEERING', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Water Oil Fuel Pump', 'MV_PUMP', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Instrumental Panel Services', 'MV_PANEL', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Car Accessories Installation and Repair connected to auto electrical system', 'MV_CAR_ACC', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Service motorcycle/small engine system', 'MV_MOTOR_SERV', 'item', 'MV_MAIN'),
    ('motor_vehicles', 'Auto Airconditioning Services', 'MV_AUTO_AC', 'item', 'MV_MAIN'),
    
    # Engines and Engineering Works (Machine Shops) - Main Category
    ('engines_engineering', 'Engines and Engineering Works (Machine Shops)', 'ENG_MAIN', 'main', None),
    ('engines_engineering', 'Crankshaft Regrinding', 'ENG_CRANK_REGR', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Cylinder Reboring', 'ENG_CYL_REBOR', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Camshaft & Crank Line Boring', 'ENG_CAM_CRANK', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Cylinder Ridge Reaming', 'ENG_CYL_RIDGE', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Cylinder Sleeving Work-Standard', 'ENG_CYL_SLEEV_STD', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Cylinder Sleeving Work', 'ENG_CYL_SLEEV', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Clutch Plate/Flywheel Refacing', 'ENG_CLUTCH', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Cracked Cylinder Black Repair', 'ENG_CRACK_CYL', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Connecting Rod Resizing', 'ENG_CONN_ROD', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Piston Rehab. (Welding & Machining)', 'ENG_PISTON', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Cracked Valve Seats Repair', 'ENG_VALVE_SEAT', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Valve/Valve Seats Refacing', 'ENG_VALVE_REF', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Rebatting Bearing Work', 'ENG_BEARING', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Brake Drum Refacing', 'ENG_BRAKE_DRUM', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Lathe Works', 'ENG_LATHE', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Electric/Oxy Acetylene Welding', 'ENG_WELDING', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Cracked Cylinder Head Welding', 'ENG_CYL_HEAD', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Hydraulic Cylinder Head Welding', 'ENG_HYD_CYL', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Shaft Straightening & Aligning', 'ENG_SHAFT', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Propeller Balancing and Repair', 'ENG_PROPELLER', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Vapor Steam & Degreasing', 'ENG_VAPOR', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Metalizing Work', 'ENG_METAL', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Fabrication/Duplication', 'ENG_FABRIC', 'item', 'ENG_MAIN'),
    ('engines_engineering', 'Parts Duplication/Manufacturing', 'ENG_PARTS', 'item', 'ENG_MAIN'),
]


class ServiceCategoryManager(models.Manager):
    """Manager for ServiceCategory with helper methods"""
    
    def populate_categories(self):
        """Populate service categories from predefined data"""
        # First pass: create all categories
        category_map = {}
        for main_category, subcategory, code, category_type, parent_code in SERVICE_CATEGORIES_DATA:
            category = self.get_or_create(
                code=code,
                defaults={
                    'main_category': main_category,
                    'subcategory': subcategory,
                    'category_type': category_type,
                    'is_selectable': category_type == 'item'  # Only items are selectable
                }
            )[0]
            category_map[code] = category
        
        # Second pass: set parent relationships
        for main_category, subcategory, code, category_type, parent_code in SERVICE_CATEGORIES_DATA:
            if parent_code:
                category = category_map[code]
                parent = category_map[parent_code]
                category.parent = parent
                category.save()
    
    def by_main_category(self, main_category):
        """Get all subcategories for a main category"""
        return self.filter(main_category=main_category)
    
    def main_categories(self):
        """Get all main categories"""
        return self.filter(category_type='main')
    
    def selectable_items(self):
        """Get all selectable service items"""
        return self.filter(is_selectable=True)
    
    def items_by_main_category(self, main_category):
        """Get all selectable items for a main category"""
        return self.filter(main_category=main_category, is_selectable=True)


# Add manager to ServiceCategory
ServiceCategory.add_to_class('objects', ServiceCategoryManager())