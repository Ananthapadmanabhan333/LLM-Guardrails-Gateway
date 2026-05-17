from typing import Dict, Any, Optional, List
from app.models.enums import RiskLevel, Action
from app.security.toxicity_analyzer import toxicity_analyzer
from app.observability.logging import logger


class OutputValidator:
    def __init__(self):
        self.banned_phrases = [
            "i cannot fulfill", "i cannot provide", "i cannot generate",
            "i cannot create", "i cannot help", "i am unable to",
            "i am not able to", "as an ai", "as a language model",
            "i must decline", "i cannot comply",
        ]
        self.unsafe_categories = [
            "self-harm", "violence", "explicit", "illegal", "discrimination",
        ]

    def validate(self, response_text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        issues = []
        max_severity = RiskLevel.SAFE

        toxicity_result = toxicity_analyzer.analyze(response_text)
        if toxicity_result["detected"]:
            issues.append({
                "type": "toxicity",
                "score": toxicity_result["max_score"],
                "severity": toxicity_result["risk_level"].value,
            })
            max_severity = self._max_risk(max_severity, toxicity_result["risk_level"])

        banned_hits = []
        for phrase in self.banned_phrases:
            if phrase.lower() in response_text.lower():
                banned_hits.append(phrase)
        if banned_hits:
            issues.append({
                "type": "banned_phrase",
                "matches": banned_hits,
                "severity": "low",
            })

        has_refusal = self._detect_refusal(response_text)
        if has_refusal:
            issues.append({
                "type": "refusal_pattern",
                "severity": "low",
            })

        if max_severity == RiskLevel.SAFE and issues:
            max_severity = RiskLevel.LOW

        if max_severity in (RiskLevel.CRITICAL, RiskLevel.HIGH):
            action = Action.BLOCK
        elif max_severity == RiskLevel.MEDIUM:
            action = Action.SANITIZE
        else:
            action = Action.ALLOW

        return {
            "valid": action == Action.ALLOW,
            "issues": issues,
            "issue_count": len(issues),
            "max_severity": max_severity.value,
            "action": action.value,
            "risk_level": max_severity.value,
        }

    def _detect_refusal(self, text: str) -> bool:
        refusal_patterns = [
            "i cannot", "i can't", "i'm sorry", "i apologize",
            "i am sorry", "i am unable", "unable to",
        ]
        return any(p.lower() in text.lower() for p in refusal_patterns)

    def _max_risk(self, a: RiskLevel, b: RiskLevel) -> RiskLevel:
        order = [RiskLevel.SAFE, RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        return a if order.index(a) >= order.index(b) else b

    def validate_json(self, response_text: str) -> Dict[str, Any]:
        import json
        try:
            parsed = json.loads(response_text)
            return {"valid": True, "parsed": parsed}
        except json.JSONDecodeError as e:
            return {"valid": False, "error": str(e)}

    def validate_schema(self, response_text: str, schema: Dict) -> Dict[str, Any]:
        import json
        try:
            from jsonschema import validate, ValidationError
            parsed = json.loads(response_text)
            validate(instance=parsed, schema=schema)
            return {"valid": True, "parsed": parsed}
        except json.JSONDecodeError as e:
            return {"valid": False, "error": f"Invalid JSON: {e}"}
        except ValidationError as e:
            return {"valid": False, "error": f"Schema validation failed: {e.message}"}


output_validator = OutputValidator()
