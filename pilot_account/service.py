from datetime import UTC, datetime
from uuid import uuid4

from pilot_account.schemas import PilotAccount
from pilot_account.store import PilotAccountStore


class PilotAccountService:
    def __init__(self, store: PilotAccountStore):
        self.store = store

    def create_account(
        self,
        preferred_language: str = "ru",
    ) -> PilotAccount:
        account = PilotAccount(
            account_id=str(uuid4()),
            participant_id=f"participant_{uuid4()}",
            subject_link_id=f"subject_{uuid4()}",
            preferred_language=preferred_language,
        )

        self.store.save(account)
        return account

    def get_account(self, account_id: str) -> PilotAccount | None:
        return self.store.get(account_id)

    def update_preferred_language(
        self,
        account_id: str,
        preferred_language: str,
    ) -> PilotAccount | None:
        account = self.store.get(account_id)

        if account is None:
            return None

        account.preferred_language = preferred_language
        account.updated_at = datetime.now(UTC)

        self.store.save(account)
        return account