from __future__ import annotations

import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from research.lab_store import (
    account_deletion_impact,
    apply_account_deletion_disposition,
    create_research_object,
    list_research_objects,
)
from research.researcher_accounts import (
    ResearcherAccountError,
    ResearcherAccountService,
)


@contextmanager
def working_directory(path: str):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


class ResearcherAccountTests(unittest.TestCase):
    def register(self, service: ResearcherAccountService):
        return service.register_and_login(
            login="marina.research",
            display_name="Marina Researcher",
            password="a long unique research passphrase",
            preferred_language="ru",
        )

    def test_registration_creates_server_session_and_separate_author_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = ResearcherAccountService(tmp)
            result = self.register(service)
            self.assertEqual(len(result["recovery_codes"]), 10)
            self.assertNotEqual(
                result["account"]["account_id"],
                result["account"]["author_identity_id"],
            )
            context = service.require_session(
                result["session_token"], result["csrf_token"]
            )
            self.assertEqual(context["account"]["login"], "marina.research")
            raw_store = Path(tmp, "researcher_accounts", "accounts.json").read_text()
            self.assertNotIn("a long unique research passphrase", raw_store)
            self.assertNotIn(result["session_token"], Path(tmp, "researcher_accounts", "sessions.json").read_text())

    def test_wrong_csrf_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = ResearcherAccountService(tmp)
            result = self.register(service)
            with self.assertRaisesRegex(ResearcherAccountError, "CSRF_TOKEN_INVALID"):
                service.require_session(result["session_token"], "wrong-token")

    def test_research_profiles_are_multiple_and_do_not_change_authorship(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = ResearcherAccountService(tmp)
            result = self.register(service)
            account = service.update_preferences(
                account_id=result["account"]["account_id"],
                research_profiles=["humanities_qualitative", "quantitative_technical"],
                preferred_language="ru",
            )
            self.assertEqual(
                account["research_profiles"],
                ["humanities_qualitative", "quantitative_technical"],
            )
            self.assertEqual(
                account["author_identity_id"], result["account"]["author_identity_id"]
            )
            with self.assertRaisesRegex(ResearcherAccountError, "PROFILE_UNSUPPORTED"):
                service.update_preferences(
                    account_id=account["account_id"],
                    research_profiles=["unscientific_profile"],
                )

    def test_recovery_code_is_one_time_and_revokes_sessions(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = ResearcherAccountService(tmp)
            result = self.register(service)
            code = result["recovery_codes"][0]
            recovered = service.recover(
                login="marina.research",
                recovery_code=code,
                new_password="another long unique research passphrase",
            )
            self.assertEqual(recovered["remaining_recovery_codes"], 9)
            with self.assertRaisesRegex(ResearcherAccountError, "SESSION_INVALID_OR_EXPIRED"):
                service.require_session(result["session_token"])
            with self.assertRaisesRegex(ResearcherAccountError, "RECOVERY_FAILED"):
                service.recover(
                    login="marina.research",
                    recovery_code=code,
                    new_password="third long unique research passphrase",
                )

    def test_account_deletion_preserves_authorship_of_retained_objects(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            service = ResearcherAccountService("data")
            result = self.register(service)
            account = result["account"]
            author = service.authorship_snapshot(account["account_id"])
            draft = create_research_object(
                "project", account["account_id"], "Draft project", status="draft",
                authorship={"contributions": [{
                    "author_identity_id": author["author_identity_id"],
                    "display_name": author["display_name"],
                    "roles": ["creator"],
                }]},
            )
            active = create_research_object(
                "result", account["account_id"], "Active result", status="active",
                authorship={"contributions": [{
                    "author_identity_id": author["author_identity_id"],
                    "display_name": author["display_name"],
                    "roles": ["scientific_author"],
                }]},
            )
            impact = account_deletion_impact(account["account_id"])
            self.assertEqual(impact["by_status"], {"draft": 1, "trial": 0, "active": 1})
            disposition = apply_account_deletion_disposition(
                account["account_id"],
                delete_owned_drafts=True,
                authorship_snapshot=author,
            )
            self.assertIn(draft["id"], disposition["deleted_draft_object_ids"])
            service.verify_deletion(
                account_id=account["account_id"],
                password="a long unique research passphrase",
                confirmation="DELETE marina.research",
            )
            service.delete_verified_account(account["account_id"])
            remaining = list_research_objects()
            retained = next(item for item in remaining if item["id"] == active["id"])
            contribution = retained["authorship"]["contributions"][0]
            self.assertEqual(contribution["display_name"], "Marina Researcher")
            self.assertEqual(contribution["author_identity_id"], author["author_identity_id"])
            author_store = json.loads(
                Path("data/researcher_accounts/author_identities.json").read_text()
            )
            self.assertEqual(
                author_store[0]["account_link_status"],
                "account_deleted_authorship_preserved",
            )

    def test_account_deletion_requires_password_and_exact_phrase(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = ResearcherAccountService(tmp)
            account = self.register(service)["account"]
            with self.assertRaisesRegex(ResearcherAccountError, "CONFIRMATION_INVALID"):
                service.verify_deletion(
                    account_id=account["account_id"],
                    password="a long unique research passphrase",
                    confirmation="DELETE",
                )
            with self.assertRaisesRegex(ResearcherAccountError, "PASSWORD_RECONFIRMATION_FAILED"):
                service.verify_deletion(
                    account_id=account["account_id"],
                    password="wrong password but long enough",
                    confirmation="DELETE marina.research",
                )

    def test_legacy_account_store_migration_is_non_destructive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy_service = ResearcherAccountService(root / "legacy")
            registered = self.register(legacy_service)
            persistent_service = ResearcherAccountService(root / "persistent")
            result = persistent_service.migrate_legacy_store(root / "legacy")
            self.assertTrue(result["migrated"])
            self.assertTrue(legacy_service.accounts_path.exists())
            authenticated = persistent_service.authenticate(
                login=registered["account"]["login"],
                password="a long unique research passphrase",
            )
            self.assertEqual(
                authenticated["account"]["author_identity_id"],
                registered["account"]["author_identity_id"],
            )


if __name__ == "__main__":
    unittest.main()
