WARNING_REGISTRY = {
    "CRITICAL_K23": {
        "severity": "critical",
        "type": "safety",
        "public": True,
        "message": {
            "en": "Critical response detected.",
            "es": "Se detectó una respuesta crítica.",
        },
    },
    "CRITICAL_K24": {
        "severity": "critical",
        "type": "safety",
        "public": True,
        "message": {
            "en": "Critical response detected.",
            "es": "Se detectó una respuesta crítica.",
        },
    },
    "LOW_COVERAGE": {
        "severity": "info",
        "type": "coverage",
        "public": True,
        "message": {
            "en": "Additional data is recommended.",
            "es": "Se recomienda información adicional.",
        },
    },
}


def normalize_warning(reason_code: str):
    item = WARNING_REGISTRY.get(reason_code)

    if item is None:
        return None

    return {
        "code": reason_code,
        "severity": item["severity"],
        "type": item["type"],
        "public": item["public"],
        "message": item["message"],
    }


def build_warnings(reason_codes: list):
    warnings = []

    for code in reason_codes:
        warning = normalize_warning(code)

        if warning is not None:
            warnings.append(warning)

    return warnings


def extract_public_warnings(warnings: list):
    return [
        item
        for item in warnings
        if item.get("public") is True
    ]