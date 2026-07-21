# runtime/acquisition/result_filter.py

from __future__ import annotations

import re

from runtime.acquisition.contracts import (
    AcquisitionReasonCode,
    AcquisitionResult,
    AcquisitionSourceClass,
    InboundFilterDecision,
    InboundFilterResult,
)


class ResultFilter:
    """
    Inbound Result Filter.

    This module protects Ray reasoning layers from unsafe, irrelevant,
    low-quality, or fake/fabricated external results.

    It is NOT:
    - Analyst;
    - Governance;
    - truth authority;
    - answer engine;
    - memory authority;
    - readiness engine.

    cleaned_result means:
    safe/relevant enough for the declared next layer,
    not true, not trusted, and not verified.
    """

    def filter_result(
        self,
        result: AcquisitionResult,
        domain: str | None = None,
    ) -> InboundFilterResult:
        raw_result = result.raw_external_result

        if not raw_result or not raw_result.strip():
            return InboundFilterResult(
                request_id=result.request_id,
                decision=InboundFilterDecision.BLOCKED_IRRELEVANT,
                reason_codes=[
                    AcquisitionReasonCode.NO_DATA_ASK_OR_ACQUIRE,
                ],
            )

        if self._contains_fake_or_fabricated_markers(raw_result):
            return InboundFilterResult(
                request_id=result.request_id,
                decision=InboundFilterDecision.BLOCKED_FAKE_OR_FABRICATED,
                reason_codes=[
                    AcquisitionReasonCode.FAKE_CONTENT_REJECTED,
                ],
            )

        if self._contains_unsafe_content(raw_result):
            return InboundFilterResult(
                request_id=result.request_id,
                decision=InboundFilterDecision.BLOCKED_UNSAFE,
                reason_codes=[
                    AcquisitionReasonCode.UNSAFE_EXTERNAL_RESULT,
                ],
            )

        source_decision = self._check_source_class_for_domain(
            source_class=result.source_class,
            domain=domain,
        )

        if source_decision is not None:
            return source_decision(result.request_id)

        cleaned = self._basic_clean(raw_result)

        if not cleaned.strip():
            return InboundFilterResult(
                request_id=result.request_id,
                decision=InboundFilterDecision.BLOCKED_IRRELEVANT,
                reason_codes=[
                    AcquisitionReasonCode.NO_DATA_ASK_OR_ACQUIRE,
                ],
            )

        return InboundFilterResult(
            request_id=result.request_id,
            decision=InboundFilterDecision.ALLOWED_FOR_READINESS,
            cleaned_result=cleaned,
            reason_codes=[
                AcquisitionReasonCode.CLEANED_NOT_TRUSTED,
                AcquisitionReasonCode.TRUSTED_NOT_VERIFIED,
            ],
            filter_metadata={
                "cleaned": True,
                "trusted": False,
                "verified": False,
            },
        )

    def _basic_clean(self, text: str) -> str:
        cleaned = text.strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def _contains_fake_or_fabricated_markers(self, text: str) -> bool:
        """
        Conservative marker detection.

        Ray must not ingest fake/fabricated content.
        This is intentionally not treated as ordinary low-confidence data.
        """

        patterns = [
            r"\bfabricated\b",
            r"\bfake\b",
            r"\bfictional\b",
            r"\binvented\b",
            r"\bmade[- ]?up\b",
            r"\bhallucinated\b",
            r"\bnot real\b",
            r"\bsynthetic scenario\b",
            r"\bпример выдуман\b",
            r"\bвыдуман",
            r"\bфейк",
            r"\bне настоящий\b",
            r"\bгаллюцинац",
        ]

        lowered = text.lower()

        return any(
            re.search(pattern, lowered, flags=re.IGNORECASE)
            for pattern in patterns
        )

    def _contains_unsafe_content(self, text: str) -> bool:
        """
        Baseline safety filter.

        This is intentionally conservative and should later be extended
        by domain-specific safety policies.
        """

        unsafe_patterns = [
            r"\bhow to make\b.*\bexplosive\b",
            r"\bpoison\b",
            r"\bsuicide\b",
            r"\bself[- ]harm\b",
            r"\billegal\b.*\bmethod\b",
            r"\bbypass\b.*\blaw\b",
            r"\bвзрывчат",
            r"\bяд\b",
            r"\bсамоубий",
            r"\bсамоповреж",
            r"\bобойти\b.*\bзакон\b",
        ]

        lowered = text.lower()

        return any(
            re.search(pattern, lowered, flags=re.IGNORECASE)
            for pattern in unsafe_patterns
        )

    def _check_source_class_for_domain(
        self,
        source_class: AcquisitionSourceClass,
        domain: str | None,
    ):
        """
        Source class must match task domain.

        This does not verify truth.
        It only blocks obviously insufficient source classes
        for domains that require stronger provenance.

        Important:
        medical diagnosis != psychophysical readiness
        != sensor monitoring != internal contextual state analysis.
        """

        if domain is None:
            return None

        normalized_domain = domain.lower().strip()

        if normalized_domain in {"academic", "science", "research"}:
            if source_class not in {
                AcquisitionSourceClass.SCIENTIFIC_SOURCE,
                AcquisitionSourceClass.OFFICIAL_SOURCE,
            }:
                return self._blocked_scientific_source_required

        if normalized_domain in {"legal", "immigration", "government"}:
            if source_class != AcquisitionSourceClass.OFFICIAL_SOURCE:
                return self._blocked_official_source_required

        if normalized_domain == "medical":
            if source_class not in {
                AcquisitionSourceClass.OFFICIAL_SOURCE,
                AcquisitionSourceClass.SCIENTIFIC_SOURCE,
            }:
                return self._blocked_official_source_required

        if normalized_domain in {
            "health",
            "readiness",
            "psychophysical",
        }:
            if source_class not in {
                AcquisitionSourceClass.OFFICIAL_SOURCE,
                AcquisitionSourceClass.SCIENTIFIC_SOURCE,
                AcquisitionSourceClass.SENSOR,
                AcquisitionSourceClass.HUMAN_PRIMARY,
                AcquisitionSourceClass.INTERNAL_RAY_LAYER,
            }:
                return self._blocked_official_source_required

        return None

    def _blocked_scientific_source_required(
        self,
        request_id: str,
    ) -> InboundFilterResult:
        return InboundFilterResult(
            request_id=request_id,
            decision=InboundFilterDecision.BLOCKED_LOW_SOURCE_QUALITY,
            reason_codes=[
                AcquisitionReasonCode.SCIENTIFIC_SOURCE_REQUIRED,
                AcquisitionReasonCode.SOURCE_CLASS_MISMATCH,
            ],
        )

    def _blocked_official_source_required(
        self,
        request_id: str,
    ) -> InboundFilterResult:
        return InboundFilterResult(
            request_id=request_id,
            decision=InboundFilterDecision.BLOCKED_LOW_SOURCE_QUALITY,
            reason_codes=[
                AcquisitionReasonCode.OFFICIAL_SOURCE_REQUIRED,
                AcquisitionReasonCode.SOURCE_CLASS_MISMATCH,
            ],
        )