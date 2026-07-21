from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class PilotAccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


@dataclass
class PilotAccount:
    account_id: str
    participant_id: str
    subject_link_id: str

    preferred_language: str = "ru"
    status: PilotAccountStatus = PilotAccountStatus.ACTIVE

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )