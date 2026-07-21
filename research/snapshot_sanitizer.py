ALLOWED_NEXT_QUESTION_FIELDS = {
    "variable_code",
    "priority",
    "reason_code",
    "domain",
}

ALLOWED_ACQUISITION_REQUEST_FIELDS = {
    "request_type",
    "target_data",
    "acquisition_scope",
    "priority",
    "reason_code",
}


def _sanitize_dict(item: dict, allowed_fields: set[str]) -> dict:
    if not isinstance(item, dict):
        return {}

    return {
        key: value
        for key, value in item.items()
        if key in allowed_fields
    }


def sanitize_next_questions(next_questions: list) -> list:
    if not isinstance(next_questions, list):
        return []

    return [
        sanitized
        for sanitized in (
            _sanitize_dict(item, ALLOWED_NEXT_QUESTION_FIELDS)
            for item in next_questions
        )
        if sanitized
    ]


def sanitize_acquisition_requests(requests):
    if isinstance(requests, list):
        return [
            sanitized
            for sanitized in (
                _sanitize_dict(
                    item,
                    ALLOWED_ACQUISITION_REQUEST_FIELDS,
                )
                for item in requests
            )
            if sanitized
        ]

    if isinstance(requests, dict):
        return _sanitize_dict(
            requests,
            ALLOWED_ACQUISITION_REQUEST_FIELDS,
        )

    return {}
