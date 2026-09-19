from typing import Dict, Any, Optional
from datetime import datetime


class FactValidator:
    """Validates facts before they are accepted"""
    
    @staticmethod
    def validate(fact: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate a fact.
        Returns (is_valid, reason)
        """
        # Required fields
        if "source_url" not in fact or not fact["source_url"]:
            return False, "Missing source URL"
        
        if "source_name" not in fact or not fact["source_name"]:
            return False, "Missing source name"
        
        if "retrieved_at" not in fact or not fact["retrieved_at"]:
            return False, "Missing retrieved_at timestamp"
        
        if "field" not in fact or not fact["field"]:
            return False, "Missing field name"
        
        # Validate URL format
        if not FactValidator._is_valid_url(fact["source_url"]):
            return False, "Invalid source URL format"
        
        # Validate date format
        if fact.get("retrieved_at"):
            if not FactValidator._is_valid_datetime(fact["retrieved_at"]):
                return False, "Invalid retrieved_at datetime format"
        
        # Financial facts require additional validation
        if FactValidator._is_financial_field(fact["field"]):
            if "financial_year" not in fact or not fact["financial_year"]:
                return False, "Financial facts require financial_year"
            
            if "currency" not in fact or not fact["currency"]:
                return False, "Financial facts require currency"
            
            if "value" not in fact or fact["value"] is None:
                return False, "Financial facts require value"
        
        # Validate value
        if "value" in fact and fact["value"] is not None:
            if not FactValidator._is_valid_value(fact["value"]):
                return False, "Invalid value format"
        
        return True, "Valid"
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Basic URL validation"""
        return url.startswith(("http://", "https://"))
    
    @staticmethod
    def _is_valid_datetime(dt_str: str) -> bool:
        """Validate datetime string"""
        try:
            if isinstance(dt_str, datetime):
                return True
            datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return True
        except:
            return False
    
    @staticmethod
    def _is_financial_field(field: str) -> bool:
        """Check if field is a financial metric"""
        financial_fields = [
            "revenue", "operating_profit", "profit_before_tax", "net_income",
            "total_assets", "equity", "liabilities", "cash", "employees"
        ]
        return field.lower() in financial_fields
    
    @staticmethod
    def _is_valid_value(value: Any) -> bool:
        """Validate value format"""
        if value is None:
            return True
        if isinstance(value, (str, int, float)):
            return True
        return False
    
    @staticmethod
    def validate_financial_value(value: Any, field: str) -> tuple[bool, str, Optional[float]]:
        """
        Validate and normalize financial value.
        Returns (is_valid, reason, normalized_value)
        """
        if value is None:
            return False, "Financial value cannot be None", None
        
        try:
            # Handle string values like "NOK 12.5 million"
            if isinstance(value, str):
                value = value.lower().replace("nok", "").replace("million", "000000").replace("billion", "000000000").strip()
                normalized = float(value)
            else:
                normalized = float(value)
            
            # Sanity check - Norwegian companies typically have reasonable ranges
            if normalized < 0:
                return False, "Negative financial value", None
            
            if normalized > 1e15:  # More than 1 quadrillion NOK is suspicious
                return False, "Financial value suspiciously large", None
            
            return True, "Valid", normalized
        except (ValueError, TypeError):
            return False, "Could not parse financial value", None
