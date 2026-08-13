"""Tests for PII Replacer"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.replacer import PIIReplacer

@pytest.fixture
def replacer():
    """Create a replacer instance"""
    return PIIReplacer(seed=42)

def test_consistent_replacement(replacer):
    """Test that same value gets same replacement"""
    email1 = replacer.get_replacement('EMAIL', 'test@example.com')
    email2 = replacer.get_replacement('EMAIL', 'test@example.com')
    
    assert email1 == email2

def test_different_values_different_replacements(replacer):
    """Test that different values get different replacements"""
    email1 = replacer.get_replacement('EMAIL', 'test1@example.com')
    email2 = replacer.get_replacement('EMAIL', 'test2@example.com')
    
    assert email1 != email2

def test_generate_email(replacer):
    """Test email generation"""
    email = replacer._generate_email('original@example.com')
    
    assert '@' in email
    assert '.' in email

def test_generate_phone_indian(replacer):
    """Test Indian phone generation"""
    phone = replacer._generate_phone('+91 9876543210')
    
    assert '+91' in phone

def test_generate_person_name(replacer):
    """Test person name generation"""
    name = replacer._generate_person_name()
    
    assert len(name) > 0
    assert ' ' in name  # Should have first and last name

def test_generate_company_name(replacer):
    """Test company name generation"""
    company = replacer._generate_company_name('Test Company Limited')
    
    assert 'Limited' in company

def test_generate_ssn(replacer):
    """Test SSN generation"""
    ssn = replacer._generate_ssn()
    
    assert len(ssn) == 11  # Format: XXX-XX-XXXX
    assert ssn[3] == '-'
    assert ssn[6] == '-'

def test_generate_credit_card(replacer):
    """Test credit card generation"""
    cc = replacer._generate_credit_card('4111 1111 1111 1111')
    
    assert ' ' in cc
    assert len(cc.replace(' ', '')) == 16

def test_generate_ip(replacer):
    """Test IP generation"""
    ip = replacer._generate_ip()
    
    assert ip.count('.') == 3
    octets = ip.split('.')
    assert len(octets) == 4

def test_replace_in_text(replacer):
    """Test full text replacement"""
    text = "Contact john@example.com or call +91 9876543210"
    detections = {
        'EMAIL': [('john@example.com', 8, 25)],
        'PHONE': [('+91 9876543210', 38, 53)]
    }
    
    redacted, mapping = replacer.replace_in_text(text, detections)
    
    assert 'john@example.com' not in redacted
    assert '+91 9876543210' not in redacted
    assert len(mapping) == 2

def test_get_statistics(replacer):
    """Test statistics generation"""
    detections = {
        'EMAIL': [('test1@example.com', 0, 17), ('test2@example.com', 20, 37)],
        'PHONE': [('+91 9876543210', 40, 55)],
        'PERSON': []
    }
    
    stats = replacer.get_statistics(detections)
    
    assert stats['EMAIL'] == 2
    assert stats['PHONE'] == 1
    assert stats['PERSON'] == 0

def test_replacement_map_persistence(replacer):
    """Test that replacement map persists across calls"""
    text1 = "Email: test@example.com"
    text2 = "Another email: test@example.com"
    
    detections1 = {'EMAIL': [('test@example.com', 7, 24)]}
    detections2 = {'EMAIL': [('test@example.com', 15, 32)]}
    
    redacted1, map1 = replacer.replace_in_text(text1, detections1)
    redacted2, map2 = replacer.replace_in_text(text2, detections2)
    
    # Both should use the same replacement
    replacement = map1[('EMAIL', 'test@example.com')]
    assert replacement in redacted1
    assert replacement in redacted2

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
