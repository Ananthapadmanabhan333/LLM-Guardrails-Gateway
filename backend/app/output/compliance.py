import re
from typing import Dict, Any, Optional, List


class ComplianceValidator:
    def __init__(self):
        self.compliance_rules = {
            "gdpr": {
                "patterns": [
                    r"(?i)\b(electronic\s+?consent|data\s+?subject\s+?access\s+?request|right\s+?to\s+?be\s+?forgotten)\b",
                    r"(?i)\b(personal\s+?data\s+?breach|data\s+?protection\s+?officer|supervisory\s+?authority)\b",
                ],
                "require_disclaimer": True,
            },
            "hipaa": {
                "patterns": [
                    r"(?i)\b(phi|protected\s+health\s+information|medical\s+record|patient\s+data)\b",
                    r"(?i)\b(treatment|payment|health\s+care\s+operations|covered\s+entity)\b",
                ],
                "require_disclaimer": True,
            },
            "sox": {
                "patterns": [
                    r"(?i)\b(financial\s+reporting|internal\s+controls|audit\s+committee|disclosure)\b",
                ],
                "require_disclaimer": True,
            },
            "ccpa": {
                "patterns": [
                    r"(?i)\b(california\s+consumer|right\s+to\s+opt.out|personal\s+information\s+sale)\b",
                ],
                "require_disclaimer": True,
            },
        }

    def validate(self, text: str, compliance_flags: Optional[List[str]] = None) -> Dict[str, Any]:
        violations = []
        flags = compliance_flags or list(self.compliance_rules.keys())

        for flag in flags:
            rule = self.compliance_rules.get(flag)
            if not rule:
                continue

            for pattern in rule["patterns"]:
                if re.search(pattern, text):
                    violations.append({
                        "framework": flag.upper(),
                        "pattern": str(pattern),
                        "type": "potential_regulatory_reference",
                        "requires_disclaimer": rule.get("require_disclaimer", False),
                    })

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "violation_count": len(violations),
            "frameworks_triggered": list(set(v["framework"] for v in violations)),
        }


compliance_validator = ComplianceValidator()
