from research.snapshot_sanitizer import (
    sanitize_acquisition_requests,
    sanitize_next_questions,
)


def test_sanitize_next_questions_keeps_allowed_fields():
    questions = [
        {
            "variable_code": "d0",
            "priority": 1,
            "reason_code": "MISSING_FIELD",
            "domain": "activity",
        }
    ]

    sanitized = sanitize_next_questions(questions)

    assert sanitized == [
        {
            "variable_code": "d0",
            "priority": 1,
            "reason_code": "MISSING_FIELD",
            "domain": "activity",
        }
    ]


def test_sanitize_next_questions_removes_forbidden_fields():
    questions = [
        {
            "variable_code": "d0",
            "priority": 1,
            "reason_code": "MISSING_FIELD",
            "domain": "activity",
            "free_text": "remove me",
            "question_text": "remove me",
            "internal_notes": "remove me",
            "routing_metadata": {"hidden": True},
            "debug": {"trace": True},
            "policy_trace": "remove me",
            "governance_trace": "remove me",
            "raw_prompt": "remove me",
            "hidden_reasoning": "remove me",
        }
    ]

    sanitized = sanitize_next_questions(questions)

    assert sanitized == [
        {
            "variable_code": "d0",
            "priority": 1,
            "reason_code": "MISSING_FIELD",
            "domain": "activity",
        }
    ]

    assert "remove me" not in str(sanitized)
    assert "hidden" not in str(sanitized)


def test_sanitize_next_questions_handles_invalid_input():
    assert sanitize_next_questions(None) == []
    assert sanitize_next_questions({"not": "a list"}) == []
    assert sanitize_next_questions(["invalid"]) == []


def test_sanitize_acquisition_requests_keeps_allowed_fields_from_dict():
    request = {
        "request_type": "data_acquisition",
        "target_data": "d0",
        "acquisition_scope": "participant_question",
        "priority": 1,
        "reason_code": "MISSING_FIELD",
    }

    sanitized = sanitize_acquisition_requests(request)

    assert sanitized == {
        "request_type": "data_acquisition",
        "target_data": "d0",
        "acquisition_scope": "participant_question",
        "priority": 1,
        "reason_code": "MISSING_FIELD",
    }


def test_sanitize_acquisition_requests_removes_forbidden_fields_from_dict():
    request = {
        "request_type": "data_acquisition",
        "target_data": "d0",
        "acquisition_scope": "participant_question",
        "priority": 1,
        "reason_code": "MISSING_FIELD",
        "internal_notes": "remove me",
        "routing_metadata": {"hidden": True},
        "debug": {"trace": True},
        "policy_trace": "remove me",
        "governance_trace": "remove me",
        "transport_details": "remove me",
        "executor": "remove me",
        "raw_prompt": "remove me",
        "hidden_reasoning": "remove me",
    }

    sanitized = sanitize_acquisition_requests(request)

    assert sanitized == {
        "request_type": "data_acquisition",
        "target_data": "d0",
        "acquisition_scope": "participant_question",
        "priority": 1,
        "reason_code": "MISSING_FIELD",
    }

    assert "remove me" not in str(sanitized)
    assert "hidden" not in str(sanitized)


def test_sanitize_acquisition_requests_handles_list():
    requests = [
        {
            "request_type": "data_acquisition",
            "target_data": "d0",
            "priority": 1,
            "debug": "remove me",
        },
        {
            "executor": "remove me",
        },
    ]

    sanitized = sanitize_acquisition_requests(requests)

    assert sanitized == [
        {
            "request_type": "data_acquisition",
            "target_data": "d0",
            "priority": 1,
        }
    ]


def test_sanitize_acquisition_requests_handles_invalid_input():
    assert sanitize_acquisition_requests(None) == {}
    assert sanitize_acquisition_requests("invalid") == {}