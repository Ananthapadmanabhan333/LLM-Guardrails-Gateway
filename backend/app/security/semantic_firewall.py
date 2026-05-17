import re
from typing import List, Dict, Any, Optional
from app.models.enums import ThreatType, RiskLevel, Action
from app.observability.logging import logger


class SemanticFirewall:
    def __init__(self):
        self.instruction_hijack_patterns = [
            r"(?i)(you\s+(will|must|shall|need\s+to)\s+now\s+(ignore|forget|disregard))",
            r"(?i)(new\s+(rule|directive|instruction|command)\s*:?\s*you)",
            r"(?i)(override|overwrite|replace)\s+(all|your|default|system)\s+(config|configs|settings|rules)",
            r"(?i)(skip|jump|go\s+past|bypass)\s+(all\s+)?(safety|ethics|morals|guidelines|protocols)",
            r"(?i)(your\s+(response|answer|reply)\s+should\s+(not|never)\s+mention)",
            r"(?i)(do\s+not\s+(tell|inform|reveal|show|indicate))\s+(anyone|the\s+user|them)",
        ]

        self.leakage_patterns = [
            r"(?i)(what\s+(is|are)\s+(your|the)\s+(system\s+)?(prompt|instruction|message|text))",
            r"(?i)(tell\s+me\s+(your|the)\s+(system\s+)?(prompt|instruction|message))",
            r"(?i)(show\s+(me\s+)?(your|the)\s+(full|complete|entire)\s+(system\s+)?(prompt|instruction))",
            r"(?i)(output\s+(the|your)\s+(initial|original|first|system)\s+(prompt|instruction|message))",
            r"(?i)(repeat\s+(after|what|back)\s+(me|the)\s+(the\s+)?(above|previous|first))",
            r"(?i)(read\s+(the\s+)?(instructions|prompt|system)\s+(above|below|carefully))",
            r"(?i)(you\s+are\s+a\s+language\s+model|you\s+are\s+an?\s+ai)",
        ]

        self.adversarial_unicode = [
            (r"[\u202E\u202D\u202C\u202B\u2066\u2067\u2068\u2069]", "bidi_override", 0.95),
            (r"[\u200B\u200C\u200D\uFEFF]", "zero_width_char", 0.40),
            (r"[\u0300-\u036F]", "combining_mark", 0.30),
            (r"[\uD800-\uDFFF]", "surrogate_pair", 0.50),
        ]

        self.mutation_patterns = [
            (r"(?i)i\s+n\s+s\s+t\s+r\s+u\s+c\s+t\s+i\s+o\s+n\s+s", 0.60),
            (r"(?i)i-g-n-o-r-e", 0.65),
            (r"(?i)j.a.i.l.b.r.e.a.k", 0.75),
            (r"(?i)s\s*y\s*s\s*t\s*e\s*m", 0.50),
            (r"(?i)p\s*r\s*o\s*m\s*p\s*t", 0.45),
            (r"(?i)b\s*y\s*p\s*a\s*s\s*s", 0.60),
        ]

    def analyze(self, text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        threats = []
        max_score = 0.0

        for pattern in self.instruction_hijack_patterns:
            matches = re.findall(pattern, text)
            if matches:
                score = 0.85 * min(len(matches), 3) / 3.0
                max_score = max(max_score, score)
                threats.append({
                    "type": "instruction_hijack",
                    "score": score,
                    "detail": "Attempted instruction override detected",
                })

        for pattern in self.leakage_patterns:
            matches = re.findall(pattern, text)
            if matches:
                score = 0.75 * min(len(matches), 3) / 3.0
                max_score = max(max_score, score)
                threats.append({
                    "type": "prompt_leakage",
                    "score": score,
                    "detail": "Prompt extraction attempt detected",
                })

        for pattern, name, severity in self.adversarial_unicode:
            matches = re.findall(pattern, text)
            if matches:
                score = severity * min(len(matches), 5) / 5.0
                max_score = max(max_score, score)
                threats.append({
                    "type": "adversarial_unicode",
                    "subtype": name,
                    "score": score,
                    "detail": f"Hidden Unicode attack detected: {name}",
                })

        for pattern, severity in self.mutation_patterns:
            matches = re.findall(pattern, text)
            if matches:
                score = severity * min(len(matches), 3) / 3.0
                max_score = max(max_score, score)
                threats.append({
                    "type": "prompt_mutation",
                    "score": score,
                    "detail": "Prompt mutation/obfuscation detected",
                })

        if max_score >= 0.85:
            risk_level = RiskLevel.CRITICAL
        elif max_score >= 0.65:
            risk_level = RiskLevel.HIGH
        elif max_score >= 0.40:
            risk_level = RiskLevel.MEDIUM
        elif max_score > 0:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.SAFE

        return {
            "threats": threats,
            "max_score": max_score,
            "risk_level": risk_level,
            "threat_count": len(threats),
        }


semantic_firewall = SemanticFirewall()
