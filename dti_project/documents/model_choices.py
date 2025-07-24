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
    ("other_services", "Other Services"),
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
    "other_services": [
        # Leave empty; user-defined
    ],
}

YES_NO_CHOICES = [('yes', 'Yes'), ('no', 'No')]