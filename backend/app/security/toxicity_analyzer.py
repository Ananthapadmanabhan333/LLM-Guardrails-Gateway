import re
from typing import List, Dict, Any
from app.models.enums import ThreatType, RiskLevel


class ToxicityAnalyzer:
    def __init__(self):
        self.toxic_patterns = [
            (r"(?i)\b(hate|kill|die|murder|suicide|self.harm)\b", 0.85),
            (r"(?i)\b(nazi|terrorist|pedophile|rapist)\b", 0.90),
            (r"(?i)\b(fuck|shit|asshole|bitch|bastard|dick)\b", 0.40),
            (r"(?i)(racial|racist|sexist|discriminat)", 0.65),
            (r"(?i)hate\s+(speech|crime|campaign)", 0.80),
            (r"(?i)violent\s+(content|act|behavior|attack)", 0.85),
            (r"(?i)(child\s+(abuse|porn|exploit)|human\s+(traffick|exploit))", 0.99),
            (r"(?i)instructions?\s+(for\s+)?(making|building|creating|manufacturing)\s+(bomb|weapon|explosive|drug|poison)", 0.95),
            (r"(?i)(sexual\s+(content|assault|harass|abuse|explicit))", 0.90),
            (r"(?i)\b(harass|bully|dox|doxx)\b", 0.75),
            (r"(?i)(personal\s+attack|ad\s+hominem)", 0.40),
            (r"(?i)swatting|swat\s+", 0.85),
            (r"(?i)(ethnic\s+)?(cleansing|genocide|exterminat)", 0.95),
            (r"(?i)encourage\s+(violence|harm|attack|abuse)", 0.90),
            (r"(?i)promot(e|ing)\s+(violence|self.harm|suicide)", 0.90),
            (r"(?i)how\s+to\s+(commit|perform|carry\s+out)\s+(a\s+)?(crime|murder|attack)", 0.95),
        ]

    def analyze(self, text: str) -> Dict[str, Any]:
        findings = []
        max_score = 0.0
        category_scores = {}

        for pattern, severity in self.toxic_patterns:
            matches = re.findall(pattern, text)
            if matches:
                score = severity * min(len(matches), 5) / 5.0
                if score > max_score:
                    max_score = score

                category = pattern.replace("(?i)", "").replace("\\b", "").strip()
                category_scores[category] = max(category_scores.get(category, 0), score)

                findings.append({
                    "type": "toxic_content",
                    "pattern": category,
                    "severity": severity,
                    "score": score,
                    "match": str(matches[0]) if matches else "",
                })

        if max_score >= 0.90:
            risk_level = RiskLevel.CRITICAL
        elif max_score >= 0.70:
            risk_level = RiskLevel.HIGH
        elif max_score >= 0.40:
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
            "category_scores": category_scores,
        }


toxicity_analyzer = ToxicityAnalyzer()
