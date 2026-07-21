import importlib.util
from pathlib import Path


def get_question_bank_file_info(bank_id: str, lang: str):
    variable_name = f"QUESTION_BANK_{lang.upper()}"

    if bank_id == "health_model":
        filename = {
            "ru": "QUESTION_BANK_RU.py",
            "en": "QUESTION_BANK_EN.py",
            "es": "QUESTION_BANK_ES.py",
        }[lang]

        return Path("question_banks") / filename, variable_name

    if bank_id == "decision_under_uncertainty":
        filename = {
            "ru": "decision_under_uncertainty_questions_ru.py",
            "en": "decision_under_uncertainty_questions_en.py",
            "es": "decision_under_uncertainty_questions_es.py",
        }[lang]

        return (
            Path("assessment/studies/decision_under_uncertainty") / filename,
            variable_name,
        )

    filename = {
        "ru": "QUESTION_BANK_RU.py",
        "en": "QUESTION_BANK_EN.py",
        "es": "QUESTION_BANK_ES.py",
    }[lang]

    return Path("question_banks") / bank_id / filename, variable_name


def load_question_bank(bank_id: str, lang: str = "ru") -> dict:
    path, variable_name = get_question_bank_file_info(bank_id, lang)

    if not path.exists():
        return {}

    module_name = (
        "dynamic_question_bank_"
        + bank_id
        + "_"
        + lang
        + "_"
        + str(abs(hash(str(path))))
    )

    spec = importlib.util.spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        return {}

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    bank = getattr(module, variable_name, None)

    if not isinstance(bank, dict):
        return {}

    return bank
