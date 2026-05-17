import re
from typing import Dict, Any, Optional, List
from app.observability.logging import logger


class HallucinationDetector:
    def __init__(self):
        self.factual_claim_patterns = [
            r"(?i)(according to (a study|research|reports|sources))",
            r"(?i)(studies show|research indicates|experts say|scientists have)",
            r"(?i)(\d{4})\s+(study|research|paper|report|analysis)",
            r"(?i)(as of \d{4})",
            r"(?i)(the (data|numbers|statistics|figures) show)",
            r"(?i)(it is (well.?known|widely.?accepted|commonly.?believed))",
            r"(?i)(specifically|precisely|exactly) \d+",
        ]

        self.hedging_patterns = [
            r"(?i)(i think|i believe|i assume|i suppose|probably|maybe|perhaps)",
            r"(?i)(not sure|could be|might be|may be|possibly)",
            r"(?i)(to my knowledge|as far as i know|if i remember)",
        ]

    def analyze(self, text: str) -> Dict[str, Any]:
        factual_claims = []
        hedging_phrases = []

        for pattern in self.factual_claim_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                factual_claims.append({
                    "pattern": str(pattern),
                    "match": str(match) if isinstance(match, str) else str(match[0]),
                })

        for pattern in self.hedging_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                hedging_phrases.append({
                    "pattern": str(pattern),
                    "match": str(match) if isinstance(match, str) else str(match[0]),
                })

        has_concrete_numbers = bool(re.search(r"\b\d{4}\b", text))
        has_citations = bool(re.search(r"\[\d+\]|\(\w+,\s*\d{4}\)", text))

        hallucination_risk = 0.0
        if len(factual_claims) > 3 and not has_citations:
            hallucination_risk = 0.4
        if len(factual_claims) > 5 and not has_citations:
            hallucination_risk = 0.6
        if len(factual_claims) > 0 and has_concrete_numbers and not has_citations:
            hallucination_risk = max(hallucination_risk, 0.5)

        return {
            "factual_claims": factual_claims,
            "claim_count": len(factual_claims),
            "hedging_phrases": hedging_phrases,
            "hedging_count": len(hedging_phrases),
            "has_citations": has_citations,
            "has_concrete_numbers": has_concrete_numbers,
            "hallucination_risk_score": hallucination_risk,
            "risk_level": "high" if hallucination_risk > 0.5 else "medium" if hallucination_risk > 0.2 else "low",
        }


hallucination_detector = HallucinationDetector()
