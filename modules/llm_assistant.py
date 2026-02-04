import requests
import os
from typing import Dict, List
import json

class ClaudeAssistant:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API directly via REST"""
        try:
            url = f"{self.base_url}?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error calling API: {str(e)}"
    
    def generate_plain_summary(self, contract_text: str, entities: Dict, risk_analysis: Dict) -> str:
        """Generate business-friendly contract summary"""
        
        prompt = f"""You are a legal assistant helping small business owners understand contracts.

Contract Text (excerpts):
{contract_text[:3000]}

Extracted Information:
- Parties: {entities.get('organizations', [])}
- Key Dates: {entities.get('dates', [])}
- Financial Terms: {entities.get('money', [])}

Risk Analysis Results:
- Composite Risk Score: {risk_analysis.get('composite_score', 0)}/100
- High Risk Issues: {len(risk_analysis.get('high', []))}
- Medium Risk Issues: {len(risk_analysis.get('medium', []))}

Task: Create a 4-5 sentence plain-language summary for a busy business owner. Focus on:
1. What type of contract this is
2. Who the parties are
3. Main obligations
4. Key risks they should know about
5. Overall recommendation

Use simple business language, avoid legal jargon. Be direct and actionable."""

        return self._call_gemini(prompt)
    
    def explain_clause(self, clause_text: str, context: str = "") -> Dict:
        """Explain a specific clause in plain language"""
        
        prompt = f"""Explain this contract clause to a non-lawyer:

Clause: "{clause_text}"

Context: {context}

Provide:
1. Plain English explanation (2-3 sentences)
2. What this means for the business
3. Any potential concerns
4. Whether this is standard or unusual

Be concise and practical."""

        return {
            'explanation': self._call_gemini(prompt),
            'original_clause': clause_text
        }
    
    def suggest_alternatives(self, unfavorable_clause: str, concern: str) -> List[str]:
        """Suggest alternative clause wording"""
        
        prompt = f"""This contract clause is concerning:

Original Clause: "{unfavorable_clause}"
Concern: {concern}

Suggest 2 alternative wordings that would be more balanced and fair for an SME. Make them:
- Legally sound
- Protecting both parties
- Clear and unambiguous
- Suitable for Indian business context

Format: Return only the alternative clauses, numbered 1 and 2."""

        result = self._call_gemini(prompt)
        alternatives = result.strip().split('\n\n')
        return [alt.strip() for alt in alternatives if alt.strip()]
    
    def classify_contract_type(self, text: str) -> str:
        """Classify the type of contract"""
        
        prompt = f"""Classify this contract into ONE of these categories:
- Employment Agreement
- Vendor/Supplier Contract
- Service Agreement
- Lease Agreement
- Partnership Deed
- NDA/Confidentiality Agreement
- Sales Agreement
- Consulting Agreement
- Other

Contract excerpt:
{text[:1500]}

Return ONLY the category name, nothing else."""

        return self._call_gemini(prompt)