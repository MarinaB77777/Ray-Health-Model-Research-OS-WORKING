from pathlib import Path

import pytest

from ray_colleague.contracts import LearningStatus, MemoryClass, MemoryScope, RayRole, TruthType
from ray_colleague.learning import LearningCandidate, LearningRegistry
from ray_colleague.memory import MemoryRecord, RayMemoryStore


def test_ray_colleague_memory_rejects_protected_memory_class(tmp_path: Path):
    store = RayMemoryStore(tmp_path / "memory.json")
    record = MemoryRecord(
        role=RayRole.RESEARCH_COLLEAGUE,
        owner_id="researcher-1",
        scope=MemoryScope.SESSION,
        summary="must not be accepted",
        provenance={"source": "test"},
        retention_reason="test",
        session_id="session-1",
        memory_class=MemoryClass.HEART_OF_HUMAN,
        truth_type=TruthType.HUMAN_DECLARATION,
        subject="human",
        purpose="test",
    )
    with pytest.raises(PermissionError, match="PROTECTED_MEMORY_CLASS_FORBIDDEN"):
        store.add(record)


def test_ray_colleague_memory_migrates_legacy_record_conservatively(tmp_path: Path):
    path = tmp_path / "memory.json"
    path.write_text(
        '[{"role":"research_colleague","owner_id":"r1","scope":"session",'
        '"summary":"legacy","provenance":{"source":"legacy"},'
        '"retention_reason":"legacy","session_id":"s1","record_id":"m1",'
        '"status":"active","created_at":"2026-01-01T00:00:00+00:00",'
        '"updated_at":"2026-01-01T00:00:00+00:00"}]',
        encoding="utf-8",
    )
    item = RayMemoryStore(path).list_for_owner(
        RayRole.RESEARCH_COLLEAGUE,
        "r1",
        session_id="s1",
    )[0]
    assert item["memory_class"] == "working_operational"
    assert item["truth_type"] == "external_claim"
    assert item["subject"] == "unspecified"
    assert item["freshness_status"] == "unknown"


def test_learning_candidate_rejects_constitutional_target():
    candidate = LearningCandidate(
        role=RayRole.RESEARCH_COLLEAGUE,
        submitted_by="r1",
        target_type="heart_of_ray",
        target_id="heart",
        feedback="change heart",
        expected_behavior="different identity",
        context_scope="global",
    )
    with pytest.raises(PermissionError, match="LEARNING_TARGET_PROTECTED"):
        candidate.validate()


def test_learning_active_requires_evaluation_and_human_approval(tmp_path: Path):
    registry = LearningRegistry(tmp_path / "learning.json")
    added = registry.add(
        LearningCandidate(
            role=RayRole.RESEARCH_COLLEAGUE,
            submitted_by="r1",
            target_type="coordination_rule",
            target_id="rule-1",
            feedback="improve timing",
            expected_behavior="batch low-value questions",
            context_scope="research_workspace",
        )
    )
    trial = registry.transition(
        added["candidate_id"],
        LearningStatus.TRIAL,
        evaluation={"evidence": "reviewed"},
    )
    assert trial["status"] == "trial"
    with pytest.raises(ValueError, match="HUMAN_APPROVAL_REQUIRED_FOR_ACTIVE"):
        registry.transition(
            added["candidate_id"],
            LearningStatus.ACTIVE,
            evaluation={"evidence": "reviewed"},
        )
