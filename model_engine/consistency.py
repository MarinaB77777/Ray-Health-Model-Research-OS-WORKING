CONSISTENCY_WEIGHTS = {
    "C3_R_K_CONFLICT": 1.2,
}

MAX_C_FINAL = 5.0


def compute_consistency(delta_data: dict):
    flags = []

    for domain, item in delta_data.items():
        if not item.get("calculated"):
            continue

        interpretation = item.get("interpretation")
        if interpretation == "accumulated_pressure":
            flags.append({
                "flag_code": "C3_R_K_CONFLICT",
                "domain": domain,
                "active": True,
                "weight": CONSISTENCY_WEIGHTS["C3_R_K_CONFLICT"],
                "reason": item.get("reason_code"),
                "delta": item.get("delta"),
            })

    if not flags:
        return {
            "c_final": 0,
            "c_score": 0,
            "c_max": 0,
            "flags": [],
        }

    c_score = sum(flag["weight"] for flag in flags)
    c_max = max(flag["weight"] for flag in flags)

    # MVP: normalize by number of possible domains, not by one flag type.
    # This prevents repeated domain-level C3 from exploding.
    possible_domain_count = max(len(delta_data), 1)
    c_density = min(1.0, len(flags) / possible_domain_count)

    c_final = (0.6 * c_max) + (0.4 * (c_density * MAX_C_FINAL))
    c_final = min(MAX_C_FINAL, c_final)

    return {
        "c_final": round(c_final, 3),
        "c_score": round(c_score, 3),
        "c_max": round(c_max, 3),
        "flags": flags,
    }