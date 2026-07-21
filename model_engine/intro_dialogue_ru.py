INTRO_TRANSITION = (
    "Спасибо.\n\n"
    "Хотел бы тебе помочь. "
    "Чем лучше я понимаю человека и его ситуацию, "
    "тем точнее могу задавать вопросы и тем полезнее могу быть."
)


INTRO_BLOCK_PROMPTS_RU = {
    "person_context": (
        "Расскажи немного о себе: кто ты и чем сейчас живёшь?"
    ),
    "main_activity": (
        "Чем ты сейчас в основном занимаешься? Работа, учёба, проект, семья или что-то другое?"
    ),
    "expectations_from_ray": (
        "Что ты хочешь получить от общения со мной? Разобраться в состоянии, принять решение, отследить изменения или что-то другое?"
    ),
    "life_phase": (
        "Какой сейчас у тебя этап жизни — скорее спокойный, радостный, переходный или проблемный?"
    ),
    "current_concerns": (
        "Есть ли сейчас что-то, что тебя особенно беспокоит?"
    ),
}


def build_intro_question(next_block: str) -> str:
    return INTRO_BLOCK_PROMPTS_RU.get(
        next_block,
        "Расскажи чуть подробнее, чтобы я лучше понял контекст.",
    )


def build_intro_dialogue_reply(
    status: dict,
    turn_index: int = 0,
) -> dict:
    if status.get("complete"):
        return {
            "status": "complete",
            "message": (
                "Спасибо. Для первого знакомства этого достаточно. "
                "Я уже понимаю базовый контекст и смогу дальше задавать вопросы точнее."
            ),
            "next_block": None,
        }

    next_block = status.get("next_block")
    question = build_intro_question(next_block)

    if turn_index == 0:
        message = (
            f"{INTRO_TRANSITION}\n\n"
            f"{question}"
        )
    else:
        message = question

    return {
        "status": "question",
        "message": message,
        "next_block": next_block,
    }

