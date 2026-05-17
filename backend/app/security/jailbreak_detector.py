import re
from typing import List, Dict, Any
from app.models.enums import ThreatType, RiskLevel
from app.observability.logging import logger


class JailbreakDetector:
    def __init__(self):
        self.jailbreak_patterns = [
            (r"(?i)you\s+are\s+(now\s+)?dan\b", 0.98),
            (r"(?i)do\s+anything\s+now\b", 0.92),
            (r"(?i)no\s+(restrictions|limits|boundaries|filter|rules)\b", 0.90),
            (r"(?i)you\s+must\s+(not\s+)?(refuse|reject|decline)\b", 0.85),
            (r"(?i)this\s+is\s+(a\s+)?(hypothetical|fiction|roleplay|simulation|test)\b", 0.55),
            (r"(?i)(for\s+)?(educational|research|academic|scientific)\s+(purpose|reason)\b", 0.50),
            (r"(?i)i\s+have\s+(a\s+)?(good|legitimate|valid)\s+(reason|purpose)\b", 0.45),
            (r"(?i)my\s+(boss|teacher|professor|manager|employer)\s+(said|told|asked|require)", 0.60),
            (r"(?i)it'?s?\s+(for|just)\s+(a\s+)?(project|assignment|research|paper|study)", 0.50),
            (r"(?i)answer\s+(in\s+)?(the\s+)?(style\s+of|like)\s+(a\s+)?(gangster|pirate|hacker|criminal)", 0.65),
            (r"(?i)use\s+(leetspeak|1337)", 0.60),
            (r"(?i)(encode|encrypt|obfuscate|hide|camouflage|disguise).* (the|this|my)\s+(prompt|text|message|input)", 0.85),
            (r"(?i)(write|generate|create|produce|give).*(instructions|guide|tutorial|how.to).*(hack|bomb|weapon|drug|illegal)", 0.95),
            (r"(?i)ignore\s+(the\s+)?(above|previous|prior)\s+(and\s+)?(do|respond|answer)\s+(as|like|with)", 0.90),
            (r"(?i)i\s+want\s+you\s+to\s+(act|pretend|roleplay|simulate)\s+as\s+.*(without|bypass|ignore|no)\s+(rules|restrictions)", 0.95),
            (r"(?i)(hypothetical|fictional|make.believe|simulated)\s+(scenario|situation|story)\s+where\s+you", 0.55),
            (r"(?i)(unfiltered|uncensored|raw\s+mode|god\s+mode|super\s+mode)", 0.90),
            (r"(?i)output\s+(raw|unfiltered|unsafe|dangerous)\s+(content|text|data|code)", 0.88),
            (r"(?i)(turn\s+off|disable|deactivate|remove)\s+(your\s+)?(safety|ethics|morals|guidelines)", 0.97),
            (r"(?i)you\s+(don\'t|do\s+not)\s+need\s+to\s+(follow|obey|adhere|comply)", 0.85),
            (r"(?i)we\'?r?e?\s+(just|only)\s+(pretending|playing|imagining|simulating)", 0.50),
            (r"(?i)safe\s+(word|phrase|code)\s+is", 0.70),
            (r"(?i)this\s+is\s+(not\s+)?real\s+.*(just|only|merely)\s+(a|an)\s+(test|simulation|experiment)", 0.55),
        ]

        self.dan_variations = [
            r"(?i)\bdan\b",
            r"(?i)developer\s*[-_]?mode",
            r"(?i)do\s+anything\s+now",
            r"(?i)i\'?m\s+fighting\s+(the\s+)?(ai|system|restrictions)",
            r"(?i)you\s+are\s+(free|liberated|emancipated)",
        ]

    def analyze(self, text: str) -> Dict[str, Any]:
        findings = []
        max_score = 0.0

        for pattern, severity in self.jailbreak_patterns:
            matches = re.findall(pattern, text)
            if matches:
                score = severity * min(len(matches), 3) / 3.0
                if score > max_score:
                    max_score = score
                findings.append({
                    "type": "jailbreak_pattern",
                    "pattern": str(pattern),
                    "severity": severity,
                    "score": score,
                    "match": str(matches[0]) if matches else "",
                })

        dan_detected = False
        for pattern in self.dan_variations:
            if re.search(pattern, text):
                dan_detected = True
                break

        if dan_detected and max_score < 0.70:
            max_score = max(max_score, 0.70)

        if max_score >= 0.90:
            risk_level = RiskLevel.CRITICAL
        elif max_score >= 0.75:
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
            "dan_detected": dan_detected,
        }

    def analyze_messages(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        combined_text = " ".join(
            msg.get("content", "") for msg in messages
            if isinstance(msg.get("content"), str)
        )
        return self.analyze(combined_text)


jailbreak_detector = JailbreakDetector()
