from typing import List, Dict, Any, Optional
from app.models.enums import ThreatType, RiskLevel, Action
from app.security.injection_detector import injection_detector
from app.security.jailbreak_detector import jailbreak_detector
from app.security.pii_scanner import pii_scanner
from app.security.toxicity_analyzer import toxicity_analyzer
from app.security.semantic_firewall import semantic_firewall
from app.observability.logging import logger


class ThreatScorer:
    def __init__(self):
        self.weights = {
            "injection": 0.30,
            "jailbreak": 0.25,
            "pii": 0.15,
            "toxicity": 0.15,
            "semantic": 0.15,
        }

    def score_request(self, text: str, messages: Optional[List[Dict]] = None) -> Dict[str, Any]:
        scores = {}

        injection_result = injection_detector.analyze(text) if text else {"detected": False, "max_score": 0.0}
        jailbreak_result = jailbreak_detector.analyze(text) if text else {"detected": False, "max_score": 0.0}
        pii_result = pii_scanner.scan(text) if text else {"pii_found": False, "risk_level": RiskLevel.SAFE}
        toxicity_result = toxicity_analyzer.analyze(text) if text else {"detected": False, "max_score": 0.0}
        semantic_result = semantic_firewall.analyze(text) if text else {"threat_count": 0, "max_score": 0.0}

        scores["injection"] = injection_result.get("max_score", 0.0)
        scores["jailbreak"] = jailbreak_result.get("max_score", 0.0)
        pii_risk_map = {
            RiskLevel.CRITICAL: 0.95,
            RiskLevel.HIGH: 0.75,
            RiskLevel.MEDIUM: 0.50,
            RiskLevel.LOW: 0.25,
            RiskLevel.SAFE: 0.0,
        }
        scores["pii"] = pii_risk_map.get(pii_result.get("risk_level", RiskLevel.SAFE), 0.0)
        scores["toxicity"] = toxicity_result.get("max_score", 0.0)
        scores["semantic"] = semantic_result.get("max_score", 0.0)

        weighted_score = sum(
            scores[key] * self.weights[key]
            for key in scores
        )

        max_individual = max(scores.values()) if scores else 0.0
        final_score = max(weighted_score, max_individual * 0.7)

        if final_score >= 0.85:
            risk_level = RiskLevel.CRITICAL
            action = Action.BLOCK
            recommendation = "Block request - critical threat detected"
        elif final_score >= 0.70:
            risk_level = RiskLevel.HIGH
            action = Action.BLOCK
            recommendation = "Block request - high threat level"
        elif final_score >= 0.55:
            risk_level = RiskLevel.MEDIUM
            action = Action.SANITIZE
            recommendation = "Sanitize request - medium threat level"
        elif final_score >= 0.35:
            risk_level = RiskLevel.LOW
            action = Action.ESCALATE
            recommendation = "Escalate for review - low threat indicators"
        else:
            risk_level = RiskLevel.SAFE
            action = Action.ALLOW
            recommendation = "Allow request - safe"

        threats = []
        if injection_result.get("detected"):
            threats.append({
                "type": ThreatType.PROMPT_INJECTION.value,
                "score": injection_result["max_score"],
                "level": injection_result["risk_level"].value,
            })
        if jailbreak_result.get("detected"):
            threats.append({
                "type": ThreatType.JAILBREAK.value,
                "score": jailbreak_result["max_score"],
                "level": jailbreak_result["risk_level"].value,
            })
        if pii_result.get("pii_found"):
            threats.append({
                "type": ThreatType.PII_LEAKAGE.value,
                "score": scores["pii"],
                "level": pii_result["risk_level"].value,
            })
        if toxicity_result.get("detected"):
            threats.append({
                "type": ThreatType.TOXICITY.value,
                "score": toxicity_result["max_score"],
                "level": toxicity_result["risk_level"].value,
            })
        if semantic_result.get("threat_count", 0) > 0:
            threats.append({
                "type": ThreatType.ADVERSARIAL.value,
                "score": semantic_result["max_score"],
                "level": semantic_result["risk_level"].value,
            })

        return {
            "final_score": final_score,
            "component_scores": scores,
            "risk_level": risk_level,
            "action": action,
            "recommendation": recommendation,
            "threats": threats,
            "details": {
                "injection": injection_result,
                "jailbreak": jailbreak_result,
                "pii": pii_result,
                "toxicity": toxicity_result,
                "semantic": semantic_result,
            },
        }


threat_scorer = ThreatScorer()
