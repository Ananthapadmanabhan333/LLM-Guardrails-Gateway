from typing import List, Dict, Any, Optional, AsyncGenerator
from enum import Enum
import httpx
import json
from app.config import settings
from app.models.enums import ModelProvider
from app.observability.logging import logger


class LLMProvider:
    def __init__(self, provider: ModelProvider, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    async def chat_stream(self, model: str, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(ModelProvider.OPENAI, api_key or settings.openai_api_key, "https://api.openai.com/v1")

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                    **({} if not kwargs.get("stream") else {"stream": True}),
                },
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "finish_reason": data["choices"][0]["finish_reason"],
                "usage": data.get("usage", {}),
                "model": model,
                "provider": ModelProvider.OPENAI.value,
            }

    async def chat_stream(self, model: str, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk["choices"][0].get("delta", {})
                            if delta.get("content"):
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError):
                            continue


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(ModelProvider.ANTHROPIC, api_key or settings.anthropic_api_key, "https://api.anthropic.com/v1")

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        system_msg = None
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                filtered_messages.append(msg)

        async with httpx.AsyncClient(timeout=60.0) as client:
            request_body = {
                "model": model,
                "messages": filtered_messages,
                "max_tokens": kwargs.get("max_tokens", 2048),
            }
            if system_msg:
                request_body["system"] = system_msg
            if kwargs.get("temperature"):
                request_body["temperature"] = kwargs["temperature"]

            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["content"][0]["text"],
                "finish_reason": data.get("stop_reason", "stop"),
                "usage": {"input_tokens": data.get("usage", {}).get("input_tokens", 0), "output_tokens": data.get("usage", {}).get("output_tokens", 0)},
                "model": model,
                "provider": ModelProvider.ANTHROPIC.value,
            }

    async def chat_stream(self, model: str, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        yield ""


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(ModelProvider.GEMINI, api_key or settings.gemini_api_key, "https://generativelanguage.googleapis.com/v1")

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        contents = []
        for msg in messages:
            if msg["role"] in ("user", "assistant"):
                contents.append({
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [{"text": msg["content"]}],
                })

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/models/{model}:generateContent",
                params={"key": self.api_key},
                json={"contents": contents},
            )
            response.raise_for_status()
            data = response.json()
            candidate = data["candidates"][0]
            return {
                "content": candidate["content"]["parts"][0]["text"],
                "finish_reason": candidate.get("finishReason", "stop"),
                "usage": data.get("usageMetadata", {}),
                "model": model,
                "provider": ModelProvider.GEMINI.value,
            }

    async def chat_stream(self, model: str, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        yield ""


class GroqProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(ModelProvider.GROQ, api_key or settings.groq_api_key, "https://api.groq.com/openai/v1")

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                },
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "finish_reason": data["choices"][0]["finish_reason"],
                "usage": data.get("usage", {}),
                "model": model,
                "provider": ModelProvider.GROQ.value,
            }

    async def chat_stream(self, model: str, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        yield ""


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: Optional[str] = None):
        super().__init__(ModelProvider.OLLAMA, base_url=base_url or settings.ollama_base_url)

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        model_name = model.replace("ollama/", "")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model_name,
                    "messages": messages,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["message"]["content"],
                "finish_reason": "stop",
                "usage": {"total_tokens": data.get("eval_count", 0)},
                "model": model,
                "provider": ModelProvider.OLLAMA.value,
            }

    async def chat_stream(self, model: str, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        yield ""


class ProviderFactory:
    _instances = {}

    @classmethod
    def get_provider(cls, provider: ModelProvider) -> LLMProvider:
        if provider not in cls._instances:
            if provider == ModelProvider.OPENAI:
                cls._instances[provider] = OpenAIProvider()
            elif provider == ModelProvider.ANTHROPIC:
                cls._instances[provider] = AnthropicProvider()
            elif provider == ModelProvider.GEMINI:
                cls._instances[provider] = GeminiProvider()
            elif provider == ModelProvider.GROQ:
                cls._instances[provider] = GroqProvider()
            elif provider == ModelProvider.OLLAMA:
                cls._instances[provider] = OllamaProvider()
        return cls._instances[provider]
