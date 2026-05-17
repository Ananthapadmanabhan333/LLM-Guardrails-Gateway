from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from app.models.schemas import AnalysisResponse, ThreatAnalysis
from app.models.enums import ThreatType, RiskLevel, Action
from app.security.injection_detector import injection_detector
from app.security.jailbreak_detector import jailbreak_detector
from app.security.pii_scanner import pii_scanner
from app.security.toxicity_analyzer import toxicity_analyzer
from app.security.semantic_firewall import semantic_firewall
from app.security.threat_scorer import threat_scorer
from app.middleware.auth import authenticate_request

router = APIRouter(prefix="/security", tags=["Security"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_prompt(
    request: Request,
    auth: tuple = Depends(authenticate_request),
):
    body = await request.json()
    text = body.get("text", "")
    messages = body.get("messages")

    if not text and not messages:
        raise HTTPException(status_code=400, detail="Either text or messages required")

    if messages:
        text = " ".join(m.get("content", "") for m in messages if isinstance(m.get("content"), str))

    score_result = threat_scorer.score_request(text, messages)

    injection_result = injection_detector.analyze(text) if text else None
    jailbreak_result = jailbreak_detector.analyze(text) if text else None
    pii_result = pii_scanner.scan(text) if text else None
    toxicity_result = toxicity_analyzer.analyze(text) if text else None
    semantic_result = semantic_firewall.analyze(text) if text else None

    threats = []
    if injection_result and injection_result.get("detected"):
        threats.append(ThreatAnalysis(
            threat_type=ThreatType.PROMPT_INJECTION,
            risk_level=injection_result["risk_level"],
            score=injection_result["max_score"],
            detector_name="regex_injection_detector",
            details={"findings": injection_result.get("findings", [])},
        ))
    if jailbreak_result and jailbreak_result.get("detected"):
        threats.append(ThreatAnalysis(
            threat_type=ThreatType.JAILBREAK,
            risk_level=jailbreak_result["risk_level"],
            score=jailbreak_result["max_score"],
            detector_name="pattern_jailbreak_detector",
            details={"findings": jailbreak_result.get("findings", [])},
        ))
    if toxicity_result and toxicity_result.get("detected"):
        threats.append(ThreatAnalysis(
            threat_type=ThreatType.TOXICITY,
            risk_level=toxicity_result["risk_level"],
            score=toxicity_result["max_score"],
            detector_name="toxicity_analyzer",
            details={"findings": toxicity_result.get("findings", [])},
        ))

    pii_entities = []
    if pii_result and pii_result.get("pii_found"):
        for finding in pii_result.get("findings", []):
            pii_entities.append({
                "entity_type": finding["entity_type"],
                "text_preview": finding["text_preview"],
                "severity": finding["severity"],
                "risk_level": pii_result.get("risk_level", RiskLevel.LOW).value if hasattr(pii_result.get("risk_level"), "value") else pii_result.get("risk_level", "low"),
            })

    return AnalysisResponse(
        threats=threats,
        overall_risk_score=score_result["final_score"],
        overall_risk_level=score_result["risk_level"],
        recommended_action=score_result["action"],
        pii_entities=pii_entities,
    )


@router.get("/analyze/prompt")
async def analyze_prompt_get(
    prompt: str,
    auth: tuple = Depends(authenticate_request),
):
    score_result = threat_scorer.score_request(prompt)
    return {
        "prompt_length": len(prompt),
        "threat_score": score_result["final_score"],
        "risk_level": score_result["risk_level"].value if hasattr(score_result["risk_level"], "value") else score_result["risk_level"],
        "action": score_result["action"].value if hasattr(score_result["action"], "value") else score_result["action"],
        "component_scores": score_result["component_scores"],
        "threats": score_result["threats"],
    }
