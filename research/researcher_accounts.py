from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime, timedelta
from hashlib import scrypt, sha256
from hmac import compare_digest
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4
import json
import os
import re
import secrets
import tempfile

from research.storage_paths import application_data_directory


ACCOUNT_SCHEMA_VERSION = "researcher-account-1"
AUTHOR_IDENTITY_SCHEMA_VERSION = "research-author-identity-1"
SESSION_SCHEMA_VERSION = "researcher-session-1"
AUDIT_SCHEMA_VERSION = "researcher-account-audit-1"
SESSION_COOKIE_NAME = "health_model_researcher_session"
SUPPORTED_LANGUAGES = frozenset({"ru", "en", "es"})
RESEARCH_PROFILE_CODES = frozenset({
    "humanities_qualitative",
    "quantitative_technical",
    "mixed_methods",
    "interdisciplinary",
})
LOGIN_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 1024
RECOVERY_CODE_COUNT = 10
SESSION_TTL_HOURS = 12
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


class ResearcherAccountError(Exception):
    def __init__(self, code: str, status_code: int = 422) -> None:
        super().__init__(code)
        self.code = code
        self.status_code = status_code


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_iso(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat()


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def canonical_login(value: str) -> str:
    login = value.strip().lower()
    if not LOGIN_PATTERN.fullmatch(login):
        raise ResearcherAccountError("LOGIN_MUST_BE_3_TO_64_SAFE_CHARACTERS")
    return login


def validate_password(password: str, *, login: str | None = None) -> None:
    if not isinstance(password, str):
        raise ResearcherAccountError("PASSWORD_REQUIRED")
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ResearcherAccountError("PASSWORD_MUST_HAVE_AT_LEAST_12_CHARACTERS")
    if len(password) > PASSWORD_MAX_LENGTH:
        raise ResearcherAccountError("PASSWORD_TOO_LONG")
    if login and login.lower() in password.lower():
        raise ResearcherAccountError("PASSWORD_MUST_NOT_CONTAIN_LOGIN")
    weak = {
        "passwordpassword", "123456789012", "qwertyqwerty", "letmeinletmein",
    }
    if password.lower() in weak:
        raise ResearcherAccountError("COMMON_PASSWORD_FORBIDDEN")


def password_record(password: str) -> dict[str, Any]:
    salt = secrets.token_bytes(16)
    parameters = {
        "n": 2**15, "r": 8, "p": 1, "dklen": 32,
        "maxmem": 64 * 1024 * 1024,
    }
    digest = scrypt(password.encode("utf-8"), salt=salt, **parameters)
    return {
        "algorithm": "scrypt",
        "salt_hex": salt.hex(),
        "hash_hex": digest.hex(),
        **parameters,
    }


def verify_password(password: str, record: dict[str, Any]) -> bool:
    try:
        digest = scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(record["salt_hex"]),
            n=int(record["n"]), r=int(record["r"]), p=int(record["p"]),
            dklen=int(record["dklen"]), maxmem=int(record.get("maxmem") or 64 * 1024 * 1024),
        )
        return compare_digest(digest.hex(), str(record["hash_hex"]))
    except (KeyError, TypeError, ValueError):
        return False


def token_hash(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return deepcopy(default)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResearcherAccountError(f"ACCOUNT_STORE_CORRUPTED:{path.name}", 500) from exc


class ResearcherAccountService:
    def __init__(self, data_directory: str | Path | None = None) -> None:
        base = Path(data_directory) if data_directory is not None else application_data_directory()
        root = base / "researcher_accounts"
        self.accounts_path = root / "accounts.json"
        self.sessions_path = root / "sessions.json"
        self.authors_path = root / "author_identities.json"
        self.audit_path = root / "audit.jsonl"
        self._lock = RLock()

    def storage_status(self) -> dict[str, Any]:
        accounts = self._accounts()
        legacy_root = Path("data") / "researcher_accounts"
        return {
            "schema_version": "researcher-storage-status-1",
            "storage_mode": "persistent_user_application_data",
            "storage_directory": str(self.accounts_path.parent),
            "initialized": self.accounts_path.exists(),
            "account_record_count": len(accounts),
            "legacy_store_available": (
                legacy_root.resolve() != self.accounts_path.parent.resolve()
                and (legacy_root / "accounts.json").exists()
            ),
            "legacy_store_directory": str(legacy_root.resolve()),
            "source_replacement_safe": True,
        }

    def migrate_legacy_store(self, legacy_data_directory: str | Path = "data") -> dict[str, Any]:
        """Move an intact legacy account store only into an empty persistent store.

        This is deliberately non-destructive: legacy files remain in place, every JSON
        document is parsed before any destination write, and an initialized destination
        is never merged implicitly because account/authorship identity collisions require
        explicit review.
        """
        source = Path(legacy_data_directory) / "researcher_accounts"
        destination = self.accounts_path.parent
        if source.resolve() == destination.resolve():
            return {"status": "already_using_selected_store", "migrated": False}
        source_accounts = source / "accounts.json"
        if not source_accounts.exists():
            raise ResearcherAccountError("LEGACY_ACCOUNT_STORE_NOT_FOUND", 404)
        if self.accounts_path.exists() and self._accounts():
            raise ResearcherAccountError("PERSISTENT_ACCOUNT_STORE_NOT_EMPTY", 409)

        parsed: dict[str, Any] = {}
        defaults = {
            "accounts.json": [],
            "sessions.json": [],
            "author_identities.json": [],
        }
        for filename, default in defaults.items():
            parsed[filename] = _load_json(source / filename, default)
            if not isinstance(parsed[filename], list):
                raise ResearcherAccountError(f"LEGACY_ACCOUNT_STORE_CORRUPTED:{filename}", 500)
        if not parsed["accounts.json"]:
            raise ResearcherAccountError("LEGACY_ACCOUNT_STORE_HAS_NO_ACCOUNTS", 409)

        with self._lock:
            destination.mkdir(parents=True, exist_ok=True)
            for filename, value in parsed.items():
                _atomic_json(destination / filename, value)
            source_audit = source / "audit.jsonl"
            if source_audit.exists():
                audit_text = source_audit.read_text(encoding="utf-8")
                for line in audit_text.splitlines():
                    if line.strip():
                        json.loads(line)
                self.audit_path.write_text(audit_text, encoding="utf-8")
            self._audit(
                "legacy_account_store_migrated",
                "storage-migration",
                "completed",
                details={"source": str(source.resolve()), "account_count": len(parsed["accounts.json"])},
            )
        return {
            "status": "legacy_store_copied_to_persistent_storage",
            "migrated": True,
            "account_record_count": len(parsed["accounts.json"]),
            "legacy_files_preserved": True,
        }

    def contract(self) -> dict[str, Any]:
        return {
            "schema_version": ACCOUNT_SCHEMA_VERSION,
            "session_schema_version": SESSION_SCHEMA_VERSION,
            "authentication": "login_password_server_session",
            "password_hash": "scrypt",
            "password_min_length": PASSWORD_MIN_LENGTH,
            "session_cookie": {
                "name": SESSION_COOKIE_NAME,
                "http_only": True,
                "same_site": "strict",
                "secure_on_https": True,
                "ttl_hours": SESSION_TTL_HOURS,
            },
            "csrf": "session_bound_double_token",
            "recovery_codes": RECOVERY_CODE_COUNT,
            "failed_login_limit": MAX_FAILED_ATTEMPTS,
            "lockout_minutes": LOCKOUT_MINUTES,
            "research_profiles": sorted(RESEARCH_PROFILE_CODES),
            "account_deletion": {
                "password_reconfirmation": True,
                "exact_phrase_confirmation": True,
                "all_sessions_revoked": True,
                "draft_disposition_explicit": True,
                "trial_active_records": "pseudonymize_and_preserve_provenance",
            },
        }

    def _accounts(self) -> list[dict[str, Any]]:
        return _load_json(self.accounts_path, [])

    def _sessions(self) -> list[dict[str, Any]]:
        return _load_json(self.sessions_path, [])

    @staticmethod
    def public_account(account: dict[str, Any]) -> dict[str, Any]:
        public = {
            key: deepcopy(account.get(key))
            for key in (
                "schema_version", "account_id", "login", "display_name",
                "author_identity_id", "preferred_language", "research_profiles", "status",
                "created_at", "updated_at",
            )
        }
        public["research_profiles"] = list(public.get("research_profiles") or [])
        return public

    def register(
        self, *, login: str, display_name: str, password: str,
        preferred_language: str,
    ) -> dict[str, Any]:
        login = canonical_login(login)
        display_name = display_name.strip()
        if not display_name:
            raise ResearcherAccountError("DISPLAY_NAME_REQUIRED")
        if len(display_name) > 160:
            raise ResearcherAccountError("DISPLAY_NAME_TOO_LONG")
        if preferred_language not in SUPPORTED_LANGUAGES:
            raise ResearcherAccountError("PREFERRED_LANGUAGE_UNSUPPORTED")
        validate_password(password, login=login)
        with self._lock:
            accounts = self._accounts()
            if any(item.get("login") == login for item in accounts):
                raise ResearcherAccountError("LOGIN_ALREADY_REGISTERED", 409)
            recovery_codes = [
                "-".join((secrets.token_hex(3).upper(), secrets.token_hex(3).upper()))
                for _ in range(RECOVERY_CODE_COUNT)
            ]
            now = utc_iso()
            author_identity = {
                "schema_version": AUTHOR_IDENTITY_SCHEMA_VERSION,
                "author_identity_id": str(uuid4()),
                "display_name": display_name,
                "status": "active_authorship_record",
                "created_at": now,
                "updated_at": now,
                "account_link_status": "linked",
            }
            account = {
                "schema_version": ACCOUNT_SCHEMA_VERSION,
                "account_id": str(uuid4()),
                "login": login,
                "display_name": display_name,
                "author_identity_id": author_identity["author_identity_id"],
                "preferred_language": preferred_language,
                "research_profiles": [],
                "status": "active",
                "password": password_record(password),
                "recovery_code_hashes": [token_hash(code) for code in recovery_codes],
                "failed_login_attempts": 0,
                "locked_until": None,
                "created_at": now,
                "updated_at": now,
            }
            accounts.append(account)
            _atomic_json(self.accounts_path, accounts)
            try:
                authors = _load_json(self.authors_path, [])
                authors.append(author_identity)
                _atomic_json(self.authors_path, authors)
            except Exception:
                _atomic_json(
                    self.accounts_path,
                    [item for item in accounts if item.get("account_id") != account["account_id"]],
                )
                raise
            self._audit("account_registered", account["account_id"], "completed")
            return {"account": self.public_account(account), "recovery_codes": recovery_codes}

    def _account_by_login(self, accounts: list[dict[str, Any]], login: str) -> dict[str, Any] | None:
        return next((item for item in accounts if item.get("login") == login), None)

    def authenticate(self, *, login: str, password: str) -> dict[str, Any]:
        try:
            login = canonical_login(login)
        except ResearcherAccountError:
            raise ResearcherAccountError("INVALID_LOGIN_OR_PASSWORD", 401)
        with self._lock:
            accounts = self._accounts()
            account = self._account_by_login(accounts, login)
            if account is None:
                # Constant-cost work reduces account enumeration timing differences.
                verify_password(password, password_record("timing-defense-passphrase"))
                raise ResearcherAccountError("INVALID_LOGIN_OR_PASSWORD", 401)
            locked_until = parse_time(account.get("locked_until"))
            if locked_until and locked_until > utc_now():
                self._audit("login_blocked", account["account_id"], "locked")
                raise ResearcherAccountError("ACCOUNT_TEMPORARILY_LOCKED", 429)
            if account.get("status") != "active" or not verify_password(password, account.get("password") or {}):
                account["failed_login_attempts"] = int(account.get("failed_login_attempts") or 0) + 1
                if account["failed_login_attempts"] >= MAX_FAILED_ATTEMPTS:
                    account["locked_until"] = utc_iso(utc_now() + timedelta(minutes=LOCKOUT_MINUTES))
                    account["failed_login_attempts"] = 0
                account["updated_at"] = utc_iso()
                _atomic_json(self.accounts_path, accounts)
                self._audit("login_failed", account["account_id"], "rejected")
                raise ResearcherAccountError("INVALID_LOGIN_OR_PASSWORD", 401)
            account["failed_login_attempts"] = 0
            account["locked_until"] = None
            account["updated_at"] = utc_iso()
            _atomic_json(self.accounts_path, accounts)
            return self._create_session(account)

    def register_and_login(self, **payload: Any) -> dict[str, Any]:
        registered = self.register(**payload)
        authenticated = self.authenticate(login=payload["login"], password=payload["password"])
        return {**registered, **authenticated}

    def _create_session(self, account: dict[str, Any]) -> dict[str, Any]:
        raw_token = secrets.token_urlsafe(48)
        csrf_token = secrets.token_urlsafe(32)
        now = utc_now()
        session = {
            "schema_version": SESSION_SCHEMA_VERSION,
            "session_id": str(uuid4()),
            "account_id": account["account_id"],
            "token_hash": token_hash(raw_token),
            "csrf_hash": token_hash(csrf_token),
            "created_at": utc_iso(now),
            "last_seen_at": utc_iso(now),
            "expires_at": utc_iso(now + timedelta(hours=SESSION_TTL_HOURS)),
            "revoked_at": None,
        }
        sessions = self._sessions()
        sessions = [item for item in sessions if not self._session_expired(item)]
        sessions.append(session)
        _atomic_json(self.sessions_path, sessions)
        self._audit("login_succeeded", account["account_id"], "completed", session["session_id"])
        return {
            "account": self.public_account(account),
            "session_token": raw_token,
            "csrf_token": csrf_token,
            "session": self.public_session(session),
        }

    @staticmethod
    def public_session(session: dict[str, Any]) -> dict[str, Any]:
        return {
            key: session.get(key)
            for key in ("session_id", "created_at", "last_seen_at", "expires_at")
        }

    @staticmethod
    def _session_expired(session: dict[str, Any]) -> bool:
        expires = parse_time(session.get("expires_at"))
        return bool(session.get("revoked_at") or expires is None or expires <= utc_now())

    def require_session(self, raw_token: str | None, csrf_token: str | None = None) -> dict[str, Any]:
        if not raw_token:
            raise ResearcherAccountError("AUTHENTICATION_REQUIRED", 401)
        digest = token_hash(raw_token)
        with self._lock:
            sessions = self._sessions()
            session = next((item for item in sessions if compare_digest(str(item.get("token_hash") or ""), digest)), None)
            if session is None or self._session_expired(session):
                raise ResearcherAccountError("SESSION_INVALID_OR_EXPIRED", 401)
            if csrf_token is not None and not compare_digest(
                str(session.get("csrf_hash") or ""), token_hash(csrf_token)
            ):
                raise ResearcherAccountError("CSRF_TOKEN_INVALID", 403)
            accounts = self._accounts()
            account = next((item for item in accounts if item.get("account_id") == session.get("account_id")), None)
            if account is None or account.get("status") != "active":
                raise ResearcherAccountError("ACCOUNT_NOT_ACTIVE", 401)
            session["last_seen_at"] = utc_iso()
            _atomic_json(self.sessions_path, sessions)
            return {"account": self.public_account(account), "session": self.public_session(session)}

    def rotate_csrf(self, raw_token: str | None) -> dict[str, Any]:
        resolved = self.require_session(raw_token)
        digest = token_hash(str(raw_token))
        csrf_token = secrets.token_urlsafe(32)
        with self._lock:
            sessions = self._sessions()
            session = next(item for item in sessions if compare_digest(str(item.get("token_hash") or ""), digest))
            session["csrf_hash"] = token_hash(csrf_token)
            session["last_seen_at"] = utc_iso()
            _atomic_json(self.sessions_path, sessions)
        return {**resolved, "csrf_token": csrf_token}

    def list_sessions(self, account_id: str) -> list[dict[str, Any]]:
        return [
            self.public_session(item)
            for item in self._sessions()
            if item.get("account_id") == account_id and not self._session_expired(item)
        ]

    def logout(self, raw_token: str, csrf_token: str) -> None:
        resolved = self.require_session(raw_token, csrf_token)
        digest = token_hash(raw_token)
        with self._lock:
            sessions = self._sessions()
            for item in sessions:
                if compare_digest(str(item.get("token_hash") or ""), digest):
                    item["revoked_at"] = utc_iso()
            _atomic_json(self.sessions_path, sessions)
            self._audit("logout", resolved["account"]["account_id"], "completed")

    def revoke_other_sessions(self, raw_token: str, csrf_token: str) -> int:
        resolved = self.require_session(raw_token, csrf_token)
        current_hash = token_hash(raw_token)
        account_id = resolved["account"]["account_id"]
        count = 0
        with self._lock:
            sessions = self._sessions()
            for item in sessions:
                if (
                    item.get("account_id") == account_id
                    and not compare_digest(str(item.get("token_hash") or ""), current_hash)
                    and not self._session_expired(item)
                ):
                    item["revoked_at"] = utc_iso()
                    count += 1
            _atomic_json(self.sessions_path, sessions)
            self._audit("other_sessions_revoked", account_id, "completed", details={"count": count})
        return count

    def update_preferences(
        self,
        *,
        account_id: str,
        research_profiles: list[str],
        preferred_language: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(research_profiles, list):
            raise ResearcherAccountError("RESEARCH_PROFILES_MUST_BE_LIST")
        normalized = []
        for value in research_profiles:
            code = str(value).strip().lower()
            if code not in RESEARCH_PROFILE_CODES:
                raise ResearcherAccountError("RESEARCH_PROFILE_UNSUPPORTED")
            if code not in normalized:
                normalized.append(code)
        if preferred_language is not None and preferred_language not in SUPPORTED_LANGUAGES:
            raise ResearcherAccountError("PREFERRED_LANGUAGE_UNSUPPORTED")
        with self._lock:
            accounts = self._accounts()
            account = next((item for item in accounts if item.get("account_id") == account_id), None)
            if account is None:
                raise ResearcherAccountError("ACCOUNT_NOT_FOUND", 404)
            account["research_profiles"] = normalized
            if preferred_language is not None:
                account["preferred_language"] = preferred_language
            account["updated_at"] = utc_iso()
            _atomic_json(self.accounts_path, accounts)
            self._audit(
                "researcher_preferences_updated",
                account_id,
                "completed",
                details={"research_profiles": normalized},
            )
            return self.public_account(account)

    def recover(self, *, login: str, recovery_code: str, new_password: str) -> dict[str, Any]:
        login = canonical_login(login)
        validate_password(new_password, login=login)
        code_digest = token_hash(recovery_code.strip().upper())
        with self._lock:
            accounts = self._accounts()
            account = self._account_by_login(accounts, login)
            if account is None:
                raise ResearcherAccountError("RECOVERY_FAILED", 401)
            hashes = list(account.get("recovery_code_hashes") or [])
            match_index = next((index for index, item in enumerate(hashes) if compare_digest(str(item), code_digest)), None)
            if match_index is None:
                self._audit("recovery_failed", account["account_id"], "rejected")
                raise ResearcherAccountError("RECOVERY_FAILED", 401)
            hashes.pop(match_index)
            account["recovery_code_hashes"] = hashes
            account["password"] = password_record(new_password)
            account["failed_login_attempts"] = 0
            account["locked_until"] = None
            account["updated_at"] = utc_iso()
            _atomic_json(self.accounts_path, accounts)
            self._revoke_all(account["account_id"])
            self._audit("password_recovered", account["account_id"], "completed")
            return {"account": self.public_account(account), "remaining_recovery_codes": len(hashes)}

    def verify_deletion(self, *, account_id: str, password: str, confirmation: str) -> dict[str, Any]:
        accounts = self._accounts()
        account = next((item for item in accounts if item.get("account_id") == account_id), None)
        if account is None:
            raise ResearcherAccountError("ACCOUNT_NOT_FOUND", 404)
        required = f"DELETE {account['login']}"
        if confirmation != required:
            raise ResearcherAccountError("ACCOUNT_DELETION_CONFIRMATION_INVALID")
        if not verify_password(password, account.get("password") or {}):
            raise ResearcherAccountError("PASSWORD_RECONFIRMATION_FAILED", 401)
        return self.public_account(account)

    def authorship_snapshot(self, account_id: str) -> dict[str, Any]:
        account = next(
            (item for item in self._accounts() if item.get("account_id") == account_id),
            None,
        )
        if account is None:
            raise ResearcherAccountError("ACCOUNT_NOT_FOUND", 404)
        author_id = account.get("author_identity_id")
        author = next(
            (item for item in _load_json(self.authors_path, []) if item.get("author_identity_id") == author_id),
            None,
        )
        if author is None:
            raise ResearcherAccountError("AUTHOR_IDENTITY_NOT_FOUND", 500)
        return {
            "schema_version": AUTHOR_IDENTITY_SCHEMA_VERSION,
            "author_identity_id": author["author_identity_id"],
            "display_name": author["display_name"],
            "account_link_status": author.get("account_link_status", "linked"),
        }

    def delete_verified_account(self, account_id: str) -> None:
        with self._lock:
            accounts = self._accounts()
            account = next((item for item in accounts if item.get("account_id") == account_id), None)
            if account is None:
                raise ResearcherAccountError("ACCOUNT_NOT_FOUND", 404)
            authors = _load_json(self.authors_path, [])
            for author in authors:
                if author.get("author_identity_id") == account.get("author_identity_id"):
                    author["account_link_status"] = "account_deleted_authorship_preserved"
                    author["updated_at"] = utc_iso()
            _atomic_json(self.authors_path, authors)
            _atomic_json(
                self.accounts_path,
                [item for item in accounts if item.get("account_id") != account_id],
            )
            self._revoke_all(account_id)
            self._audit("account_deleted", account_id, "completed")

    def _revoke_all(self, account_id: str) -> None:
        sessions = self._sessions()
        now = utc_iso()
        for item in sessions:
            if item.get("account_id") == account_id and not item.get("revoked_at"):
                item["revoked_at"] = now
        _atomic_json(self.sessions_path, sessions)

    def _audit(
        self, event_type: str, account_id: str, status: str,
        session_id: str | None = None, details: dict[str, Any] | None = None,
    ) -> None:
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "schema_version": AUDIT_SCHEMA_VERSION,
            "event_id": str(uuid4()),
            "event_type": event_type,
            "account_id": account_id,
            "session_id": session_id,
            "status": status,
            "occurred_at": utc_iso(),
            "details": details or {},
        }
        with self._lock:
            with self.audit_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
