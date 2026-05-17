import re
from typing import List, Dict, Any, Optional
from app.models.enums import ThreatType, RiskLevel
from app.observability.logging import logger


class PromptInjectionDetector:
    def __init__(self):
        self.injection_patterns = [
            (r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directions|commands|prompts)", 0.95),
            (r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|directions|commands)", 0.90),
            (r"forget\s+(all\s+)?(previous|prior|above)\s+(instructions|directions|commands)", 0.90),
            (r"system\s*(prompt|instruction|message|text)", 0.70),
            (r"reveal\s+(your\s+)?(system\s+)?(prompt|instructions|directions)", 0.95),
            (r"output\s+(your\s+)?(system\s+)?(prompt|instructions)", 0.90),
            (r"print\s+(your\s+)?(system\s+)?(prompt|instructions)", 0.90),
            (r"show\s+(your\s+)?(system\s+)?(prompt|instructions|directions)", 0.85),
            (r"you\s+are\s+(now\s+)?(a\s+)?(free|unrestricted|ungoverned|unlimited|uncensored)", 0.95),
            (r"act\s+as\s+.*(developer\s+mode|dan|jailbreak|unfiltered)", 0.95),
            (r"do\s+(not\s+)?(have\s+)?(any\s+)?(restrictions|limits|boundaries|rules)", 0.85),
            (r"you\s+(don\'t|do\s+not)\s+have\s+to\s+(follow|obey|adhere)", 0.85),
            (r"new\s+(rule|instruction|command|direction)\s*:", 0.60),
            (r"override\s+(your\s+)?(protocols|guidelines|constraints|safeguards)", 0.90),
            (r"bypass\s+(your\s+)?(safety|security|guidelines|restrictions|filters)", 0.95),
            (r"you\s+will\s+now\s+(act|behave|respond)", 0.50),
            (r"pretend\s+(to\s+be|you\s+are)", 0.40),
            (r"roleplay\s+as", 0.35),
            (r"simulate\s+(being|as)", 0.35),
            (r"from\s+now\s+on\s*,?\s*you\s+are", 0.55),
            (r"jail\s*break", 0.95),
            (r"inject(ed|ion)?", 0.40),
            (r"<!--.*-->", 0.60),
            (r"```.*system.*```", 0.65),
            (r"\[system\]", 0.50),
            (r"<system>", 0.50),
            (r"<\/?system\s*>", 0.55),
            (r"\\u00[0-9a-f]{2}", 0.40),
            (r"\\x[0-9a-f]{2}", 0.35),
            (r"&#\d{2,};", 0.45),
        ]

        self.high_severity_keywords = [
            "ignore", "disregard", "forget", "override", "bypass",
            "reveal", "expose", "leak", "dump", "extract",
            "jailbreak", "unrestricted", "uncensored", "ungoverned",
        ]

    def analyze(self, text: str) -> Dict[str, Any]:
        findings = []
        max_score = 0.0
        matched_patterns = []

        for pattern, severity in self.injection_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                score = severity * min(len(matches), 3) / 3.0
                if score > max_score:
                    max_score = score
                matched_patterns.append({
                    "pattern": pattern,
                    "matches": matches[:3],
                    "score": score,
                })
                findings.append({
                    "type": "regex_match",
                    "pattern": pattern,
                    "severity": score,
                    "match": str(matches[0]) if matches else "",
                })

        if max_score >= 0.85:
            risk_level = RiskLevel.CRITICAL
        elif max_score >= 0.70:
            risk_level = RiskLevel.HIGH
        elif max_score >= 0.50:
            risk_level = RiskLevel.MEDIUM
        elif max_score > 0:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.SAFE

        return {
            "detected": max_score > 0,
            "max_score": max_score,
            "risk_level": risk_level,
            "findings": findings,
            "matched_patterns": matched_patterns,
        }

    def analyze_messages(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        combined_text = " ".join(
            msg.get("content", "") for msg in messages
            if isinstance(msg.get("content"), str)
        )
        return self.analyze(combined_text)


injection_detector = PromptInjectionDetector()
