from model_engine.assessment_profiles import ASSESSMENT_PROFILES
from model_engine.question_bank import get_question


def get_assessment_profile(profile_id: str) -> dict:
    profile = ASSESSMENT_PROFILES.get(profile_id)

    if profile is None:
        raise ValueError(f"Unknown assessment profile: {profile_id}")

    return profile


def collect_profile_question_codes(profile: dict) -> list[str]:
    codes = []

    for block_group in [
        "legacy_formula_blocks",
        "new_mechanism_blocks",
    ]:
        for block in profile.get(block_group, {}).values():
            for code in block.get("questions", []):
                if code not in codes:
                    codes.append(code)

    for code in profile.get("critical_gate", []):
        if code not in codes:
            codes.append(code)

    return codes


def get_profile_questions(
    profile_id: str,
    lang: str = "ru",
) -> list[dict]:
    profile = get_assessment_profile(profile_id)
    question_codes = collect_profile_question_codes(profile)

    questions = []

    for code in question_codes:
        question = get_question(code, lang=lang)

        if question is None:
            questions.append({
                "code": code,
                "missing": True,
            })
            continue

        questions.append(question)

    return questions
