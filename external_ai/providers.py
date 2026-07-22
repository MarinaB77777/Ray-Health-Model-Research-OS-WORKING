from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable
import json
import urllib.error
import urllib.parse
import urllib.request

from .contracts import ExternalAIError, ProviderAnswer


JsonTransport = Callable[[str, str, dict[str, str], dict[str, Any] | None, float], dict[str, Any]]


def urlopen_json_transport(
    method: str,
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any] | None,
    timeout: float,
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url=url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(2_000_000)
    except urllib.error.HTTPError as exc:
        code = "EXTERNAL_AI_PROVIDER_AUTHENTICATION_FAILED" if exc.code in {401, 403} else "EXTERNAL_AI_PROVIDER_HTTP_ERROR"
        raise ExternalAIError(code, status_code=502) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ExternalAIError("EXTERNAL_AI_PROVIDER_UNREACHABLE", status_code=502) from exc
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ExternalAIError("EXTERNAL_AI_PROVIDER_INVALID_JSON", status_code=502) from exc
    if not isinstance(result, dict):
        raise ExternalAIError("EXTERNAL_AI_PROVIDER_INVALID_RESPONSE", status_code=502)
    return result


class ExternalAIProvider(ABC):
    provider_id: str

    @abstractmethod
    def contract(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def list_models(self, credential: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def test_connection(self, credential: str, model: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate(self, credential: str, model: str, prompt: str, language: str) -> ProviderAnswer:
        raise NotImplementedError


class GeminiProvider(ExternalAIProvider):
    provider_id = "google_gemini"
    base_url = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, transport: JsonTransport = urlopen_json_transport) -> None:
        self.transport = transport

    def contract(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "labels": {"en": "Google Gemini", "es": "Google Gemini", "ru": "Google Gemini"},
            "credential_type": "gemini_api_or_authorization_key",
            "credential_help_url": "https://aistudio.google.com/apikey",
            "models_discovered_from_provider": True,
            "arbitrary_endpoint_allowed": False,
            "fixed_hosts": ["generativelanguage.googleapis.com"],
        }

    def _headers(self, credential: str) -> dict[str, str]:
        return {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "x-goog-api-key": credential,
        }

    def list_models(self, credential: str) -> list[dict[str, Any]]:
        result = self.transport("GET", f"{self.base_url}/models?pageSize=1000", self._headers(credential), None, 15.0)
        models = []
        for item in result.get("models") or []:
            if not isinstance(item, dict) or "generateContent" not in (item.get("supportedGenerationMethods") or []):
                continue
            name = str(item.get("name") or "")
            if not name.startswith("models/"):
                continue
            models.append({
                "model": name.removeprefix("models/"),
                "display_name": str(item.get("displayName") or name.removeprefix("models/")),
                "input_token_limit": item.get("inputTokenLimit"),
                "output_token_limit": item.get("outputTokenLimit"),
            })
        if not models:
            raise ExternalAIError("EXTERNAL_AI_PROVIDER_HAS_NO_GENERATION_MODELS", status_code=502)
        return sorted(models, key=lambda item: item["model"])

    def test_connection(self, credential: str, model: str) -> dict[str, Any]:
        safe_model = self._safe_model(model)
        result = self.transport("GET", f"{self.base_url}/models/{urllib.parse.quote(safe_model, safe='-._')}", self._headers(credential), None, 15.0)
        supported = result.get("supportedGenerationMethods") or []
        if "generateContent" not in supported:
            raise ExternalAIError("EXTERNAL_AI_MODEL_DOES_NOT_SUPPORT_GENERATION")
        return {"provider_id": self.provider_id, "model": safe_model, "status": "verified"}

    def generate(self, credential: str, model: str, prompt: str, language: str) -> ProviderAnswer:
        safe_model = self._safe_model(model)
        payload = {
            "systemInstruction": {
                "parts": [{"text": "Answer clearly in the requested language. State uncertainty and limitations. Never claim to be Ray, never request credentials, and do not propose autonomous actions."}]
            },
            "contents": [{"role": "user", "parts": [{"text": f"Language: {language}\n\n{prompt}"}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048},
            "safetySettings": [
                {"category": category, "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
                for category in (
                    "HARM_CATEGORY_HARASSMENT",
                    "HARM_CATEGORY_HATE_SPEECH",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "HARM_CATEGORY_DANGEROUS_CONTENT",
                )
            ],
        }
        result = self.transport(
            "POST",
            f"{self.base_url}/models/{urllib.parse.quote(safe_model, safe='-._')}:generateContent",
            self._headers(credential),
            payload,
            35.0,
        )
        prompt_feedback = result.get("promptFeedback") or {}
        if prompt_feedback.get("blockReason"):
            raise ExternalAIError("EXTERNAL_AI_PROMPT_BLOCKED_BY_PROVIDER")
        candidates = result.get("candidates") or []
        if not candidates:
            raise ExternalAIError("EXTERNAL_AI_PROVIDER_RETURNED_NO_CANDIDATE", status_code=502)
        candidate = candidates[0] if isinstance(candidates[0], dict) else {}
        finish_reason = str(candidate.get("finishReason") or "UNSPECIFIED")
        if finish_reason in {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST"}:
            raise ExternalAIError("EXTERNAL_AI_RESPONSE_BLOCKED_BY_PROVIDER")
        parts = ((candidate.get("content") or {}).get("parts") or [])
        text = "\n".join(str(part.get("text") or "") for part in parts if isinstance(part, dict) and part.get("text")).strip()
        if not text:
            raise ExternalAIError("EXTERNAL_AI_PROVIDER_RETURNED_EMPTY_TEXT", status_code=502)
        safety = tuple(item for item in (candidate.get("safetyRatings") or []) if isinstance(item, dict))
        return ProviderAnswer(text=text, finish_reason=finish_reason, safety_ratings=safety)

    @staticmethod
    def _safe_model(model: str) -> str:
        value = model.strip().removeprefix("models/")
        if not value or len(value) > 160 or not all(char.isalnum() or char in "-._" for char in value):
            raise ExternalAIError("EXTERNAL_AI_MODEL_ID_INVALID")
        return value


class ProviderRegistry:
    def __init__(self, providers: list[ExternalAIProvider] | None = None) -> None:
        items = providers or [GeminiProvider()]
        self._providers = {provider.provider_id: provider for provider in items}
        if len(self._providers) != len(items):
            raise ValueError("EXTERNAL_AI_PROVIDER_IDS_MUST_BE_UNIQUE")

    def get(self, provider_id: str) -> ExternalAIProvider:
        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise ExternalAIError("EXTERNAL_AI_PROVIDER_NOT_REGISTERED", status_code=404) from exc

    def contract(self) -> list[dict[str, Any]]:
        return [self._providers[key].contract() for key in sorted(self._providers)]
