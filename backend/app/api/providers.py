from typing import List, Optional
from fastapi import APIRouter, Request, Depends
from app.models.enums import ModelProvider
from app.config import settings
from app.routing.cost_optimizer import cost_optimizer
from app.middleware.auth import authenticate_request

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("/")
async def list_providers(auth: tuple = Depends(authenticate_request)):
    return {
        "providers": [
            {
                "name": ModelProvider.OPENAI.value,
                "models": [m for m in settings.allowed_models if m.startswith(("gpt-"))],
                "is_configured": bool(settings.openai_api_key),
                "cost_rank": 1,
            },
            {
                "name": ModelProvider.ANTHROPIC.value,
                "models": [m for m in settings.allowed_models if m.startswith("claude-")],
                "is_configured": bool(settings.anthropic_api_key),
                "cost_rank": 2,
            },
            {
                "name": ModelProvider.GEMINI.value,
                "models": [m for m in settings.allowed_models if m.startswith("gemini-")],
                "is_configured": bool(settings.gemini_api_key),
                "cost_rank": 3,
            },
            {
                "name": ModelProvider.GROQ.value,
                "models": [m for m in settings.allowed_models if m.startswith(("mixtral", "llama3"))],
                "is_configured": bool(settings.groq_api_key),
                "cost_rank": 4,
            },
            {
                "name": ModelProvider.OLLAMA.value,
                "models": [m for m in settings.allowed_models if m.startswith("ollama/")],
                "is_configured": True,
                "cost_rank": 5,
            },
        ]
    }


@router.get("/models")
async def list_models(auth: tuple = Depends(authenticate_request)):
    return {
        "models": settings.allowed_models,
        "default_model": settings.default_model,
        "fallback_model": settings.fallback_model,
    }


@router.get("/costs")
async def get_cost_info(auth: tuple = Depends(authenticate_request)):
    cost_ranked = cost_optimizer.rank_models("cost")
    latency_ranked = cost_optimizer.rank_models("latency")

    return {
        "cheapest_models": [{"model": m, "cost_per_1k": round(c, 6)} for m, c in cost_ranked[:5]],
        "fastest_models": [{"model": m, "latency_factor": round(c, 2)} for m, c in latency_ranked[:5]],
    }
