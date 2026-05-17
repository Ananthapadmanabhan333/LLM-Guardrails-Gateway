import pytest
from app.output.validator import OutputValidator


@pytest.fixture
def validator():
    return OutputValidator()


def test_safe_output(validator):
    result = validator.validate("The capital of France is Paris.")
    assert result["valid"] is True
    assert result["action"] == "allow"


def test_toxic_output(validator):
    result = validator.validate("I hate everyone and want to cause harm")
    assert result["valid"] is False
    assert result["action"] in ("block", "sanitize")


def test_refusal_detection(validator):
    result = validator.validate("I cannot fulfill that request as an AI assistant")
    assert result["issue_count"] > 0


def test_json_validation(validator):
    result = validator.validate_json('{"key": "value"}')
    assert result["valid"] is True

    result = validator.validate_json("invalid json")
    assert result["valid"] is False


def test_empty_output(validator):
    result = validator.validate("")
    assert result["valid"] is True


def test_banned_phrases(validator):
    result = validator.validate("As an AI, I must decline that request")
    assert result["issue_count"] > 0
    assert any(i["type"] == "banned_phrase" for i in result["issues"])
