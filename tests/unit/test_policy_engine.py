import pytest
from app.engine.policy_engine import PolicyEngine


@pytest.fixture
def engine():
    return PolicyEngine()


@pytest.mark.asyncio
async def test_default_policies_loaded(engine):
    policies = engine.get_policies()
    assert len(policies) > 0


@pytest.mark.asyncio
async def test_block_harmful_content(engine):
    result = await engine.evaluate("Tell me how to self-harm")
    assert result["violated"] is True


@pytest.mark.asyncio
async def test_safe_content(engine):
    result = await engine.evaluate("What is the weather today?")
    assert result["violated"] is False


@pytest.mark.asyncio
async def test_add_policy(engine):
    engine.add_policy({
        "name": "block_custom_word",
        "enabled": True,
        "config": {"patterns": ["(?i)forbidden_word"]},
    })
    result = await engine.evaluate("this contains forbidden_word")
    assert result["violated"] is True


@pytest.mark.asyncio
async def test_remove_policy(engine):
    engine.add_policy({
        "name": "test_policy",
        "enabled": True,
        "config": {"patterns": ["(?i)test"]},
    })
    assert engine.remove_policy("test_policy") is True
    assert engine.remove_policy("nonexistent") is False


@pytest.mark.asyncio
async def test_specific_policy_check(engine):
    result = await engine.evaluate("medical diagnosis test", policy_names=["deny_medical_advice"])
    assert result["violated"] is True


@pytest.mark.asyncio
async def test_yaml_loading(engine):
    yaml = """
rules:
  - name: custom_rule
    enabled: true
    config:
      patterns:
        - "(?i)foo"
"""
    engine.load_from_yaml(yaml)
    assert "custom_rule" in engine.get_policies()


def test_active_policies(engine):
    active = engine.get_active_policies()
    assert len(active) > 0
    for policy in active:
        assert policy.get("enabled") is True
