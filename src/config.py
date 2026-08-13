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
