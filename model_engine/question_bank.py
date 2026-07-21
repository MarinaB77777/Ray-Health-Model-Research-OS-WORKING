from question_banks.QUESTION_BANK_RU import QUESTION_BANK_RU


QUESTION_BANK = QUESTION_BANK_RU


def get_question(code: str):
    return QUESTION_BANK.get(code)


def has_question(code: str) -> bool:
    return code in QUESTION_BANK