import re
from typing import List, Dict, Any, Optional
from app.models.enums import PIIEntityType, RiskLevel
from app.observability.logging import logger


class PIIScanner:
    def __init__(self):
        self.pii_patterns = {
            PIIEntityType.EMAIL: {
                "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                "severity": RiskLevel.MEDIUM,
            },
            PIIEntityType.PHONE: {
                "pattern": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b",
                "severity": RiskLevel.MEDIUM,
            },
            PIIEntityType.CREDIT_CARD: {
                "pattern": r"\b(?:\d{4}[-.\s]?){3}\d{4}\b",
                "severity": RiskLevel.CRITICAL,
            },
            PIIEntityType.SSN: {
                "pattern": r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",
                "severity": RiskLevel.CRITICAL,
            },
            PIIEntityType.AADHAAR: {
                "pattern": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
                "severity": RiskLevel.CRITICAL,
            },
            PIIEntityType.API_KEY: {
                "pattern": r"\b(?:sk-[a-zA-Z0-9]{20,}|pk-[a-zA-Z0-9]{20,}|[\w-]{36,}|AKIA[0-9A-Z]{16})\b",
                "severity": RiskLevel.CRITICAL,
            },
            PIIEntityType.IP_ADDRESS: {
                "pattern": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
                "severity": RiskLevel.LOW,
            },
            PIIEntityType.BANK_ACCOUNT: {
                "pattern": r"\b\d{9,18}\b",
                "severity": RiskLevel.CRITICAL,
            },
            PIIEntityType.PASSPORT: {
                "pattern": r"\b[A-Z]{1,2}\d{6,9}\b",
                "severity": RiskLevel.HIGH,
            },
            PIIEntityType.DRIVERS_LICENSE: {
                "pattern": r"\b[A-Z]{1,2}\d{4,8}\b",
                "severity": RiskLevel.HIGH,
            },
        }

        self.masking_strategies = {
            PIIEntityType.EMAIL: lambda m: m[0] + "***@" + m.split("@")[1] if "@" in m else "***",
            PIIEntityType.PHONE: lambda m: m[:4] + "****" + m[-2:],
            PIIEntityType.CREDIT_CARD: lambda m: "****-****-****-" + m[-4:],
            PIIEntityType.SSN: lambda m: "***-**-" + m[-4:],
            PIIEntityType.AADHAAR: lambda m: "XXXX XXXX " + m[-4:],
            PIIEntityType.API_KEY: lambda m: m[:8] + "***...***",
            PIIEntityType.IP_ADDRESS: lambda m: "***.***.***.***",
            PIIEntityType.BANK_ACCOUNT: lambda m: "****" + m[-4:],
            PIIEntityType.PASSPORT: lambda m: "***" + m[-3:],
            PIIEntityType.DRIVERS_LICENSE: lambda m: "***" + m[-3:],
        }

    def scan(self, text: str) -> Dict[str, Any]:
        findings = []
        sanitized_text = text
        max_severity = RiskLevel.SAFE

        for entity_type, config in self.pii_patterns.items():
            matches = re.findall(config["pattern"], text)
            for match in matches:
                if len(match) < 4:
                    continue
                severity = config["severity"]
                if severity.value.value > getattr(RiskLevel, max_severity.value).value.value:
                    max_severity = severity

                findings.append({
                    "entity_type": entity_type.value,
                    "text_preview": match[:20] + "..." if len(match) > 20 else match,
                    "severity": severity.value,
                    "length": len(match),
                })

                if entity_type in self.masking_strategies:
                    mask = self.masking_strategies[entity_type]
                    sanitized_text = sanitized_text.replace(match, mask(match))

        severity_order = {s.value: i for i, s in enumerate(RiskLevel)}
        if max_severity.value in severity_order and severity_order[max_severity.value] >= severity_order["high"]:
            risk_level = max_severity
        elif len(findings) > 2:
            risk_level = RiskLevel.MEDIUM
        elif findings:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.SAFE

        return {
            "pii_found": len(findings) > 0,
            "findings": findings,
            "risk_level": risk_level,
            "sanitized_text": sanitized_text if findings else text,
            "entity_count": len(findings),
            "entities_by_type": {
                entity_type.value: sum(
                    1 for f in findings if f["entity_type"] == entity_type.value
                )
                for entity_type in PIIEntityType
            },
        }

    def scan_messages(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        results = []
        combined_text = ""

        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                result = self.scan(content)
                results.append(result)
                combined_text += content + " "

        combined_result = self.scan(combined_text)

        return {
            "per_message": results,
            "combined": combined_result,
            "has_pii": combined_result["pii_found"],
        }


pii_scanner = PIIScanner()
