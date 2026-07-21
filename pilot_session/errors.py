class PilotSessionError(Exception):
    error_code = "PILOT_SESSION_ERROR"
    status_code = 400

    def to_dict(self):
        return {
            "ok": False,
            "error": {
                "code": self.error_code,
                "message": str(self),
            },
        }


class SessionNotFoundError(PilotSessionError):
    error_code = "SESSION_NOT_FOUND"
    status_code = 404


class InvalidStatusTransitionError(PilotSessionError):
    error_code = "INVALID_STATUS_TRANSITION"
    status_code = 409


class SessionInvalidatedError(PilotSessionError):
    error_code = "SESSION_INVALIDATED"
    status_code = 409


class ExportBlockedError(PilotSessionError):
    error_code = "EXPORT_BLOCKED"
    status_code = 409


class SessionDeletedError(PilotSessionError):
    error_code = "SESSION_DELETED"
    status_code = 410


class RunFailedError(PilotSessionError):
    error_code = "RUN_FAILED"
    status_code = 500
