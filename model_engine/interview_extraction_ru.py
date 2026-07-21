from model_engine.interview_logic_ru import build_intro_block_value


def extract_intro_blocks_from_text(message: str) -> dict:
    text = message.lower()

    extracted = {}

    for keyword in MAIN_ACTIVITY_KEYWORDS:
        if keyword in text:
            confidence = 0.5

            for pattern in DIRECT_MAIN_ACTIVITY_PATTERNS:
                if pattern in text:
                    confidence = 0.7
                    break

            extracted["main_activity"] = (
                build_intro_block_value(
                    value=message,
                    source="human_free_text_inferred",
                    confidence=confidence,
                )
            )

            break

    for keyword in PERSON_CONTEXT_KEYWORDS:
        if keyword in text:
            extracted["person_context"] = (
                build_intro_block_value(
                    value=message,
                    source="human_free_text_inferred",
                    confidence=0.7,
                )
            )
            break
    for keyword in EXPECTATIONS_FROM_RAY_KEYWORDS:
        if keyword in text:
            extracted["expectations_from_ray"] = (
                build_intro_block_value(
                    value=message,
                    source="human_free_text_inferred",
                    confidence=0.7,
                )
            )
            break
    for keyword in LIFE_PHASE_PROBLEM_KEYWORDS:
        if keyword in text:
            extracted["life_phase"] = (
                build_intro_block_value(
                    value="problem_or_difficult_phase",
                    source="human_free_text_inferred",
                    confidence=0.7,
                    notes=message,
                )
            )
            break

    if "life_phase" not in extracted:
        for keyword in LIFE_PHASE_POSITIVE_KEYWORDS:
            if keyword in text:
                extracted["life_phase"] = (
                    build_intro_block_value(
                        value="positive_or_stable_phase",
                        source="human_free_text_inferred",
                        confidence=0.7,
                        notes=message,
                    )
                )
                break
    for keyword in CURRENT_CONCERNS_KEYWORDS:
        if keyword in text:
            extracted["current_concerns"] = (
                build_intro_block_value(
                    value=message,
                    source="human_free_text_inferred",
                    confidence=0.7,
                )
            )
            break

    return extracted


def merge_intro_knowledge(
    current_knowledge: dict,
    extracted_blocks: dict,
) -> dict:
    merged = dict(current_knowledge)

    for block_id, block_value in extracted_blocks.items():
        if block_id not in merged:
            merged[block_id] = block_value
            continue

        old_confidence = merged[block_id].get("confidence", 0.0)
        new_confidence = block_value.get("confidence", 0.0)

        if new_confidence > old_confidence:
            merged[block_id] = block_value

    return merged

MAIN_ACTIVITY_KEYWORDS = [
    "работаю",
    "работа",
    "студент",
    "учусь",
    "учёба",
    "учеба",
    "проект",
    "стартап",
    "бизнес",
    "компания",
    "исследование",
]

DIRECT_MAIN_ACTIVITY_PATTERNS = [
    "я работаю",
    "я учусь",
    "я занимаюсь",
    "сейчас работаю",
    "сейчас учусь",
    "сейчас занимаюсь",
]

PERSON_CONTEXT_KEYWORDS = [
    "преподав",
    "учител",
    "врач",
    "студент",
    "исследоват",
    "учён",
    "учен",
    "инженер",
    "предпринимат",
    "мама",
    "отец",
    "родител",
]

EXPECTATIONS_FROM_RAY_KEYWORDS = [
    "хочу",
    "нужно",
    "помоги",
    "помощ",
    "разобраться",
    "понять",
    "совет",
    "поддерж",
    "отслеживать",
    "анализ",
]
LIFE_PHASE_PROBLEM_KEYWORDS = [
    "проблем",
    "тяжел",
    "тяжёл",
    "кризис",
    "сложно",
    "трудно",
    "застрял",
    "застряла",
    "не получается",
    "непонятно",
    "устал",
    "устала",
]

LIFE_PHASE_POSITIVE_KEYWORDS = [
    "радост",
    "хорош",
    "стабиль",
    "интересн",
    "развива",
    "получается",
    "спокойн",
]
CURRENT_CONCERNS_KEYWORDS = [
    "беспокоит",
    "переживаю",
    "тревож",
    "проблем",
    "сложно",
    "трудно",
    "не получается",
    "не знаю что делать",
    "давит",
    "мешает",
    "страшно",
    "устал",
    "устала",
]