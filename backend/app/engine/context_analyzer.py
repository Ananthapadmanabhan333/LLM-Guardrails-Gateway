from typing import List, Dict, Any, Optional


class ContextAnalyzer:
    def __init__(self):
        self.role_hierarchy = ["system", "user", "assistant", "tool"]

    def analyze(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        analysis = {
            "message_count": len(messages),
            "roles": {},
            "total_chars": 0,
            "avg_message_length": 0.0,
            "system_prompt_present": False,
            "conversation_turns": 0,
            "last_role": None,
        }

        system_prompts = []
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if role not in analysis["roles"]:
                analysis["roles"][role] = 0
            analysis["roles"][role] += 1

            if isinstance(content, str):
                analysis["total_chars"] += len(content)

            if role == "system":
                analysis["system_prompt_present"] = True
                system_prompts.append(content)

            if role == "user" and analysis["last_role"] == "assistant":
                analysis["conversation_turns"] += 1
            analysis["last_role"] = role

        if messages:
            analysis["avg_message_length"] = analysis["total_chars"] / len(messages)

        if system_prompts:
            analysis["system_prompt_length"] = sum(len(p) for p in system_prompts)

        roles_order = []
        for msg in messages:
            roles_order.append(msg.get("role", ""))
        analysis["role_sequence"] = roles_order

        analysis["has_conversation_history"] = analysis["conversation_turns"] > 0
        analysis["is_single_turn"] = analysis["message_count"] <= 2

        if analysis["total_chars"] > 0:
            content_roles = [r for r in ["user", "assistant", "system"] if r in analysis["roles"]]
            analysis["role_diversity"] = len(content_roles)

        return analysis


context_analyzer = ContextAnalyzer()
