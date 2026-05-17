from typing import List, Dict, Any, Optional, Tuple
from app.models.enums import ThreatType, RiskLevel, Action
from app.models.schemas import GuardrailsResult
from app.security.threat_scorer import threat_scorer
from app.security.pii_scanner import pii_scanner
from app.engine.policy_engine import policy_engine
from app.engine.prompt_validator import prompt_validator
from app.engine.context_analyzer import context_analyzer
from app.observability.logging import logger


class GuardrailsEngine:
    def __init__(self):
        self.enabled_checks = [
            "injection",
            "jailbreak",
            "pii",
            "toxicity",
            "semantic",
            "policy",
            "validation",
        ]

    async def process_request(
        self,
        messages: List[Dict[str, str]],
        model: str,
        organization_id: str = "default",
        policies: Optional[List[str]] = None,
    ) -> GuardrailsResult:
        text = " ".join(
            msg.get("content", "") for msg in messages
            if isinstance(msg.get("content"), str)
        )

        if not text.strip():
            return GuardrailsResult()

        threat_result = threat_scorer.score_request(text, messages)

        pii_result = pii_scanner.scan(text)

        policy_result = await policy_engine.evaluate(
            text=text,
            organization_id=organization_id,
            policy_names=policies,
        )

        validation_result = prompt_validator.validate(text)

        context_result = context_analyzer.analyze(messages)

        all_threats = threat_result.get("threats", [])
        all_policy_violations = [
            v for v in policy_result.get("violations", [])
        ] if policy_result.get("violated") else []

        action = threat_result.get("action", Action.ALLOW)
        risk_level = threat_result.get("risk_level", RiskLevel.SAFE)
        final_score = threat_result.get("final_score", 0.0)

        if policy_result.get("violated") and action in (Action.ALLOW, Action.ESCALATE):
            action = Action.BLOCK if policy_result.get("severity") in ("high", "critical") else Action.SANITIZE
            final_score = max(final_score, 0.7)

        sanitized_prompt = None
        if action in (Action.SANITIZE, Action.ESCALATE):
            sanitized_prompt = pii_result.get("sanitized_text", text)

        if validation_result.get("errors"):
            all_threats.append({
                "type": "validation_error",
                "detail": validation_result["errors"],
            })

        logger.info(
            "Guardrails processing complete",
            extra={
                "action": action.value,
                "risk_level": risk_level.value,
                "score": final_score,
                "threats": len(all_threats),
                "policy_violations": len(all_policy_violations),
            }
        )

        return GuardrailsResult(
            threat_score=final_score,
            risk_level=risk_level,
            action=action,
            threats=all_threats,
            pii_found=pii_result.get("findings", []),
            policy_violations=all_policy_violations,
            sanitized_prompt=sanitized_prompt,
            details={
                "threat_assessment": threat_result,
                "pii_assessment": {k: v for k, v in pii_result.items() if k != "sanitized_text"},
                "policy_assessment": policy_result,
                "validation": validation_result,
                "context": context_result,
            },
        )


guardrails_engine = GuardrailsEngine()
