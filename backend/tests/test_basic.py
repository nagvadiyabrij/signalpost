import pytest
from app.validators.identity import IdentityVerifier


def test_normalize_org_number():
    verifier = IdentityVerifier()
    
    # Test normalization
    assert verifier._normalize_org_number("912 345 678") == "912345678"
    assert verifier._normalize_org_number("912.345.678") == "912345678"
    assert verifier._normalize_org_number("912-345-678") == "912345678"
    assert verifier._normalize_org_number("912345678") == "912345678"
    assert verifier._normalize_org_number("091234567") == "091234567"  # Preserve leading zero


def test_is_valid_norwegian_org_number():
    verifier = IdentityVerifier()
    
    # Valid numbers (after normalization)
    assert verifier.is_valid_norwegian_org_number("123456785") == True
    assert verifier.is_valid_norwegian_org_number("123 456 785") == True  # Normalized to valid
    assert verifier.is_valid_norwegian_org_number("123.456.785") == True  # Normalized to valid
    assert verifier.is_valid_norwegian_org_number("000000000") == False  # All-zero identifiers are invalid
    
    # Invalid numbers
    assert verifier.is_valid_norwegian_org_number("91234567") == False  # Too short
    assert verifier.is_valid_norwegian_org_number("9123456789") == False  # Too long
    assert verifier.is_valid_norwegian_org_number("abc123456") == False  # Contains letters


def test_is_valid_norwegian_org_number_checksum():
    verifier = IdentityVerifier()

    # Official checksum validation for Norwegian organization numbers
    assert verifier.is_valid_norwegian_org_number("123456785") == True
    assert verifier.is_valid_norwegian_org_number("910029817") == False

    # Invalid checksum / wrong last digit
    assert verifier.is_valid_norwegian_org_number("123456789") == False
    assert verifier.is_valid_norwegian_org_number("912345679") == False


def test_verify_organization_number():
    verifier = IdentityVerifier()
    
    # Exact match
    is_valid, reason = verifier.verify_organization_number("912345678", "912345678")
    assert is_valid == True
    assert "matches exactly" in reason
    
    # Mismatch
    is_valid, reason = verifier.verify_organization_number("912345678", "987654321")
    assert is_valid == False
    assert "mismatch" in reason


def test_verify_company_name():
    verifier = IdentityVerifier()
    
    # Exact match
    is_valid, reason = verifier.verify_company_name("Example AS", "Example AS")
    assert is_valid == True
    
    # Partial match
    is_valid, reason = verifier.verify_company_name("Example AS", "Example AS Norway")
    assert is_valid == True
    
    # No match
    is_valid, reason = verifier.verify_company_name("Example AS", "Different AS")
    assert is_valid == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
