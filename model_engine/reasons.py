REASON_REGISTRY = {
    "LOW_COVERAGE": {
        "severity": "info",
        "type": "coverage",
        "public": True,
    },
    "STATE_NOT_ENOUGH_DATA": {
        "severity": "info",
        "type": "state",
        "public": True,
    },
    "SAFE_DATA_REQUEST_OVERRIDE": {
        "severity": "info",
        "type": "state",
        "public": True,
    },
    "CRITICAL_K23": {
        "severity": "critical",
        "type": "safety",
        "public": False,
    },
    "CRITICAL_K24": {
        "severity": "critical",
        "type": "safety",
        "public": False,
    },
    "CRITICAL_OVERRIDE": {
        "severity": "critical",
        "type": "state",
        "public": True,
    },
    "STATE_DIAGNOSTIC": {
        "severity": "info",
        "type": "state",
        "public": True,
    },
    "STATE_FORECAST": {
        "severity": "caution",
        "type": "forecast",
        "public": True,
    },
    "STATE_HIDDEN_FACTOR": {
        "severity": "caution",
        "type": "state",
        "public": True,
    },
    "CONSISTENCY_FAILURE": {
        "severity": "caution",
        "type": "consistency",
        "public": True,
    },
"VNEXT_OPTION_SPACE_COLLAPSE": {
        "severity": "caution",
        "type": "vnext",
        "public": True,
    },

    "VNEXT_HOPELESSNESS_SIGNAL": {
        "severity": "caution",
        "type": "vnext",
        "public": True,
    },

    "VNEXT_NEGATIVE_SPIRAL": {
        "severity": "caution",
        "type": "vnext",
        "public": True,
    },

    "VNEXT_RESOURCE_EXHAUSTION": {
        "severity": "caution",
        "type": "vnext",
        "public": True,
    },
}


def normalize_reason(reason_code: str):
    item = REASON_REGISTRY.get(reason_code)

    if item is None:
        return {
            "code": reason_code,
            "severity": "info",
            "type": "unknown",
            "public": False,
        }

    return {
        "code": reason_code,
        "severity": item["severity"],
        "type": item["type"],
        "public": item["public"],
    }


def normalize_reason_codes(reason_codes: list):
    normalized = []

    for code in reason_codes:
        normalized.append(normalize_reason(code))

    return normalized


def extract_public_reasons(normalized_reasons: list):
    return [
        item
        for item in normalized_reasons
        if item.get("public") is True
    ]