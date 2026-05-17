from typing import List, Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from app.models.schemas import PolicyDefinition, PolicyRule
from app.engine.policy_engine import policy_engine
from app.middleware.auth import authenticate_request

router = APIRouter(prefix="/policies", tags=["Policies"])


@router.get("/")
async def list_policies(auth: tuple = Depends(authenticate_request)):
    return {
        "policies": policy_engine.get_policies(),
        "active_count": len(policy_engine.get_active_policies()),
        "total_count": len(policy_engine.get_policies()),
    }


@router.post("/")
async def create_policy(policy: PolicyDefinition, auth: tuple = Depends(authenticate_request)):
    policy_dict = {
        "name": policy.name,
        "description": policy.description,
        "policy_type": policy.policy_type,
        "rules": [r.dict() if hasattr(r, "dict") else r.model_dump() for r in policy.rules],
        "enabled": policy.is_active,
        "priority": policy.priority,
        "version": policy.version,
    }
    policy_engine.add_policy(policy_dict)
    return {"status": "created", "policy": policy.name}


@router.delete("/{policy_name}")
async def delete_policy(policy_name: str, auth: tuple = Depends(authenticate_request)):
    if policy_engine.remove_policy(policy_name):
        return {"status": "deleted", "policy": policy_name}
    raise HTTPException(status_code=404, detail=f"Policy '{policy_name}' not found")


@router.post("/load/yaml")
async def load_yaml_policies(request: Request, auth: tuple = Depends(authenticate_request)):
    body = await request.json()
    yaml_content = body.get("yaml", "")
    if not yaml_content:
        raise HTTPException(status_code=400, detail="YAML content required")
    try:
        policy_engine.load_from_yaml(yaml_content)
        return {"status": "loaded", "policies": list(policy_engine.get_policies().keys())}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load YAML: {str(e)}")


@router.post("/load/json")
async def load_json_policies(request: Request, auth: tuple = Depends(authenticate_request)):
    body = await request.json()
    json_content = body.get("json", "")
    if not json_content:
        raise HTTPException(status_code=400, detail="JSON content required")
    try:
        policy_engine.load_from_json(json_content)
        return {"status": "loaded", "policies": list(policy_engine.get_policies().keys())}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load JSON: {str(e)}")


@router.get("/active")
async def get_active_policies(auth: tuple = Depends(authenticate_request)):
    return {"active_policies": policy_engine.get_active_policies()}
