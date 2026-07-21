from pilot_session.errors import (
    ExportBlockedError,
    InvalidStatusTransitionError,
    RunFailedError,
    SessionDeletedError,
    SessionInvalidatedError,
    SessionNotFoundError,
)


def test_session_not_found_error_contract():
    error = SessionNotFoundError("Session not found")

    assert error.status_code == 404
    assert error.to_dict()["ok"] is False
    assert error.to_dict()["error"]["code"] == "SESSION_NOT_FOUND"


def test_invalid_status_transition_error_contract():
    error = InvalidStatusTransitionError("Invalid status transition")

    assert error.status_code == 409
    assert error.to_dict()["error"]["code"] == "INVALID_STATUS_TRANSITION"


def test_session_invalidated_error_contract():
    error = SessionInvalidatedError("Session invalidated")

    assert error.status_code == 409
    assert error.to_dict()["error"]["code"] == "SESSION_INVALIDATED"


def test_export_blocked_error_contract():
    error = ExportBlockedError("Export blocked")

    assert error.status_code == 409
    assert error.to_dict()["error"]["code"] == "EXPORT_BLOCKED"


def test_session_deleted_error_contract():
    error = SessionDeletedError("Session deleted")

    assert error.status_code == 410
    assert error.to_dict()["error"]["code"] == "SESSION_DELETED"


def test_run_failed_error_contract():
    error = RunFailedError("Run failed")

    assert error.status_code == 500
    assert error.to_dict()["error"]["code"] == "RUN_FAILED"
