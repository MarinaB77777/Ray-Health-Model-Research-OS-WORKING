from pilot_session.schemas import ParticipantSession


def _localize_text(text: dict | str | None, lang: str = "ru") -> str:
    if text is None:
        return ""

    if isinstance(text, str):
        return text

    return (
        text.get(lang)
        or text.get("ru")
        or text.get("en")
        or text.get("es")
        or ""
    )


def _answer_instruction(variable_code: str, lang: str = "ru") -> str:
    if variable_code == "PEP2":
        instructions = {
            "ru": "Ответь числом от 0 до 4.",
            "en": "Answer with a number from 0 to 4.",
            "es": "Responde con un número del 0 al 4.",
        }
        return instructions.get(lang, instructions["ru"])

    instructions = {
        "ru": "Ответь числом от 0 до 5.",
        "en": "Answer with a number from 0 to 5.",
        "es": "Responde con un número del 0 al 5.",
    }
    return instructions.get(lang, instructions["ru"])

def _format_question_meta(question_meta: dict, lang: str = "ru") -> str:
    text = (
        question_meta.get("prompt")
        or question_meta.get("text")
        or ""
    )

    options = question_meta.get("options", [])

    if not options:
        return text

    lines = []

    if isinstance(options, list):
        for option in options:
            value = option.get("value")
            option_text = option.get("text", "")
            lines.append(f"{value} — {option_text}")

    elif isinstance(options, dict):
        for key in sorted(options.keys()):
            lines.append(f"{key} — {options[key]}")

    return text + "\n\n" + "\n".join(lines)


def build_ray_next_question(
    session: ParticipantSession,
    lang: str = "ru",
) -> dict:
    public_output = session.public_output or {}

    questions_block = public_output.get("questions", {})
    next_questions = questions_block.get("next_questions", [])

    if not next_questions:
        return {
            "status": "complete",
            "message": (
                "Сейчас дополнительных вопросов нет. "
                "Можно показать текущий результат."
            ),
            "variable_code": None,
            "expected_response_target": None,
        }

    question = next_questions[0]
    variable_code = question.get("variable_code")
    question_meta = question.get("question_meta")

    if isinstance(question_meta, dict):
        question_text = _format_question_meta(
            question_meta=question_meta,
            lang=lang,
        )
    else:
        question_text = _localize_text(
            question.get("text"),
            lang=lang,
        )

    prefixes = {
        "ru": "Чтобы лучше понять ситуацию, мне нужно уточнить один момент.",
        "en": "To understand the situation better, I need to clarify one point.",
        "es": "Para entender mejor la situación, necesito aclarar un punto.",
    }

    return {
        "status": "question",
        "message": (
            f"{prefixes.get(lang, prefixes['ru'])}\n\n"
            f"{question_text}"
        ),
        "variable_code": variable_code,
        "expected_response_target": (
            f"answers.{variable_code}"
            if variable_code
            else None
        ),
    }
def parse_numeric_reply(message: str):
    text = str(message).strip()

    if text == "":
        return None

    try:
        value = int(text)
    except ValueError:
        return None

    return value


def build_ray_chat_response(
    session: ParticipantSession,
    message: str,
    lang: str = "ru",
) -> dict:
    next_question = build_ray_next_question(
        session=session,
        lang=lang,
    )

    return {
        "status": next_question.get("status"),
        "message": next_question.get("message"),
        "awaiting_variable_code": next_question.get("variable_code"),
        "expected_response_target": next_question.get(
            "expected_response_target"
        ),
        "received_message": message,
    }