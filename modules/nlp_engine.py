import re
from collections import Counter

class LegalNLPEngine:
    def __init__(self):
        # Legal entity patterns
        self.legal_patterns = {
            'party': [r'(?i)(party|company|firm|organization)\s+[A-Z][a-zA-Z\s&,\.]+',
                     r'(?i)(hereinafter referred to as|referred to as)\s+"([^"]+)"'],
            'amount': [r'(?i)(rs\.?|inr|rupees)\s*[\d,]+(?:\.\d{2})?',
                      r'₹\s*[\d,]+(?:\.\d{2})?',
                      r'(?i)\d+\s*(lakh|crore|thousand)'],
            'date': [r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
                    r'(?i)(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}'],
            'duration': [r'(?i)\d+\s*(days?|weeks?|months?|years?)',
                        r'(?i)(term of|period of)\s+\d+\s*(days?|months?|years?)']
        }
        
        # Obligation keywords
        self.obligation_markers = ['shall', 'must', 'required to', 'obligated to', 'agrees to']
        self.right_markers = ['may', 'entitled to', 'has the right to', 'permitted to']
        self.prohibition_markers = ['shall not', 'must not', 'prohibited from', 'restricted from']
    
    def extract_entities(self, text):
        """Extract named entities using regex patterns"""
        entities = {
            'organizations': [],
            'persons': [],
            'dates': [],
            'money': [],
            'locations': [],
            'custom': {}
        }
        
        # Simple regex-based extraction
        # Organizations - look for capitalized words
        org_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Ltd|Limited|Inc|Corp|Company|Pvt)\b'
        entities['organizations'] = list(set(re.findall(org_pattern, text)))
        
        # Custom pattern matching
        for entity_type, patterns in self.legal_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text)
                if found and isinstance(found[0], tuple):
                    matches.extend([m for group in found for m in group if m])
                else:
                    matches.extend(found)
            entities['custom'][entity_type] = list(set(matches))
        
        return entities
    
    def classify_clauses(self, text):
        """Classify clauses as obligations, rights, or prohibitions"""
        # Split into sentences using simple method
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        classified = {
            'obligations': [],
            'rights': [],
            'prohibitions': []
        }
        
        for sent in sentences:
            sent_lower = sent.lower()
            
            # Check for prohibitions first (more specific)
            if any(marker in sent_lower for marker in self.prohibition_markers):
                classified['prohibitions'].append(sent)
            # Then obligations
            elif any(marker in sent_lower for marker in self.obligation_markers):
                classified['obligations'].append(sent)
            # Then rights
            elif any(marker in sent_lower for marker in self.right_markers):
                classified['rights'].append(sent)
        
        return classified
    
    def detect_ambiguous_terms(self, text):
        """Flag vague or ambiguous language"""
        ambiguous_terms = [
            'reasonable', 'appropriate', 'as soon as possible', 'promptly',
            'substantial', 'material', 'best efforts', 'good faith',
            'approximately', 'around', 'may', 'might', 'could'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        flagged = []
        
        for sent in sentences:
            sent_lower = sent.lower()
            found_terms = [term for term in ambiguous_terms if term in sent_lower]
            
            if found_terms:
                flagged.append({
                    'sentence': sent,
                    'terms': found_terms,
                    'concern': 'Vague language may lead to disputes'
                })
        
        return flagged