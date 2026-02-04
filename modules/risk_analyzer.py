import re
import json
from typing import Dict, List

class RiskAnalyzer:
    def __init__(self):
        # Risk patterns based on Indian Contract Act & common issues
        self.risk_patterns = {
            'high': {
                'unlimited_liability': [
                    r'(?i)unlimited\s+liability',
                    r'(?i)without\s+any\s+limit',
                    r'(?i)entire\s+liability'
                ],
                'unilateral_termination': [
                    r'(?i)(party\s+[AB]|company|first\s+party)\s+may\s+terminate.*without\s+(notice|cause)',
                    r'(?i)terminate\s+at\s+will',
                    r'(?i)sole\s+discretion.*terminate'
                ],
                'ip_transfer': [
                    r'(?i)all\s+intellectual\s+property.*transferred',
                    r'(?i)ownership.*vests.*exclusively',
                    r'(?i)irrevocable.*assignment.*ip'
                ],
                'non_compete_broad': [
                    r'(?i)non-compete.*\d+\s+(years|year)',
                    r'(?i)not\s+engage.*competing.*business',
                    r'(?i)restricted.*similar.*activity'
                ]
            },
            'medium': {
                'auto_renewal': [
                    r'(?i)automatically\s+renewed?',
                    r'(?i)auto-renewal',
                    r'(?i)unless.*notice.*\d+\s+days.*renew'
                ],
                'penalty_clause': [
                    r'(?i)penalty.*₹?\d+',
                    r'(?i)liquidated\s+damages',
                    r'(?i)shall\s+pay.*breach'
                ],
                'jurisdiction_limited': [
                    r'(?i)exclusive\s+jurisdiction',
                    r'(?i)courts?\s+at\s+\w+\s+only',
                    r'(?i)subject\s+to.*jurisdiction.*\w+'
                ],
                'indemnity_broad': [
                    r'(?i)indemnify.*hold\s+harmless',
                    r'(?i)defend.*against\s+any\s+claims?',
                    r'(?i)indemnification.*losses'
                ]
            },
            'low': {
                'notice_period': [
                    r'(?i)\d+\s+days?\s+notice',
                    r'(?i)notice\s+period.*\d+'
                ],
                'confidentiality': [
                    r'(?i)confidential\s+information',
                    r'(?i)non-disclosure'
                ]
            }
        }
    
    def analyze_contract(self, text: str, entities: Dict) -> Dict:
        """Comprehensive risk analysis"""
        
        risk_findings = {
            'high': [],
            'medium': [],
            'low': [],
            'composite_score': 0
        }
        
        # Pattern-based detection
        for risk_level, categories in self.risk_patterns.items():
            for category, patterns in categories.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        # Extract context (50 chars before and after)
                        start = max(0, match.start() - 50)
                        end = min(len(text), match.end() + 50)
                        context = text[start:end]
                        
                        risk_findings[risk_level].append({
                            'category': category,
                            'matched_text': match.group(0),
                            'context': context,
                            'position': match.start()
                        })
        
        # Calculate composite score
        weights = {'high': 10, 'medium': 5, 'low': 1}
        total_score = sum(
            len(risk_findings[level]) * weights[level]
            for level in weights.keys()
        )
        
        # Normalize to 0-100
        risk_findings['composite_score'] = min(100, total_score)
        
        # Add risk level interpretation
        if risk_findings['composite_score'] > 60:
            risk_findings['level'] = 'HIGH RISK'
            risk_findings['recommendation'] = 'Immediate legal review recommended'
        elif risk_findings['composite_score'] > 30:
            risk_findings['level'] = 'MEDIUM RISK'
            risk_findings['recommendation'] = 'Review and negotiate key clauses'
        else:
            risk_findings['level'] = 'LOW RISK'
            risk_findings['recommendation'] = 'Standard contract with minor concerns'
        
        return risk_findings
    
    def check_indian_compliance(self, text: str, contract_type: str) -> List[Dict]:
        """Check compliance with Indian Contract Act, 1872 & related laws"""
        
        compliance_checks = []
        
        # Essential elements under Indian Contract Act
        essential_elements = {
            'consideration': r'(?i)(consideration|valuable\s+consideration|monetary|payment)',
            'free_consent': r'(?i)(consent|agree|acceptance|mutual\s+understanding)',
            'competent_parties': r'(?i)(major|age\s+of\s+majority|sound\s+mind|competent)',
            'lawful_object': r'(?i)(lawful\s+purpose|legal\s+object|legitimate)'
        }
        
        for element, pattern in essential_elements.items():
            if not re.search(pattern, text):
                compliance_checks.append({
                    'element': element,
                    'status': 'MISSING',
                    'severity': 'high',
                    'note': f'Contract should explicitly mention {element} as per Section 10, Indian Contract Act'
                })
            else:
                compliance_checks.append({
                    'element': element,
                    'status': 'PRESENT',
                    'severity': 'none'
                })
        
        return compliance_checks