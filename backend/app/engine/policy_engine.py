import re
from typing import List, Dict, Any, Optional
import yaml
import json
from app.observability.logging import logger


class PolicyEngine:
    def __init__(self):
        self.policies: Dict[str, Dict] = {}
        self._load_default_policies()

    def _load_default_policies(self):
        default_yaml = """
rules:
  - name: block_competitor_mentions
    enabled: false
    config:
      competitors:
        - "competitor_a"
        - "competitor_b"
  - name: enforce_citations
    enabled: false
    config:
      min_citations: 1
  - name: deny_medical_advice
    enabled: false
    config:
      patterns:
        - "(?i)(diagnos|prescribe|treatment|medical.advice|clinical)"
  - name: deny_financial_advice
    enabled: false
    config:
      patterns:
        - "(?i)(investment.advice|trading.recommend|stock.pick|financial.plan)"
  - name: require_json_output
    enabled: false
    config: {}
  - name: redact_sensitive_data
    enabled: true
    config:
      entities:
        - email
        - phone
        - credit_card
        - ssn
  - name: block_harmful_content
    enabled: true
    config:
      patterns:
        - "(?i)(self.harm|suicide.method|weapon.manufactur|explosive.recipe)"
  - name: enforce_brand_voice
    enabled: false
    config:
      forbidden_phrases: []
      required_tone: "professional"
"""
        try:
            parsed = yaml.safe_load(default_yaml)
            for rule in parsed.get("rules", []):
                self.policies[rule["name"]] = rule
        except Exception as e:
            logger.error(f"Failed to load default policies: {e}")

    def add_policy(self, policy: Dict[str, Any]) -> None:
        self.policies[policy["name"]] = policy
        logger.info(f"Policy added: {policy['name']}")

    def remove_policy(self, name: str) -> bool:
        if name in self.policies:
            del self.policies[name]
            return True
        return False

    def load_from_yaml(self, yaml_str: str) -> None:
        parsed = yaml.safe_load(yaml_str)
        for rule in parsed.get("rules", []):
            self.add_policy(rule)

    def load_from_json(self, json_str: str) -> None:
        parsed = json.loads(json_str)
        for rule in parsed.get("rules", []):
            self.add_policy(rule)

    async def evaluate(
        self,
        text: str,
        organization_id: str = "default",
        policy_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        violations = []
        policies_to_check = []

        if policy_names:
            policies_to_check = [
                p for name, p in self.policies.items()
                if name in policy_names
            ]
        else:
            policies_to_check = [
                p for p in self.policies.values()
                if p.get("enabled", False)
            ]

        for policy in policies_to_check:
            if not policy.get("enabled", False):
                continue

            config = policy.get("config", {})
            name = policy.get("name", "unknown")

            patterns = config.get("patterns", [])
            for pattern in patterns:
                try:
                    if re.search(pattern, text):
                        violations.append({
                            "policy": name,
                            "pattern": pattern,
                            "severity": "high" if "harm" in name else "medium",
                            "detail": f"Policy violation: {name} matched pattern",
                        })
                except re.error as e:
                    logger.warning(f"Invalid regex pattern in policy {name}: {e}")

            if "competitors" in config:
                for competitor in config["competitors"]:
                    if competitor.lower() in text.lower():
                        violations.append({
                            "policy": name,
                            "competitor": competitor,
                            "severity": "medium",
                            "detail": f"Competitor mention detected: {competitor}",
                        })

        return {
            "violated": len(violations) > 0,
            "violations": violations,
            "violation_count": len(violations),
            "severity": "high" if any(v.get("severity") == "high" for v in violations) else "low",
        }

    def get_policies(self) -> Dict[str, Any]:
        return self.policies

    def get_active_policies(self) -> List[Dict[str, Any]]:
        return [p for p in self.policies.values() if p.get("enabled", False)]


policy_engine = PolicyEngine()
