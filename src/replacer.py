"""PII Replacement Module"""
from typing import Dict, List, Tuple
from faker import Faker
import re
import hashlib

class PIIReplacer:
    """Replaces detected PII with fake values"""
    
    def __init__(self, seed: int = 42):
        """Initialize the replacer with a seed for consistency
        
        Args:
            seed: Random seed for Faker to ensure deterministic replacements
        """
        self.faker = Faker()
        Faker.seed(seed)
        self.replacement_map = {}
        self.used_replacements = set()
    
    def get_replacement(self, pii_type: str, original_value: str) -> str:
        """Get a consistent replacement for a PII value
        
        Args:
            pii_type: Type of PII (EMAIL, PHONE, etc.)
            original_value: Original PII value
            
        Returns:
            Fake replacement value
        """
        # Check if we already have a replacement
        key = (pii_type, original_value)
        if key in self.replacement_map:
            return self.replacement_map[key]
        
        # Generate new replacement
        replacement = self._generate_replacement(pii_type, original_value)
        
        # Ensure uniqueness
        attempt = 0
        while replacement in self.used_replacements and attempt < 100:
            replacement = self._generate_replacement(pii_type, original_value)
            attempt += 1
        
        # Store mapping
        self.replacement_map[key] = replacement
        self.used_replacements.add(replacement)
        
        return replacement
    
    def _generate_replacement(self, pii_type: str, original_value: str) -> str:
        """Generate a fake replacement value
        
        Args:
            pii_type: Type of PII
            original_value: Original value (used for seeding similar formats)
            
        Returns:
            Fake replacement value
        """
        if pii_type == 'EMAIL':
            return self._generate_email(original_value)
        elif pii_type == 'PHONE':
            return self._generate_phone(original_value)
        elif pii_type == 'PERSON':
            return self._generate_person_name()
        elif pii_type == 'COMPANY':
            return self._generate_company_name(original_value)
        elif pii_type == 'ADDRESS':
            return self._generate_address()
        elif pii_type == 'SSN':
            return self._generate_ssn()
        elif pii_type == 'CREDIT_CARD':
            return self._generate_credit_card(original_value)
        elif pii_type == 'DOB':
            return self._generate_dob(original_value)
        elif pii_type == 'IP':
            return self._generate_ip()
        else:
            return '[REDACTED]'
    
    def _generate_email(self, original: str) -> str:
        """Generate a fake email address"""
        # Use a deterministic approach based on hash
        hash_val = int(hashlib.md5(original.encode()).hexdigest()[:8], 16)
        Faker.seed(hash_val)
        temp_faker = Faker()
        
        first = temp_faker.first_name().lower()
        last = temp_faker.last_name().lower()
        domain = temp_faker.domain_name()
        
        return f"{first}.{last}@{domain}"
    
    def _generate_phone(self, original: str) -> str:
        """Generate a fake phone number matching the format"""
        # Detect format
        if '+91' in original:
            # Indian format
            return f"+91 {self.faker.numerify('##### #####')}"
        elif re.match(r'\+\d', original):
            # International format
            return f"+{self.faker.numerify('#')} {self.faker.numerify('### ### ####')}"
        else:
            # Local format
            return self.faker.numerify('##########')
    
    def _generate_person_name(self) -> str:
        """Generate a fake person name"""
        return self.faker.name()
    
    def _generate_company_name(self, original: str) -> str:
        """Generate a fake company name preserving suffix"""
        # Extract suffix (Limited, Pvt. Ltd., etc.)
        suffixes = ['Limited', 'Ltd.', 'Ltd', 'Private Limited', 'Pvt. Ltd.', 
                   'Pvt Ltd', 'LLP', 'Corporation', 'Corp.', 'Inc.']
        
        suffix = ''
        for s in suffixes:
            if s in original:
                suffix = s
                break
        
        base_name = self.faker.company().replace(',', '').replace('Inc', '').replace('LLC', '').strip()
        
        if suffix:
            return f"{base_name} {suffix}"
        else:
            return base_name
    
    def _generate_address(self) -> str:
        """Generate a fake address"""
        return self.faker.address().replace('\n', ', ')
    
    def _generate_ssn(self) -> str:
        """Generate a fake SSN"""
        return self.faker.numerify('###-##-####')
    
    def _generate_credit_card(self, original: str) -> str:
        """Generate a fake credit card number matching format"""
        # Preserve format (spaces or hyphens)
        if ' ' in original:
            separator = ' '
        elif '-' in original:
            separator = '-'
        else:
            separator = ''
        
        # Generate test credit card number
        digits = '4000000000000002'  # Test Visa number
        
        if separator:
            parts = [digits[i:i+4] for i in range(0, 16, 4)]
            return separator.join(parts)
        else:
            return digits
    
    def _generate_dob(self, original: str) -> str:
        """Generate a fake date of birth matching format"""
        # Detect format
        if '/' in original:
            separator = '/'
        elif '-' in original:
            separator = '-'
        else:
            separator = '/'
        
        # Generate date
        fake_date = self.faker.date_of_birth(minimum_age=25, maximum_age=70)
        
        # Match format
        if len(original.split(separator)[0]) == 4:  # YYYY/MM/DD
            return fake_date.strftime(f'%Y{separator}%m{separator}%d')
        else:  # DD/MM/YYYY or MM/DD/YYYY
            return fake_date.strftime(f'%d{separator}%m{separator}%Y')
    
    def _generate_ip(self) -> str:
        """Generate a fake IP address"""
        return self.faker.ipv4_private()
    
    def replace_in_text(self, text: str, detections: Dict[str, List[Tuple[str, int, int]]]) -> Tuple[str, Dict]:
        """Replace all detected PII in text
        
        Args:
            text: Original text
            detections: Dictionary of PII detections from detector
            
        Returns:
            Tuple of (redacted_text, replacement_map)
        """
        # Collect all replacements with positions
        all_replacements = []
        
        for pii_type, matches in detections.items():
            for original_value, start, end in matches:
                replacement = self.get_replacement(pii_type, original_value)
                all_replacements.append((start, end, original_value, replacement))
        
        # Sort by position (reverse order to maintain positions)
        all_replacements.sort(key=lambda x: x[0], reverse=True)
        
        # Apply replacements
        redacted_text = text
        for start, end, original, replacement in all_replacements:
            redacted_text = redacted_text[:start] + replacement + redacted_text[end:]
        
        return redacted_text, self.replacement_map
    
    def get_statistics(self, detections: Dict[str, List[Tuple[str, int, int]]]) -> Dict[str, int]:
        """Get statistics about detected PII
        
        Args:
            detections: Dictionary of PII detections
            
        Returns:
            Dictionary mapping PII type to count
        """
        stats = {}
        for pii_type, matches in detections.items():
            # Count unique values
            unique_values = set(match[0] for match in matches)
            stats[pii_type] = len(unique_values)
        return stats
