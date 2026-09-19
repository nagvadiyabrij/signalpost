from typing import Dict, Any, Optional, List
import re


class IdentityVerifier:
    """Verifies that extracted information belongs to the correct company"""
    
    @staticmethod
    def verify_organization_number(
        requested_org_number: str,
        source_org_number: Optional[str] = None,
        source_text: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Verify organization number match.
        Returns (is_valid, reason)
        """
        # Normalize organization numbers
        requested_normalized = IdentityVerifier._normalize_org_number(requested_org_number)
        
        if source_org_number:
            source_normalized = IdentityVerifier._normalize_org_number(source_org_number)
            if requested_normalized == source_normalized:
                return True, "Organization number matches exactly"
            else:
                return False, f"Organization number mismatch: {requested_normalized} vs {source_normalized}"
        
        if source_text:
            # Search for organization number in text
            pattern = r'(?:organisasjonsnummer|org\.?\s*nr\.?|organization\s*number)[:\s]*(\d{9})'
            match = re.search(pattern, source_text, re.IGNORECASE)
            if match:
                found_number = match.group(1)
                found_normalized = IdentityVerifier._normalize_org_number(found_number)
                if requested_normalized == found_normalized:
                    return True, "Organization number found in source text"
                else:
                    return False, f"Organization number in text mismatch: {requested_normalized} vs {found_normalized}"
        
        return False, "No organization number found in source"
    
    @staticmethod
    def verify_company_name(
        requested_name: str,
        source_name: Optional[str] = None,
        source_text: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Verify company name match.
        Returns (is_valid, reason)
        """
        if not source_name and not source_text:
            return False, "No company name in source"
        
        # Normalize names for comparison
        requested_normalized = requested_name.lower().strip()
        
        if source_name:
            source_normalized = source_name.lower().strip()
            # Exact match
            if requested_normalized == source_normalized:
                return True, "Company name matches exactly"
            # Partial match (allowing for some variations)
            if requested_normalized in source_normalized or source_normalized in requested_normalized:
                return True, "Company name matches closely"
        
        if source_text:
            source_normalized = source_text.lower()
            if requested_normalized in source_normalized:
                return True, "Company name found in source text"
        
        return False, "Company name does not match"
    
    @staticmethod
    def verify_company_identity(
        requested_org_number: str,
        requested_name: str,
        source_data: Dict[str, Any]
    ) -> tuple[bool, str, float]:
        """
        Comprehensive company identity verification.
        Returns (is_valid, reason, confidence)
        """
        confidence = 0.0
        reasons = []
        
        # Check organization number (highest weight)
        source_org_number = source_data.get("organization_number")
        source_text = source_data.get("raw_text", "")
        
        org_valid, org_reason = IdentityVerifier.verify_organization_number(
            requested_org_number, source_org_number, source_text
        )
        
        if org_valid:
            confidence += 0.7
            reasons.append(org_reason)
        else:
            # Organization number mismatch is critical
            return False, f"Critical: {org_reason}", 0.0
        
        # Check company name (secondary verification)
        source_name = source_data.get("company_name")
        name_valid, name_reason = IdentityVerifier.verify_company_name(
            requested_name, source_name, source_text
        )
        
        if name_valid:
            confidence += 0.2
            reasons.append(name_reason)
        
        # Check address if available (tertiary verification)
        source_address = source_data.get("address")
        requested_address = source_data.get("requested_address")
        
        if source_address and requested_address:
            if source_address.lower() in requested_address.lower() or \
               requested_address.lower() in source_address.lower():
                confidence += 0.1
                reasons.append("Address matches")
        
        # Minimum confidence threshold
        if confidence >= 0.7:
            return True, "; ".join(reasons), confidence
        else:
            return False, f"Insufficient confidence ({confidence:.2f}): " + "; ".join(reasons), confidence
    
    @staticmethod
    def _normalize_org_number(org_number: str) -> str:
        """Normalize organization number to standard format"""
        # Remove spaces, dots, hyphens
        normalized = org_number.replace(" ", "").replace(".", "").replace("-", "")
        # Keep leading zeros
        return normalized
    
    @staticmethod
    def is_valid_norwegian_org_number(org_number: str) -> bool:
        """Validate Norwegian organization number format"""
        normalized = IdentityVerifier._normalize_org_number(org_number)
        # Should be 9 digits
        return bool(re.match(r'^\d{9}$', normalized))
