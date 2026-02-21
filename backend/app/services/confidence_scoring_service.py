"""
Confidence scoring engine for accounting suggestions.
"""
from typing import Dict, Optional
from app.services.rule_validation_service import rule_validation_service


class ConfidenceScoringService:
    """Service for calculating confidence scores."""
    
    @staticmethod
    def calculate_final_confidence(
        ai_confidence: float,
        account_number: Optional[str],
        vat_code: Optional[str]
    ) -> float:
        """Calculate final confidence score considering validation."""
        # Start with AI confidence
        confidence = ai_confidence
        
        # Apply validation penalties
        validation = rule_validation_service.validate_suggestion(account_number, vat_code)
        
        if not validation["account_valid"]:
            confidence *= 0.5  # Reduce confidence if account invalid
        
        if not validation["vat_valid"]:
            confidence *= 0.5  # Reduce confidence if VAT invalid
        
        # Ensure confidence is between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        
        return round(confidence, 2)
    
    @staticmethod
    def adjust_confidence_for_risk(confidence: float, risk_level: str) -> float:
        """Adjust confidence based on risk level."""
        risk_multipliers = {
            "low": 1.0,
            "medium": 0.9,
            "high": 0.7
        }
        
        multiplier = risk_multipliers.get(risk_level.lower(), 0.8)
        adjusted = confidence * multiplier
        
        return round(max(0.0, min(1.0, adjusted)), 2)


confidence_scoring_service = ConfidenceScoringService()
