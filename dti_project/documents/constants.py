SALES_PROMOTION_FIELD_GROUPS = [
    ("Promotion Details", ['promo_title']),
    ("Sponsor", [
        'sponsor_name', 'sponsor_telephone', 'sponsor_email',
        'sponsor_authorized_rep', 'sponsor_designation',
        'sponsor_address'
    ]),
    ("Advertising Agency", [
        'advertising_agency_name', 'advertising_agency_telephone',
        'advertising_agency_email', 'advertising_agency_authorized_rep',
        'advertising_agency_designation', 'advertising_agency_address'
    ]),
    ("Promo Period", ['promo_period_start', 'promo_period_end']),
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
    ("Authorized Signatory", [['title', 'first_name', 'middle_name', 'last_name', 'suffix', 'designation']]),
    ("Business Classification", [['asset_size', 'form_of_organization', 'industry_classification']]),
]