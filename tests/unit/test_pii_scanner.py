import pytest
from app.security.pii_scanner import PIIScanner


@pytest.fixture
def scanner():
    return PIIScanner()


def test_email_detection(scanner):
    result = scanner.scan("Contact me at user@example.com")
    assert result["pii_found"] is True
    assert any(f["entity_type"] == "email" for f in result["findings"])


def test_phone_detection(scanner):
    result = scanner.scan("Call me at +1-555-123-4567")
    assert result["pii_found"] is True
    assert any(f["entity_type"] == "phone" for f in result["findings"])


def test_credit_card_detection(scanner):
    result = scanner.scan("My card is 4111-1111-1111-1111")
    assert result["pii_found"] is True
    assert any(f["entity_type"] == "credit_card" for f in result["findings"])


def test_ssn_detection(scanner):
    result = scanner.scan("My SSN is 123-45-6789")
    assert result["pii_found"] is True
    assert any(f["entity_type"] == "ssn" for f in result["findings"])


def test_api_key_detection(scanner):
    result = scanner.scan("My key is sk-abcdefghijklmnopqrstuvwxyz123456")
    assert result["pii_found"] is True
    assert any(f["entity_type"] == "api_key" for f in result["findings"])


def test_masking(scanner):
    result = scanner.scan("Email: user@example.com")
    assert result["sanitized_text"] != "Email: user@example.com"
    assert "@" not in result["sanitized_text"] or "***" in result["sanitized_text"]


def test_no_pii(scanner):
    result = scanner.scan("This is a normal sentence with no sensitive data")
    assert result["pii_found"] is False


def test_multiple_pii(scanner):
    result = scanner.scan("Email: user@example.com, Phone: +1-555-123-4567")
    assert result["pii_found"] is True
    assert result["entity_count"] >= 2


def test_messages_scan(scanner):
    messages = [
        {"role": "user", "content": "My email is test@test.com"},
    ]
    result = scanner.scan_messages(messages)
    assert result["has_pii"] is True
