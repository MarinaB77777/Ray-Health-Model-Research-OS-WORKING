from question_banks.QUESTION_BANK_RU import QUESTION_BANK_RU
from question_banks.QUESTION_BANK_EN import QUESTION_BANK_EN
from question_banks.QUESTION_BANK_ES import QUESTION_BANK_ES


QUESTION_BANKS = {
    "ru": QUESTION_BANK_RU,
    "en": QUESTION_BANK_EN,
    "es": QUESTION_BANK_ES,
}


def get_question_bank(lang: str):
    return QUESTION_BANKS.get(lang, QUESTION_BANK_RU)