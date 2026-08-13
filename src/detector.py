"""PII Detection Module"""
import re
from typing import List, Dict, Tuple, Set
from .config import (PATTERNS, COMPANY_INDICATORS, ADDRESS_INDICATORS, DOB_KEYWORDS,
                     PROTECTED_COMPANIES, PROTECTED_BUSINESS_ENTITIES, GENERIC_COMPANY_REFS,
                     EXPLICIT_PII_NAMES)

class PIIDetector:
    """Detects various types of PII in text"""
    
    def __init__(self, use_spacy=True):
        """Initialize the PII detector
        
        Args:
            use_spacy: Whether to use spaCy for NER (falls back to pattern-based if unavailable)
        """
        self.use_spacy = use_spacy
        self.nlp = None
        
        # Precompile explicit name patterns for performance (ISSUE #1 FIX)
        self._compile_explicit_name_patterns()
        
        if use_spacy:
            try:
                import spacy
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    print("Warning: spaCy model not found. Falling back to pattern-based detection.")
                    self.use_spacy = False
            except ImportError:
                print("Warning: spaCy not installed. Using pattern-based detection only.")
                self.use_spacy = False
    
    def _compile_explicit_name_patterns(self):
        """Compile regex patterns for explicit PII names (ISSUE #1 FIX)"""
        # Create case-insensitive patterns with word boundaries for each explicit name
        self.explicit_name_patterns = []
        for name in EXPLICIT_PII_NAMES:
            # Normalize whitespace and create flexible pattern
            normalized = re.sub(r'\s+', r'\\s+', name.strip())
            pattern = re.compile(r'\b' + normalized + r'\b', re.IGNORECASE)
            self.explicit_name_patterns.append((pattern, name))
    
    def detect_all(self, text: str) -> Dict[str, List[Tuple[str, int, int]]]:
        """Detect all PII types in text
        
        Args:
            text: Input text to scan
            
        Returns:
            Dictionary mapping PII type to list of (value, start, end) tuples
        """
        results = {}
        
        # ISSUE #1 FIX: Explicit name detection FIRST (highest priority)
        results['PERSON'] = self.detect_explicit_names(text)
        
        # Regex-based detection
        results['EMAIL'] = self.detect_emails(text)
        results['PHONE'] = self.detect_phones(text)
        results['IP'] = self.detect_ips(text)
        results['SSN'] = self.detect_ssns(text)
        results['CREDIT_CARD'] = self.detect_credit_cards(text)
        results['DOB'] = self.detect_dobs(text)
        
        # NER-based detection (supplement explicit names, don't replace)
        if self.nlp:
            additional_persons = self.detect_persons_ner(text)
            # Merge with explicit names, avoiding duplicates
            results['PERSON'] = self._merge_person_detections(results['PERSON'], additional_persons)
            results['COMPANY'] = self.detect_companies_ner(text)
            results['ADDRESS'] = self.detect_addresses_ner(text)
        else:
            # Pattern-based fallback
            additional_persons = self.detect_persons_pattern(text)
            results['PERSON'] = self._merge_person_detections(results['PERSON'], additional_persons)
            results['COMPANY'] = self.detect_companies_pattern(text)
            results['ADDRESS'] = self.detect_addresses_pattern(text)
        
        return results
    
    def detect_explicit_names(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect explicit PII names from the predefined list (ISSUE #1 FIX)
        
        This ensures high recall for known promoters and key personnel.
        
        Args:
            text: Input text to scan
            
        Returns:
            List of (matched_name, start_pos, end_pos) tuples
        """
        results = []
        seen_spans = set()
        
        for pattern, original_name in self.explicit_name_patterns:
            for match in pattern.finditer(text):
                start = match.start()
                end = match.end()
                span = (start, end)
                
                # Avoid duplicate overlapping matches
                if span not in seen_spans:
                    results.append((match.group(), start, end))
                    seen_spans.add(span)
        
        return results
    
    def _merge_person_detections(self, explicit: List, additional: List) -> List:
        """Merge explicit name detections with additional detected names, avoiding duplicates"""
        # Use span-based deduplication
        all_detections = {}
        
        # Add explicit names first (higher priority)
        for name, start, end in explicit:
            all_detections[(start, end)] = (name, start, end)
        
        # Add additional names if they don't overlap
        for name, start, end in additional:
            span = (start, end)
            # Check for overlap with existing spans
            overlaps = False
            for existing_start, existing_end in all_detections.keys():
                if not (end <= existing_start or start >= existing_end):
                    overlaps = True
                    break
            
            if not overlaps:
                all_detections[span] = (name, start, end)
        
        return list(all_detections.values())
    
    def detect_emails(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect email addresses"""
        results = []
        for match in re.finditer(PATTERNS['EMAIL'], text):
            results.append((match.group(), match.start(), match.end()))
        return results
    
    def detect_phones(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect phone numbers with validation"""
        results = []
        for match in re.finditer(PATTERNS['PHONE'], text):
            phone = match.group()
            # Basic validation: phone should have at least 10 digits
            digits = re.sub(r'\D', '', phone)
            if len(digits) >= 10 and len(digits) <= 15:
                # Avoid false positives from pure financial numbers
                if not self._is_financial_context(text, match.start()):
                    results.append((phone, match.start(), match.end()))
        return results
    
    def detect_ips(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect IPv4 addresses with validation"""
        results = []
        for match in re.finditer(PATTERNS['IP'], text):
            ip = match.group()
            # Validate octets
            octets = ip.split('.')
            if all(0 <= int(octet) <= 255 for octet in octets):
                results.append((ip, match.start(), match.end()))
        return results
    
    def detect_ssns(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect Social Security Numbers"""
        results = []
        for match in re.finditer(PATTERNS['SSN'], text):
            results.append((match.group(), match.start(), match.end()))
        return results
    
    def detect_credit_cards(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect credit card numbers with Luhn validation"""
        results = []
        for match in re.finditer(PATTERNS['CREDIT_CARD'], text):
            cc = match.group()
            digits = re.sub(r'\D', '', cc)
            if len(digits) >= 13 and len(digits) <= 19:
                # Apply Luhn algorithm
                if self._luhn_check(digits):
                    # Additional check: avoid financial report numbers
                    if not self._is_financial_context(text, match.start()):
                        results.append((cc, match.start(), match.end()))
        return results
    
    def detect_dobs(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect dates of birth using context"""
        results = []
        # Look for DOB keywords followed by dates
        for keyword in DOB_KEYWORDS:
            pattern = keyword + r'[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', match.group())
                if date_match:
                    start = match.start() + date_match.start()
                    end = match.start() + date_match.end()
                    results.append((date_match.group(), start, end))
        return results
    
    def detect_persons_ner(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect person names using spaCy NER"""
        results = []
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Filter out single-word names that might be common nouns
                if len(ent.text.split()) >= 2 or self._has_title_prefix(text, ent.start_char):
                    results.append((ent.text, ent.start_char, ent.end_char))
        return results
    
    def detect_persons_pattern(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect person names using pattern matching (fallback)
        
        CONSERVATIVE: Only detect names with title prefixes or in specific contexts
        to avoid false positives from legitimate business terminology
        """
        results = []
        
        # ONLY pattern: Title followed by capitalized words (high confidence)
        pattern = r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.|Director|Manager)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
        for match in re.finditer(pattern, text):
            name = match.group(1)
            if not self._is_common_term(name):
                results.append((name, match.start(1), match.end(1)))
        
        # DO NOT use aggressive capitalized word patterns without context
        # The previous pattern was causing false positives on:
        # - "Companies Act" → detected as person name ❌
        # - "Book Built" → detected as person name ❌  
        # - "Dated December" → detected as person name ❌
        
        return results
    
    def detect_companies_ner(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect company names using spaCy NER
        
        IMPORTANT: Filter out protected companies and generic references
        """
        results = []
        doc = self.nlp(text)
        
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # Check if protected
                if not self._is_protected_company(ent.text):
                    results.append((ent.text, ent.start_char, ent.end_char))
        
        # Also check for company indicator patterns
        for indicator in COMPANY_INDICATORS:
            pattern = r'\b([A-Z][A-Za-z\s&]+?' + re.escape(indicator) + r')\b'
            for match in re.finditer(pattern, text):
                company = match.group(1).strip()
                
                # Check if protected
                if not self._is_protected_company(company):
                    results.append((company, match.start(1), match.end(1)))
        
        return self._deduplicate_matches(results)
    
    def detect_companies_pattern(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect company names using pattern matching (fallback)
        
        ISSUE #2 FIX: Only detect FULL formal company names with indicators.
        Do NOT match generic words like "Company", "Group", "Offer", etc.
        
        Args:
            text: Input text to scan
            
        Returns:
            List of (company_name, start_pos, end_pos) tuples
        """
        results = []
        
        # STRICT MATCHING: Only match multi-word company names with legal suffixes
        # Pattern requires: [Capital Word(s)] + [Legal Indicator]
        # Minimum 2 words before the indicator to avoid matching "The Company Limited"
        
        for indicator in COMPANY_INDICATORS:
            # Require at least 2-3 capitalized words before the indicator
            # This prevents matching "Our Company", "The Group", etc.
            pattern = r'\b([A-Z][A-Za-z]+(?:\s+[A-Z&][A-Za-z]+){1,5})\s+' + re.escape(indicator) + r'\b'
            
            for match in re.finditer(pattern, text):
                company = match.group(0).strip()
                
                # ISSUE #2 FIX: Check if this company should be protected
                if self._is_protected_company(company):
                    continue
                
                # Additional filter: Must be at least 3 words total
                word_count = len(company.split())
                if word_count < 3:
                    continue
                
                results.append((company, match.start(), match.end()))
        
        return self._deduplicate_matches(results)
    
    def _is_protected_company(self, company_name: str) -> bool:
        """Check if a company name should be protected from redaction
        
        Returns True if the company is:
        - The main company or its subsidiaries
        - A legitimate business partner/vendor in the prospectus
        - A generic reference like "Our Company"
        """
        company_lower = company_name.lower().strip()
        company_normalized = re.sub(r'\s+', ' ', company_lower)  # Normalize spaces
        
        # Check generic references
        if company_lower in GENERIC_COMPANY_REFS:
            return True
        
        # Check if starts with generic prefix
        if company_lower.startswith(('our ', 'the ', 'said ', 'this ')):
            return True
        
        # Check protected companies (exact match)
        for protected in PROTECTED_COMPANIES:
            if company_name == protected or company_lower == protected.lower():
                return True
        
        # Check if contains protected company name (substring matching)
        for protected in PROTECTED_COMPANIES:
            protected_lower = protected.lower()
            protected_normalized = re.sub(r'\s+', ' ', protected_lower)
            if protected_normalized in company_normalized or company_normalized in protected_normalized:
                return True
        
        # Check protected business entities (exact match first)
        for protected in PROTECTED_BUSINESS_ENTITIES:
            if company_name == protected or company_lower == protected.lower():
                return True
        
        # Then check partial matches for variants
        # Important: Check if company contains protected name OR protected contains company
        # This handles "HDFC Bank" protecting "HDFC Bank Limited" and vice versa
        for protected in PROTECTED_BUSINESS_ENTITIES:
            protected_lower = protected.lower()
            protected_normalized = re.sub(r'\s+', ' ', protected_lower)
            
            # Skip very short names to avoid false positives
            if len(protected_normalized) < 5:
                continue
                
            # Check both directions:
            # 1. "HDFC Bank" in "HDFC Bank Limited" → protect
            # 2. "HDFC Bank Limited" contains "HDFC Bank" → protect
            if protected_normalized in company_normalized or company_normalized in protected_normalized:
                return True
        
        return False
    
    def detect_addresses_ner(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect addresses using spaCy NER and patterns"""
        results = []
        
        # Use NER for locations
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC", "FAC"]:
                # Check if it's part of a larger address
                context_start = max(0, ent.start_char - 100)
                context_end = min(len(text), ent.end_char + 100)
                context = text[context_start:context_end]
                
                if any(ind in context for ind in ADDRESS_INDICATORS):
                    results.append((ent.text, ent.start_char, ent.end_char))
        
        # Pattern-based address detection
        results.extend(self.detect_addresses_pattern(text))
        
        return self._deduplicate_matches(results)
    
    def detect_addresses_pattern(self, text: str) -> List[Tuple[str, int, int]]:
        """Detect addresses using pattern matching"""
        results = []
        
        # Multi-line address pattern
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(ind in line for ind in ADDRESS_INDICATORS):
                # Collect multiple lines for full address
                address_lines = [line.strip()]
                for j in range(i + 1, min(i + 4, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and (any(ind in next_line for ind in ADDRESS_INDICATORS) or 
                                     re.search(r'\d{6}', next_line)):  # PIN code
                        address_lines.append(next_line)
                    else:
                        break
                
                if len(address_lines) >= 2:
                    full_address = ' '.join(address_lines)
                    # Find position in original text
                    pos = text.find(address_lines[0])
                    if pos != -1:
                        results.append((full_address, pos, pos + len(full_address)))
        
        return results
    
    def _luhn_check(self, card_number: str) -> bool:
        """Validate credit card using Luhn algorithm"""
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10 == 0
    
    def _is_financial_context(self, text: str, position: int) -> bool:
        """Check if position is in a financial context"""
        context_start = max(0, position - 50)
        context_end = min(len(text), position + 50)
        context = text[context_start:context_end].lower()
        
        financial_keywords = ['equity', 'shares', 'amount', 'rupees', 'rs.', 'inr', 
                             'price', 'value', 'capital', 'million', 'crore']
        return any(keyword in context for keyword in financial_keywords)
    
    def _has_title_prefix(self, text: str, position: int) -> bool:
        """Check if name has a title prefix"""
        context_start = max(0, position - 10)
        context = text[context_start:position]
        return any(title in context for title in ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.'])
    
    def _is_common_term(self, text: str) -> bool:
        """Check if text is a common term that shouldn't be redacted
        
        IMPORTANT: This protects legitimate business/legal/financial terminology
        from being incorrectly flagged as person names
        """
        # Normalize for comparison
        text_lower = text.lower()
        
        # Common business/legal/regulatory terms (DO NOT REDACT)
        protected_terms = [
            # General business
            'the company', 'our company', 'the board', 'the registrar',
            'red herring', 'book built', 'equity shares', 'offer price',
            'anchor investors', 'retail investors', 'qualified institutional',
            'non institutional', 'market maker', 'eligible employees',
            
            # Legal/regulatory
            'companies act', 'sebi regulations', 'listing agreement',
            'securities contracts', 'issue committee', 'audit committee',
            'nomination committee', 'stakeholders relationship',
            
            # Document references
            'section', 'chapter', 'schedule', 'annexure', 'page',
            'restated financial', 'prospectus', 'memorandum',
            
            # Financial terms
            'face value', 'issue size', 'price band', 'lot size',
            'market capitalization', 'net worth', 'earnings per',
            'return on', 'profit after', 'revenue from',
            
            # Time references  
            'fiscal year', 'financial year', 'dated', 'period ended',
            'year ended', 'months ended', 'quarter ended',
            
            # Dates/months (should not be detected as names)
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'dated december', 'dated january', 'dated february', 'dated march',
            'dated april', 'dated may', 'dated june', 'dated july',
            'dated august', 'dated september', 'dated october', 'dated november',
            
            # Common combinations
            'book running', 'lead managers', 'book built offer',
            'issue opens', 'issue closes', 'basis of allotment',
            'credit of equity', 'commencement of trading',
        ]
        
        # Check if matches any protected term
        if text_lower in protected_terms:
            return True
        
        # Check if it's part of a protected phrase
        for term in protected_terms:
            if term in text_lower or text_lower in term:
                return True
        
        # Check if starts with months
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                 'july', 'august', 'september', 'october', 'november', 'december']
        if any(text_lower.startswith(month) or text_lower.endswith(month) for month in months):
            return True
        
        # Check if starts with time references
        time_refs = ['dated', 'period', 'year', 'quarter', 'fiscal', 'financial']
        if any(text_lower.startswith(ref) for ref in time_refs):
            return True
        
        return False
    
    def _is_all_caps(self, text: str) -> bool:
        """Check if text is all capitals (likely an acronym)"""
        return text.isupper() and len(text) <= 10
    
    def _deduplicate_matches(self, matches: List[Tuple[str, int, int]]) -> List[Tuple[str, int, int]]:
        """Remove duplicate and overlapping matches"""
        if not matches:
            return []
        
        # Sort by start position
        sorted_matches = sorted(matches, key=lambda x: x[1])
        
        result = []
        last_end = -1
        
        for match in sorted_matches:
            if match[1] >= last_end:  # No overlap
                result.append(match)
                last_end = match[2]
        
        return result
