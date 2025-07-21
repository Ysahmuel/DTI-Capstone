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
        'id': 'training-courses',
        'title': 'Training Courses',
        'relation': 'training_courses',
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
