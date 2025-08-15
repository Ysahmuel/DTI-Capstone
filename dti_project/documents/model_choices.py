YES_NO_CHOICES = [
    ('Yes', 'Yes'),
    ('No', 'No'),
]

APPLICATION_OR_ACTIVITY_CHOICES = [
    ('new', 'New Application'),
    ('renewal', 'Renewal Application'),
    ('monitoring', 'Monitoring/Issuance of SCO'),
    ('continuing', 'Continuing Accreditation'),
]

OFFICE_SHOP_CHOICES = [
    ('Main', 'Main'),
    ('Branch', 'Branch'),
]

APPLICATION_OR_ACTIVITY_CHOICES = [
    ('new', 'New'),
    ('renewal', 'Renewal'),
    ('monitoring', 'Monitoring'),
]

SERVICE_CATEGORY_CHOICES = [
    ("electronics", "Electronics"),
    ("aircon_refrigeration", "Aircon/Refrigeration"),
    ("office_machines", "Office Machines"),
    ("motor_vehicles", "Motor Vehicles and Heavy Equipment"),
    ("wheel_services", "Complete Wheel Services"),
    ("engineering_works", "Engines and Engineering Works (Machine Shops)"),
    ("welding", "Welding Services"),
]

SERVICES_BY_CATEGORY = {
    "electronics": [
        "Installation",
        "Maintenance",
        "Service",
        "Repair",
        "Reconditioning",
        "Reinstallation",
        "Disassembly",
        "Reassembly",
    ],
    "aircon_refrigeration": [
        "RAC Servicing (DonRac) (Type A)",
        "Commercial Air-Conditioning Installation and Servicing (Type B)",
        "Commercial Refrigeration Installation and Servicing (Type B)",
        "Land-Based Transport Mobile Air-Conditioning (MAC) (Type C)",
    ],
    "office_machines": [
        "Mechanical/Electromechanical Equipment Servicing",
        "Electrical/Data Processing Equipment Servicing",
    ],
    "motor_vehicles": [
        "Painting",
        "Body Works",
        "Brake System",
        "Transmission – Standard",
        "Transmission – Automatic",
        "Hydraulic/Pneumatic/Air Systems",
        "Electrical System",
        "Engine Overhauling",
        "Front Suspension",
        "Lubricating System",
        "Glass Replacement & Door Repair",
        "Truck Rebuilding/Assembly",
        "Steering Mechanism",
        "Water/Oil Fuel Pump",
        "Instrumental Panel Services",
        "Car Accessories Installation and Repair",
        "Service Motorcycle/Small Engine System",
        "Auto Airconditioning Services",
    ],
    "wheel_services": [
        "Complete Wheel Alignment",
        "Wheel Balancing",
        "Overhaul Motorcycle/Small Engine",
    ],
    "engineering_works": [
        "Crankshaft Regrinding",
        "Cylinder Reboring",
        "Camshaft & Crank Line Boring",
        "Cylinder Ridge Reaming",
        "Cylinder Sleeving Re-standard",
        "Cylinder Sleeving Works",
        "Clutch Plate/Flywheel Refacing",
        "Cracked Cylinder Head Welding",
        "Connecting Rod Resizing",
        "Piston Rehabilitation (Welding & Machining)",
        "Cracked Valve Seats Refacing",
        "Valve/Valve Seats Refacing",
    ],
    "welding": [
        "Rebabitting Bearing Work",
        "Brake Drum Refacing",
        "Lathe Works",
        "Electric/Oxy Acetylene Welding",
        "Cracked Cylinder Head Welding",
        "Shaft Straightening & Aligning",
        "Propeller Balancing and Repair",
        "Vapor Steam & Degreasing",
        "Metalworking",
        "Fabrication/Duplication",
        "Parts Duplication/Manufacturing",
    ],
}

YES_NO_CHOICES = [('yes', 'Yes'), ('no', 'No')]

RECOMMENDATION_CHOICES = [
    ('approval', 'Approval'),
    ('disapproval', 'Disapproval'),
    ('monitoring', 'Monitoring/Issuance of SCO'),
    ('new_application', 'New Application'),
    ('renewal', 'Renewal Application'),
    ('continuing_accreditation', 'Continuing Accreditation'),
]

STAR_RATING_CHOICES = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5')
]

REQUIREMENT_CHOICES = [
    ("req_1", "Original/e-copy notarized completely filled out application form with Undertaking/Warranty (Minimum of 90 days) signed by the owner or authorized agent (signed by the proprietor for SPP, if other than the Proprietor, attach SPA/Authorization: President/Managing Partner for Corporation/Partnership, otherwise, copy of Board Resolution/Secretary's Certificate with authorized signatory)"),
    ("req_2", "Copy of Valid Business Name Certificate of Registration for Single Proprietorship or Certified true copy of company Partnership and Articles of Incorporation/Partnership for Corporation/Partnership, GDA certificate of registration and Articles of Cooperation for Cooperatives, SEC Registration Certificate only, if no amendments made in Albay Ps"),
    ("req_3", "Copy of Latest Accreditation Certificate"),
    ("req_4", "Original-copy Certified List of Mechanics/Technicians and Position with Personnel/no Data Sheet"), 
    ("req_5", "Copy of valid and relevant TESDA Certificate (National Certificate or Certificate of Competency for Technical Employees)"),
    ("req_6", "Original/e-copy Certified List of Trainings Attended by the Employees/Technicians within the past 2 years"),
    ("req_7", "Original/e-copy List of Shop Tools and Equipment"),
    ("req_8", "Original/e-copy Shop Floor Plan/Layout/Size/No. of Stalls/Working Bays and interior pictures of the Shop/Office – showing front (with signages) and interior/working area"),
    ("req_9", "Originally issued Certification (in lieu of items 6 and 8) that there are no changes on the said items for renewals, provided that said requirements have been previously submitted"),
    ("req_10", "Copy of Comprehensive Insurance Policy covering the customer's motor vehicle while in custody and use against theft, pilferage, fire, flood and loss. Insurance coverage must be P100,000.00 year and its expiry date must be on or after December 31st 20__, and copy of official receipt (proof of payment of insurance premiums)"),
    ("req_11", "Original Affidavit stating that all services and repairs are done in the clients presence and that they conduct all services and repairs in their client's premises. (In lieu of insurance policy)"),
    ("req_12", "In places where there are no insurance companies willing to undertake the risk due to the peace and order situation in the area the Director may grant exemption upon sufficient proof of such circumstances"),
    ("req_13", "Copy of valid dealership agreement (five star only) Motor Vehicle, Ref and Aircon, Office Machine/Data Processing Equipment)"),
    ("req_14", "Copy of Valid Contract of Service, (if any)"),
    ("req_15", "Original copy of Performance Bond policy and official receipt with minimum coverage of P50,000. (in favor of the DTI valid up to December 31, 20__ for 3 to 5 STAR, New or Renewal)")
]

REMARKS_CHOICES = [
    ("applicable_only", "applicable only for ref/aircon shops"),
    ("not_applicable_if_no_changes", "not applicable, if no changes"),
    ("not_applicable_if_not_charges", "not applicable, if not charges"),
    ("not_applicable", "not applicable"),
    ("see_attached_sample_form", "see attached sample form"),
    ("applicable_only_for_5_star", "applicable only for 5 star application"),
    ("not_applicable_for_one_and_two_star", "not applicable for one & two star application")
]

PERMIT_FEE_REMARK_CHOICES = [
    ('R', 'R - Several provinces / cities / municipalities within a single region'),
    ('P', 'P - Single province / city / municipality'),
    ('X', 'X - 2 or more regions excluding Metro Manila'),
    ('A', 'A - Additional fees due to reassessment of premium and prizes'),
]

REGION_CHOICES = [
    ("NCR", "National Capital Region (NCR)"),
    ("CAR", "Cordillera Administrative Region (CAR)"),
    ("Region I", "Ilocos Region (Region I)"),
    ("Region II", "Cagayan Valley (Region II)"),
    ("Region III", "Central Luzon (Region III)"),
    ("Region IV-A", "CALABARZON (Region IV-A)"),
    ("MIMAROPA", "MIMAROPA Region"),
    ("Region V", "Bicol Region (Region V)"),
    ("Region VI", "Western Visayas (Region VI)"),
    ("Region VII", "Central Visayas (Region VII)"),
    ("Region VIII", "Eastern Visayas (Region VIII)"),
    ("Region IX", "Zamboanga Peninsula (Region IX)"),
    ("Region X", "Northern Mindanao (Region X)"),
    ("Region XI", "Davao Region (Region XI)"),
    ("Region XII", "SOCCSKSARGEN (Region XII)"),
    ("Region XIII", "Caraga (Region XIII)"),
    ("BARMM", "Bangsamoro Autonomous Region in Muslim Mindanao (BARMM)"),
]