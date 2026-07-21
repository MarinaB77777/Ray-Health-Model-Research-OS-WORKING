from typing import Optional

from pilot_account.schemas import PilotAccount


class PilotAccountStore:
    def __init__(self):
        self._accounts: dict[str, PilotAccount] = {}

    def save(self, account: PilotAccount) -> None:
        self._accounts[account.account_id] = account

    def get(self, account_id: str) -> Optional[PilotAccount]:
        return self._accounts.get(account_id)

    def exists(self, account_id: str) -> bool:
        return account_id in self._accounts

    def list_all(self) -> list[PilotAccount]:
        return list(self._accounts.values())