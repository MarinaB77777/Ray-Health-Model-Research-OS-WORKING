from assessment.analysis.check_registry import CHECK_REGISTRY


def get_registered_check_function_name(
    check_id: str,
) -> str | None:
    return CHECK_REGISTRY.get(check_id)