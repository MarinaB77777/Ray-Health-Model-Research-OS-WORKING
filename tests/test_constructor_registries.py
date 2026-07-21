from pathlib import Path

from research.analyses.health_model import mechanism_registry
from research.analyses.health_model import model_parameter_registry


def _parameter_definition():
    return {
        "parameter_code": "constructor_test_parameter",
        "title": {"ru": "Тест", "en": "Test", "es": "Prueba"},
        "parameter_kind": "scalar",
        "value_type": "float",
        "scale_type": "continuous",
        "calculation": {
            "value_path": "constructor.test",
            "model_id": "health_model_v6_1",
            "calculation_version": "constructor-1",
        },
        "value_schema": {"minimum": 0, "maximum": 10, "unit": None},
        "research": {"available": True, "allowed_analysis_roles": ["outcome"]},
        "meaning": {
            "construct_definition": {
                "ru": "Смысл", "en": "Meaning", "es": "Significado",
            }
        },
        "measurement_design": {
            "measurement_type": "derived",
            "required_input_roles": ["input_x"],
            "optional_input_roles": [],
            "minimum_required_inputs": 1,
        },
        "temporal_design": {
            "time_dependent": False,
            "time_roles": ["observation_time"],
            "observation_time_required": True,
            "global_time_reference_required": True,
            "aggregation": "single_observation",
            "minimum_observation_count": 1,
            "ordering_required": False,
            "temporal_meaning": "Момент получения измерения",
            "time_scale": {"scale_type": "datetime"},
            "time_window": {"type": None, "value": None, "unit": "days"},
            "missing_time_semantics": "not_enough_data",
        },
        "calculation_design": {
            "operator": "mean", "components": ["input_x"], "unknown_is_zero": False,
        },
        "marker_validation": {"included_in_parameter_value": False, "marker_mappings": []},
        "feedback": {"feedback_status": "not_evaluated", "human_review_required": True},
    }


def _mechanism_definition():
    return {
        "mechanism_code": "constructor_test_mechanism",
        "title": {"ru": "Механизм", "en": "Mechanism", "es": "Mecanismo"},
        "meaning": {
            "construct_definition": {
                "ru": "Смысл", "en": "Meaning", "es": "Significado",
            }
        },
        "input_contract": {
            "required_parameter_codes": ["constructor_test_parameter"],
            "optional_parameter_codes": [],
            "required_mechanism_codes": [],
            "optional_mechanism_codes": [],
            "required_function_codes": [],
            "supporting_function_codes": [],
            "minimum_required_inputs": 1,
        },
        "output_scale": {"scale_type": "model_index", "minimum": 0, "maximum": 5},
        "temporal_design": {
            "time_dependent": True,
            "temporal_form": "trajectory",
            "aggregation": "sequence_pattern",
            "minimum_observation_count": 2,
            "ordering_required": True,
            "temporal_meaning": "Изменение механизма в общей временной оси",
            "time_scale": {"scale_type": "datetime"},
            "time_window": {"type": None, "value": None, "unit": "days"},
        },
        "calculation_design": {"operator": "mean", "components": ["constructor_test_parameter"]},
        "confirmed_requires_repeated_measurement": True,
    }


def test_parameter_draft_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setattr(
        model_parameter_registry,
        "CUSTOM_PARAMETER_DEFINITIONS_PATH",
        Path(tmp_path) / "parameters.json",
    )
    created = model_parameter_registry.upsert_custom_model_parameter_draft(
        _parameter_definition()
    )
    assert created["ok"] is True
    version = created["definition"]["definition_version"]
    assert model_parameter_registry.transition_custom_model_parameter_definition(
        "constructor_test_parameter", version, "trial"
    )["ok"] is True
    assert model_parameter_registry.transition_custom_model_parameter_definition(
        "constructor_test_parameter", version, "active"
    )["ok"] is True


def test_mechanism_draft_lifecycle_and_precise_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(
        mechanism_registry,
        "CUSTOM_MECHANISM_DEFINITIONS_PATH",
        Path(tmp_path) / "mechanisms.json",
    )
    created = mechanism_registry.upsert_custom_mechanism_draft(
        _mechanism_definition()
    )
    assert created["ok"] is True
    version = created["definition"]["definition_version"]
    deleted = mechanism_registry.delete_custom_mechanism_draft(
        "constructor_test_mechanism", version
    )
    assert deleted["ok"] is True
    assert deleted["calculation_cleanup"]["performed"] is False


def test_existing_mechanism_layer_contract_is_preserved():
    definitions = mechanism_registry.list_mechanisms()
    assert len(definitions) == 7
    assert all(isinstance(definition["title"], str) for definition in definitions)
    assert all(
        definition["temporal_design"]["global_time_reference_required"] is True
        for definition in definitions
    )
    assert all(
        definition["temporal_design"]["global_time_scale"]["scale_type"]
        == "datetime"
        for definition in definitions
    )


def test_incompatible_time_scale_and_role_are_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(
        model_parameter_registry,
        "CUSTOM_PARAMETER_DEFINITIONS_PATH",
        Path(tmp_path) / "parameters.json",
    )
    definition = _parameter_definition()
    definition["parameter_code"] = "invalid_time_scale_pair"
    definition["temporal_design"]["time_roles"] = ["latency"]
    definition["temporal_design"]["time_scale"] = {"scale_type": "date"}
    result = model_parameter_registry.upsert_custom_model_parameter_draft(
        definition
    )
    assert result["ok"] is False
    assert any(
        error["code"] == "TIME_SCALE_ROLE_MISMATCH"
        for error in result["validation"]["errors"]
    )


def test_parameter_can_reach_active_without_scale_binding(tmp_path, monkeypatch):
    monkeypatch.setattr(
        model_parameter_registry,
        "CUSTOM_PARAMETER_DEFINITIONS_PATH",
        Path(tmp_path) / "parameters.json",
    )
    definition = _parameter_definition()
    definition["parameter_code"] = "individual_parameter_without_scale"
    definition["scale_type"] = None
    definition["output_scale"] = {
        "scale_type": None,
        "binding_status": "unbound",
    }
    definition["temporal_design"]["time_scale"] = {
        "scale_type": None,
        "binding_status": "unbound",
    }
    created = model_parameter_registry.upsert_custom_model_parameter_draft(
        definition
    )
    assert created["ok"] is True
    assert created["definition"]["scale_binding_status"] == "unbound"
    version = created["definition"]["definition_version"]
    trial = model_parameter_registry.transition_custom_model_parameter_definition(
        "individual_parameter_without_scale", version, "trial"
    )
    assert trial["ok"] is True
    active = model_parameter_registry.transition_custom_model_parameter_definition(
        "individual_parameter_without_scale", version, "active"
    )
    assert active["ok"] is True


def test_mechanism_can_reach_active_without_scale_binding(tmp_path, monkeypatch):
    monkeypatch.setattr(
        mechanism_registry,
        "CUSTOM_MECHANISM_DEFINITIONS_PATH",
        Path(tmp_path) / "mechanisms.json",
    )
    definition = _mechanism_definition()
    definition["mechanism_code"] = "individual_mechanism_without_scale"
    definition["output_scale"] = {
        "scale_type": None,
        "binding_status": "unbound",
    }
    definition["temporal_design"]["time_scale"] = {
        "scale_type": None,
        "binding_status": "unbound",
    }
    created = mechanism_registry.upsert_custom_mechanism_draft(definition)
    assert created["ok"] is True
    assert created["definition"]["output_scale"]["binding_status"] == "unbound"
    version = created["definition"]["definition_version"]
    trial = mechanism_registry.transition_custom_mechanism_definition(
        "individual_mechanism_without_scale", version, "trial"
    )
    assert trial["ok"] is True
    active = mechanism_registry.transition_custom_mechanism_definition(
        "individual_mechanism_without_scale", version, "active"
    )
    assert active["ok"] is True
