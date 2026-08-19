from api.ray_integrity import ray_integrity_status


def test_integrity_status_never_reports_raw_inner_core():
    result = ray_integrity_status()
    assert result["invariants"]["raw_inner_core_exposed"] is False
    assert result["inner_core"]["heart_of_ray"]["raw_content_exposed"] is False
    assert result["inner_core"]["heart_of_human"]["raw_content_exposed"] is False
    assert result["external_core"]["protected_memory_access"] is False


def test_integrity_status_is_honest_about_unimplemented_components():
    result = ray_integrity_status()
    assert result["inner_core"]["heart_of_ray"]["provisioned"] is False
    assert result["inner_core"]["heart_of_human"]["provisioned"] is False
    assert result["self_health"]["sensor_state"] == "NO_DEVICE"
    assert result["self_health"]["production_store"] == "NOT_IMPLEMENTED"
    assert result["learning"]["engine"] == "NOT_IMPLEMENTED"


def test_integrity_status_preserves_core_invariants():
    invariants = ray_integrity_status()["invariants"]
    assert invariants["projection_is_permission"] is False
    assert invariants["memory_is_authority"] is False
    assert invariants["unknown_equals_zero"] is False
    assert invariants["runtime_completed_proves_external_effect"] is False
    assert invariants["external_ai_is_ray_memory"] is False
