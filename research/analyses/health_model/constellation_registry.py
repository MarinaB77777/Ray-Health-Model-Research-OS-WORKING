CONSTELLATION_REGISTRY_SCHEMA_VERSION = "constellation-registry-1"


def _constellation(
    constellation_id: str,
    title: str,
    constellation_type: str,
    required_mechanisms: list[str],
    optional_amplifiers: list[str],
    protective_signals: list[str],
    threshold: float,
    priority: str,
    configuration_adjustment: float,
    interpretation: str,
    likely_trajectory: str,
    user_facing_explanation: str,
    first_safe_action: str,
    protective_factors: list[str],
    forecast_targets: list[str],
    do_not_say: list[str],
    status: str = "DRAFT_ACTIVE",
):
    return {
        "id": constellation_id,
        "title": title,
        "type": constellation_type,
        "required_mechanisms": required_mechanisms,
        "optional_amplifiers": optional_amplifiers,
        "protective_signals": protective_signals,
        "threshold": threshold,
        "priority": priority,
        "configuration_adjustment": configuration_adjustment,
        "interpretation": interpretation,
        "likely_trajectory": likely_trajectory,
        "user_facing_explanation": user_facing_explanation,
        "first_safe_action": first_safe_action,
        "protective_factors": protective_factors,
        "forecast_targets": forecast_targets,
        "do_not_say": do_not_say,
        "status": status,
        "schema_version": CONSTELLATION_REGISTRY_SCHEMA_VERSION,
    }


CONSTELLATION_REGISTRY = {
    "self_worsening_trajectory": _constellation(
        constellation_id="self_worsening_trajectory",
        title="Self-Worsening Trajectory",
        constellation_type="risk_constellation",
        required_mechanisms=[
            "resource_exhaustion",
            "decision_degradation",
        ],
        optional_amplifiers=[],
        protective_signals=[
            "external_decision_support",
            "pause_before_irreversible_decisions",
            "load_reduction",
            "recovery_support",
            "trusted_person_review",
        ],
        threshold=2.5,
        priority="high",
        configuration_adjustment=0.5,
        interpretation=(
            "Reduced ability to withstand or recover is combined with "
            "decision degradation that may increase future burden, losses, "
            "constraints, or harm."
        ),
        likely_trajectory=(
            "The situation may worsen through decisions whose consequences "
            "become harder to absorb and correct."
        ),
        user_facing_explanation=(
            "Resources may be depleted, and some current decisions may increase "
            "future burden if the situation continues unchanged."
        ),
        first_safe_action=(
            "Pause irreversible decisions and add external decision support."
        ),
        protective_factors=[
            "external decision support",
            "pause before irreversible decisions",
            "reducing load",
            "increasing recovery",
            "trusted person review",
            "specialist support if risk is high",
        ],
        forecast_targets=[
            "increasing future burden through own decisions",
            "higher cost of mistakes",
            "reduced ability to repair consequences",
            "avoidable losses becoming harder to reverse",
            "need for decision support before irreversible actions",
        ],
        do_not_say=[
            "deterioration is inevitable",
            "the person is doomed",
            "the model knows the future",
        ],
    ),

    "entrapment_pattern": _constellation(
        constellation_id="entrapment_pattern",
        title="Entrapment Pattern",
        constellation_type="risk_constellation",
        required_mechanisms=[
            "commitment_trap",
            "option_space_collapse",
        ],
        optional_amplifiers=[
            "pep_negative",
            "resource_exhaustion",
        ],
        protective_signals=[
            "reserve_discovery",
            "external_options_mapping",
            "practical_exit_plan",
            "trusted_support",
        ],
        threshold=2.5,
        priority="high",
        configuration_adjustment=0.5,
        interpretation=(
            "The current path may be recognized as harmful while workable exits "
            "feel unavailable, unsafe, unrealistic, or inaccessible."
        ),
        likely_trajectory=(
            "Staying on a harmful path despite awareness of harm."
        ),
        user_facing_explanation=(
            "The current path may feel damaging, while available exits may feel "
            "unavailable, unsafe, or unrealistic."
        ),
        first_safe_action=(
            "Map objective options separately from options that only feel unavailable."
        ),
        protective_factors=[
            "discovery of reserve",
            "external options mapping",
            "practical exit plan",
            "reduction of irreversible commitments",
            "trusted support",
        ],
        forecast_targets=[
            "staying on a harmful path despite recognizing harm",
            "increasing subjective no-exit feeling",
            "delay of exit decisions",
            "rising cost of stopping later",
            "need for external options mapping",
        ],
        do_not_say=[
            "there is no exit",
            "the person cannot change anything",
            "deterioration is inevitable",
        ],
    ),

    "locked_repetition_pattern": _constellation(
        constellation_id="locked_repetition_pattern",
        title="Locked Repetition Pattern",
        constellation_type="risk_constellation",
        required_mechanisms=[
            "learning_failure",
            "commitment_trap",
        ],
        optional_amplifiers=[],
        protective_signals=[
            "explicit_pattern_review",
            "stop_rule",
            "alternative_strategy",
            "external_accountability",
        ],
        threshold=2.5,
        priority="moderate_high",
        configuration_adjustment=0.5,
        interpretation=(
            "Negative outcomes may repeat while the same or similar strategy "
            "continues and stopping the path is difficult."
        ),
        likely_trajectory=(
            "Repetition of a known harmful pattern with accumulating cost."
        ),
        user_facing_explanation=(
            "A repeated pattern may be continuing without enough strategy change."
        ),
        first_safe_action=(
            "Define a stop-rule and test one alternative strategy."
        ),
        protective_factors=[
            "explicit pattern review",
            "stop-rule",
            "alternative strategy",
            "external accountability",
            "reducing sunk-cost pressure",
        ],
        forecast_targets=[
            "repetition of known harmful strategy",
            "accumulation of preventable losses",
            "reduced learning from negative outcomes",
            "stronger sunk-cost effect",
            "need for stop-rules and alternative strategy testing",
        ],
        do_not_say=[
            "the person never learns",
            "failure is certain",
            "the model knows the future",
        ],
    ),

    "recovery_block_pattern": _constellation(
        constellation_id="recovery_block_pattern",
        title="Recovery Block Pattern",
        constellation_type="risk_constellation",
        required_mechanisms=[
            "recovery_mismatch",
            "resource_exhaustion",
        ],
        optional_amplifiers=[],
        protective_signals=[
            "hidden_pressure_identified",
            "structured_recovery_plan",
            "medical_review",
            "destructive_coping_reduction",
        ],
        threshold=2.5,
        priority="high",
        configuration_adjustment=0.5,
        interpretation=(
            "The system appears depleted, and recovery does not match expected "
            "improvement."
        ),
        likely_trajectory=(
            "Rest or reduced pressure may not be enough if hidden load, blocked "
            "recovery, or biological/contextual factors remain active."
        ),
        user_facing_explanation=(
            "Even when recovery should be happening, capacity may not be restoring "
            "as expected."
        ),
        first_safe_action=(
            "Check for hidden pressure, hidden load, sleep/health factors, and "
            "destructive coping."
        ),
        protective_factors=[
            "identify hidden pressure",
            "sleep / health / medical review",
            "reduce destructive coping",
            "structured recovery plan",
            "check sensor and manifestation trends",
        ],
        forecast_targets=[
            "insufficient restoration despite rest",
            "delayed worsening of markers",
            "persistence of fatigue or manifestations",
            "hidden load or hidden pressure",
            "need to search for blocked recovery causes",
        ],
        do_not_say=[
            "rest cannot help",
            "recovery is impossible",
            "the condition is permanent",
        ],
    ),

    "negative_spiral_pattern": _constellation(
        constellation_id="negative_spiral_pattern",
        title="Negative Spiral Pattern",
        constellation_type="risk_constellation",
        required_mechanisms=[
            "negative_spiral",
            "resource_exhaustion",
        ],
        optional_amplifiers=[
            "decision_degradation",
            "learning_failure",
        ],
        protective_signals=[
            "loop_identified",
            "leverage_point_selected",
            "external_support",
            "load_reduction",
        ],
        threshold=2.5,
        priority="high",
        configuration_adjustment=0.7,
        interpretation=(
            "A cross-domain feedback loop may be active while capacity to interrupt "
            "it is reduced."
        ),
        likely_trajectory=(
            "One domain may worsen another, creating a self-reinforcing "
            "deterioration loop."
        ),
        user_facing_explanation=(
            "Several life domains may be feeding into each other, making the "
            "situation harder to stop from inside the system."
        ),
        first_safe_action=(
            "Identify one link in the loop that can be interrupted first."
        ),
        protective_factors=[
            "identify the loop",
            "break one link in the loop",
            "prioritize leverage point",
            "external support",
            "reduce load in the most connected domain",
        ],
        forecast_targets=[
            "worsening across connected domains",
            "self-reinforcing deterioration loop",
            "one domain becoming leverage point",
            "increasing difficulty to interrupt from inside",
            "need to break one link in the loop",
        ],
        do_not_say=[
            "everything is collapsing",
            "the person cannot stop it",
            "deterioration is inevitable",
        ],
    ),

    "pressure_depletion_pattern": _constellation(
        constellation_id="pressure_depletion_pattern",
        title="Pressure-Depletion Pattern",
        constellation_type="risk_constellation",
        required_mechanisms=[
            "coincidence_burden",
            "resource_exhaustion",
        ],
        optional_amplifiers=[],
        protective_signals=[
            "pressure_reduction",
            "load_reduction",
            "recovery_support",
            "reserve_discovery",
            "temporary_external_help",
        ],
        threshold=2.5,
        priority="high",
        configuration_adjustment=0.5,
        interpretation=(
            "Pressure is active while resources are insufficient, and the ability "
            "to keep paying that cost is decreasing."
        ),
        likely_trajectory=(
            "Markers may worsen later if pressure continues and recovery does not "
            "interrupt depletion."
        ),
        user_facing_explanation=(
            "The system may be paying a high cost while its ability to pay is "
            "decreasing."
        ),
        first_safe_action=(
            "Reduce pressure or load temporarily and protect recovery."
        ),
        protective_factors=[
            "pressure reduction",
            "load reduction",
            "recovery support",
            "reserve discovery",
            "temporary external help",
        ],
        forecast_targets=[
            "markers catching up later",
            "reduced capacity to sustain current load",
            "rising effort-cost for the same situation",
            "higher risk if pressure continues",
            "need for pressure reduction or temporary external support",
        ],
        do_not_say=[
            "collapse is certain",
            "pressure alone proves deterioration",
            "the person is unsafe without additional evidence",
        ],
    ),

    "perceived_no_exit_pattern": _constellation(
        constellation_id="perceived_no_exit_pattern",
        title="Perceived No-Exit Pattern",
        constellation_type="risk_constellation",
        required_mechanisms=[
            "option_space_collapse",
            "pep_negative",
        ],
        optional_amplifiers=[
            "resource_exhaustion",
            "commitment_trap",
        ],
        protective_signals=[
            "objective_option_mapping",
            "hidden_reserve_identified",
            "small_reversible_option_test",
            "external_perspective",
        ],
        threshold=2.5,
        priority="moderate_high",
        configuration_adjustment=0.3,
        interpretation=(
            "Few workable options are perceived, and future expectancy may make "
            "available paths feel less workable."
        ),
        likely_trajectory=(
            "The future may feel more closed or hostile than the objective "
            "situation alone supports."
        ),
        user_facing_explanation=(
            "Available paths may feel less workable because future events are "
            "expected to turn against them."
        ),
        first_safe_action=(
            "Separate objective option loss from perceived option loss."
        ),
        protective_factors=[
            "distinguish objective options from perceived options",
            "identify hidden reserve",
            "test small reversible options",
            "external perspective",
            "reduce catastrophic expectation",
        ],
        forecast_targets=[
            "narrowing of perceived future options",
            "stronger belief that available options will not work",
            "higher vulnerability to negative PEP",
            "underuse of objectively available paths",
            "need to distinguish objective vs perceived option loss",
        ],
        do_not_say=[
            "there are no options",
            "the future will turn against the person",
            "negative expectation is fact",
        ],
    ),

    "adaptive_recovery_window": _constellation(
        constellation_id="adaptive_recovery_window",
        title="Adaptive Recovery Window",
        constellation_type="protective_constellation",
        required_mechanisms=[
            "resource_exhaustion",
        ],
        optional_amplifiers=[],
        protective_signals=[
            "recovery_signal",
            "reserve_discovered",
            "pep_positive",
            "decision_degradation_low",
        ],
        threshold=2.5,
        priority="protective",
        configuration_adjustment=-0.3,
        interpretation=(
            "Depletion is present, but trajectory may remain recoverable because "
            "adaptive control and recovery pathways may still be available."
        ),
        likely_trajectory=(
            "Risk exists, but an intervention window may be open."
        ),
        user_facing_explanation=(
            "Resources may be low, but there may still be signs of recoverability "
            "and adaptive control."
        ),
        first_safe_action=(
            "Protect recovery and avoid irreversible decisions while depleted."
        ),
        protective_factors=[
            "protect recovery",
            "avoid irreversible decisions",
            "strengthen reserve",
            "reduce pressure",
            "maintain support",
        ],
        forecast_targets=[
            "recoverability if support is protected",
            "improvement if pressure decreases",
            "preservation of adaptive control",
            "reduced trajectory risk if reserve becomes operational",
            "need to avoid irreversible decisions while depleted",
        ],
        do_not_say=[
            "risk is gone",
            "protective factors erase risk",
            "recovery is guaranteed",
        ],
    ),
}


def get_constellation(constellation_id: str) -> dict | None:
    return CONSTELLATION_REGISTRY.get(constellation_id)


def list_constellations() -> list[dict]:
    return list(CONSTELLATION_REGISTRY.values())