from assessment.measurement.scale_registry import (
    get_questionnaire_scale_components,
    get_scale_definition,
    normalize_scale_id,
)


QUESTIONNAIRE_COMPONENTS_SCHEMA_VERSION = "questionnaire-components-1"


def _component(
    component_id: str,
    title: str,
    component_type: str,
    **metadata,
) -> dict:
    return {
        "id": component_id,
        "title": title,
        "component_type": component_type,
        "schema_version": QUESTIONNAIRE_COMPONENTS_SCHEMA_VERSION,
        **metadata,
    }


QUESTION_TYPES = {
    "single_choice": _component(
        "single_choice",
        "Single choice",
        "question_type",
        description="Respondent selects exactly one option from a predefined list.",
        constructor_hint="Use for radio buttons, dropdowns, categories, Likert-type items, routing choices, and ordered answer options.",
        requires_options=True,
        supports_branching=True,
        compatible_scale_types=["nominal", "ordinal", "binary", "likert"],
    ),
    "multiple_choice": _component(
        "multiple_choice",
        "Multiple choice",
        "question_type",
        description="Respondent may select more than one option from a predefined list.",
        constructor_hint="Use when several categories may be true at the same time. Do not use for ordered severity unless multiple selections are scientifically intended.",
        requires_options=True,
        supports_branching=True,
        compatible_scale_types=["nominal"],
    ),
    "numeric": _component(
        "numeric",
        "Numeric input",
        "question_type",
        description="Respondent enters a numeric value.",
        constructor_hint="Use for measurable quantities, counts, age, duration, frequency, money, or any value with numeric meaning.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["interval", "ratio", "continuous", "duration"],
    ),
    "slider": _component(
        "slider",
        "Slider",
        "question_type",
        description="Respondent selects a value on a continuous or stepwise numeric range.",
        constructor_hint="Use when visual positioning on a range is important. Define min, max and step.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["interval", "ratio", "continuous", "visual_analog"],
    ),
    "visual_analog_scale": _component(
        "visual_analog_scale",
        "Visual analog scale",
        "question_type",
        description="Respondent marks a position on a continuous visual line.",
        constructor_hint="Use for subjective intensity when a continuous representation is intended, such as pain, fatigue, tension or confidence.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["visual_analog"],
    ),
    "text": _component(
        "text",
        "Free text",
        "question_type",
        description="Respondent writes an unrestricted text answer.",
        constructor_hint="Use for explanations, comments, context, or qualitative data. Not directly numeric unless coded later.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["text"],
    ),
    "date": _component(
        "date",
        "Date",
        "question_type",
        description="Respondent provides a calendar date.",
        constructor_hint="Use for dates of events, start dates, deadlines, or temporal anchors.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["date"],
    ),
    "time": _component(
        "time",
        "Time",
        "question_type",
        description="Respondent provides a time of day.",
        constructor_hint="Use for time points within a day. Use duration/numeric for elapsed time.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["time"],
    ),
    "duration": _component(
        "duration",
        "Duration",
        "question_type",
        description="Respondent provides elapsed time or length of time.",
        constructor_hint="Use for sleep duration, waiting time, exposure duration, work time, or recovery time.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["duration", "ratio"],
    ),
    "file": _component(
        "file",
        "File upload",
        "question_type",
        description="Respondent uploads or references a file.",
        constructor_hint="Use for documents, images, attachments, or external measurement files. The answer is a file reference, not a psychometric score.",
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=["file"],
    ),
    "ranking": _component(
        "ranking",
        "Ranking",
        "question_type",
        description="Respondent orders items by priority, preference, importance, or sequence.",
        constructor_hint="Use when relative order matters more than absolute distance between items.",
        requires_options=True,
        supports_branching=False,
        compatible_scale_types=["ordinal"],
    ),
}

# Canonical response-value structures used by the new constructor.
# QUESTION_TYPES remains unchanged for backward compatibility.
RESPONSE_TYPES = {
    "single_choice": _component(
        "single_choice",
        "Single selected value",
        "response_type",
        description=(
            "The response contains exactly one selected value "
            "from a predefined set of options."
        ),
        requires_options=True,
        supports_branching=True,
        compatible_scale_types=[
            "nominal",
            "ordinal",
            "binary",
            "likert",
        ],
        compatible_presentation_types=[
            "radio",
            "dropdown",
            "cards",
        ],
    ),
    "multiple_choice": _component(
        "multiple_choice",
        "Multiple selected values",
        "response_type",
        description=(
            "The response contains zero, one, or several selected "
            "values from a predefined set of options."
        ),
        requires_options=True,
        supports_branching=True,
        compatible_scale_types=[
            "nominal",
        ],
        compatible_presentation_types=[
            "checkbox",
            "cards",
        ],
    ),
    "numeric": _component(
        "numeric",
        "Numeric value",
        "response_type",
        description=(
            "The response contains one numeric value."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "interval",
            "ratio",
            "continuous",
            "duration",
            "visual_analog",
        ],
        compatible_presentation_types=[
            "number_input",
            "slider",
            "visual_analog_line",
        ],
    ),
    "text": _component(
        "text",
        "Text value",
        "response_type",
        description=(
            "The response contains free-form text."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "text",
        ],
        compatible_presentation_types=[
            "text_input",
        ],
    ),
    "date": _component(
        "date",
        "Date value",
        "response_type",
        description=(
            "The response contains a calendar date."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "date",
        ],
        compatible_presentation_types=[
            "date_input",
        ],
    ),
    "time": _component(
        "time",
        "Time value",
        "response_type",
        description=(
            "The response contains a time of day."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "time",
        ],
        compatible_presentation_types=[
            "time_input",
        ],
    ),
    "duration": _component(
        "duration",
        "Duration value",
        "response_type",
        description=(
            "The response contains an elapsed-time value "
            "with an explicit unit."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "duration",
            "ratio",
        ],
        compatible_presentation_types=[
            "duration_input",
            "number_input",
        ],
    ),
    "file": _component(
        "file",
        "File reference",
        "response_type",
        description=(
            "The response contains a stored file reference "
            "or upload identifier."
        ),
        requires_options=False,
        supports_branching=True,
        compatible_scale_types=[
            "file",
        ],
        compatible_presentation_types=[
            "file_input",
        ],
    ),
    "ranking": _component(
        "ranking",
        "Ordered list of values",
        "response_type",
        description=(
            "The response contains an ordered sequence of predefined items."
        ),
        requires_options=True,
        supports_branching=False,
        compatible_scale_types=[
            "ordinal",
        ],
        compatible_presentation_types=[
            "ranking",
        ],
    ),
}

SCALE_TYPES = get_questionnaire_scale_components()


PRESENTATION_TYPES = {
    "radio": _component(
        "radio",
        "Radio buttons",
        "presentation_type",
    ),
    "dropdown": _component(
        "dropdown",
        "Dropdown",
        "presentation_type",
    ),
    "cards": _component(
        "cards",
        "Cards",
        "presentation_type",
    ),
    "checkbox": _component(
        "checkbox",
        "Checkboxes",
        "presentation_type",
    ),
    "slider": _component(
        "slider",
        "Slider UI",
        "presentation_type",
    ),
    "visual_analog_line": _component(
        "visual_analog_line",
        "Visual analog line",
        "presentation_type",
    ),
    "text_input": _component(
        "text_input",
        "Text input",
        "presentation_type",
    ),
    "number_input": _component(
        "number_input",
        "Number input",
        "presentation_type",
    ),
    "date_input": _component(
        "date_input",
        "Date input",
        "presentation_type",
    ),
    "time_input": _component(
        "time_input",
        "Time input",
        "presentation_type",
    ),
    "duration_input": _component(
        "duration_input",
        "Duration input",
        "presentation_type",
    ),
    "file_input": _component(
        "file_input",
        "File input",
        "presentation_type",
    ),
    "ranking": _component(
        "ranking",
        "Ranking interface",
        "presentation_type",
    ),
}


QUESTION_TYPE_GUIDANCE = {
    "single_choice": {
        "title": {"ru": "Один вариант", "en": "Single choice", "es": "Una opción"},
        "description": {
            "ru": "Человек выбирает ровно один вариант из заранее заданного списка.",
            "en": "The participant selects exactly one predefined option.",
            "es": "La persona selecciona exactamente una opción predefinida.",
        },
        "visual_kind": "radio",
    },
    "multiple_choice": {
        "title": {"ru": "Несколько вариантов", "en": "Multiple choice", "es": "Varias opciones"},
        "description": {
            "ru": "Можно выбрать несколько независимых вариантов; это не шкала выраженности.",
            "en": "Several independent options may be selected; this is not a severity scale.",
            "es": "Se pueden elegir varias opciones independientes; no es una escala de intensidad.",
        },
        "visual_kind": "checkbox",
    },
    "numeric": {
        "title": {"ru": "Число", "en": "Numeric input", "es": "Número"},
        "description": {
            "ru": "Ввод одного числа с заданной единицей, точностью и допустимым диапазоном.",
            "en": "One number with an explicit unit, precision, and allowed range.",
            "es": "Un número con unidad, precisión y rango permitido explícitos.",
        },
        "visual_kind": "number",
    },
    "slider": {
        "title": {"ru": "Ползунок", "en": "Slider", "es": "Deslizador"},
        "description": {
            "ru": "Выбор значения на видимом диапазоне с минимумом, максимумом и шагом.",
            "en": "A value is selected on a visible range with minimum, maximum, and step.",
            "es": "Se selecciona un valor en un rango visible con mínimo, máximo y paso.",
        },
        "visual_kind": "slider",
    },
    "visual_analog_scale": {
        "title": {"ru": "Визуальная аналоговая шкала", "en": "Visual analog scale", "es": "Escala visual analógica"},
        "description": {
            "ru": "Отметка положения на непрерывной линии; метрические свойства требуют обоснования инструмента.",
            "en": "A position on a continuous line; metric properties require instrument-specific evidence.",
            "es": "Una posición en una línea continua; las propiedades métricas requieren evidencia del instrumento.",
        },
        "visual_kind": "visual_analog",
    },
    "text": {
        "title": {"ru": "Свободный текст", "en": "Free text", "es": "Texto libre"},
        "description": {
            "ru": "Текстовый ответ; числом он становится только после отдельного кодирования.",
            "en": "A text response; it becomes numeric only through a separate coding procedure.",
            "es": "Una respuesta textual; solo se vuelve numérica mediante una codificación separada.",
        },
        "visual_kind": "text",
    },
    "date": {
        "title": {"ru": "Дата", "en": "Date", "es": "Fecha"},
        "description": {"ru": "Календарная дата события.", "en": "A calendar date for an event.", "es": "Una fecha calendario de un evento."},
        "visual_kind": "date",
    },
    "time": {
        "title": {"ru": "Время суток", "en": "Time of day", "es": "Hora del día"},
        "description": {"ru": "Время на часах, а не длительность.", "en": "Clock time, not elapsed duration.", "es": "Hora del reloj, no duración transcurrida."},
        "visual_kind": "time",
    },
    "duration": {
        "title": {"ru": "Длительность", "en": "Duration", "es": "Duración"},
        "description": {"ru": "Прошедшее время с обязательной единицей измерения.", "en": "Elapsed time with an explicit unit.", "es": "Tiempo transcurrido con una unidad explícita."},
        "visual_kind": "duration",
    },
    "file": {
        "title": {"ru": "Файл", "en": "File", "es": "Archivo"},
        "description": {"ru": "Ссылка на загруженный файл; содержимое анализируется отдельным процессом.", "en": "A stored-file reference; its content is analysed separately.", "es": "Una referencia a un archivo; su contenido se analiza por separado."},
        "visual_kind": "file",
    },
    "ranking": {
        "title": {"ru": "Ранжирование", "en": "Ranking", "es": "Ordenación"},
        "description": {"ru": "Упорядочивание объектов; расстояния между местами не считаются равными.", "en": "Items are ordered; distances between ranks are not assumed equal.", "es": "Los elementos se ordenan; no se suponen distancias iguales entre rangos."},
        "visual_kind": "ranking",
    },
}


RESPONSE_TYPE_GUIDANCE = {
    "single_choice": ("Одно выбранное значение", "Single selected value", "Un valor seleccionado", "scalar_category"),
    "multiple_choice": ("Набор выбранных значений", "Set of selected values", "Conjunto de valores", "category_set"),
    "numeric": ("Одно число", "One numeric value", "Un valor numérico", "number"),
    "text": ("Текст", "Text value", "Texto", "text"),
    "date": ("Календарная дата", "Calendar date", "Fecha calendario", "date"),
    "time": ("Время суток", "Time of day", "Hora del día", "time_of_day"),
    "duration": ("Число и единица времени", "Value and time unit", "Valor y unidad de tiempo", "duration"),
    "file": ("Ссылка на файл", "File reference", "Referencia de archivo", "file_reference"),
    "ranking": ("Упорядоченный список", "Ordered list", "Lista ordenada", "ordered_sequence"),
}


for _code, _guidance in QUESTION_TYPE_GUIDANCE.items():
    QUESTION_TYPES[_code]["localized_title"] = _guidance["title"]
    QUESTION_TYPES[_code]["localized_description"] = _guidance["description"]
    QUESTION_TYPES[_code]["visual_kind"] = _guidance["visual_kind"]

for _code, (_ru, _en, _es, _shape) in RESPONSE_TYPE_GUIDANCE.items():
    RESPONSE_TYPES[_code]["localized_title"] = {"ru": _ru, "en": _en, "es": _es}
    RESPONSE_TYPES[_code]["value_shape"] = _shape

PRESENTATION_TYPE_TITLES = {
    "radio": ("Круглые переключатели", "Radio buttons", "Botones de opción"),
    "dropdown": ("Раскрывающийся список", "Dropdown", "Lista desplegable"),
    "cards": ("Карточки вариантов", "Option cards", "Tarjetas de opciones"),
    "checkbox": ("Флажки для нескольких вариантов", "Checkboxes", "Casillas"),
    "slider": ("Ползунок", "Slider", "Deslizador"),
    "visual_analog_line": ("Непрерывная линия", "Visual analog line", "Línea visual analógica"),
    "text_input": ("Поле текста", "Text field", "Campo de texto"),
    "number_input": ("Поле числа", "Number field", "Campo numérico"),
    "date_input": ("Выбор даты", "Date picker", "Selector de fecha"),
    "time_input": ("Выбор времени", "Time picker", "Selector de hora"),
    "duration_input": ("Длительность и единица", "Duration and unit", "Duración y unidad"),
    "file_input": ("Загрузка файла", "File upload", "Carga de archivo"),
    "ranking": ("Перетаскиваемый порядок", "Sortable ranking", "Ordenación interactiva"),
}

for _code, (_ru, _en, _es) in PRESENTATION_TYPE_TITLES.items():
    PRESENTATION_TYPES[_code]["localized_title"] = {"ru": _ru, "en": _en, "es": _es}


EXPECTED_RESPONSE_TYPES_BY_QUESTION = {
    "single_choice": {"single_choice"},
    "multiple_choice": {"multiple_choice"},
    "numeric": {"numeric"},
    "slider": {"numeric"},
    "visual_analog_scale": {"numeric"},
    "text": {"text"},
    "date": {"date"},
    "time": {"time"},
    "duration": {"duration", "numeric"},
    "file": {"file"},
    "ranking": {"ranking"},
}

VALIDATION_COMPONENTS = {
    "required": _component("required", "Required", "validation_component"),
    "optional": _component("optional", "Optional", "validation_component"),
    "min_value": _component("min_value", "Minimum value", "validation_component"),
    "max_value": _component("max_value", "Maximum value", "validation_component"),
    "min_selections": _component(
        "min_selections",
        "Minimum selections",
        "validation_component",
    ),
    "max_selections": _component(
        "max_selections",
        "Maximum selections",
        "validation_component",
    ),
}


TRANSITION_TYPES = {
    "sequential": _component("sequential", "Sequential", "transition_type"),
    "conditional": _component("conditional", "Conditional", "transition_type"),
    "terminal": _component("terminal", "Terminal", "transition_type"),
}


LEGACY_QUESTION_TYPE_ALIASES = {
    "single_select": "single_choice",
    "multi_select": "multiple_choice",
    "free_text": "text",
    "long_text": "text",
    "number": "numeric",
    "scale": "slider",
}

LEGACY_RESPONSE_TYPE_ALIASES = {
    **LEGACY_QUESTION_TYPE_ALIASES,
    "scale": "numeric",
    "slider": "numeric",
    "visual_analog_scale": "numeric",
    "integer": "numeric",
    "float": "numeric",
    "number_input": "numeric",
    "file_upload": "file",
}

def normalize_question_type_id(question_type_id: str | None) -> str | None:
    if question_type_id is None:
        return None

    return LEGACY_QUESTION_TYPE_ALIASES.get(
        question_type_id,
        question_type_id,
    )


def normalize_response_type_id(response_type_id: str | None) -> str | None:
    if response_type_id is None:
        return None

    return LEGACY_RESPONSE_TYPE_ALIASES.get(
        response_type_id,
        response_type_id,
    )


def normalize_scale_type_id(scale_type_id) -> str | None:
    return normalize_scale_id(scale_type_id)


def get_question_type(question_type_id: str) -> dict | None:
    return QUESTION_TYPES.get(normalize_question_type_id(question_type_id))

def get_response_type(response_type_id: str) -> dict | None:
    return RESPONSE_TYPES.get(normalize_response_type_id(response_type_id))

def get_scale_type(scale_type_id: str) -> dict | None:
    return SCALE_TYPES.get(normalize_scale_type_id(scale_type_id))


def get_presentation_type(presentation_type_id: str) -> dict | None:
    return PRESENTATION_TYPES.get(presentation_type_id)


def get_transition_type(transition_type_id: str) -> dict | None:
    return TRANSITION_TYPES.get(transition_type_id)


def list_question_types() -> list[dict]:
    return list(QUESTION_TYPES.values())

def list_response_types() -> list[dict]:
    return list(RESPONSE_TYPES.values())

def list_scale_types() -> list[dict]:
    return list(SCALE_TYPES.values())


def list_presentation_types() -> list[dict]:
    return list(PRESENTATION_TYPES.values())


def list_validation_components() -> list[dict]:
    return list(VALIDATION_COMPONENTS.values())

def list_transition_types() -> list[dict]:
    return list(TRANSITION_TYPES.values())


def is_question_type_compatible_with_scale(
    question_type_id: str,
    scale_type_id: str,
) -> bool:
    question_type = get_question_type(question_type_id)
    scale_type_id = normalize_scale_type_id(scale_type_id)

    if question_type is None:
        return False

    if scale_type_id in question_type.get("compatible_scale_types", []):
        return True

    scale_definition = get_scale_definition(scale_type_id)

    if scale_definition is None:
        return False

    normalized_question_type = normalize_question_type_id(
        question_type_id
    )

    return normalized_question_type in scale_definition.get(
        "compatible_response_types",
        [],
    )


def is_response_type_compatible_with_scale(
    response_type_id: str,
    scale_type_id: str,
) -> bool:
    response_type = get_response_type(response_type_id)
    scale_type_id = normalize_scale_type_id(scale_type_id)

    if response_type is None:
        return False

    if scale_type_id in response_type.get("compatible_scale_types", []):
        return True

    scale_definition = get_scale_definition(scale_type_id)

    if scale_definition is None:
        return False

    normalized_response_type = normalize_response_type_id(
        response_type_id
    )

    return normalized_response_type in scale_definition.get(
        "compatible_response_types",
        [],
    )


def get_compatible_scale_types_for_response(
    response_type_id: str,
) -> list[str]:
    return sorted(
        scale_id
        for scale_id in SCALE_TYPES
        if is_response_type_compatible_with_scale(
            response_type_id,
            scale_id,
        )
    )


def is_response_type_compatible_with_presentation(
    response_type_id: str,
    presentation_type_id: str,
) -> bool:
    response_type = get_response_type(response_type_id)

    if response_type is None:
        return False

    return presentation_type_id in response_type.get(
        "compatible_presentation_types",
        [],
    )


def validate_question_measurement_contract(
    question_type_id: str | None,
    response_type_id: str | None,
    scale_type_id: str | None,
    presentation_type_id: str | None = None,
) -> dict:
    """Validate the complete question-to-value contract without inferring science.

    A compatible scale only defines admissible operations. It does not by itself
    establish validity, reliability, distributional assumptions, or fitness for
    a particular statistical model.
    """
    question_type_id = normalize_question_type_id(question_type_id)
    response_type_id = normalize_response_type_id(response_type_id)
    scale_type_id = normalize_scale_type_id(scale_type_id)
    errors: list[dict] = []
    warnings: list[dict] = []

    question_type = get_question_type(question_type_id) if question_type_id else None
    response_type = get_response_type(response_type_id) if response_type_id else None
    scale = get_scale_definition(scale_type_id) if scale_type_id else None

    if question_type is None:
        errors.append({"field": "question_type", "code": "UNKNOWN_QUESTION_TYPE"})
    if response_type is None:
        errors.append({"field": "response_type", "code": "UNKNOWN_RESPONSE_TYPE"})
    if scale_type_id and scale is None:
        errors.append({"field": "scale_type", "code": "UNKNOWN_SCALE"})

    expected = EXPECTED_RESPONSE_TYPES_BY_QUESTION.get(question_type_id or "", set())
    if response_type is not None and expected and response_type_id not in expected:
        errors.append({
            "field": "response_type",
            "code": "QUESTION_RESPONSE_INCOMPATIBLE",
            "expected": sorted(expected),
        })

    if scale is not None and question_type is not None and not is_question_type_compatible_with_scale(question_type_id, scale_type_id):
        errors.append({"field": "scale_type", "code": "QUESTION_SCALE_INCOMPATIBLE"})
    if scale is not None and response_type is not None and not is_response_type_compatible_with_scale(response_type_id, scale_type_id):
        errors.append({"field": "scale_type", "code": "RESPONSE_SCALE_INCOMPATIBLE"})

    if presentation_type_id:
        if get_presentation_type(presentation_type_id) is None:
            errors.append({"field": "presentation_type", "code": "UNKNOWN_PRESENTATION_TYPE"})
        elif response_type is not None and not is_response_type_compatible_with_presentation(response_type_id, presentation_type_id):
            errors.append({"field": "presentation_type", "code": "RESPONSE_PRESENTATION_INCOMPATIBLE"})

    if scale is None:
        warnings.append({
            "field": "scale_type",
            "code": "SCALE_UNBOUND",
            "message": "No standard statistical capability may be inferred until a scale is bound.",
        })
    elif scale.get("requires_context_validation"):
        warnings.append({
            "field": "scale_type",
            "code": "CONTEXT_VALIDATION_REQUIRED",
            "limitations": list(scale.get("limitations") or []),
        })

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "normalized": {
            "question_type": question_type_id,
            "response_type": response_type_id,
            "scale_type": scale_type_id,
            "presentation_type": presentation_type_id,
        },
        "scale_contract": (
            {
                "scale_id": scale["scale_id"],
                "scale_code": scale["scale_code"],
                "scale_definition_version": scale["definition_version"],
                "measurement_level": scale["measurement_level"],
                "value_structure": scale["value_structure"],
                "numeric_nature": scale["numeric_nature"],
                "unit_policy": scale["unit_policy"],
                "bounds": scale.get("bounds"),
                "statistical_capabilities": list(scale["statistical_capabilities"]),
                "limitations": list(scale.get("limitations") or []),
            }
            if scale is not None
            else None
        ),
    }
