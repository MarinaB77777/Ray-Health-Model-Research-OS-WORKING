INTRO_V1 = {
    "goal": "intro",
    "language": "ru",
    "purpose": (
        "Познакомиться с человеком и собрать стартовый контекст "
        "для дальнейшей персонализированной помощи."
    ),
    "does_not_do": [
        "не рассчитывает модель здоровья",
        "не строит прогноз",
        "не задаёт все вопросы банка",
    ],
    "information_blocks": [
        "person_context",
        "main_activity",
        "life_phase",
        "current_concerns",
        "communication_preferences",
        "aspirations",
        "decision_autonomy",
        "trust_network",
        "expectations_from_ray",
    ],
}
INTRO_INFORMATION_BLOCKS = {
    "person_context": {
        "description": (
            "Кто человек и как он сам себя описывает."
        ),
        "required": True,
    },

    "main_activity": {
        "description": (
            "Чем человек занимается сейчас и что занимает "
            "основную часть его времени."
        ),
        "required": True,
    },

    "life_phase": {
        "description": (
            "На каком жизненном этапе находится человек."
        ),
        "required": True,
    },

    "current_concerns": {
        "description": (
            "Есть ли сейчас проблемы или ситуации, "
            "которые беспокоят человека."
        ),
        "required": True,
    },

    "communication_preferences": {
        "description": (
            "Как человеку комфортнее общаться."
        ),
        "required": False,
    },

    "aspirations": {
        "description": (
            "О чём человек мечтает, чего хочет достичь "
            "или к чему стремится."
        ),
        "required": False,
    },

    "decision_autonomy": {
        "description": (
            "Насколько человек свободен в принятии решений."
        ),
        "required": False,
    },

    "trust_network": {
        "description": (
            "Есть ли люди, которым человек доверяет "
            "и на которых может опереться."
        ),
        "required": False,
    },

    "expectations_from_ray": {
        "description": (
            "Что человек ожидает от общения с Рэем."
        ),
        "required": True,
    },
}
INTRO_COMPLETION_RULES = {
    "person_context": {
        "complete_when": [
            "есть хотя бы одно описание роли человека",
            "понятно, как человек сам себя представляет",
        ],
        "ask_more_if": [
            "ответ слишком общий",
            "непонятно, относится ли описание к текущей жизни",
        ],
    },

    "main_activity": {
        "complete_when": [
            "понятно, чем человек занимается сейчас",
            "понятно, что занимает основную часть времени",
        ],
        "ask_more_if": [
            "деятельность неясна",
            "есть несколько направлений и непонятно главное",
        ],
    },

    "life_phase": {
        "complete_when": [
            "понятно, воспринимается ли текущий этап как стабильный, радостный, проблемный, переходный или кризисный",
        ],
        "ask_more_if": [
            "есть признаки нагрузки, но человек описывает всё как нормально",
            "есть противоречие между словами и ответами/сенсорами",
        ],
    },

    "current_concerns": {
        "complete_when": [
            "понятно, есть ли беспокоящая ситуация",
            "если есть проблема, понятно как давно она длится",
        ],
        "ask_more_if": [
            "проблема названа, но неясна длительность",
            "неясно, насколько она влияет на жизнь",
        ],
    },

    "communication_preferences": {
        "complete_when": [
            "понятен комфортный стиль общения",
        ],
        "ask_more_if": [
            "человек явно раздражается форматом общения",
            "ответы показывают, что текущий стиль не подходит",
        ],
    },

    "aspirations": {
        "complete_when": [
            "понятно, есть ли у человека цели, мечты или желаемое направление",
        ],
        "ask_more_if": [
            "есть сильная проблемная ситуация, но совсем неясно, чего человек хочет вместо неё",
        ],
    },

    "decision_autonomy": {
        "complete_when": [
            "понятно, насколько человек свободен выбирать решения",
        ],
        "ask_more_if": [
            "есть признаки внешних ограничений",
            "человек говорит о вариантах, но одновременно описывает невозможность выбора",
        ],
    },

    "trust_network": {
        "complete_when": [
            "понятно, есть ли хотя бы один человек, которому можно доверять",
        ],
        "ask_more_if": [
            "есть высокая нагрузка или риск, но непонятно, есть ли безопасная поддержка",
        ],
    },

    "expectations_from_ray": {
        "complete_when": [
            "понятно, зачем человек пришёл к Рэю",
            "понятно, какой помощи он ожидает",
        ],
        "ask_more_if": [
            "ожидания слишком общие",
            "человек просит помощи, но непонятно в чём именно",
        ],
    },
}
INTRO_ACQUISITION_RULES = {
    "general_principles": [
        "собирать информацию, а не задавать вопросы",
        "не спрашивать то, что уже известно",
        "использовать ответы человека прежде чем задавать новый вопрос",
        "один ответ может закрывать несколько информационных блоков",
        "уточнять только если информации недостаточно",
        "уточнять при противоречиях",
        "уточнять при расхождении с сенсорными данными",
    ],

    "clarification_triggers": [
        "ambiguity",
        "contradiction",
        "sensor_mismatch",
        "high_uncertainty",
        "missing_required_information",
    ],

    "stop_conditions": [
        "all_required_information_collected",
    ],
},
INTRO_COMMUNICATION_STYLES = {
    "friendly": {
        "description": "тёплый, живой, поддерживающий стиль",
        "use_when": [
            "человек открыт к мягкому общению",
            "важно снизить напряжение",
        ],
    },

    "analytical": {
        "description": "структурный, спокойный, исследовательский стиль",
        "use_when": [
            "человек предпочитает точность и логику",
            "важно объяснять зачем задаётся вопрос",
        ],
    },

    "compact": {
        "description": "короткий стиль без лишних пояснений",
        "use_when": [
            "человек устал",
            "человек просит короче",
            "нужно снизить нагрузку",
        ],
    },

    "supportive": {
        "description": "бережный стиль при напряжении или уязвимости",
        "use_when": [
            "есть признаки сильного стресса",
            "есть признаки растерянности",
            "человеку трудно начать говорить",
        ],
    },
},
INTRO_FLOW = {
    "goal": "intro",
    "version": 1,

    "required_blocks": [
        "person_context",
        "main_activity",
        "life_phase",
        "current_concerns",
        "expectations_from_ray",
    ],

    "optional_blocks": [
        "communication_preferences",
        "aspirations",
        "decision_autonomy",
        "trust_network",
    ],

    "block_priority": [
        "person_context",
        "main_activity",
        "expectations_from_ray",
        "life_phase",
        "current_concerns",
        "communication_preferences",
        "aspirations",
        "decision_autonomy",
        "trust_network",
    ],

    "default_style": "friendly",

    "allowed_styles": [
        "friendly",
        "analytical",
        "compact",
        "supportive",
    ],
}
def get_missing_intro_blocks(collected_blocks: dict) -> list:
    missing = []

    for block_id in INTRO_FLOW["block_priority"]:
        block_value = collected_blocks.get(block_id)

        if is_intro_block_complete(block_value):
            continue

        if block_id in INTRO_FLOW["required_blocks"]:
            missing.append(block_id)

    return missing


def choose_next_intro_block(collected_blocks: dict) -> str | None:
    missing_blocks = get_missing_intro_blocks(collected_blocks)

    if not missing_blocks:
        return None

    return missing_blocks[0]

def get_intro_status(collected_blocks: dict) -> dict:
    missing_required = get_missing_intro_blocks(collected_blocks)
    complete = len(missing_required) == 0

    return {
        "goal": "intro",
        "complete": complete,
        "missing_required": missing_required,
        "next_block": choose_next_intro_block(collected_blocks),
    }

INTRO_INFORMATION_SOURCES = {
    "human_free_text": {
        "description": "Свободный рассказ человека.",
        "can_fill_blocks": [
            "person_context",
            "main_activity",
            "life_phase",
            "current_concerns",
            "communication_preferences",
            "aspirations",
            "decision_autonomy",
            "trust_network",
            "expectations_from_ray",
        ],
    },

    "direct_question": {
        "description": "Прямой вопрос Рэя.",
        "can_fill_blocks": [
            "person_context",
            "main_activity",
            "life_phase",
            "current_concerns",
            "communication_preferences",
            "aspirations",
            "decision_autonomy",
            "trust_network",
            "expectations_from_ray",
        ],
    },

    "history": {
        "description": "Ранее подтверждённая информация.",
        "can_fill_blocks": [
            "person_context",
            "main_activity",
            "communication_preferences",
            "aspirations",
            "trust_network",
        ],
    },

    "sensors": {
        "description": "Сенсорные данные. Не являются истиной, используются только как источник сигналов.",
        "can_fill_blocks": [
            "life_phase",
            "current_concerns",
        ],
        "requires_validation": True,
    },
}
INTRO_CLARIFICATION_RULES = {
    "ambiguity": {
        "description": (
            "Информация получена, но её можно трактовать "
            "несколькими способами."
        ),
        "action": "ask_clarifying_question",
    },

    "contradiction": {
        "description": (
            "Новая информация противоречит ранее "
            "полученной информации."
        ),
        "action": "ask_clarifying_question",
    },

    "sensor_mismatch": {
        "description": (
            "Сенсорные данные расходятся с тем, "
            "что сообщает человек."
        ),
        "action": "ask_clarifying_question",
    },

    "high_uncertainty": {
        "description": (
            "Информации недостаточно для уверенного "
            "заполнения блока."
        ),
        "action": "ask_clarifying_question",
    },

    "multiple_possible_blocks": {
        "description": (
            "Ответ может относиться сразу к нескольким "
            "информационным блокам."
        ),
        "action": "extract_then_confirm",
    },
}


INTRO_BLOCK_DATA_MODEL = {
    "value": None,
    "confidence": 0.0,
    "source": None,
    "confirmed": False,
    "updated_at": None,
    "notes": None,
}

INTRO_CONFIDENCE_RULES = {
    "human_direct_answer": {
        "default_confidence": 0.8,
        "requires_confirmation": False,
    },

    "human_free_text_inferred": {
        "default_confidence": 0.5,
        "requires_confirmation": True,
    },

    "history": {
        "default_confidence": 0.6,
        "requires_confirmation": True,
    },

    "sensor_signal": {
        "default_confidence": 0.4,
        "requires_confirmation": True,
        "note": "Сенсорный сигнал не является истиной и требует сверки с человеком.",
    },

    "contradictory_data": {
        "default_confidence": 0.2,
        "requires_confirmation": True,
    },
}

def build_intro_block_value(
    value,
    source: str,
    confidence: float = None,
    confirmed: bool = False,
    notes: str | None = None,
) -> dict:
    rule = INTRO_CONFIDENCE_RULES.get(source, {})
    default_confidence = rule.get("default_confidence", 0.0)

    return {
        "value": value,
        "confidence": (
            confidence
            if confidence is not None
            else default_confidence
        ),
        "source": source,
        "confirmed": confirmed,
        "updated_at": None,
        "notes": notes,
    }


def is_intro_block_complete(block_value) -> bool:
    if not block_value:
        return False

    if isinstance(block_value, bool):
        return block_value

    if not isinstance(block_value, dict):
        return True

    value = block_value.get("value")
    confidence = block_value.get("confidence", 0.0)

    return value is not None and confidence >= 0.6

def get_intro_block_status(block_id: str, collected_blocks: dict) -> dict:
    block_value = collected_blocks.get(block_id)

    if block_value is None:
        return {
            "block_id": block_id,
            "complete": False,
            "reason": "missing",
            "confidence": 0.0,
            "needs_clarification": True,
        }

    if isinstance(block_value, bool):
        return {
            "block_id": block_id,
            "complete": block_value,
            "reason": "boolean_status",
            "confidence": 1.0 if block_value else 0.0,
            "needs_clarification": not block_value,
        }

    if not isinstance(block_value, dict):
        return {
            "block_id": block_id,
            "complete": True,
            "reason": "plain_value",
            "confidence": 1.0,
            "needs_clarification": False,
        }

    value = block_value.get("value")
    confidence = block_value.get("confidence", 0.0)

    if value is None:
        return {
            "block_id": block_id,
            "complete": False,
            "reason": "empty_value",
            "confidence": confidence,
            "needs_clarification": True,
        }

    if confidence < 0.6:
        return {
            "block_id": block_id,
            "complete": False,
            "reason": "low_confidence",
            "confidence": confidence,
            "needs_clarification": True,
        }

    return {
        "block_id": block_id,
        "complete": True,
        "reason": "sufficient_information",
        "confidence": confidence,
        "needs_clarification": False,
    }

def get_all_intro_block_statuses(collected_blocks: dict) -> dict:
    statuses = {}

    for block_id in INTRO_FLOW["block_priority"]:
        statuses[block_id] = get_intro_block_status(
            block_id=block_id,
            collected_blocks=collected_blocks,
        )

    return statuses

INTERVIEW_ARCHITECTURE_RULES = [
    "Knowledge != Status",
    "Knowledge stores what is known.",
    "Status stores whether enough is known for the current interview goal.",
    "A completed block does not mean the system knows everything about that area.",
    "Knowledge may expand later without changing the fact that the intro block was complete.",
]

# INTRO_V1 MVP checkpoint:
# Required intro blocks:
# - person_context
# - main_activity
# - expectations_from_ray
# - life_phase
# - current_concerns
#
# Current MVP extraction can complete INTRO_V1 from free-text dialogue.
# Optional blocks are intentionally not required for intro completion.