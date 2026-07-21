HEALTH_MODEL_V61_REQUIRED_INPUTS_SCHEMA_VERSION = (
    "health-model-v61-required-inputs-1"
)

LOAD_INPUTS = [
    "d7", "d8", "d9", "d10",
    "d11a", "d11b", "d11c", "d11d",
    "d12", "d13",
    "b8",
    "d4b", "d5a", "d6b",
    "e1b", "e1c", "e1d",
    "e2b", "e2c",
    "e3b", "e3c",
    "e4b", "e4c",
    "e5", "e6",
    "e7b", "e7c",
    "b9",
    "d14", "d15",
    "l_environment_additional",
]

RESOURCE_INPUTS = [
    "t1", "t2", "t3", "t4",
    "b3", "b4",
    "m1", "m2", "m3", "m4",
    "g1", "g2", "g3",
    "c1", "c2", "c3",
    "f1", "f2", "f3", "f4",
    "p1", "p2", "p3",
]

COPING_X_INPUTS = [
    "x1", "x1_x5", "x1_x6", "x1_x7",
    "x2", "x2_x5", "x2_x6", "x2_x7",
    "x3", "x3_x5", "x3_x6", "x3_x7",
    "x4", "x4_x5", "x4_x6", "x4_x7",
]

LOAD_FAILURE_INPUTS = [
    "d1a", "d1b", "d1c",
    "d2a", "d2b", "d2c",
    "d3a", "d3b", "d3c",
]

MULTIPLIER_INPUTS = [
    "b12", "d5a",
    "b11_affected",
    "b13",
    "v_level",
]

MANIFESTATION_INPUTS = [
    f"k{i}" for i in range(1, 23)
]

CRITICAL_INPUTS = [
    "k23",
    "k24",
]

CORE_REQUIRED_INPUTS = sorted(set(
    LOAD_INPUTS
    + RESOURCE_INPUTS
    + LOAD_FAILURE_INPUTS
    + MULTIPLIER_INPUTS
    + MANIFESTATION_INPUTS
    + CRITICAL_INPUTS
))

ALL_DIRECT_INPUTS = sorted(set(
    CORE_REQUIRED_INPUTS
    + COPING_X_INPUTS
))


def build_health_model_v61_input_coverage(
    calculator_input: dict,
) -> dict:
    provided = sorted(
        key for key, value in (calculator_input or {}).items()
        if value is not None and value != ""
    )

    provided_set = set(provided)

    missing_core = [
        code for code in CORE_REQUIRED_INPUTS
        if code not in provided_set
    ]

    missing_critical = [
        code for code in CRITICAL_INPUTS
        if code not in provided_set
    ]

    return {
        "schema_version": HEALTH_MODEL_V61_REQUIRED_INPUTS_SCHEMA_VERSION,
        "provided_inputs": provided,
        "provided_count": len(provided),
        "core_required_count": len(CORE_REQUIRED_INPUTS),
        "missing_required_data": missing_core,
        "missing_critical_data": missing_critical,
        "coverage_ratio": (
            len(provided_set.intersection(CORE_REQUIRED_INPUTS))
            / len(CORE_REQUIRED_INPUTS)
            if CORE_REQUIRED_INPUTS
            else 0
        ),
    }