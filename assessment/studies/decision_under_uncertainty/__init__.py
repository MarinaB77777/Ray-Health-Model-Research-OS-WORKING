from .decision_under_uncertainty_questions_ru import QUESTION_BANK_RU
from .decision_under_uncertainty_questions_en import QUESTION_BANK_EN
from .decision_under_uncertainty_questions_es import QUESTION_BANK_ES


def _apply_defaults(bank: dict) -> dict:
    for question in bank.values():
        question.setdefault("is_required", True)
        question.setdefault("can_go_back", False)
        question.setdefault("save_answer", True)
        question.setdefault("display_type", "buttons")
    return bank


QUESTION_BANK = {
    "ru": _apply_defaults(QUESTION_BANK_RU),
    "en": _apply_defaults(QUESTION_BANK_EN),
    "es": _apply_defaults(QUESTION_BANK_ES),
}
