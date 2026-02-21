"""
AI service for generating accounting suggestions using LLM.
"""
from openai import OpenAI
from typing import Dict, Optional
from app.core.config import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class AIService:
    """Service for AI-powered accounting suggestions."""
    
    SYSTEM_PROMPT = """You are an expert accounting assistant for Norwegian accounting firms.
Your task is to analyze invoice documents and suggest appropriate accounting entries.

Given OCR-extracted text from an invoice, provide:
1. Suggested account number (Norwegian chart of accounts format)
2. Suggested VAT code (Norwegian VAT codes: 0, 1, 2, 3, 5, 6)
3. Confidence level (0.0 to 1.0)
4. Risk assessment (low, medium, high)

Respond ONLY with valid JSON in this exact format:
{
    "account_number": "string or null",
    "vat_code": "string or null",
    "confidence": 0.0-1.0,
    "risk_level": "low|medium|high",
    "reasoning": "brief explanation"
}

Be conservative with confidence scores. If information is unclear, use lower confidence.
Flag high risk if:
- Account number seems unusual for the transaction type
- VAT code doesn't match typical patterns
- Amounts are unusually large
- Missing critical information"""

    @staticmethod
    def generate_suggestion(ocr_text: str) -> Dict:
        """Generate accounting suggestion from OCR text."""
        try:
            user_prompt = f"""Analyze this invoice document and provide accounting suggestions:

{ocr_text}

Provide your analysis in the required JSON format."""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": AIService.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Validate and normalize response
            return {
                "account_number": result.get("account_number"),
                "vat_code": result.get("vat_code"),
                "confidence": float(result.get("confidence", 0.0)),
                "risk_level": result.get("risk_level", "medium").lower(),
                "reasoning": result.get("reasoning", "")
            }
        except Exception as e:
            raise Exception(f"AI suggestion generation failed: {str(e)}")
    
    @staticmethod
    def get_prompt_for_audit(ocr_text: str) -> str:
        """Get the full prompt used for AI processing (for audit logging)."""
        return f"""System: {AIService.SYSTEM_PROMPT}

User: Analyze this invoice document and provide accounting suggestions:

{ocr_text}

Provide your analysis in the required JSON format."""


ai_service = AIService()
