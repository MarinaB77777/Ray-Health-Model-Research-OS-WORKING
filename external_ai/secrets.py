from __future__ import annotations

from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4
import json
import os
import tempfile

from cryptography.fernet import Fernet, InvalidToken

from .contracts import ExternalAIError


class EncryptedSecretVault:
    """Encrypted credential storage kept outside ordinary Ray settings and audits."""

    MASTER_KEY_ENV = "RAY_EXTERNAL_AI_MASTER_KEY"

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.path = self.root / "credentials.enc.json"
        self.key_path = self.root / "credential-master.key"
        self._lock = RLock()
        self._fernet = Fernet(self._load_or_create_master_key())

    @property
    def storage_mode(self) -> str:
        return "environment_master_key" if os.environ.get(self.MASTER_KEY_ENV) else "local_persistent_master_key"

    def put(self, secret: str) -> str:
        value = secret.strip()
        if not value:
            raise ExternalAIError("EXTERNAL_AI_CREDENTIAL_REQUIRED")
        if len(value) > 8192:
            raise ExternalAIError("EXTERNAL_AI_CREDENTIAL_TOO_LONG")
        credential_ref = str(uuid4())
        token = self._fernet.encrypt(value.encode("utf-8")).decode("ascii")
        with self._lock:
            state = self._load()
            state[credential_ref] = token
            self._write(state)
        return credential_ref

    def get(self, credential_ref: str) -> str:
        with self._lock:
            token = self._load().get(credential_ref)
        if not token:
            raise ExternalAIError("EXTERNAL_AI_CREDENTIAL_NOT_FOUND", status_code=500)
        try:
            return self._fernet.decrypt(token.encode("ascii")).decode("utf-8")
        except (InvalidToken, UnicodeError) as exc:
            raise ExternalAIError("EXTERNAL_AI_CREDENTIAL_DECRYPTION_FAILED", status_code=500) from exc

    def delete(self, credential_ref: str) -> None:
        with self._lock:
            state = self._load()
            state.pop(credential_ref, None)
            self._write(state)

    def _load_or_create_master_key(self) -> bytes:
        configured = os.environ.get(self.MASTER_KEY_ENV)
        if configured:
            try:
                Fernet(configured.encode("ascii"))
            except (ValueError, TypeError) as exc:
                raise ExternalAIError("EXTERNAL_AI_MASTER_KEY_INVALID", status_code=500) from exc
            return configured.encode("ascii")
        self.root.mkdir(parents=True, exist_ok=True)
        if self.key_path.exists():
            key = self.key_path.read_bytes().strip()
            try:
                Fernet(key)
            except (ValueError, TypeError) as exc:
                raise ExternalAIError("EXTERNAL_AI_MASTER_KEY_FILE_INVALID", status_code=500) from exc
            return key
        key = Fernet.generate_key()
        fd = os.open(self.key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(key)
            handle.flush()
            os.fsync(handle.fileno())
        return key

    def _load(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        try:
            data: Any = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExternalAIError("EXTERNAL_AI_CREDENTIAL_STORE_CORRUPTED", status_code=500) from exc
        if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
            raise ExternalAIError("EXTERNAL_AI_CREDENTIAL_STORE_CORRUPTED", status_code=500)
        return data

    def _write(self, state: dict[str, str]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=self.path.name, dir=self.root, text=True)
        try:
            os.chmod(temp_name, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
            os.chmod(self.path, 0o600)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
