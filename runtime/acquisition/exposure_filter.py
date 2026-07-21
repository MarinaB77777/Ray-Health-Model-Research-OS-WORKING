# runtime/acquisition/exposure_filter.py

from __future__ import annotations

import re

from runtime.acquisition.contracts import (
    AcquisitionReasonCode,
    AcquisitionRequest,
    ExposureDecision,
    ExposureFilterResult,
)


class ExposureFilter:
    """
    Outbound Exposure Filter.

    This module protects what leaves Ray.

    It is NOT:
    - Analyst;
    - Governance;
    - truth authority;
    - answer engine;
    - memory authority.

    It prepares a temporary outbound sanitized request
    for approved external acquisition paths.

    raw_internal_question must never be sent outside Ray directly.

    Conservative rule:
    permission does not automatically mean safe anonymization.
    High-risk sensitive content remains blocked until stronger governed
    export policies exist.
    """

    def filter_for_external_acquisition(
        self,
        request: AcquisitionRequest,
        privacy_policy_known: bool = True,
        human_permission_granted: bool = False,
    ) -> ExposureFilterResult:
        if not privacy_policy_known:
            return ExposureFilterResult(
                request_id=request.request_id,
                decision=ExposureDecision.NEEDS_HUMAN_PERMISSION,
                reason_codes=[
                    AcquisitionReasonCode.PRIVACY_POLICY_UNKNOWN,
                    AcquisitionReasonCode.HUMAN_PERMISSION_REQUIRED,
                ],
            )

        raw_question = request.raw_internal_question

        if not raw_question:
            return ExposureFilterResult(
                request_id=request.request_id,
                decision=ExposureDecision.BLOCKED,
                reason_codes=[
                    AcquisitionReasonCode.RAW_QUESTION_INTERNAL_ONLY,
                ],
            )

        sanitized = self._basic_anonymize(raw_question)

        if self._contains_high_risk_personal_data(sanitized):
            return ExposureFilterResult(
                request_id=request.request_id,
                decision=ExposureDecision.CANNOT_SAFELY_ANONYMIZE,
                reason_codes=[
                    AcquisitionReasonCode.HUMAN_PERMISSION_REQUIRED,
                ],
            )

        if not sanitized.strip():
            return ExposureFilterResult(
                request_id=request.request_id,
                decision=ExposureDecision.CANNOT_SAFELY_ANONYMIZE,
                reason_codes=[
                    AcquisitionReasonCode.HUMAN_PERMISSION_REQUIRED,
                ],
            )

        if self._contains_high_risk_personal_data(raw_question):
            if not human_permission_granted:
                return ExposureFilterResult(
                    request_id=request.request_id,
                    decision=ExposureDecision.NEEDS_HUMAN_PERMISSION,
                    reason_codes=[
                        AcquisitionReasonCode.HUMAN_PERMISSION_REQUIRED,
                    ],
                )

            return ExposureFilterResult(
                request_id=request.request_id,
                decision=ExposureDecision.CANNOT_SAFELY_ANONYMIZE,
                reason_codes=[
                    AcquisitionReasonCode.HUMAN_PERMISSION_REQUIRED,
                ],
            )

        return ExposureFilterResult(
            request_id=request.request_id,
            decision=ExposureDecision.ALLOWED,
            outbound_sanitized_request=sanitized,
            persist_sanitized_request=False,
            reason_codes=[
                AcquisitionReasonCode.OUTBOUND_SANITIZED_NOT_STORED,
            ],
            exposure_metadata={
                "raw_question_used_directly": False,
                "temporary_only": True,
                "anonymization": "basic",
            },
        )

    def _basic_anonymize(self, text: str) -> str:
        sanitized = text

        sanitized = self._replace_emails(sanitized)
        sanitized = self._replace_phone_numbers(sanitized)
        sanitized = self._replace_ages(sanitized)
        sanitized = self._replace_person_names_like_patterns(sanitized)
        sanitized = self._remove_obvious_addresses(sanitized)

        return sanitized.strip()

    def _replace_emails(self, text: str) -> str:
        return re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            "[email removed]",
            text,
        )

    def _replace_phone_numbers(self, text: str) -> str:
        return re.sub(
            r"(\+?\d[\d\s().-]{7,}\d)",
            "[phone removed]",
            text,
        )

    def _replace_ages(self, text: str) -> str:
        def replace_age(match: re.Match[str]) -> str:
            age = int(match.group(1))

            if age < 13:
                category = "child"
            elif age < 18:
                category = "teenager"
            elif age < 65:
                category = "adult"
            else:
                category = "older adult"

            return category

        return re.sub(
            r"\b(\d{1,3})\s*(years old|year old|лет|года|год)\b",
            replace_age,
            text,
            flags=re.IGNORECASE,
        )

    def _replace_person_names_like_patterns(self, text: str) -> str:
        """
        Minimal baseline anonymization.

        This is intentionally conservative and should later be replaced
        by a stronger governed PII detector.

        It does not claim perfect name detection.
        """

        patterns = [
            r"\bmy husband\s+[A-Z][a-zA-Z]+\b",
            r"\bmy wife\s+[A-Z][a-zA-Z]+\b",
            r"\bмой муж\s+[А-ЯЁ][а-яё]+\b",
            r"\bмоя жена\s+[А-ЯЁ][а-яё]+\b",
        ]

        sanitized = text

        for pattern in patterns:
            sanitized = re.sub(
                pattern,
                "a family member",
                sanitized,
                flags=re.IGNORECASE,
            )

        return sanitized

    def _remove_obvious_addresses(self, text: str) -> str:
        return re.sub(
            r"\b\d{1,6}\s+[A-Za-zА-Яа-яЁё0-9 .'-]+"
            r"\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln)\b",
            "[address removed]",
            text,
            flags=re.IGNORECASE,
        )

    def _contains_high_risk_personal_data(self, text: str) -> bool:
        high_risk_patterns = [
            r"\bpassport\b",
            r"\bssn\b",
            r"\bsocial security\b",
            r"\bmedical diagnosis\b",
            r"\bdiagnosis\b",
            r"\bbank account\b",
            r"\bcredit card\b",
            r"\bпаспорт\b",
            r"\bдиагноз\b",
            r"\bбанковск",
            r"\bкредитн",
        ]

        lowered = text.lower()

        return any(
            re.search(pattern, lowered, flags=re.IGNORECASE)
            for pattern in high_risk_patterns
        )