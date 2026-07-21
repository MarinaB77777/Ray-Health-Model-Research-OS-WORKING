def compute_q_basic(answers: dict, coverage_data: dict):
    q_score = 0
    critical_unknown = False

    if coverage_data["coverage"] < 0.6:
        q_score += 1

    for field in ["k23", "k24"]:
        if answers.get(field) is None:
            critical_unknown = True

    if critical_unknown:
        q_score += 1

    return {
        "q_global": q_score,
        "critical_unknown": critical_unknown,
    }

