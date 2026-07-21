from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from uuid import uuid4

from research.repository import OBJECT_STORE_LOCK, load_objects, save_objects


_LOCK = OBJECT_STORE_LOCK


def now_utc() -> str:
    return datetime.now(UTC).isoformat()


def create_research_object(
    object_type: str,
    owner: str,
    title: str,
    description: str = "",
    status: str = "draft",
    variables: list | None = None,
    analysis_methods: list | None = None,
    research_question: str | None = None,
    hypothesis_basis: str | None = None,
    basis_notes: str | None = None,
    authorship: dict | None = None,
    scientific_definition: dict | None = None,
    provenance_links: list | None = None,
) -> dict:
    if status not in {"draft", "trial", "active"}:
        raise ValueError("RESEARCH_OBJECT_STATUS_UNSUPPORTED")
    if not object_type.strip() or not owner.strip() or not title.strip():
        raise ValueError("RESEARCH_OBJECT_TYPE_OWNER_TITLE_REQUIRED")
    timestamp = now_utc()
    record = {
        "id": str(uuid4()),
        "object_type": object_type,
        "owner": owner,
        "status": status,
        "title": title,
        "description": description,
        "research_question": research_question,
        "hypothesis_basis": hypothesis_basis,
        "basis_notes": basis_notes,
        "variables": variables or [],
        "analysis_methods": analysis_methods or [],
        "evidence": [],
        "validation": {},
        "created_at": timestamp,
        "updated_at": timestamp,
        "approved_by_researcher": owner == "researcher",
        "authorship": authorship or {},
        "scientific_definition": scientific_definition or {},
        "provenance_links": provenance_links or [],
    }
    with _LOCK:
        objects = load_objects()
        objects.append(record)
        save_objects(objects)
    return record


def list_research_objects(
    owner: str | None = None, object_type: str | None = None
) -> list[dict]:
    result = load_objects()
    if owner:
        result = [item for item in result if item.get("owner") == owner]
    if object_type:
        result = [item for item in result if item.get("object_type") == object_type]
    return result


def account_deletion_impact(owner: str) -> dict:
    owned = [item for item in load_objects() if item.get("owner") == owner]
    by_status = {
        status: sum(item.get("status", "draft") == status for item in owned)
        for status in ("draft", "trial", "active")
    }
    return {
        "owner_account_id": owner,
        "total_owned_objects": len(owned),
        "by_status": by_status,
        "draft_object_ids": [item["id"] for item in owned if item.get("status", "draft") == "draft"],
        "immutable_object_ids": [item["id"] for item in owned if item.get("status") in {"trial", "active"}],
    }


def apply_account_deletion_disposition(
    owner: str,
    *,
    delete_owned_drafts: bool,
    authorship_snapshot: dict,
) -> dict:
    pseudonym = "deleted_researcher_" + sha256(owner.encode("utf-8")).hexdigest()[:16]
    removed, pseudonymized = [], []
    timestamp = now_utc()
    with _LOCK:
        objects = load_objects()
        retained = []
        for item in objects:
            if item.get("owner") != owner:
                retained.append(item)
                continue
            status = item.get("status", "draft")
            if status == "draft" and delete_owned_drafts:
                removed.append(item.get("id"))
                continue
            migrated = dict(item)
            migrated["owner"] = pseudonym
            existing_authorship = dict(migrated.get("authorship") or {})
            contributions = list(existing_authorship.get("contributions") or [])
            author_id = authorship_snapshot.get("author_identity_id")
            if not any(entry.get("author_identity_id") == author_id for entry in contributions):
                contributions.append({
                    "author_identity_id": author_id,
                    "display_name": authorship_snapshot.get("display_name"),
                    "roles": ["creator"],
                    "recorded_at": migrated.get("created_at") or timestamp,
                    "account_deletion_does_not_remove_authorship": True,
                })
            existing_authorship["contributions"] = contributions
            existing_authorship["preservation_policy"] = "authorship_survives_account_deletion"
            migrated["authorship"] = existing_authorship
            provenance = dict(migrated.get("provenance") or {})
            provenance["account_deletion"] = {
                "policy": "pseudonymize_and_preserve_provenance",
                "occurred_at": timestamp,
                "former_owner_digest": sha256(owner.encode("utf-8")).hexdigest(),
            }
            migrated["provenance"] = provenance
            migrated["updated_at"] = timestamp
            retained.append(migrated)
            pseudonymized.append(migrated.get("id"))
        save_objects(retained)
    return {
        "deleted_draft_object_ids": removed,
        "pseudonymized_object_ids": pseudonymized,
        "pseudonymous_owner": pseudonym if pseudonymized else None,
    }
