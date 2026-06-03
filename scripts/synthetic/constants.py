RANDOM_SEED = 42

PLAN_COUNT = 5
DRUG_COUNT = 25
PHARMACY_COUNT = 10
MEMBER_COUNT = 50
PROVIDER_COUNT = 15
CLAIM_COUNT = 100

TERMINATED_MEMBER_COUNT = 5
OUT_OF_NETWORK_PHARMACY_COUNT = 2

US_STATES = [
    "AL", "AZ", "CA", "CO", "FL", "GA", "IL", "MA", "MI", "NC",
    "NJ", "NY", "OH", "PA", "TX", "VA", "WA",
]

PLAN_TYPES = ["commercial", "medicare", "medicaid", "hmo", "ppo"]

PLAN_NAMES = [
    "Gold PPO",
    "Silver HMO",
    "Bronze Commercial",
    "Medicare Advantage",
    "Medicaid Basic",
]

CLAIM_STATUSES = ["paid", "rejected", "reversed"]

NETWORK_STATUSES = ["in_network", "out_of_network"]

MEMBER_STATUSES = ["active", "terminated"]

SPECIALTIES = [
    "Family Medicine",
    "Internal Medicine",
    "Cardiology",
    "Endocrinology",
    "Psychiatry",
    "Pediatrics",
]

THERAPEUTIC_CLASSES = [
    "ACE Inhibitor",
    "Statin",
    "Beta Blocker",
    "SSRI",
    "Proton Pump Inhibitor",
    "NSAID",
    "Antibiotic",
    "Antidiabetic",
    "Antihypertensive",
    "Bronchodilator",
]

DRUG_CATALOG = [
    {"ndc_code": "00002-0800-01", "drug_name": "Humalog 100U/mL", "therapeutic_class": "Antidiabetic", "brand_generic": "brand"},
    {"ndc_code": "00003-0293-20", "drug_name": "Lipitor 20mg Tablet", "therapeutic_class": "Statin", "brand_generic": "brand"},
    {"ndc_code": "00004-0802-85", "drug_name": "Lisinopril 10mg Tablet", "therapeutic_class": "ACE Inhibitor", "brand_generic": "generic"},
    {"ndc_code": "00006-4095-31", "drug_name": "Metformin 500mg Tablet", "therapeutic_class": "Antidiabetic", "brand_generic": "generic"},
    {"ndc_code": "00007-4888-13", "drug_name": "Atorvastatin 40mg Tablet", "therapeutic_class": "Statin", "brand_generic": "generic"},
    {"ndc_code": "00009-1234-01", "drug_name": "Amlodipine 5mg Tablet", "therapeutic_class": "Antihypertensive", "brand_generic": "generic"},
    {"ndc_code": "00009-2345-02", "drug_name": "Metoprolol 50mg Tablet", "therapeutic_class": "Beta Blocker", "brand_generic": "generic"},
    {"ndc_code": "00009-3456-03", "drug_name": "Omeprazole 20mg Capsule", "therapeutic_class": "Proton Pump Inhibitor", "brand_generic": "generic"},
    {"ndc_code": "00009-4567-04", "drug_name": "Sertraline 50mg Tablet", "therapeutic_class": "SSRI", "brand_generic": "generic"},
    {"ndc_code": "00009-5678-05", "drug_name": "Ibuprofen 200mg Tablet", "therapeutic_class": "NSAID", "brand_generic": "generic"},
    {"ndc_code": "00009-6789-06", "drug_name": "Amoxicillin 500mg Capsule", "therapeutic_class": "Antibiotic", "brand_generic": "generic"},
    {"ndc_code": "00009-7890-07", "drug_name": "Albuterol 90mcg Inhaler", "therapeutic_class": "Bronchodilator", "brand_generic": "brand"},
    {"ndc_code": "00009-8901-08", "drug_name": "Losartan 50mg Tablet", "therapeutic_class": "Antihypertensive", "brand_generic": "generic"},
    {"ndc_code": "00009-9012-09", "drug_name": "Gabapentin 300mg Capsule", "therapeutic_class": "NSAID", "brand_generic": "generic"},
    {"ndc_code": "00009-0123-10", "drug_name": "Levothyroxine 50mcg Tablet", "therapeutic_class": "Antidiabetic", "brand_generic": "generic"},
    {"ndc_code": "00009-1122-11", "drug_name": "Crestor 10mg Tablet", "therapeutic_class": "Statin", "brand_generic": "brand"},
    {"ndc_code": "00009-2233-12", "drug_name": "Zoloft 100mg Tablet", "therapeutic_class": "SSRI", "brand_generic": "brand"},
    {"ndc_code": "00009-3344-13", "drug_name": "Prilosec 20mg Capsule", "therapeutic_class": "Proton Pump Inhibitor", "brand_generic": "brand"},
    {"ndc_code": "00009-4455-14", "drug_name": "Carvedilol 25mg Tablet", "therapeutic_class": "Beta Blocker", "brand_generic": "generic"},
    {"ndc_code": "00009-5566-15", "drug_name": "Azithromycin 250mg Tablet", "therapeutic_class": "Antibiotic", "brand_generic": "generic"},
    {"ndc_code": "00009-6677-16", "drug_name": "Glipizide 5mg Tablet", "therapeutic_class": "Antidiabetic", "brand_generic": "generic"},
    {"ndc_code": "00009-7788-17", "drug_name": "Enalapril 10mg Tablet", "therapeutic_class": "ACE Inhibitor", "brand_generic": "generic"},
    {"ndc_code": "00009-8899-18", "drug_name": "Advair 250/50 Inhaler", "therapeutic_class": "Bronchodilator", "brand_generic": "brand"},
    {"ndc_code": "00009-9900-19", "drug_name": "Simvastatin 20mg Tablet", "therapeutic_class": "Statin", "brand_generic": "generic"},
    {"ndc_code": "00009-0011-20", "drug_name": "Escitalopram 10mg Tablet", "therapeutic_class": "SSRI", "brand_generic": "generic"},
]

DAYS_SUPPLY_OPTIONS = [30, 60, 90]
