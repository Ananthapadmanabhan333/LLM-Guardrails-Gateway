from typing import Dict, Any, Optional, List, Tuple
from app.models.enums import ModelProvider


class CostOptimizer:
    def __init__(self):
        self.model_costs = {
            "gpt-4o": {"input": 0.0025, "output": 0.01, "provider": ModelProvider.OPENAI},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006, "provider": ModelProvider.OPENAI},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03, "provider": ModelProvider.OPENAI},
            "claude-3-opus": {"input": 0.015, "output": 0.075, "provider": ModelProvider.ANTHROPIC},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015, "provider": ModelProvider.ANTHROPIC},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125, "provider": ModelProvider.ANTHROPIC},
            "gemini-1.5-pro": {"input": 0.00125, "output": 0.005, "provider": ModelProvider.GEMINI},
            "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003, "provider": ModelProvider.GEMINI},
            "mixtral-8x7b": {"input": 0.0006, "output": 0.0006, "provider": ModelProvider.GROQ},
            "llama3-70b": {"input": 0.00059, "output": 0.00079, "provider": ModelProvider.GROQ},
        }
        self.model_latency = {
            "gpt-4o": 1.5,
            "gpt-4o-mini": 0.8,
            "gpt-4-turbo": 2.0,
            "claude-3-opus": 3.0,
            "claude-3-sonnet": 1.5,
            "claude-3-haiku": 0.6,
            "gemini-1.5-pro": 1.5,
            "gemini-1.5-flash": 0.5,
            "mixtral-8x7b": 0.8,
            "llama3-70b": 1.0,
        }

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        costs = self.model_costs.get(model, {"input": 0.001, "output": 0.002})
        return (input_tokens / 1000 * costs["input"]) + (output_tokens / 1000 * costs["output"])

    def estimate_latency(self, model: str, input_tokens: int) -> float:
        base = self.model_latency.get(model, 1.0)
        return base + (input_tokens / 1000) * 0.5

    def get_provider_for_model(self, model: str) -> Optional[ModelProvider]:
        info = self.model_costs.get(model)
        return info["provider"] if info else ModelProvider.OPENAI

    def rank_models(self, criteria: str = "cost") -> List[Tuple[str, float]]:
        if criteria == "cost":
            ranked = sorted(
                self.model_costs.items(),
                key=lambda x: x[1]["input"] + x[1]["output"],
            )
        elif criteria == "latency":
            ranked = sorted(
                self.model_latency.items(),
                key=lambda x: x[1],
            )
        else:
            ranked = list(self.model_costs.items())
        return [(model, info["input"] + info["output"] if criteria == "cost" else self.model_latency.get(model, 1.0)) for model, info in ranked]

    def suggest_models(
        self,
        input_tokens: int,
        output_tokens: int,
        max_cost: Optional[float] = None,
        max_latency: Optional[float] = None,
        safety_level: Optional[str] = None,
    ) -> List[str]:
        suggestions = []
        for model, info in self.model_costs.items():
            cost = self.estimate_cost(model, input_tokens, output_tokens)
            latency = self.estimate_latency(model, input_tokens)

            if max_cost and cost > max_cost:
                continue
            if max_latency and latency > max_latency:
                continue

            suggestions.append(model)

        if safety_level == "high":
            safety_models = [m for m in suggestions if "opus" in m or "4o" in m or "pro" in m]
            return safety_models[:3] if safety_models else suggestions[:3]

        return suggestions[:3]


cost_optimizer = CostOptimizer()
