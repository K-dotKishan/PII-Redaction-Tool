"""Configuration for PII Redaction Tool"""
import re

# PII Categories
PII_CATEGORIES = [
    "PERSON",
    "EMAIL", 
    "PHONE",
    "COMPANY",
    "ADDRESS",
    "SSN",
    "CREDIT_CARD",
    "DOB",
    "IP"
]

# DOCUMENT-SPECIFIC CONFIGURATION
# For a Red Herring Prospectus, the main company and subsidiaries are NOT PII
# They are the subject of the document and must be preserved

# Main company and subsidiaries to PRESERVE (do not redact)
PROTECTED_COMPANIES = [
    'KSH International Limited',
    'KSH INTERNATIONAL LIMITED',
    'KSH Distriparks Private Limited',
    'KSH Integrated Logistics Private Limited',
    'Waterloo Industrial Park',  # Covers all variants
    'Kushal Motors and Electricals Private Limited',
    'Bhandary Metal Extrusion Private Limited',  # Historical name
]

# Partner/vendor companies to PRESERVE (legitimate business entities in prospectus)
PROTECTED_BUSINESS_ENTITIES = [
    'ICICI Bank Limited',
    'ICICI Securities',
    'HDFC Bank',
    'HDFC Limited',
    'State Bank of India',
    'Nuvama Wealth Management Limited',
    'CARE Ratings Limited',
    'Care Analytics and Advisory Private Limited',
    'Kirtane & Pandit LLP',
    'MUFG',
    'Vedanta Limited',
    'Nidec Industrial',
    'Link Intime',
    'Formerly Link Intime India Private Limited',
    'BSE Limited',
    'National Stock Exchange',
    'SEBI',
    'Registrar of Companies',
]

# Generic references to ALWAYS preserve
GENERIC_COMPANY_REFS = [
    'our company', 'the company', 'said company', 'this company',
    'the issuer', 'our issuer', 'the promoter', 'our promoter',
    'the promoters', 'our promoters', 'the board', 'our board',
]

# Regex patterns for PII detection
PATTERNS = {
    "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "PHONE": r'(?:\+91[\s-]?)?(?:\d{2,4}[\s-]?)?\d{3,4}[\s-]?\d{3,4}',
    "IP": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
    "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
    "CREDIT_CARD": r'\b(?:\d{4}[\s-]?){3}\d{4}\b',
    "DOB_CONTEXT": r'(?:Date of Birth|DOB|Birth Date|Born|Date Of Birth)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
}

# Company name indicators
COMPANY_INDICATORS = [
    'Limited', 'Ltd.', 'Ltd', 'Private Limited', 'Pvt. Ltd.', 'Pvt Ltd',
    'LLP', 'Corporation', 'Corp.', 'Company', 'Co.', 'Bank', 'Securities',
    'Industries', 'Inc.', 'Incorporated'
]

# Address indicators
ADDRESS_INDICATORS = [
    'Street', 'Road', 'Marg', 'Village', 'Taluka', 'District', 'Pune', 'Mumbai',
    'Maharashtra', 'PIN', 'Plot No.', 'Tower', 'Building', 'Office', 'Floor',
    'Lane', 'House No.', 'Nagar', 'Colony', 'Area'
]

# Common titles to help identify person names
PERSON_TITLES = [
    'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Sir', 'Madam'
]

# Context indicators for different PII types
DOB_KEYWORDS = ['Date of Birth', 'DOB', 'Birth Date', 'Born', 'Date Of Birth']
