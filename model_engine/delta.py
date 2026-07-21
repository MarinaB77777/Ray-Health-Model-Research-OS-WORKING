DELTA_THRESHOLD = 1.5


def compute_delta(r_data: dict, k_self_data: dict):
    result = {}

    r_domains = r_data.get("domains", {})
    k_domains = k_self_data.get("domains", {})

    all_domains = set(r_domains.keys()) | set(k_domains.keys())

    for domain in all_domains:
        r_item = r_domains.get(domain, {})
        k_item = k_domains.get(domain, {})

        r_score = r_item.get("score")
        k_score = k_item.get("score")

        r_coverage = r_item.get("coverage", 0)
        k_coverage = k_item.get("coverage", 0)

        if (
            r_score is None
            or k_score is None
            or r_coverage < 0.6
            or k_coverage < 0.6
        ):
            result[domain] = {
                "calculated": False,
                "delta": None,
                "interpretation": "not_calculated",
                "reason_code": "DELTA_NOT_ENOUGH_DOMAIN_DATA",
                "r_score": r_score,
                "k_self_score": k_score,
                "coverage_r": r_coverage,
                "coverage_k": k_coverage,
            }
            continue

        delta = r_score - k_score

        if delta > DELTA_THRESHOLD:
            interpretation = "accumulated_pressure"
            reason_code = "DELTA_ACCUMULATED_PRESSURE"
        elif delta < -DELTA_THRESHOLD:
            interpretation = "hidden_factor"
            reason_code = "DELTA_HIDDEN_FACTOR"
        else:
            interpretation = "aligned"
            reason_code = "DELTA_ALIGNED"


        result[domain] = {
            "calculated": True,
            "delta": round(delta, 3),
            "interpretation": interpretation,
            "reason_code": reason_code,
            "r_score": r_score,
            "k_self_score": k_score,
            "coverage_r": r_coverage,
            "coverage_k": k_coverage,
        }

    return result