from model_engine.questionnaire_vnext import VNEXT_SIGNAL_GROUPS


def to_num(value):
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def mean(values: list):
    if not values:
        return None

    return sum(values) / len(values)


def cap_0_5(value):
    if value is None:
        return None

    return max(0, min(5, value))


def compute_signal_group(answers: dict, config: dict):
    values = []

    for question_id in config.get("questions", []):
        value = to_num(answers.get(question_id))

        if value is not None:
            values.append(value)

    if config.get("type") == "single":
        score = values[0] if values else None
    else:
        score = mean(values)

    return {
        "score": cap_0_5(score),
        "valid_count": len(values),
        "required_count": len(config.get("questions", [])),
        "coverage": round(
            len(values) / len(config.get("questions", [])),
            3
        ) if config.get("questions") else 0,
    }


def compute_vnext_signals(answers: dict):
    signals = {}

    for signal_name, config in VNEXT_SIGNAL_GROUPS.items():
        signals[signal_name] = compute_signal_group(
            answers=answers,
            config=config,
        )

    return {
        "signals": signals,
    }