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

PERSONAL_DATA_SHEET_DETAIL_GROUPS = [
    ("Personal Information", [
        ("First Name", "first_name"),
        ("Last Name", "last_name"),
        ("Middle Name", "middle_name"),
        ("Email", "email"),
        ("Phone", "phone"),
        ("Date of Birth", "date_of_birth"),
    ], "personal-info"),
]