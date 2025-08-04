# SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS defines the structure of each form step.
# Each item in the list represents a fieldset (form section) and follows this structure:
# (
#     "Fieldset Title",                  # str: Legend/title of the fieldset
#     [                                  # list: A list of rows
#         [field_name_1, field_name_2],  # Each row is a list of field names to be rendered together
#         [field_name_3],
#         ...
#     ],
#     "fieldset-id"                      # str: The HTML id attribute to assign to this fieldset
# )

# ---------- CREATE VIEW GROUPS ---------------- #

SALES_PROMOTION_FIELD_GROUPS = [
    ("Promotion Details", [['promo_title']], 'promo-title'),
    ("Sponsor", [
        ['sponsor_name', 'sponsor_telephone', 'sponsor_email', 'sponsor_authorized_rep', 'sponsor_designation',
        'sponsor_address']
    ], 'sponsors'),
    ("Advertising Agency", [[
        'advertising_agency_name', 
        'advertising_agency_telephone', 'advertising_agency_email', 'advertising_agency_authorized_rep',
        'advertising_agency_designation', 'advertising_agency_address'
    ]], 'advertising'),
    ("Promo Period",[['promo_period_start', 'promo_period_end']], 'promo-period'),
]

PERSONAL_DATA_SHEET_FIELD_GROUPS = [
    ("Personal Background", 
        [
            ['last_name', 'first_name', 'middle_name'],
            ['email_address', 'contact_number', 'current_address'],
            ['position', 'nationality', 'date_of_birth', 'sex', 'civil_status'],
            ['image']
        ],
        "personal-background"
    ),
]

SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS = [
    ("Application Details", [['application_type', 'category', 'star_rating']], 'application-details'),
    ("Business/Personal Information", [
        ['name_of_business'],
        ['building_name_or_number', 'street_name', 'barangay', 'city_or_municipality', 'province', 'region', 'zip_code'],
        ['email_address', 'mobile_number', 'telephone_number', 'fax_number'],
        ['sex', 'social_classification'] 
    ], 'business-information'),
    ("Authorized Signatory", [['first_name', 'middle_name', 'last_name', 'title', 'suffix', 'designation']]),
    ("Business Classification", 
     [
        ['asset_size', 'form_of_organization', 'industry_classification', 
         'industry_classification', 'annual_gross_service_revenue', 'capital_investment', 'tax_identification_number',
         'date_established', 'total_employees'
         ]
        
        ]
    ),
]

INSPECTION_VALIDATION_REPORT_FIELD_GROUPS = [
    ("Business Name and Address", [['name_of_business', 'address']], 'business'),

    ("Basic Information", [
        ['type_of_application_activity', 'years_in_service', 'types_of_office_shop'],
        ['business_name_cert', 'business_name_cert_remarks'],
        ['accreditation_cert', 'accreditation_cert_remarks'],
        ['service_rates', 'service_rates_remarks'],
    ], 'basic-information'),

    'service_categories', # Already added custom fieldset

    ("Tools and Equipment", [
        ['tools_equipment_complete', 'tools_equipment_serial_no'],
        ['racmac_sres_recovery_machine', 'racmac_serial_no'],
        ['proof_acquisition_recovery_machine'],
    ], 'tools-equipment'),

    ("Competence of Technicians", [
        ['employed_technicians_count', 'average_technician_experience', 'tesda_certification_nc', 'tesda_certification_coc'],
        ['continuous_training_program', 'list_employees_past_2_years'],
        ['refrigerant_storage_disposal_system'],
    ], 'competence-technicians'),

    ("Facilities", [
        ['office_work_area_sqm', 'working_stalls_count'],
        ['tool_equipment_storage_existing', 'tool_equipment_storage_adequate'],
        ['existing_record_keeping_system'],
        ['customers_reception_waiting_area_existing', 'customers_reception_waiting_area_adequate', 'customers_reception_waiting_area_suitable'],
        ['fire_extinguishers_count', ],
        ['available_personal_protective_equipment'],
        ['security_personnel_count', 'available_medical_kit'],
        ['inflammable_areas']
    ], 'facilities'),

    ("Insurance Coverage", [
        ['type_of_insurance_coverage'],
        ['insurance_expiry_date', 'insurance_coverage_amount'],
    ], 'insurance'),

    ("Customer Satisfaction & Complaints", [
        ['complaints_handling_process_exists', 'complaints_handling_process_documented'],
        ['customer_satisfaction_feedback_form_exists'],
    ], 'csf-complaints'),

    ("Findings and Remarks", [
        ['findings_remarks'],
    ], 'findings-remarks'),

    ("Recommendation", [
        ['recommendation', 'inspected_by_accreditation_officer', 'inspected_by_member'], 
    ], 'recommendation'),

    ("Certification", [
        ['authorized_signatory_name', 'authorized_signatory_date']
    ], 'certification')
]

ORDER_OF_PAYMENT_FIELD_GROUPS = [
    ("Name and Address", [
        ['name', 'address']
    ], 'name-and-address'),
    ('Account/Special Collecting Officer', [
        ['account_officer_date', 'account_officer_signature'],
        ['special_collecting_officer_date', 'special_collecting_officer_or_number', 'special_collecting_officer_signature']
    ], 'account-special-collecting-officer')
]

CHECKLIST_EVALUATION_FIELD_GROUPS = [
    ("Business Details", [
        ['name_of_business', 'type_of_application', 'renewal_year', 'star_rating']
    ], 'business-details')
]

# ---------- DETAIL VIEW GROUPS ---------------- #

SALES_PROMOTION_DETAIL_GROUPS = [
    ("Base Details", [
        ("User", "user"),
        ("Date Filed", "date_filed"),
        ("Promo Period Start", "promo_period_start"),
        ("Promo Period End", "promo_period_end"),
    ], "dates"),
    ("Sponsor Details", [
        ("Sponsor Name", "sponsor_name"),
        ("Sponsor Address", "sponsor_address"),
        ("Sponsor Telephone", "sponsor_telephone"),
        ("Sponsor Email", "sponsor_email"),
        ("Sponsor Authorized Rep", "sponsor_authorized_rep"),
        ("Sponsor Designation", "sponsor_designation"),
    ], "sponsors"),
    ("Advertising Details", [
        ("Advertising Agency Name", "advertising_agency_name"),
        ("Advertising Agency Address", "advertising_agency_address"),
        ("Advertising Agency Telephone", "advertising_agency_telephone"),
        ("Advertising Agency Email", "advertising_agency_email"),
        ("Advertising Agency Authorized Rep", "advertising_agency_authorized_rep"),
        ("Advertising Agency Designation", "advertising_agency_designation"),
    ], "advertising"),
]

PERSONAL_DATA_SHEET_DETAIL_GROUPS = [
    ("Personal Information", [
        ("Image", 'image'),
        ("First Name", "first_name"),
        ("Middle Name", "middle_name"),
        ("Last Name", "last_name"),
        ("Email Address", "email_address"),
        ("Position", "position"),
        ("Date of Birth", "date_of_birth"),
        ("Nationality", "nationality"),
        ("Sex", "sex"),
        ("Civil Status", "civil_status"),
        ("Current Address", "current_address"),
        ("Contact Number", "contact_number")
    ], "personal-info"),
]

PERSONAL_DATA_SHEET_TAB_SECTIONS = [
    {
        'id': 'employee-backgrounds',
        'title': 'Employee Backgrounds',
        'relation': 'employee_backgrounds',
        'icon': 'fas fa-briefcase',  
        'active': True,
    },
    {
        'id': 'trainings-attended',
        'title': 'Trainings Attended',
        'relation': 'trainings_attended',
        'icon': 'fas fa-chalkboard-teacher',  
        'active': False,
    },
    {
        'id': 'educational-attainment',
        'title': 'Educational Attainment',
        'relation': 'educational_attainment',
        'icon': 'fas fa-graduation-cap', 
        'active': False,
    },
    {
        'id': 'character-references',
        'title': 'Character References',
        'relation': 'character_references',
        'icon': 'fas fa-address-book',  
        'active': False,
    }
]
