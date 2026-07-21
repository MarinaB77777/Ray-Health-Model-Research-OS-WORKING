from model_engine.question_banks.ru import QUESTION_BANK_RU


QUESTION_BANKS = {
    "ru": QUESTION_BANK_RU,
}


def get_question(
    question_code: str,
    lang: str = "ru",
):
    bank = QUESTION_BANKS.get(lang)

    if bank is None:
        bank = QUESTION_BANKS["ru"]

    return bank.get(question_code)


def question_exists(
    question_code: str,
    lang: str = "ru",
):
    return get_question(
        question_code=question_code,
        lang=lang,
    ) is not None