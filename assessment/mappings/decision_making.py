from assessments.decision_mapping import (
    ASSESSMENT_ID,
    ASSESSMENT_NAME,
    QUESTION_CODES,
    TIME_REFERENCE,
    run_decision_mapping,
)


def build_decision_assessment(question_bank):
    questions = []

    for code in QUESTION_CODES:
        question = question_bank.get(code)
        if question is None:
            raise ValueError(f"Question not found in QUESTION_BANK_RU: {code}")
        questions.append(question)

    return {
        "assessment_id": ASSESSMENT_ID,
        "assessment_name": ASSESSMENT_NAME,
        "time_reference": TIME_REFERENCE,
        "questions": questions,
    }


def evaluate_decision_assessment(answers):
    return run_decision_mapping(answers)