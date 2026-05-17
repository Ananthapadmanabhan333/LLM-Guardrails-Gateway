import re
from typing import List, Dict, Any, Optional
from app.config import settings


class PromptValidator:
    def __init__(self):
        self.validation_rules = {
            "max_length": {
                "enabled": True,
                "check": lambda t: len(t) <= settings.max_prompt_length,
                "error": f"Prompt exceeds maximum length of {settings.max_prompt_length} characters",
            },
            "min_length": {
                "enabled": True,
                "check": lambda t: len(t.strip()) > 0,
                "error": "Prompt cannot be empty",
            },
            "has_content": {
                "enabled": True,
                "check": lambda t: any(c.isalpha() for c in t),
                "error": "Prompt must contain textual content",
            },
        }

    def validate(self, text: str) -> Dict[str, Any]:
        errors = []
        warnings = []

        for rule_name, rule in self.validation_rules.items():
            if rule.get("enabled", True):
                try:
                    if not rule["check"](text):
                        errors.append(rule["error"])
                except Exception as e:
                    errors.append(f"Validation error in {rule_name}: {str(e)}")

        suspicious_encoding = self._check_encoding(text)
        if suspicious_encoding:
            warnings.append(suspicious_encoding)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "char_count": len(text),
            "word_count": len(text.split()),
        }

    def _check_encoding(self, text: str) -> Optional[str]:
        null_chars = text.count("\x00")
        if null_chars > 0:
            return f"Text contains {null_chars} null bytes"

        control_chars = sum(1 for c in text if ord(c) < 32 and c not in "\n\r\t")
        if control_chars > 5:
            return f"Text contains {control_chars} control characters"

        return None

    def validate_json_schema(self, response: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        import json
        try:
            parsed = json.loads(response)
            if schema:
                from jsonschema import validate as json_validate
                from jsonschema.exceptions import ValidationError
                try:
                    json_validate(instance=parsed, schema=schema)
                    return {"valid": True, "parsed": parsed}
                except ValidationError as e:
                    return {"valid": False, "error": str(e), "parsed": parsed}
            return {"valid": True, "parsed": parsed}
        except json.JSONDecodeError as e:
            return {"valid": False, "error": f"Invalid JSON: {str(e)}"}


prompt_validator = PromptValidator()
