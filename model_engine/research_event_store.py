from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

RESEARCH_EVENT_SCHEMA_VERSION = "research-event-1"
RESEARCH_EVENT_STORE_VERSION = "research-event-store-1"
RESEARCH_CONTRACT_VERSION = "pilot-research-contract-1"

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ResearchEventRecord:
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_schema_version: str = RESEARCH_EVENT_SCHEMA_VERSION
    event_store_version: str = RESEARCH_EVENT_STORE_VERSION
    research_contract_version: str = RESEARCH_CONTRACT_VERSION

    global_time_utc: datetime = field(default_factory=utc_now)
    local_time: Optional[str] = None
    timezone: Optional[str] = None

    session_id: Optional[str] = None
    participant_id: Optional[str] = None

    subject_link_id: Optional[str] = None
    study_id: Optional[str] = None
    participant_role: Optional[str] = None

    stream: str = "intro"
    event_type: str = "dialogue_turn"

    model_version: Optional[str] = None
    logic_version: Optional[str] = None
    extraction_version: Optional[str] = None

    turn_index: Optional[int] = None

    raw_input: Optional[dict[str, Any]] = None
    extracted_data: Optional[dict[str, Any]] = None
    knowledge_snapshot: Optional[dict[str, Any]] = None
    status_snapshot: Optional[dict[str, Any]] = None
    output_snapshot: Optional[dict[str, Any]] = None

    source: str = "human_dialogue"
    time_reference: str = "global_utc"
    synchronization_reference: Optional[str] = None
    data_quality: str = "self_report"
    uncertainty_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["global_time_utc"] = self.global_time_utc.isoformat()
        return data

import json
import os


RESEARCH_EVENTS_PATH = "data/research_events.jsonl"


def append_research_event(
    event: ResearchEventRecord,
    path: str = RESEARCH_EVENTS_PATH,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                event.to_dict(),
                ensure_ascii=False,
            )
            + "\n"
        )
