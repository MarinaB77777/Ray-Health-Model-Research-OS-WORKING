def build_vnext_reason_codes(vnext_signals_data: dict):
    reasons = []

    signals = vnext_signals_data.get("signals", {})

    def get_signal(name):
        data = signals.get(name, {})
        return data.get("score"), data.get("coverage", 0)

    option_score, option_coverage = get_signal("OptionSpaceCollapse")
    if option_score is not None and option_coverage >= 0.5 and option_score >= 3.5:
        reasons.append("VNEXT_OPTION_SPACE_COLLAPSE")

    hopeless_score, hopeless_coverage = get_signal("HopelessnessSignal")
    if hopeless_score is not None and hopeless_coverage >= 0.67 and hopeless_score >= 3.5:
        reasons.append("VNEXT_HOPELESSNESS_SIGNAL")

    spiral_score, spiral_coverage = get_signal("NegativeSpiral")
    if spiral_score is not None and spiral_coverage >= 0.5 and spiral_score >= 3.5:
        reasons.append("VNEXT_NEGATIVE_SPIRAL")

    exhaustion_score, exhaustion_coverage = get_signal("ResourceExhaustionSignal")
    if exhaustion_score is not None and exhaustion_coverage >= 0.5 and exhaustion_score >= 3.5:
        reasons.append("VNEXT_RESOURCE_EXHAUSTION")

    return reasons
