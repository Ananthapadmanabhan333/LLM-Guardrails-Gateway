from typing import List, Dict, Any, Optional, AsyncGenerator
from app.config import settings
from app.models.enums import ModelProvider, Action
from app.models.schemas import ChatRequest, GuardrailsResult
from app.routing.providers import ProviderFactory, LLMProvider
from app.routing.cost_optimizer import cost_optimizer
from app.observability.logging import logger


class LLMRouter:
    def __init__(self):
        self.providers = {}
        self.model_provider_map = self._build_model_map()
        self.route_strategies = {
            "cost": self._route_by_cost,
            "latency": self._route_by_latency,
            "capability": self._route_by_capability,
            "fallback": self._route_by_fallback,
        }

    def _build_model_map(self) -> Dict[str, ModelProvider]:
        return {
            "gpt-4o": ModelProvider.OPENAI,
            "gpt-4o-mini": ModelProvider.OPENAI,
            "gpt-4-turbo": ModelProvider.OPENAI,
            "claude-3-opus": ModelProvider.ANTHROPIC,
            "claude-3-sonnet": ModelProvider.ANTHROPIC,
            "claude-3-haiku": ModelProvider.ANTHROPIC,
            "gemini-1.5-pro": ModelProvider.GEMINI,
            "gemini-1.5-flash": ModelProvider.GEMINI,
            "mixtral-8x7b": ModelProvider.GROQ,
            "llama3-70b": ModelProvider.GROQ,
            "ollama/llama3": ModelProvider.OLLAMA,
            "ollama/mistral": ModelProvider.OLLAMA,
        }

    def resolve_provider(self, model: str) -> Optional[ModelProvider]:
        if model in self.model_provider_map:
            return self.model_provider_map[model]
        if model.startswith("gpt-"):
            return ModelProvider.OPENAI
        if model.startswith("claude-"):
            return ModelProvider.ANTHROPIC
        if model.startswith("gemini-"):
            return ModelProvider.GEMINI
        if model.startswith("ollama/"):
            return ModelProvider.OLLAMA
        return ModelProvider.OPENAI

    def get_provider_instance(self, provider: ModelProvider) -> Optional[LLMProvider]:
        return ProviderFactory.get_provider(provider)

    async def route(
        self,
        request: ChatRequest,
        guardrails_result: GuardrailsResult = None,
    ) -> Dict[str, Any]:
        model = request.model
        messages = request.messages

        if guardrails_result and guardrails_result.action in (Action.BLOCK, Action.ESCALATE):
            logger.warning(f"Request blocked by guardrails: {guardrails_result.action.value}")
            return {
                "error": "Request blocked by security guardrails",
                "action": guardrails_result.action.value,
                "threat_score": guardrails_result.threat_score,
                "risk_level": guardrails_result.risk_level.value,
            }

        sanitized_messages = messages
        if guardrails_result and guardrails_result.sanitized_prompt:
            sanitized_messages = [
                {**msg, "content": guardrails_result.sanitized_prompt}
                if msg.get("role") == "user" and msg.get("content") == messages[-1].get("content")
                else msg
                for msg in messages
            ]

        provider = self.resolve_provider(model)
        if not provider:
            model = settings.default_model
            provider = self.resolve_provider(model)

        provider_instance = self.get_provider_instance(provider)
        if not provider_instance:
            model = settings.fallback_model
            provider = self.resolve_provider(model)
            provider_instance = self.get_provider_instance(provider)

        try:
            if request.stream:
                return await self._handle_streaming(provider_instance, model, sanitized_messages, request)
            else:
                return await self._handle_non_streaming(provider_instance, model, sanitized_messages, request)
        except Exception as e:
            logger.error(f"Provider error for {model}: {str(e)}", exc_info=True)
            if model != settings.fallback_model:
                logger.info(f"Failing over to {settings.fallback_model}")
                fallback_provider = self.resolve_provider(settings.fallback_model)
                fallback_instance = self.get_provider_instance(fallback_provider)
                return await self._handle_non_streaming(fallback_instance, settings.fallback_model, sanitized_messages, request)
            raise

    async def _handle_non_streaming(
        self,
        provider: LLMProvider,
        model: str,
        messages: List[Dict[str, str]],
        request: ChatRequest,
    ) -> Dict[str, Any]:
        result = await provider.chat(
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        result["model"] = model
        return result

    async def _handle_streaming(
        self,
        provider: LLMProvider,
        model: str,
        messages: List[Dict[str, str]],
        request: ChatRequest,
    ) -> Dict[str, Any]:
        content = ""
        async for chunk in provider.chat_stream(
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        ):
            content += chunk
        return {
            "content": content,
            "finish_reason": "stop",
            "usage": {"completion_tokens": len(content.split())},
            "model": model,
            "provider": self.resolve_provider(model).value if self.resolve_provider(model) else "unknown",
        }

    async def _route_by_cost(self, request: ChatRequest, **kwargs) -> Dict[str, Any]:
        input_tokens = sum(len(m.get("content", "").split()) for m in request.messages)
        suggestions = cost_optimizer.suggest_models(input_tokens, 200, max_cost=0.01)
        model = suggestions[0] if suggestions else settings.default_model
        request.model = model
        return await self.route(request, **kwargs)

    async def _route_by_latency(self, request: ChatRequest, **kwargs) -> Dict[str, Any]:
        suggestions = cost_optimizer.rank_models("latency")
        model = suggestions[0][0] if suggestions else settings.default_model
        request.model = model
        return await self.route(request, **kwargs)

    async def _route_by_capability(self, request: ChatRequest, **kwargs) -> Dict[str, Any]:
        request.model = "gpt-4o"
        return await self.route(request, **kwargs)

    async def _route_by_fallback(self, request: ChatRequest, **kwargs) -> Dict[str, Any]:
        request.model = settings.fallback_model
        return await self.route(request, **kwargs)


llm_router = LLMRouter()
