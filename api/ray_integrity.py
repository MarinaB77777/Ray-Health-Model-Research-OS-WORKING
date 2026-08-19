from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from external_core import ExternalCoreService


app = FastAPI(title="Ray Integrity Observability")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
STATIC_PAGE = ROOT / "static" / "ray_integrity.html"


ARCHITECTURE_CONTRACTS = {
    "heart_of_ray": ROOT / "docs/inner_core/heart_of_ray_specification.md",
    "conflict_resolution_kernel": ROOT / "docs/inner_core/conflict_resolution_kernel.md",
    "memory_architecture": ROOT / "docs/architecture/ray_memory_architecture.md",
    "inner_core_boundary": ROOT / "runtime/architecture/inner_core_boundary_contract.md",
    "projection_governance": ROOT / "runtime/architecture/projection_governance.md",
    "acceptable_harm_projection": ROOT / "runtime/architecture/acceptable_harm_projection.md",
    "projection_review_lifecycle": ROOT / "runtime/architecture/projection_review_lifecycle.md",
    "runtime_memory_boundary": ROOT / "runtime/architecture/runtime_memory_boundary_contract.md",
    "capability_boundary": ROOT / "runtime/architecture/runtime_capability_boundary_contract.md",
}

IMPLEMENTATION_COMPONENTS = {
    "external_core": ROOT / "external_core/service.py",
    "governance": ROOT / "governance/service.py",
    "runtime": ROOT / "runtime/service.py",
    "working_memory_compatibility": ROOT / "temporary_memory/memory_store.py",
    "ray_colleague_memory": ROOT / "ray_colleague/memory.py",
    "ray_colleague_learning": ROOT / "ray_colleague/learning.py",
    "learning_boundary": ROOT / "model_engine/learning_boundary.py",
    "analysis_checker": ROOT / "assessment/analysis/analysis_checker.py",
}

PROTECTED_COMPONENTS = {
    "heart_of_ray": {
        "architecture_defined": True,
        "provisioned": False,
        "raw_content_exposed": False,
        "status": "DRAFT_NOT_SEALED",
    },
    "heart_of_human": {
        "architecture_defined": True,
        "provisioned": False,
        "raw_content_exposed": False,
        "status": "NOT_PROVISIONED",
    },
    "ray_self_health": {
        "architecture_defined": True,
        "production_store_implemented": False,
        "raw_content_exposed": False,
        "status": "ARCHITECTURE_ONLY",
    },
}


def _file_status(path: Path) -> dict[str, Any]:
    return {
        "present": path.exists(),
        "path": str(path.relative_to(ROOT)),
    }


def _external_core_status() -> dict[str, Any]:
    try:
        service = ExternalCoreService(DATA_DIR)
        result: dict[str, Any] = {
            "available": True,
            "protected_memory_access": False,
        }
        # Observability deliberately reports contracts/scopes only. It never
        # serializes protected memory content or credentials.
        if hasattr(service, "contract"):
            contract = service.contract()
            if isinstance(contract, dict):
                result["contract"] = contract
        return result
    except Exception as exc:  # observability must expose degradation, not fake OK
        return {
            "available": False,
            "protected_memory_access": False,
            "error_type": type(exc).__name__,
            "status": "DEGRADED",
        }


@app.get("/ray-integrity", response_class=HTMLResponse)
def ray_integrity_page() -> str:
    return STATIC_PAGE.read_text(encoding="utf-8")


@app.get("/ray-integrity/status")
def ray_integrity_status() -> dict[str, Any]:
    return {
        "schema": "ray.integrity.observability.v1",
        "purpose": "developer_observability_without_raw_inner_core",
        "inner_core": PROTECTED_COMPONENTS,
        "contracts": {
            name: _file_status(path)
            for name, path in ARCHITECTURE_CONTRACTS.items()
        },
        "implementation": {
            name: _file_status(path)
            for name, path in IMPLEMENTATION_COMPONENTS.items()
        },
        "external_core": _external_core_status(),
        "self_health": {
            "sensor_state": "NO_DEVICE",
            "production_store": "NOT_IMPLEMENTED",
            "note": "No physical Self-Health sensor/store is connected yet; no measurements are fabricated.",
        },
        "learning": {
            "engine": "NOT_IMPLEMENTED",
            "boundary": "IMPLEMENTED",
            "auto_heart_promotion": False,
            "auto_permission_mutation": False,
            "truth_authority_created": False,
        },
        "invariants": {
            "raw_inner_core_exposed": False,
            "projection_is_permission": False,
            "memory_is_authority": False,
            "unknown_equals_zero": False,
            "runtime_completed_proves_external_effect": False,
            "external_ai_is_ray_memory": False,
        },
    }
