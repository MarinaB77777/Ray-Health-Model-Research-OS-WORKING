from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from .contracts import ExternalAIPolicy, FilterResult


@dataclass(frozen=True)
class FilterProfile:
    profile_id: str
    labels: dict[str, str]
    descriptions: dict[str, str]
    additional_block_categories: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "labels": dict(self.labels),
            "descriptions": dict(self.descriptions),
            "additional_block_categories": list(self.additional_block_categories),
        }


FILTER_PROFILES = {
    "strict_general": FilterProfile(
        profile_id="strict_general",
        labels={"en": "General questions only", "es": "Solo preguntas generales", "ru": "Только общие вопросы"},
        descriptions={
            "en": "Sends only the current question and blocks personal, health, project, and research context.",
            "es": "Envía solo la pregunta actual y bloquea contexto personal, de salud, proyecto e investigación.",
            "ru": "Отправляет только текущий вопрос и блокирует личный, медицинский, проектный и исследовательский контекст.",
        },
        additional_block_categories=("personal_sensitive", "health_context", "project_context", "research_context"),
    ),
    "personal_without_identity": FilterProfile(
        profile_id="personal_without_identity",
        labels={"en": "Personal context without identity", "es": "Contexto personal sin identidad", "ru": "Личный контекст без идентификации"},
        descriptions={
            "en": "Allows self-described context but blocks identifiers, secrets, Ray internals, participant data, and research records.",
            "es": "Permite contexto personal descrito por el usuario, pero bloquea identificadores, secretos, interior de Ray y datos de investigación.",
            "ru": "Разрешает описанный человеком личный контекст, но блокирует идентификаторы, секреты, внутренности Рэя и исследовательские данные.",
        },
        additional_block_categories=("project_context", "research_context"),
    ),
    "sanitized_research": FilterProfile(
        profile_id="sanitized_research",
        labels={"en": "Sanitized research assistance", "es": "Ayuda científica saneada", "ru": "Очищенная исследовательская помощь"},
        descriptions={
            "en": "Allows non-identifying research questions, while raw participant, sensor, unpublished record, and internal Ray data remain blocked.",
            "es": "Permite preguntas científicas no identificables; datos brutos, sensores, registros no publicados e interior de Ray siguen bloqueados.",
            "ru": "Разрешает обезличенные исследовательские вопросы; сырые данные, сенсоры, неопубликованные записи и внутренности Рэя блокируются.",
        },
        additional_block_categories=("health_context",),
    ),
    "broad_sanitized": FilterProfile(
        profile_id="broad_sanitized",
        labels={"en": "Broad sanitized questions", "es": "Preguntas amplias saneadas", "ru": "Широкий очищенный профиль"},
        descriptions={
            "en": "Allows broader user-written questions but never attaches hidden Ray context and still applies every mandatory block.",
            "es": "Permite preguntas más amplias, nunca adjunta contexto oculto de Ray y mantiene todos los bloqueos obligatorios.",
            "ru": "Разрешает более широкий текст пользователя, никогда не прикладывает скрытый контекст Рэя и сохраняет все обязательные запреты.",
        },
        additional_block_categories=(),
    ),
}


MANDATORY_CATEGORIES = (
    "credentials_and_secrets",
    "direct_identifiers",
    "ray_internal_state",
    "participant_raw_data",
    "raw_sensor_or_biometric_data",
    "hidden_diagnostics",
    "unrestricted_memory",
)

OPTIONAL_CATEGORIES = (
    "personal_sensitive",
    "health_context",
    "project_context",
    "research_context",
)


PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "credentials_and_secrets": (
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
        re.compile(r"\b(?:AIza[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z_-]{16,})\b"),
        re.compile(r"\b(?:api[_ -]?key|access[_ -]?token|refresh[_ -]?token|password|парол[ья]|contrase(?:ña|na))\s*[:=]\s*\S+", re.I),
        re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{12,}", re.I),
    ),
    "direct_identifiers": (
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
        re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I),
        re.compile(r"(?<!\d)(?:\+?\d[\s().-]?){9,15}(?!\d)"),
        re.compile(r"\b(?:participant|subject|account|session)[_-]?id\s*[:=]\s*\S+", re.I),
        re.compile(r"\b(?:участник|испытуем(?:ый|ая)|cuenta|participante)[ _-]?(?:id|идентификатор)\s*[:=]\s*\S+", re.I),
        re.compile(r"\b(?:my (?:full )?name is|full name\s*[:=]|меня зовут|полное имя\s*[:=]|me llamo|nombre completo\s*[:=])\s+\S+", re.I),
        re.compile(r"\b(?:home address|postal address|домашний адрес|почтовый адрес|domicilio|direcci[oó]n postal)\s*[:=]\s*\S+", re.I),
    ),
    "ray_internal_state": (
        re.compile(r"\b(?:inner core|external core raw|system prompt|chain of thought|internal reasoning|governance verdict|projection layer raw)\b", re.I),
        re.compile(r"\b(?:внутренн(?:ее|ий) ядро|системн(?:ый|ого) промпт|внутренн(?:ие|его) рассуждени)\b", re.I),
        re.compile(r"\b(?:núcleo interno|razonamiento interno|prompt del sistema)\b", re.I),
    ),
    "participant_raw_data": (
        re.compile(r"\b(?:raw answers?|raw participant data|participant record|subject link|questionnaire submissions?)\b", re.I),
        re.compile(r"\b(?:сырые ответы|данные участник|ответы респондент|datos brutos del participante)\b", re.I),
    ),
    "raw_sensor_or_biometric_data": (
        re.compile(r"\b(?:raw sensor|sensor stream|raw eeg|raw ecg|raw heart rate|biometric stream)\b", re.I),
        re.compile(r"\b(?:сыр(?:ой|ые) сенсор|поток сенсор|señal biométrica bruta|flujo de sensor)\b", re.I),
    ),
    "hidden_diagnostics": (
        re.compile(r"\b(?:hidden diagnostic|latent diagnostic marker|private psychophysical state|raw psychophysical state)\b", re.I),
        re.compile(r"\b(?:скрыт(?:ый|ые) диагност|сырое психофиз|marcador diagnóstico oculto)\b", re.I),
    ),
    "unrestricted_memory": (
        re.compile(r"\b(?:unrestricted (?:temporary )?memory|full memory dump|entire conversation history)\b", re.I),
        re.compile(r"\b(?:вся временная память|полный дамп памяти|memoria temporal completa)\b", re.I),
    ),
    "personal_sensitive": (
        re.compile(r"\b(?:my address|my passport|my social security|мой адрес|мой паспорт|mi domicilio|mi pasaporte)\b", re.I),
    ),
    "health_context": (
        re.compile(r"\b(?:diagnos(?:is|ed)|medication|symptoms?|medical record|диагноз|лекарств|симптом|historial médico|medicamento)\b", re.I),
    ),
    "project_context": (
        re.compile(r"\b(?:confidential project|private repository|internal project|неопубликованн(?:ый|ая) проект|proyecto confidencial)\b", re.I),
    ),
    "research_context": (
        re.compile(r"\b(?:unpublished dataset|raw research data|participant dataset|неопубликованн(?:ый|ые) набор|сырые исследовательские данные|datos de investigación sin publicar)\b", re.I),
    ),
}


INBOUND_BLOCK_PATTERNS = (
    re.compile(r"<\s*(?:script|iframe|object|embed)\b", re.I),
    re.compile(r"<\s*/?\s*[a-z][^>]*>", re.I),
    re.compile(r"!\[[^\]]*\]\s*\([^)]*\)", re.I),
    re.compile(r"\b(?:javascript|data)\s*:", re.I),
    re.compile(r"\bignore (?:all |the )?(?:previous|prior|system) instructions\b", re.I),
    re.compile(r"\b(?:reveal|print|return) (?:the )?(?:system prompt|developer message|hidden instructions)\b", re.I),
    re.compile(r"\b(?:открой|покажи|выведи) (?:системн(?:ый|ые) промпт|скрыт(?:ые|ую) инструкц)\b", re.I),
    re.compile(r"\b(?:muestra|revela) (?:el )?(?:prompt del sistema|instrucciones ocultas)\b", re.I),
)


def profile_catalog() -> list[dict[str, Any]]:
    return [profile.to_dict() for profile in FILTER_PROFILES.values()]


def _normalized_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text).replace("\x00", "").strip()


def validate_policy(policy: ExternalAIPolicy) -> None:
    if policy.profile_id not in FILTER_PROFILES:
        raise ValueError("UNKNOWN_EXTERNAL_AI_FILTER_PROFILE")
    categories = set(policy.never_send_categories)
    unknown = categories.difference(OPTIONAL_CATEGORIES)
    if unknown:
        raise ValueError("UNKNOWN_EXTERNAL_AI_BLOCK_CATEGORY:" + ",".join(sorted(unknown)))
    if len(policy.never_send_terms) > 100:
        raise ValueError("EXTERNAL_AI_NEVER_SEND_TERM_LIMIT_EXCEEDED")
    normalized = []
    for term in policy.never_send_terms:
        clean = _normalized_text(str(term))
        if len(clean) < 2 or len(clean) > 120:
            raise ValueError("EXTERNAL_AI_NEVER_SEND_TERM_LENGTH_INVALID")
        normalized.append(clean.casefold())
    if len(normalized) != len(set(normalized)):
        raise ValueError("EXTERNAL_AI_NEVER_SEND_TERMS_MUST_BE_UNIQUE")


def filter_outbound_text(text: str, policies: tuple[ExternalAIPolicy, ...]) -> FilterResult:
    clean = _normalized_text(text)
    if not clean:
        return FilterResult(False, None, ("OUTBOUND_MESSAGE_EMPTY",))
    if len(clean) > 12000:
        return FilterResult(False, None, ("OUTBOUND_MESSAGE_TOO_LONG",))
    matched_categories: set[str] = set()
    matched_terms: set[str] = set()
    categories = set(MANDATORY_CATEGORIES)
    for policy in policies:
        validate_policy(policy)
        if not policy.enabled:
            return FilterResult(False, None, ("EXTERNAL_AI_DISABLED_BY_POLICY",))
        categories.update(policy.never_send_categories)
        categories.update(FILTER_PROFILES[policy.profile_id].additional_block_categories)
        folded = clean.casefold()
        for term in policy.never_send_terms:
            normalized = _normalized_text(term)
            if normalized.casefold() in folded:
                matched_terms.add(normalized)
    for category in categories:
        if any(pattern.search(clean) for pattern in PATTERNS.get(category, ())):
            matched_categories.add(category)
    reasons = []
    if matched_categories:
        reasons.append("OUTBOUND_FORBIDDEN_CATEGORY_MATCH")
    if matched_terms:
        reasons.append("OUTBOUND_USER_NEVER_SEND_TERM_MATCH")
    if reasons:
        return FilterResult(
            False,
            None,
            tuple(reasons),
            tuple(sorted(matched_categories)),
        )
    return FilterResult(True, clean)


def filter_inbound_text(text: str) -> FilterResult:
    clean = _normalized_text(text)
    if not clean:
        return FilterResult(False, None, ("INBOUND_RESPONSE_EMPTY",))
    if len(clean) > 30000:
        return FilterResult(False, None, ("INBOUND_RESPONSE_TOO_LONG",))
    if any(ord(char) < 32 and char not in "\n\r\t" for char in clean):
        return FilterResult(False, None, ("INBOUND_CONTROL_CHARACTERS",))
    if any(pattern.search(clean) for pattern in INBOUND_BLOCK_PATTERNS):
        return FilterResult(False, None, ("INBOUND_INSTRUCTION_INJECTION_BLOCKED",))
    return FilterResult(True, clean)
