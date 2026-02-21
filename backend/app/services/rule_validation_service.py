"""
Rule validation service for accounting rules and compliance checks.
"""
from typing import Dict, List, Optional, Tuple
from app.db.models import RiskLevel


class RuleValidationService:
    """Service for validating accounting rules and compliance."""
    
    # Norwegian VAT codes
    VALID_VAT_CODES = ["0", "1", "2", "3", "5", "6"]
    
    # Common Norwegian account number ranges (simplified)
    # In production, this would be more comprehensive
    VALID_ACCOUNT_RANGES = {
        "1000-1999": "Assets",
        "2000-2999": "Liabilities",
        "3000-3999": "Equity",
        "4000-4999": "Revenue",
        "5000-5999": "Cost of goods sold",
        "6000-6999": "Operating expenses",
        "7000-7999": "Financial items",
        "8000-8999": "Other income/expenses",
    }
    
    @staticmethod
    def validate_account_number(account_number: Optional[str]) -> Tuple[bool, str]:
        """Validate account number format and range."""
        if not account_number:
            return False, "Account number is missing"
        
        # Remove whitespace
        account_number = account_number.strip()
        
        # Check if numeric
        if not account_number.isdigit():
            return False, "Account number must be numeric"
        
        # Check length (typically 4 digits)
        if len(account_number) != 4:
            return False, "Account number must be 4 digits"
        
        # Check if in valid range
        account_int = int(account_number)
        valid = False
        for range_str, _ in RuleValidationService.VALID_ACCOUNT_RANGES.items():
            start, end = map(int, range_str.split("-"))
            if start <= account_int <= end:
                valid = True
                break
        
        if not valid:
            return False, f"Account number {account_number} not in valid range"
        
        return True, "Valid"
    
    @staticmethod
    def validate_vat_code(vat_code: Optional[str]) -> Tuple[bool, str]:
        """Validate VAT code."""
        if not vat_code:
            return False, "VAT code is missing"
        
        vat_code = str(vat_code).strip()
        
        if vat_code not in RuleValidationService.VALID_VAT_CODES:
            return False, f"VAT code {vat_code} is not valid. Must be one of: {', '.join(RuleValidationService.VALID_VAT_CODES)}"
        
        return True, "Valid"
    
    @staticmethod
    def validate_suggestion(account_number: Optional[str], vat_code: Optional[str]) -> Dict:
        """Validate a complete suggestion."""
        account_valid, account_msg = RuleValidationService.validate_account_number(account_number)
        vat_valid, vat_msg = RuleValidationService.validate_vat_code(vat_code)
        
        validation_errors = []
        if not account_valid:
            validation_errors.append(f"Account: {account_msg}")
        if not vat_valid:
            validation_errors.append(f"VAT: {vat_msg}")
        
        return {
            "is_valid": account_valid and vat_valid,
            "account_valid": account_valid,
            "vat_valid": vat_valid,
            "errors": validation_errors
        }
    
    @staticmethod
    def check_risk_rules(account_number: Optional[str], vat_code: Optional[str], confidence: float) -> RiskLevel:
        """Apply risk assessment rules."""
        # High risk conditions
        if confidence < 0.5:
            return RiskLevel.HIGH
        
        validation = RuleValidationService.validate_suggestion(account_number, vat_code)
        if not validation["is_valid"]:
            return RiskLevel.HIGH
        
        # Medium risk conditions
        if confidence < 0.7:
            return RiskLevel.MEDIUM
        
        # Low risk
        return RiskLevel.LOW


rule_validation_service = RuleValidationService()
