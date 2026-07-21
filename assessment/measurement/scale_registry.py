from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import UUID, uuid5


SCALE_REGISTRY_SCHEMA_VERSION = "scientific-measurement-scale-registry-1"
SCALE_DEFINITION_SCHEMA_VERSION = "scientific-measurement-scale-definition-1"
SCALE_REFERENCE_SCHEMA_VERSION = "scientific-measurement-scale-reference-1"

SCALE_NAMESPACE = UUID("85f97a27-795a-4e87-a879-f6a0f2546096")

SUPPORTED_DEVELOPMENT_STATUSES = {"draft", "trial", "active"}

SUPPORTED_MEASUREMENT_LEVELS = {
    "nominal",
    "ordinal",
    "interval",
    "ratio",
    "context_dependent",
    "not_applicable",
}

SUPPORTED_VALUE_STRUCTURES = {
    "scalar",
    "category",
    "set",
    "ordered_sequence",
    "vector",
    "interval",
    "distribution",
    "time_series",
    "event",
    "event_sequence",
    "text",
    "date",
    "datetime",
    "time_of_day",
    "file_reference",
    "image",
    "signal",
    "spatial_coordinate",
    "structured",
}

SUPPORTED_NUMERIC_NATURES = {
    "not_numeric",
    "binary",
    "discrete",
    "continuous",
    "bounded_continuous",
    "mixed",
    "context_dependent",
}

SUPPORTED_UNIT_POLICIES = {
    "forbidden",
    "optional",
    "required",
    "unit_one",
    "context_dependent",
}

SCIENTIFIC_SOURCES = {
    "VIM3": {
        "title": "International Vocabulary of Metrology, JCGM 200:2012",
        "url": "https://www.bipm.org/documents/20126/2071204/JCGM_200_2012.pdf",
    },
    "VIM4_2CD": {
        "title": "International Vocabulary of Metrology, Fourth Edition, Second Committee Draft",
        "url": "https://www.bipm.org/documents/20126/115700832/VIM4_2CD_clean/c6d0dfb2-ddbf-059e-1f74-9b025c9c59d8",
    },
    "SI_BROCHURE": {
        "title": "The International System of Units (SI Brochure)",
        "url": "https://www.bipm.org/en/publications/si-brochure",
    },
    "JCGM_GUM_1": {
        "title": "Guide to the expression of uncertainty in measurement, JCGM GUM-1:2023",
        "url": "https://www.bipm.org/documents/20126/2071204/JCGM_GUM-1.pdf",
    },
    "NIST_TRACEABILITY": {
        "title": "NIST Metrological Traceability",
        "url": "https://www.nist.gov/metrology/metrological-traceability",
    },
    "FDA_PRO": {
        "title": "FDA Patient-Reported Outcome Measures Guidance",
        "url": "https://www.fda.gov/media/77832/download",
    },
    "STEVENS_1946": {
        "title": "Stevens (1946), On the Theory of Scales of Measurement",
        "url": "https://doi.org/10.1126/science.103.2684.677",
    },
    "LIDDELL_KRUSCHKE_2018": {
        "title": "Liddell and Kruschke (2018), Analyzing ordinal data with metric models",
        "url": "https://doi.org/10.1016/j.jesp.2018.08.004",
    },
}


def _scale_uuid(scale_code: str, version: int) -> str:
    return str(uuid5(SCALE_NAMESPACE, f"{scale_code}:{version}"))


def _localized(en: str, es: str, ru: str) -> dict[str, str]:
    return {"en": en, "es": es, "ru": ru}


def _definition(
    scale_code: str,
    *,
    title: dict[str, str],
    description: dict[str, str],
    definition_kind: str = "measurement_scale",
    measurement_level: str,
    value_structure: str,
    numeric_nature: str,
    quantity_kind: str,
    unit_policy: str,
    zero_semantics: str,
    order_semantics: str,
    default_representation: str,
    statistical_capabilities: list[str],
    compatible_response_types: list[str] | None = None,
    compatible_source_types: list[str] | None = None,
    temporal_roles: list[str] | None = None,
    bounds: dict[str, Any] | None = None,
    allowed_transformations: list[str] | None = None,
    limitations: list[str] | None = None,
    scientific_basis: list[str] | None = None,
    requires_context_validation: bool = False,
    question_constructor_enabled: bool = False,
    parameter_constructor_enabled: bool = True,
    version: int = 1,
    development_status: str = "active",
) -> dict:
    return {
        "schema_version": SCALE_DEFINITION_SCHEMA_VERSION,
        "registry_schema_version": SCALE_REGISTRY_SCHEMA_VERSION,
        "scale_id": _scale_uuid(scale_code, version),
        "scale_code": scale_code,
        "definition_version": version,
        "title": deepcopy(title),
        "description": deepcopy(description),
        "definition_kind": definition_kind,
        "measurement_level": measurement_level,
        "value_structure": value_structure,
        "numeric_nature": numeric_nature,
        "quantity_kind": quantity_kind,
        "unit_policy": unit_policy,
        "zero_semantics": zero_semantics,
        "order_semantics": order_semantics,
        "bounds": deepcopy(bounds),
        "compatible_response_types": list(compatible_response_types or []),
        "compatible_source_types": list(compatible_source_types or []),
        "temporal_roles": list(temporal_roles or []),
        "default_representation": default_representation,
        "statistical_capabilities": list(statistical_capabilities),
        "allowed_transformations": list(allowed_transformations or []),
        "requires_context_validation": requires_context_validation,
        "limitations": list(limitations or []),
        "scientific_basis": list(scientific_basis or []),
        "question_constructor_enabled": question_constructor_enabled,
        "parameter_constructor_enabled": parameter_constructor_enabled,
        "development_status": development_status,
        "missing_semantics": {
            "unknown_is_zero": False,
            "unknown_is_missing": True,
            "not_collected_is_distinct": True,
            "not_applicable_is_distinct": True,
            "invalid_is_distinct": True,
        },
    }


_ALL_SOURCES = ["questionnaire", "manual", "sensor", "camera", "video", "game", "model", "derived"]
_NUMERIC_CAPABILITIES = ["frequency_table", "ordered_summary", "numeric_summary", "rank_based", "numeric_plot"]
_PARAMETRIC_CAPABILITIES = _NUMERIC_CAPABILITIES + ["parametric_numeric"]


SCALE_DEFINITIONS = {
    definition["scale_code"]: definition
    for definition in [
        _definition(
            "nominal",
            title=_localized("Nominal categories", "Categorías nominales", "Номинальные категории"),
            description=_localized("Distinct categories without an intrinsic order.", "Categorías distintas sin orden intrínseco.", "Различимые категории без внутреннего порядка."),
            measurement_level="nominal", value_structure="category", numeric_nature="not_numeric",
            quantity_kind="nominal_property", unit_policy="forbidden", zero_semantics="category_label",
            order_semantics="none", default_representation="categorical_representation",
            statistical_capabilities=["frequency_table", "categorical_association", "grouping"],
            compatible_response_types=["single_choice", "multiple_choice"], compatible_source_types=_ALL_SOURCES,
            scientific_basis=["VIM3", "VIM4_2CD", "STEVENS_1946"], question_constructor_enabled=True,
        ),
        _definition(
            "binary",
            title=_localized("Binary categories", "Categorías binarias", "Бинарные категории"),
            description=_localized("Exactly two nominal states. Numeric coding does not make the states continuous.", "Exactamente dos estados nominales; la codificación numérica no los hace continuos.", "Ровно два номинальных состояния; числовое кодирование не делает их непрерывной величиной."),
            measurement_level="nominal", value_structure="category", numeric_nature="binary",
            quantity_kind="binary_property", unit_policy="forbidden", zero_semantics="category_label",
            order_semantics="none", default_representation="binary_categorical_representation",
            statistical_capabilities=["frequency_table", "categorical_association", "binary_outcome", "grouping"],
            compatible_response_types=["single_choice"], compatible_source_types=_ALL_SOURCES,
            bounds={"cardinality": 2}, scientific_basis=["VIM3", "VIM4_2CD", "STEVENS_1946"], question_constructor_enabled=True,
        ),
        _definition(
            "ordinal",
            title=_localized("Ordinal categories", "Categorías ordinales", "Порядковые категории"),
            description=_localized("Ordered categories for which distances between adjacent values are not assumed equal.", "Categorías ordenadas sin asumir distancias iguales entre valores adyacentes.", "Упорядоченные категории без предположения о равенстве расстояний между соседними значениями."),
            measurement_level="ordinal", value_structure="category", numeric_nature="discrete",
            quantity_kind="ordinal_quantity", unit_policy="forbidden", zero_semantics="ordered_category",
            order_semantics="order_only", default_representation="ordered_categorical_representation",
            statistical_capabilities=["frequency_table", "ordered_summary", "rank_based", "categorical_association", "grouping"],
            compatible_response_types=["single_choice", "ranking"], compatible_source_types=_ALL_SOURCES,
            allowed_transformations=["order_preserving"], scientific_basis=["VIM3", "VIM4_2CD", "STEVENS_1946", "LIDDELL_KRUSCHKE_2018"], question_constructor_enabled=True,
        ),
        _definition(
            "likert",
            title=_localized("Likert-type item", "Ítem tipo Likert", "Пункт типа Лайкерта"),
            description=_localized("An ordered response item. Item-level equal intervals are not assumed; a composite score requires its own validated definition.", "Ítem de respuesta ordenada; no se presuponen intervalos iguales y una puntuación compuesta requiere definición validada propia.", "Упорядоченный пункт ответа. Равные интервалы на уровне пункта не предполагаются; составной балл требует отдельного валидированного определения."),
            measurement_level="ordinal", value_structure="category", numeric_nature="discrete",
            quantity_kind="ordered_response_item", unit_policy="forbidden", zero_semantics="ordered_category",
            order_semantics="order_only", default_representation="ordered_categorical_representation",
            statistical_capabilities=["frequency_table", "ordered_summary", "rank_based", "categorical_association"],
            compatible_response_types=["single_choice"], compatible_source_types=["questionnaire", "manual"],
            allowed_transformations=["order_preserving", "validated_composite_only"], limitations=["Composite scores must not inherit item-level properties automatically."],
            scientific_basis=["FDA_PRO", "LIDDELL_KRUSCHKE_2018"], question_constructor_enabled=True,
        ),
        _definition(
            "interval",
            title=_localized("Interval quantity", "Cantidad de intervalo", "Интервальная величина"),
            description=_localized("Numeric values with meaningful differences and an arbitrary zero; ratios are not interpreted.", "Valores numéricos con diferencias significativas y cero arbitrario; no se interpretan razones.", "Числовые значения со значимыми разностями и условным нулём; отношения значений не интерпретируются."),
            measurement_level="interval", value_structure="scalar", numeric_nature="continuous",
            quantity_kind="difference_quantity", unit_policy="required", zero_semantics="arbitrary_zero",
            order_semantics="equal_intervals", default_representation="interval_numeric_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES, compatible_response_types=["numeric"], compatible_source_types=_ALL_SOURCES,
            temporal_roles=["observation_time", "time_window"], allowed_transformations=["positive_linear"], scientific_basis=["VIM4_2CD", "SI_BROCHURE", "STEVENS_1946"], question_constructor_enabled=True,
        ),
        _definition(
            "ratio",
            title=_localized("Ratio quantity", "Cantidad de razón", "Величина отношений"),
            description=_localized("Numeric values with meaningful differences, ratios, and a non-arbitrary zero.", "Valores numéricos con diferencias, razones y cero no arbitrario significativos.", "Числовые значения со значимыми разностями, отношениями и неусловным нулём."),
            measurement_level="ratio", value_structure="scalar", numeric_nature="continuous",
            quantity_kind="ratio_quantity", unit_policy="required", zero_semantics="absolute_or_natural_zero",
            order_semantics="equal_intervals", default_representation="ratio_numeric_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES, compatible_response_types=["numeric", "duration"], compatible_source_types=_ALL_SOURCES,
            temporal_roles=["observation_time", "time_window"], allowed_transformations=["similarity"], scientific_basis=["VIM3", "VIM4_2CD", "SI_BROCHURE", "STEVENS_1946"], question_constructor_enabled=True,
        ),
        _definition(
            "continuous",
            title=_localized("Continuous numeric value", "Valor numérico continuo", "Непрерывное числовое значение"),
            description=_localized("A legacy numeric profile describing continuity only. The measurement level must be declared from the measurand and measurement procedure.", "Perfil numérico heredado que describe solo continuidad; el nivel de medición debe declararse desde el mensurando y el procedimiento.", "Совместимый числовой профиль, описывающий только непрерывность. Уровень измерения должен определяться измеряемой величиной и процедурой."),
            measurement_level="context_dependent", value_structure="scalar", numeric_nature="continuous",
            quantity_kind="unspecified_numeric_quantity", unit_policy="context_dependent", zero_semantics="context_dependent",
            order_semantics="context_dependent", default_representation="continuous_numeric_representation",
            statistical_capabilities=_NUMERIC_CAPABILITIES, compatible_response_types=["numeric"], compatible_source_types=_ALL_SOURCES,
            temporal_roles=["observation_time", "time_window"], requires_context_validation=True,
            limitations=["Continuity alone does not establish interval or ratio properties.", "Parametric compatibility requires an explicit scientific measurement level."],
            scientific_basis=["VIM3", "VIM4_2CD"], question_constructor_enabled=True,
        ),
        _definition(
            "discrete",
            title=_localized("Discrete numeric value", "Valor numérico discreto", "Дискретное числовое значение"),
            description=_localized("Numeric values restricted to distinct steps; measurement level remains context dependent.", "Valores numéricos restringidos a pasos distintos; el nivel permanece dependiente del contexto.", "Числовые значения, принимающие отдельные дискретные значения; уровень измерения зависит от контекста."),
            measurement_level="context_dependent", value_structure="scalar", numeric_nature="discrete",
            quantity_kind="unspecified_discrete_quantity", unit_policy="context_dependent", zero_semantics="context_dependent",
            order_semantics="context_dependent", default_representation="discrete_numeric_representation",
            statistical_capabilities=["frequency_table", "ordered_summary", "rank_based"], compatible_response_types=["numeric"], compatible_source_types=_ALL_SOURCES,
            requires_context_validation=True, scientific_basis=["VIM3", "VIM4_2CD"], question_constructor_enabled=True,
        ),
        _definition(
            "count",
            title=_localized("Count", "Conteo", "Счёт"),
            description=_localized("A non-negative integer count of defined events or objects with a meaningful zero.", "Conteo entero no negativo de eventos u objetos definidos con cero significativo.", "Неотрицательное целое число определённых событий или объектов со значимым нулём."),
            measurement_level="ratio", value_structure="scalar", numeric_nature="discrete",
            quantity_kind="count", unit_policy="unit_one", zero_semantics="absence_of_counted_events",
            order_semantics="equal_steps", default_representation="count_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES + ["count_model"], compatible_response_types=["numeric"], compatible_source_types=_ALL_SOURCES,
            bounds={"minimum": 0, "integer_only": True}, temporal_roles=["observation_time", "time_window", "frequency"], scientific_basis=["SI_BROCHURE"], question_constructor_enabled=True,
        ),
        _definition(
            "proportion",
            title=_localized("Proportion", "Proporción", "Доля"),
            description=_localized("A bounded ratio of a part to a defined whole, expressed from 0 to 1.", "Razón acotada entre una parte y un total definido, de 0 a 1.", "Ограниченное отношение части к определённому целому в диапазоне от 0 до 1."),
            measurement_level="ratio", value_structure="scalar", numeric_nature="bounded_continuous",
            quantity_kind="proportion", unit_policy="unit_one", zero_semantics="none_of_defined_whole",
            order_semantics="equal_intervals", default_representation="bounded_ratio_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES + ["bounded_outcome"], compatible_response_types=["numeric"], compatible_source_types=_ALL_SOURCES,
            bounds={"minimum": 0.0, "maximum": 1.0}, scientific_basis=["SI_BROCHURE"], question_constructor_enabled=True,
        ),
        _definition(
            "percentage",
            title=_localized("Percentage", "Porcentaje", "Процент"),
            description=_localized("A proportion expressed per one hundred; the reference whole must be defined.", "Proporción expresada por cien; debe definirse el total de referencia.", "Доля, выраженная на сто единиц; исходное целое должно быть определено."),
            measurement_level="ratio", value_structure="scalar", numeric_nature="bounded_continuous",
            quantity_kind="percentage", unit_policy="unit_one", zero_semantics="none_of_defined_whole",
            order_semantics="equal_intervals", default_representation="percentage_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES + ["bounded_outcome"], compatible_response_types=["numeric"], compatible_source_types=_ALL_SOURCES,
            bounds={"minimum": 0.0, "maximum": 100.0}, allowed_transformations=["divide_by_100", "multiply_by_100"], scientific_basis=["SI_BROCHURE"], question_constructor_enabled=True,
        ),
        _definition(
            "probability",
            title=_localized("Probability", "Probabilidad", "Вероятность"),
            description=_localized("A bounded probability of a defined event with an explicit target event and estimation procedure.", "Probabilidad acotada de un evento definido con evento objetivo y procedimiento de estimación explícitos.", "Ограниченная вероятность определённого события с явным целевым событием и процедурой оценки."),
            measurement_level="ratio", value_structure="scalar", numeric_nature="bounded_continuous",
            quantity_kind="probability", unit_policy="unit_one", zero_semantics="impossible_under_model",
            order_semantics="equal_intervals", default_representation="probability_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES + ["bounded_outcome", "probability_model"], compatible_response_types=["numeric"], compatible_source_types=["model", "derived", "game", "manual"],
            bounds={"minimum": 0.0, "maximum": 1.0}, allowed_transformations=["logit", "probit", "complement"], requires_context_validation=True,
            limitations=["The target event, conditioning information, calibration, and model version are mandatory."], scientific_basis=["JCGM_GUM_1"], question_constructor_enabled=False,
        ),
        _definition(
            "duration",
            title=_localized("Duration", "Duración", "Длительность"),
            description=_localized("Elapsed time with an explicit time unit and non-negative values.", "Tiempo transcurrido con unidad temporal explícita y valores no negativos.", "Прошедшее время с явной единицей времени и неотрицательными значениями."),
            measurement_level="ratio", value_structure="scalar", numeric_nature="continuous",
            quantity_kind="duration", unit_policy="required", zero_semantics="zero_elapsed_time",
            order_semantics="equal_intervals", default_representation="duration_numeric_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES + ["time_to_event"], compatible_response_types=["duration", "numeric"], compatible_source_types=_ALL_SOURCES,
            bounds={"minimum": 0}, temporal_roles=["duration", "time_window"], scientific_basis=["SI_BROCHURE"], question_constructor_enabled=True,
        ),
        _definition(
            "latency",
            title=_localized("Latency / reaction time", "Latencia / tiempo de reacción", "Латентность / время реакции"),
            description=_localized("Elapsed time between a defined initiating event and a defined response event.", "Tiempo entre un evento inicial definido y un evento de respuesta definido.", "Время между определённым инициирующим событием и определённым событием ответа."),
            measurement_level="ratio", value_structure="scalar", numeric_nature="continuous",
            quantity_kind="latency", unit_policy="required", zero_semantics="simultaneous_defined_events",
            order_semantics="equal_intervals", default_representation="latency_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES + ["time_to_event", "reaction_time_distribution"], compatible_response_types=[], compatible_source_types=["sensor", "camera", "video", "game", "model", "derived"],
            bounds={"minimum": 0}, temporal_roles=["latency"], limitations=["Initiating and response event definitions and clock synchronization are mandatory."], scientific_basis=["SI_BROCHURE", "NIST_TRACEABILITY"],
        ),
        _definition(
            "frequency",
            title=_localized("Frequency", "Frecuencia", "Частота"),
            description=_localized("Number of cycles or defined events per unit time.", "Número de ciclos o eventos definidos por unidad de tiempo.", "Число циклов или определённых событий в единицу времени."),
            measurement_level="ratio", value_structure="scalar", numeric_nature="continuous",
            quantity_kind="frequency", unit_policy="required", zero_semantics="no_cycles_or_events_per_time",
            order_semantics="equal_intervals", default_representation="frequency_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES + ["frequency_domain"], compatible_source_types=["sensor", "camera", "video", "game", "model", "derived", "manual"],
            bounds={"minimum": 0}, temporal_roles=["frequency", "time_window"], scientific_basis=["SI_BROCHURE", "NIST_TRACEABILITY"],
        ),
        _definition(
            "rate",
            title=_localized("Rate", "Tasa", "Скорость изменения / интенсивность"),
            description=_localized("Change in a defined quantity or event count per defined denominator, commonly time.", "Cambio de una cantidad o conteo de eventos por un denominador definido, comúnmente tiempo.", "Изменение определённой величины или число событий на заданный знаменатель, обычно время."),
            measurement_level="ratio", value_structure="scalar", numeric_nature="continuous",
            quantity_kind="rate", unit_policy="required", zero_semantics="no_change_or_events_per_denominator",
            order_semantics="equal_intervals", default_representation="rate_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES + ["rate_model"], compatible_response_types=["numeric"], compatible_source_types=_ALL_SOURCES,
            temporal_roles=["change_rate", "time_window"], scientific_basis=["SI_BROCHURE"], question_constructor_enabled=True,
        ),
        _definition(
            "visual_analog",
            title=_localized("Visual analogue response", "Respuesta visual analógica", "Визуально-аналоговый ответ"),
            description=_localized("A position on a defined continuous line. Interval-level interpretation is not automatic and depends on instrument validation and context of use.", "Posición en una línea continua definida; la interpretación de intervalo no es automática y depende de validación y contexto.", "Положение на определённой непрерывной линии. Интервальная интерпретация не автоматическая и зависит от валидации инструмента и контекста применения."),
            measurement_level="context_dependent", value_structure="scalar", numeric_nature="bounded_continuous",
            quantity_kind="visual_analogue_response", unit_policy="optional", zero_semantics="defined_anchor",
            order_semantics="ordered_position", default_representation="visual_analog_representation",
            statistical_capabilities=["frequency_table", "ordered_summary", "numeric_summary", "rank_based", "numeric_plot"], compatible_response_types=["numeric"], compatible_source_types=["questionnaire", "manual", "game"],
            requires_context_validation=True, limitations=["Interval properties require evidence for the specific instrument and context."], scientific_basis=["FDA_PRO"], question_constructor_enabled=True,
        ),
        _definition(
            "date", title=_localized("Calendar date", "Fecha de calendario", "Календарная дата"),
            description=_localized("A calendar date used as a temporal anchor, not a numeric measurement scale by itself.", "Fecha usada como ancla temporal, no como escala numérica por sí misma.", "Календарная дата как временной якорь, а не самостоятельная числовая шкала."),
            definition_kind="observation_type", measurement_level="not_applicable", value_structure="date", numeric_nature="not_numeric",
            quantity_kind="calendar_date", unit_policy="forbidden", zero_semantics="not_applicable", order_semantics="chronological",
            default_representation="date_representation", statistical_capabilities=["temporal_ordering", "grouping"], compatible_response_types=["date"], compatible_source_types=_ALL_SOURCES,
            temporal_roles=["observation_time", "event_time"], question_constructor_enabled=True,
        ),
        _definition(
            "datetime", title=_localized("Date and time", "Fecha y hora", "Дата и время"),
            description=_localized("A timestamp on an identified time reference with timezone and synchronization metadata.", "Marca temporal en una referencia identificada con zona horaria y metadatos de sincronización.", "Временная метка на определённой временной оси с часовым поясом и метаданными синхронизации."),
            definition_kind="observation_type", measurement_level="not_applicable", value_structure="datetime", numeric_nature="not_numeric",
            quantity_kind="timestamp", unit_policy="forbidden", zero_semantics="not_applicable", order_semantics="chronological",
            default_representation="datetime_representation", statistical_capabilities=["temporal_ordering", "time_difference"], compatible_source_types=_ALL_SOURCES,
            temporal_roles=["observation_time", "event_time", "global_time_reference"], limitations=["Timezone and synchronization reference must be preserved."], scientific_basis=["VIM3", "NIST_TRACEABILITY"],
        ),
        _definition(
            "time", title=_localized("Time of day", "Hora del día", "Время суток"),
            description=_localized("A time-of-day value on a stated clock and timezone; elapsed duration is a separate scale.", "Hora del día en reloj y zona declarados; la duración transcurrida es otra escala.", "Значение времени суток на указанной временной системе и часовом поясе; прошедшая длительность является другой шкалой."),
            definition_kind="observation_type", measurement_level="not_applicable", value_structure="time_of_day", numeric_nature="not_numeric",
            quantity_kind="time_of_day", unit_policy="forbidden", zero_semantics="clock_origin", order_semantics="cyclic_chronological",
            default_representation="time_representation", statistical_capabilities=["temporal_ordering", "circular_time"], compatible_response_types=["time"], compatible_source_types=_ALL_SOURCES,
            temporal_roles=["observation_time"], question_constructor_enabled=True,
        ),
        _definition(
            "rank", title=_localized("Rank order", "Orden de rango", "Ранговый порядок"),
            description=_localized("An ordered sequence expressing relative position without equal distances.", "Secuencia ordenada que expresa posición relativa sin distancias iguales.", "Упорядоченная последовательность относительных позиций без равных расстояний."),
            measurement_level="ordinal", value_structure="ordered_sequence", numeric_nature="discrete",
            quantity_kind="rank", unit_policy="forbidden", zero_semantics="not_applicable", order_semantics="order_only",
            default_representation="rank_representation", statistical_capabilities=["frequency_table", "rank_based", "rank_agreement"], compatible_response_types=["ranking"], compatible_source_types=["questionnaire", "game", "manual", "derived"],
            allowed_transformations=["order_preserving"], question_constructor_enabled=True,
        ),
        _definition(
            "model_index", title=_localized("Model-derived index", "Índice derivado de modelo", "Расчётный индекс модели"),
            description=_localized("A numeric index produced by a registered model. Its measurement level is defined by the model contract, not by numeric storage type.", "Índice numérico producido por un modelo registrado; su nivel lo define el contrato del modelo, no el tipo numérico.", "Числовой индекс зарегистрированной модели. Его уровень измерения определяется контрактом модели, а не типом хранения числа."),
            measurement_level="context_dependent", value_structure="scalar", numeric_nature="continuous",
            quantity_kind="model_index", unit_policy="context_dependent", zero_semantics="model_defined", order_semantics="model_defined",
            default_representation="model_index_representation", statistical_capabilities=_NUMERIC_CAPABILITIES, compatible_source_types=["model", "derived"],
            requires_context_validation=True, limitations=["Model formula, version, range, direction, validation status, and uncertainty are mandatory."],
        ),
        _definition(
            "normalized_index", title=_localized("Normalized index", "Índice normalizado", "Нормированный индекс"),
            description=_localized("A model or composite index transformed to a bounded range. Normalization does not create interval properties.", "Índice transformado a un rango acotado; la normalización no crea propiedades de intervalo.", "Модельный или составной индекс, преобразованный к ограниченному диапазону. Нормирование не создаёт интервальных свойств."),
            measurement_level="context_dependent", value_structure="scalar", numeric_nature="bounded_continuous",
            quantity_kind="normalized_index", unit_policy="unit_one", zero_semantics="transformation_defined", order_semantics="source_defined",
            default_representation="normalized_index_representation", statistical_capabilities=_NUMERIC_CAPABILITIES, compatible_source_types=["model", "derived"],
            allowed_transformations=["registered_normalization"], requires_context_validation=True,
        ),
        _definition(
            "z_score", title=_localized("Standard score (z)", "Puntuación estándar (z)", "Стандартный z-балл"),
            description=_localized("A standardized value expressed in source-distribution standard deviations from its mean; the reference population is mandatory.", "Valor en desviaciones estándar respecto a la media de la distribución de referencia; la población de referencia es obligatoria.", "Стандартизованное значение в стандартных отклонениях от среднего исходного распределения; референтная популяция обязательна."),
            measurement_level="interval", value_structure="scalar", numeric_nature="continuous", quantity_kind="standard_score",
            unit_policy="unit_one", zero_semantics="reference_mean", order_semantics="equal_intervals", default_representation="standard_score_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES, compatible_source_types=["derived", "model"], allowed_transformations=["affine"],
            limitations=["Reference population, reference period, source variable, and transformation version are mandatory."],
        ),
        _definition(
            "t_score", title=_localized("Standard T-score", "Puntuación T estándar", "Стандартный T-балл"),
            description=_localized("An affine standard-score transformation with an explicit reference population and transformation convention.", "Transformación afín de puntuación estándar con población y convención explícitas.", "Аффинное преобразование стандартного балла с явной референтной популяцией и правилом преобразования."),
            measurement_level="interval", value_structure="scalar", numeric_nature="continuous", quantity_kind="standard_score",
            unit_policy="unit_one", zero_semantics="transformation_defined", order_semantics="equal_intervals", default_representation="standard_score_representation",
            statistical_capabilities=_PARAMETRIC_CAPABILITIES, compatible_source_types=["derived", "model"], allowed_transformations=["affine"],
            limitations=["Reference population and exact transformation convention are mandatory."],
        ),
        _definition(
            "percentile_rank", title=_localized("Percentile rank", "Rango percentil", "Процентильный ранг"),
            description=_localized("Relative rank within a defined reference distribution; equal percentile differences are not equal measurement intervals.", "Rango relativo en una distribución de referencia; diferencias percentiles iguales no son intervalos iguales.", "Относительный ранг в определённом референтном распределении; равные разности процентилей не являются равными интервалами измерения."),
            measurement_level="ordinal", value_structure="scalar", numeric_nature="bounded_continuous", quantity_kind="percentile_rank",
            unit_policy="unit_one", zero_semantics="lower_reference_boundary", order_semantics="order_only", default_representation="percentile_representation",
            statistical_capabilities=["frequency_table", "ordered_summary", "rank_based", "numeric_plot"], compatible_source_types=["derived", "model"],
            bounds={"minimum": 0.0, "maximum": 100.0}, limitations=["Reference distribution and tie convention are mandatory."],
        ),
        _definition(
            "vector", title=_localized("Numeric vector", "Vector numérico", "Числовой вектор"),
            description=_localized("A fixed, versioned set of named components; each component carries its own scale reference and unit.", "Conjunto fijo y versionado de componentes nombrados; cada componente tiene su propia escala y unidad.", "Фиксированный версионируемый набор именованных компонентов; каждый компонент имеет собственную ссылку на шкалу и единицу."),
            definition_kind="compound_profile", measurement_level="not_applicable", value_structure="vector", numeric_nature="mixed", quantity_kind="vector",
            unit_policy="context_dependent", zero_semantics="component_defined", order_semantics="component_defined", default_representation="vector_representation",
            statistical_capabilities=["multivariate", "component_analysis"], compatible_source_types=["sensor", "camera", "video", "game", "model", "derived"],
            limitations=["Component identity, order, scale references, units, and vector version are mandatory."],
        ),
        _definition(
            "interval_estimate", title=_localized("Interval estimate", "Estimación por intervalo", "Интервальная оценка"),
            description=_localized("Lower and upper bounds around an estimate with an explicit coverage or credibility level and construction method.", "Límites inferior y superior con nivel de cobertura o credibilidad y método explícitos.", "Нижняя и верхняя границы оценки с явным уровнем охвата или доверия и методом построения."),
            definition_kind="compound_profile", measurement_level="not_applicable", value_structure="interval", numeric_nature="continuous", quantity_kind="interval_estimate",
            unit_policy="context_dependent", zero_semantics="source_scale_defined", order_semantics="source_scale_defined", default_representation="interval_estimate_representation",
            statistical_capabilities=["interval_summary", "uncertainty_analysis"], compatible_source_types=["model", "derived"],
            limitations=["Estimate scale, lower and upper bounds, level, and construction method are mandatory."], scientific_basis=["JCGM_GUM_1"],
        ),
        _definition(
            "distribution", title=_localized("Distribution", "Distribución", "Распределение"),
            description=_localized("A probability or empirical distribution with an explicit support, parameterization or sample, and generation method.", "Distribución probabilística o empírica con soporte, parametrización o muestra y método de generación explícitos.", "Вероятностное или эмпирическое распределение с явной областью значений, параметризацией или выборкой и методом получения."),
            definition_kind="compound_profile", measurement_level="not_applicable", value_structure="distribution", numeric_nature="mixed", quantity_kind="distribution",
            unit_policy="context_dependent", zero_semantics="support_defined", order_semantics="support_defined", default_representation="distribution_representation",
            statistical_capabilities=["distribution_analysis", "uncertainty_analysis"], compatible_source_types=["sensor", "game", "model", "derived"],
            limitations=["Support scale, unit, normalization, and generation method are mandatory."], scientific_basis=["JCGM_GUM_1"],
        ),
        _definition(
            "time_series", title=_localized("Time series", "Serie temporal", "Временной ряд"),
            description=_localized("An ordered series of scale-referenced observations on a shared time axis.", "Serie ordenada de observaciones referenciadas a una escala y eje temporal compartido.", "Упорядоченный ряд наблюдений со ссылками на шкалу на общей временной оси."),
            definition_kind="compound_profile", measurement_level="not_applicable", value_structure="time_series", numeric_nature="mixed", quantity_kind="time_series",
            unit_policy="context_dependent", zero_semantics="component_defined", order_semantics="chronological", default_representation="time_series_representation",
            statistical_capabilities=["time_series_analysis", "longitudinal", "frequency_domain", "trajectory"], compatible_source_types=["sensor", "camera", "video", "game", "model", "derived"],
            temporal_roles=["observation_time", "sampling_interval", "sampling_rate", "global_time_reference"],
            limitations=["Value scale, sampling scheme, missing intervals, clock, timezone, and synchronization reference are mandatory."], scientific_basis=["VIM3", "NIST_TRACEABILITY"],
        ),
        _definition(
            "event", title=_localized("Event observation", "Observación de evento", "Наблюдение события"),
            description=_localized("A defined event with identity, occurrence status, and timestamp or interval.", "Evento definido con identidad, estado de ocurrencia y marca temporal o intervalo.", "Определённое событие с идентичностью, фактом наступления и временной меткой или интервалом."),
            definition_kind="observation_type", measurement_level="nominal", value_structure="event", numeric_nature="not_numeric", quantity_kind="event",
            unit_policy="forbidden", zero_semantics="non_occurrence", order_semantics="none", default_representation="event_representation",
            statistical_capabilities=["frequency_table", "event_analysis", "time_to_event"], compatible_source_types=_ALL_SOURCES,
            temporal_roles=["event_time", "duration", "global_time_reference"],
        ),
        _definition(
            "event_sequence", title=_localized("Event sequence", "Secuencia de eventos", "Последовательность событий"),
            description=_localized("A temporally ordered sequence of defined events preserving event identity and timing.", "Secuencia temporalmente ordenada de eventos definidos que conserva identidad y tiempo.", "Упорядоченная во времени последовательность определённых событий с сохранением идентичности и времени."),
            definition_kind="compound_profile", measurement_level="not_applicable", value_structure="event_sequence", numeric_nature="not_numeric", quantity_kind="event_sequence",
            unit_policy="forbidden", zero_semantics="empty_sequence", order_semantics="chronological", default_representation="event_sequence_representation",
            statistical_capabilities=["sequence_analysis", "event_analysis", "time_to_event", "trajectory"], compatible_source_types=["game", "sensor", "camera", "video", "model", "derived"],
            temporal_roles=["event_time", "sequence_position", "global_time_reference"],
        ),
        _definition(
            "spatial_coordinate", title=_localized("Spatial coordinate", "Coordenada espacial", "Пространственная координата"),
            description=_localized("A coordinate in an explicitly defined spatial reference system.", "Coordenada en un sistema de referencia espacial explícito.", "Координата в явно определённой пространственной системе отсчёта."),
            definition_kind="compound_profile", measurement_level="not_applicable", value_structure="spatial_coordinate", numeric_nature="continuous", quantity_kind="coordinate",
            unit_policy="required", zero_semantics="reference_origin", order_semantics="reference_system_defined", default_representation="coordinate_representation",
            statistical_capabilities=["spatial_analysis", "trajectory"], compatible_source_types=["sensor", "camera", "video", "game", "derived"],
            limitations=["Coordinate reference system, axes, unit, orientation, and calibration are mandatory."], scientific_basis=["VIM3", "NIST_TRACEABILITY"],
        ),
        *[
            _definition(
                code,
                title=_localized(en, es, ru),
                description=_localized(desc_en, desc_es, desc_ru),
                measurement_level="ratio", value_structure="scalar", numeric_nature="continuous", quantity_kind=code,
                unit_policy="required", zero_semantics=zero, order_semantics="equal_intervals", default_representation=f"{code}_representation",
                statistical_capabilities=_PARAMETRIC_CAPABILITIES + (["spatial_analysis"] if code in {"distance", "angle", "area", "velocity", "acceleration"} else []),
                compatible_source_types=["sensor", "camera", "video", "game", "manual", "model", "derived"], scientific_basis=["SI_BROCHURE", "NIST_TRACEABILITY"],
            )
            for code, en, es, ru, desc_en, desc_es, desc_ru, zero in [
                ("distance", "Distance", "Distancia", "Расстояние", "Length between defined points in a stated coordinate system.", "Longitud entre puntos definidos en un sistema declarado.", "Длина между определёнными точками в заданной системе координат.", "coincident_points"),
                ("angle", "Angle", "Ángulo", "Угол", "Angular quantity with a stated convention and unit.", "Cantidad angular con convención y unidad declaradas.", "Угловая величина с указанным правилом и единицей.", "zero_angular_displacement"),
                ("area", "Area", "Área", "Площадь", "Area in a calibrated spatial reference.", "Área en una referencia espacial calibrada.", "Площадь в калиброванной пространственной системе.", "zero_area"),
                ("velocity", "Velocity", "Velocidad", "Скорость", "Change of position per unit time with direction when applicable.", "Cambio de posición por unidad de tiempo con dirección cuando corresponda.", "Изменение положения в единицу времени с направлением, когда применимо.", "no_position_change_per_time"),
                ("acceleration", "Acceleration", "Aceleración", "Ускорение", "Change of velocity per unit time.", "Cambio de velocidad por unidad de tiempo.", "Изменение скорости в единицу времени.", "no_velocity_change_per_time"),
            ]
        ],
        _definition(
            "signal", title=_localized("Sampled signal", "Señal muestreada", "Дискретизированный сигнал"),
            description=_localized("A sampled instrument output whose value scale, unit, sampling, calibration, and uncertainty are defined separately.", "Salida de instrumento muestreada con escala, unidad, muestreo, calibración e incertidumbre definidos por separado.", "Дискретизированный выход прибора, для которого отдельно определены шкала значения, единица, дискретизация, калибровка и неопределённость."),
            definition_kind="compound_profile", measurement_level="not_applicable", value_structure="signal", numeric_nature="mixed", quantity_kind="signal",
            unit_policy="context_dependent", zero_semantics="channel_defined", order_semantics="time_ordered", default_representation="signal_representation",
            statistical_capabilities=["signal_analysis", "time_series_analysis", "frequency_domain", "feature_extraction"], compatible_source_types=["sensor", "camera", "video"],
            temporal_roles=["sampling_rate", "sampling_interval", "global_time_reference"], limitations=["Channel scales, units, sampling clock, calibration, uncertainty, and preprocessing provenance are mandatory."], scientific_basis=["VIM3", "JCGM_GUM_1", "NIST_TRACEABILITY"],
        ),
        _definition(
            "image", title=_localized("Image or frame", "Imagen o fotograma", "Изображение или кадр"),
            description=_localized("An image observation. Scientific variables arise only after a registered measurement or feature-extraction procedure.", "Observación de imagen; las variables científicas surgen tras un procedimiento registrado de medición o extracción.", "Наблюдение в виде изображения. Научные переменные возникают только после зарегистрированной процедуры измерения или извлечения признаков."),
            definition_kind="observation_type", measurement_level="not_applicable", value_structure="image", numeric_nature="not_numeric", quantity_kind="image",
            unit_policy="forbidden", zero_semantics="not_applicable", order_semantics="not_applicable", default_representation="image_representation",
            statistical_capabilities=["image_analysis", "feature_extraction"], compatible_source_types=["camera", "video", "sensor"],
            limitations=["Pixel format, dimensions, spatial calibration, acquisition settings, and provenance are mandatory."],
        ),
        _definition(
            "structured", title=_localized("Structured result", "Resultado estructurado", "Структурированный результат"),
            description=_localized("A versioned structured object whose components retain independent identities and scale references.", "Objeto estructurado versionado cuyos componentes conservan identidades y escalas independientes.", "Версионируемый структурированный объект, компоненты которого сохраняют отдельные идентичности и ссылки на шкалы."),
            definition_kind="compound_profile", measurement_level="not_applicable", value_structure="structured", numeric_nature="mixed", quantity_kind="structured_result",
            unit_policy="context_dependent", zero_semantics="component_defined", order_semantics="component_defined", default_representation="structured_representation",
            statistical_capabilities=["component_analysis"], compatible_source_types=_ALL_SOURCES,
            limitations=["A structured result must not enter scalar statistical analysis without an explicit registered projection."],
        ),
        _definition(
            "text", title=_localized("Text observation", "Observación textual", "Текстовое наблюдение"),
            description=_localized("Qualitative text. It is not a measurement scale until a registered coding procedure produces variables.", "Texto cualitativo; no es escala de medición hasta que un procedimiento registrado produzca variables.", "Качественный текст. Он не является шкалой измерения, пока зарегистрированная процедура кодирования не создаст переменные."),
            definition_kind="observation_type", measurement_level="not_applicable", value_structure="text", numeric_nature="not_numeric", quantity_kind="text",
            unit_policy="forbidden", zero_semantics="not_applicable", order_semantics="none", default_representation="text_representation",
            statistical_capabilities=["qualitative_coding", "text_analysis"], compatible_response_types=["text"], compatible_source_types=_ALL_SOURCES,
            limitations=["Derived codes require a versioned coding scheme and provenance."], question_constructor_enabled=True,
        ),
        _definition(
            "file", title=_localized("File reference", "Referencia de archivo", "Ссылка на файл"),
            description=_localized("A reference to stored data, not a measurement scale. Scientific metadata are resolved from the file and acquisition procedure.", "Referencia a datos almacenados, no escala; los metadatos se resuelven desde el archivo y el procedimiento.", "Ссылка на сохранённые данные, а не шкала измерения. Научные метаданные определяются по файлу и процедуре получения."),
            definition_kind="observation_type", measurement_level="not_applicable", value_structure="file_reference", numeric_nature="not_numeric", quantity_kind="file_reference",
            unit_policy="forbidden", zero_semantics="not_applicable", order_semantics="none", default_representation="file_reference_representation",
            statistical_capabilities=["metadata_resolution"], compatible_response_types=["file"], compatible_source_types=_ALL_SOURCES,
            question_constructor_enabled=True,
        ),
    ]
}


LEGACY_SCALE_ALIASES = {
    "number": "ratio",
    "numeric": "ratio",
    "vas": "visual_analog",
    "visual_analog_scale": "visual_analog",
    "free_text": "text",
    "long_text": "text",
    "file_upload": "file",
    "datetime_local": "datetime",
    "reaction_time": "latency",
    "percent": "percentage",
    "probability_0_1": "probability",
    "interval": "interval",
}

QUESTIONNAIRE_SCALE_ORDER = [
    "nominal", "binary", "ordinal", "likert", "interval", "ratio",
    "continuous", "discrete", "count", "proportion", "percentage",
    "duration", "rate", "visual_analog", "rank", "date", "time", "text", "file",
]


def normalize_scale_id(scale_id: Any) -> str | None:
    if scale_id is None:
        return None
    if isinstance(scale_id, dict):
        scale_id = scale_id.get("scale_code") or scale_id.get("scale_type") or scale_id.get("id")
    normalized = str(scale_id).strip().lower()
    if not normalized:
        return None
    return LEGACY_SCALE_ALIASES.get(normalized, normalized)


def get_scale_definition(scale_id: Any) -> dict | None:
    normalized = normalize_scale_id(scale_id)
    definition = SCALE_DEFINITIONS.get(normalized)
    return deepcopy(definition) if definition is not None else None


def list_scale_definitions(
    *, definition_kind: str | None = None, source_type: str | None = None,
    question_constructor_enabled: bool | None = None,
    parameter_constructor_enabled: bool | None = None,
    include_non_active: bool = False,
) -> list[dict]:
    definitions = []
    for definition in SCALE_DEFINITIONS.values():
        if not include_non_active and definition["development_status"] != "active":
            continue
        if definition_kind is not None and definition["definition_kind"] != definition_kind:
            continue
        if source_type is not None and source_type not in definition["compatible_source_types"]:
            continue
        if question_constructor_enabled is not None and definition["question_constructor_enabled"] is not question_constructor_enabled:
            continue
        if parameter_constructor_enabled is not None and definition["parameter_constructor_enabled"] is not parameter_constructor_enabled:
            continue
        definitions.append(deepcopy(definition))
    return sorted(definitions, key=lambda item: item["scale_code"])


def build_scale_reference(scale_id: Any) -> dict:
    definition = get_scale_definition(scale_id)
    if definition is None:
        raise KeyError(f"Unknown scale: {scale_id}")
    return {
        "schema_version": SCALE_REFERENCE_SCHEMA_VERSION,
        "registry_schema_version": SCALE_REGISTRY_SCHEMA_VERSION,
        "scale_id": definition["scale_id"],
        "scale_code": definition["scale_code"],
        "scale_definition_version": definition["definition_version"],
        "definition_kind": definition["definition_kind"],
        "measurement_level": definition["measurement_level"],
        "value_structure": definition["value_structure"],
        "numeric_nature": definition["numeric_nature"],
        "quantity_kind": definition["quantity_kind"],
    }


def validate_scale_reference(reference: dict) -> dict:
    errors = []
    if not isinstance(reference, dict):
        return {"valid": False, "errors": [{"code": "SCALE_REFERENCE_NOT_OBJECT"}]}
    definition = get_scale_definition(reference.get("scale_code") or reference.get("scale_type"))
    if definition is None:
        errors.append({"field": "scale_code", "code": "UNKNOWN_SCALE"})
    else:
        if reference.get("scale_id") not in {None, definition["scale_id"]}:
            errors.append({"field": "scale_id", "code": "SCALE_ID_MISMATCH"})
        if reference.get("scale_definition_version") not in {None, definition["definition_version"]}:
            errors.append({"field": "scale_definition_version", "code": "SCALE_VERSION_MISMATCH"})
    return {"valid": not errors, "errors": errors}


def scale_supports_capability(scale_id: Any, capability: str) -> bool:
    definition = get_scale_definition(scale_id)
    return bool(definition and capability in definition["statistical_capabilities"])


def scale_ids_supporting(capability: str) -> list[str]:
    return sorted(code for code, definition in SCALE_DEFINITIONS.items() if capability in definition["statistical_capabilities"])


def scale_matches_requirement(scale_id: Any, requirement: str) -> bool:
    definition = get_scale_definition(scale_id)
    if definition is None:
        return False
    normalized_requirement = normalize_scale_id(requirement) or str(requirement)
    return normalized_requirement in {
        definition["scale_code"], definition["measurement_level"],
        definition["numeric_nature"], definition["value_structure"],
        definition["quantity_kind"], *definition["statistical_capabilities"],
    }


def get_questionnaire_scale_components() -> dict[str, dict]:
    components = {}
    for scale_code in QUESTIONNAIRE_SCALE_ORDER:
        definition = SCALE_DEFINITIONS[scale_code]
        components[scale_code] = {
            "id": scale_code,
            "title": definition["title"]["en"],
            "localized_title": deepcopy(definition["title"]),
            "description": deepcopy(definition["description"]),
            "component_type": "scale_type",
            "schema_version": "questionnaire-components-1",
            "scale_id": definition["scale_id"],
            "scale_definition_version": definition["definition_version"],
            "measurement_scale": definition["measurement_level"],
            "measurement_level": definition["measurement_level"],
            "value_structure": definition["value_structure"],
            "numeric_nature": definition["numeric_nature"],
            "quantity_kind": definition["quantity_kind"],
            "unit_policy": definition["unit_policy"],
            "requires_context_validation": definition["requires_context_validation"],
            "default_representation": definition["default_representation"],
            "statistical_capabilities": list(definition["statistical_capabilities"]),
            "compatible_response_types": list(
                definition["compatible_response_types"]
            ),
            "compatible_source_types": list(
                definition["compatible_source_types"]
            ),
            "bounds": deepcopy(definition["bounds"]),
            "limitations": list(definition["limitations"]),
            "development_status": definition["development_status"],
        }
    return components


def get_scale_registry_contract() -> dict:
    return {
        "schema_version": SCALE_REGISTRY_SCHEMA_VERSION,
        "definition_schema_version": SCALE_DEFINITION_SCHEMA_VERSION,
        "reference_schema_version": SCALE_REFERENCE_SCHEMA_VERSION,
        "definition_count": len(SCALE_DEFINITIONS),
        "development_statuses": sorted(SUPPORTED_DEVELOPMENT_STATUSES),
        "measurement_levels": sorted(SUPPORTED_MEASUREMENT_LEVELS),
        "value_structures": sorted(SUPPORTED_VALUE_STRUCTURES),
        "numeric_natures": sorted(SUPPORTED_NUMERIC_NATURES),
        "unit_policies": sorted(SUPPORTED_UNIT_POLICIES),
        "scientific_sources": deepcopy(SCIENTIFIC_SOURCES),
    }


def validate_scale_registry() -> dict:
    errors = []
    seen_ids = {}
    for code, definition in SCALE_DEFINITIONS.items():
        if definition["scale_code"] != code:
            errors.append({"scale_code": code, "code": "SCALE_CODE_KEY_MISMATCH"})
        if set(definition["title"]) != {"en", "es", "ru"} or not all(definition["title"].values()):
            errors.append({"scale_code": code, "code": "THREE_LANGUAGE_TITLE_REQUIRED"})
        if set(definition["description"]) != {"en", "es", "ru"} or not all(definition["description"].values()):
            errors.append({"scale_code": code, "code": "THREE_LANGUAGE_DESCRIPTION_REQUIRED"})
        if definition["measurement_level"] not in SUPPORTED_MEASUREMENT_LEVELS:
            errors.append({"scale_code": code, "code": "INVALID_MEASUREMENT_LEVEL"})
        if definition["value_structure"] not in SUPPORTED_VALUE_STRUCTURES:
            errors.append({"scale_code": code, "code": "INVALID_VALUE_STRUCTURE"})
        if definition["numeric_nature"] not in SUPPORTED_NUMERIC_NATURES:
            errors.append({"scale_code": code, "code": "INVALID_NUMERIC_NATURE"})
        if definition["unit_policy"] not in SUPPORTED_UNIT_POLICIES:
            errors.append({"scale_code": code, "code": "INVALID_UNIT_POLICY"})
        if definition["development_status"] not in SUPPORTED_DEVELOPMENT_STATUSES:
            errors.append({"scale_code": code, "code": "INVALID_DEVELOPMENT_STATUS"})
        previous = seen_ids.get(definition["scale_id"])
        if previous is not None:
            errors.append({"scale_code": code, "code": "DUPLICATE_SCALE_ID", "other_scale_code": previous})
        seen_ids[definition["scale_id"]] = code
        for source_id in definition["scientific_basis"]:
            if source_id not in SCIENTIFIC_SOURCES:
                errors.append({"scale_code": code, "code": "UNKNOWN_SCIENTIFIC_SOURCE", "source_id": source_id})
    return {"valid": not errors, "errors": errors, "definition_count": len(SCALE_DEFINITIONS)}


_REGISTRY_VALIDATION = validate_scale_registry()
if not _REGISTRY_VALIDATION["valid"]:
    raise ValueError({"error": "SCALE_REGISTRY_INVALID", "validation": _REGISTRY_VALIDATION})
