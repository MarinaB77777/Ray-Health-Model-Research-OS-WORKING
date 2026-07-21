from __future__ import annotations

from copy import deepcopy
from typing import Any

from assessment.measurement.scale_registry import get_scale_definition


PARAMETER_CALCULATION_REGISTRY_SCHEMA_VERSION = (
    "health-model-parameter-calculation-registry-1"
)
PARAMETER_CALCULATION_DEFINITION_SCHEMA_VERSION = (
    "health-model-parameter-calculation-definition-1"
)


def _text(ru: str, en: str, es: str) -> dict[str, str]:
    return {"ru": ru, "en": en, "es": es}


def _operation(
    operation_id: str,
    *,
    title: dict[str, str],
    description: dict[str, str],
    input_rule: str,
    output_scale_rule: str,
    minimum_inputs: int = 1,
    maximum_inputs: int | None = None,
    required_configuration: list[str] | None = None,
    temporal_requirement: str = "any",
) -> dict:
    return {
        "schema_version": PARAMETER_CALCULATION_DEFINITION_SCHEMA_VERSION,
        "operation_id": operation_id,
        "definition_version": 1,
        "development_status": "active",
        "title": title,
        "description": description,
        "input_rule": input_rule,
        "minimum_inputs": minimum_inputs,
        "maximum_inputs": maximum_inputs,
        "required_configuration": list(required_configuration or []),
        "temporal_requirement": temporal_requirement,
        "output_scale_rule": output_scale_rule,
        "unknown_is_zero": False,
        "missing_data_configuration_required": True,
    }


CALCULATION_OPERATIONS = {
    item["operation_id"]: item
    for item in [
        _operation(
            "identity",
            title=_text("Использовать значение ответа", "Use answer value", "Usar el valor de la respuesta"),
            description=_text(
                "Сохраняет значение одного ответа без изменения его шкалы.",
                "Uses one answer value without changing its scale.",
                "Usa el valor de una respuesta sin cambiar su escala.",
            ),
            input_rule="single_supported_value",
            maximum_inputs=1,
            output_scale_rule="inherit_input_scale",
        ),
        _operation(
            "category_indicator",
            title=_text("Проверить выбранную категорию", "Category indicator", "Indicador de categoría"),
            description=_text(
                "Возвращает да/нет для явно выбранной категории или набора категорий.",
                "Returns yes/no for an explicitly selected category or category set.",
                "Devuelve sí/no para una categoría o conjunto definido.",
            ),
            input_rule="categorical_or_ordered",
            output_scale_rule="binary",
            required_configuration=["target_categories"],
        ),
        _operation(
            "threshold",
            title=_text("Сравнить с порогом", "Compare with a threshold", "Comparar con un umbral"),
            description=_text(
                "Возвращает да/нет по явно заданному порогу и направлению сравнения.",
                "Returns yes/no using an explicit threshold and comparison direction.",
                "Devuelve sí/no mediante un umbral y una dirección de comparación explícitos.",
            ),
            input_rule="ordered_or_numeric",
            output_scale_rule="binary",
            required_configuration=["condition"],
        ),
        _operation(
            "count_condition",
            title=_text("Посчитать ответы, соответствующие условию", "Count answers matching a condition", "Contar respuestas que cumplen una condición"),
            description=_text(
                "Считает только ответы, удовлетворяющие явно заданному условию.",
                "Counts only answers satisfying an explicit condition.",
                "Cuenta solo las respuestas que cumplen una condición explícita.",
            ),
            input_rule="condition_comparable",
            output_scale_rule="count",
            required_configuration=["condition"],
        ),
        _operation(
            "count_selected",
            title=_text("Посчитать выбранные варианты", "Count selected options", "Contar opciones seleccionadas"),
            description=_text(
                "Для вопроса с множественным выбором возвращает число выбранных вариантов.",
                "For a multiple-choice response, returns the number of selected options.",
                "Para una respuesta múltiple, devuelve el número de opciones seleccionadas.",
            ),
            input_rule="multiple_choice_response",
            maximum_inputs=1,
            output_scale_rule="count",
        ),
        _operation(
            "proportion_condition",
            title=_text("Рассчитать долю ответов по условию", "Proportion matching a condition", "Proporción que cumple una condición"),
            description=_text(
                "Делит число подходящих непустых ответов на число всех учитываемых непустых ответов.",
                "Divides matching non-missing answers by all included non-missing answers.",
                "Divide las respuestas válidas coincidentes por todas las respuestas válidas incluidas.",
            ),
            input_rule="condition_comparable",
            output_scale_rule="proportion",
            required_configuration=["condition", "denominator_rule"],
        ),
        _operation(
            "mode",
            title=_text("Найти наиболее частый ответ", "Most frequent answer", "Respuesta más frecuente"),
            description=_text(
                "Возвращает категорию или значение с наибольшей частотой; правило совпадений задаётся отдельно.",
                "Returns the most frequent category or value; ties require an explicit rule.",
                "Devuelve la categoría o valor más frecuente; los empates requieren una regla.",
            ),
            input_rule="categorical_or_ordered",
            output_scale_rule="inherit_common_input_scale",
            required_configuration=["tie_rule"],
        ),
        _operation(
            "median",
            title=_text("Найти медиану", "Median", "Mediana"),
            description=_text(
                "Использует порядок значений без предположения равных расстояний.",
                "Uses value order without assuming equal distances.",
                "Usa el orden sin suponer distancias iguales.",
            ),
            input_rule="ordered_or_numeric",
            output_scale_rule="inherit_common_input_scale",
        ),
        _operation(
            "minimum",
            title=_text("Найти минимальное значение", "Minimum", "Mínimo"),
            description=_text("Возвращает наименьшее упорядоченное значение.", "Returns the lowest ordered value.", "Devuelve el menor valor ordenado."),
            input_rule="ordered_or_numeric",
            output_scale_rule="inherit_common_input_scale",
        ),
        _operation(
            "maximum",
            title=_text("Найти максимальное значение", "Maximum", "Máximo"),
            description=_text("Возвращает наибольшее упорядоченное значение.", "Returns the highest ordered value.", "Devuelve el mayor valor ordenado."),
            input_rule="ordered_or_numeric",
            output_scale_rule="inherit_common_input_scale",
        ),
        _operation(
            "mean",
            title=_text("Рассчитать среднее", "Arithmetic mean", "Media aritmética"),
            description=_text(
                "Допустимо для интервальных или шкал отношений; отдельные порядковые пункты сюда не подставляются.",
                "Allowed for interval or ratio scales; individual ordinal items are excluded.",
                "Permitido para escalas de intervalo o razón; se excluyen los ítems ordinales individuales.",
            ),
            input_rule="interval_or_ratio",
            output_scale_rule="inherit_common_metric_scale",
        ),
        _operation(
            "weighted_mean",
            title=_text("Рассчитать взвешенное среднее", "Weighted mean", "Media ponderada"),
            description=_text(
                "Каждый совместимый числовой вход получает явно заданный вес.",
                "Every compatible numeric input receives an explicit weight.",
                "Cada entrada numérica compatible recibe un peso explícito.",
            ),
            input_rule="interval_or_ratio",
            output_scale_rule="inherit_common_metric_scale",
            required_configuration=["weights", "weight_normalization_rule"],
        ),
        _operation(
            "sum",
            title=_text("Рассчитать сумму", "Sum", "Suma"),
            description=_text(
                "Допустимо только для аддитивных величин с осмысленным нулём или для зарегистрированной составной шкалы.",
                "Allowed only for additive quantities with a meaningful zero or a registered composite scale.",
                "Permitido solo para cantidades aditivas con cero significativo o una escala compuesta registrada.",
            ),
            input_rule="additive_ratio_or_validated_composite",
            output_scale_rule="derive_additive_output",
            required_configuration=["additivity_basis"],
        ),
        _operation(
            "difference",
            title=_text("Рассчитать разность", "Difference", "Diferencia"),
            description=_text("Вычитает второе совместимое значение из первого.", "Subtracts the second compatible value from the first.", "Resta el segundo valor compatible del primero."),
            input_rule="interval_or_ratio",
            minimum_inputs=2,
            maximum_inputs=2,
            output_scale_rule="difference_scale",
            required_configuration=["input_order"],
        ),
        _operation(
            "ratio",
            title=_text("Рассчитать отношение", "Ratio", "Razón"),
            description=_text(
                "Допустимо только для совместимых шкал отношений с осмысленным нулём.",
                "Allowed only for compatible ratio scales with a meaningful zero.",
                "Permitido solo para escalas de razón compatibles con cero significativo.",
            ),
            input_rule="ratio_only",
            minimum_inputs=2,
            maximum_inputs=2,
            output_scale_rule="ratio_or_proportion",
            required_configuration=["input_order", "zero_denominator_rule"],
        ),
        _operation(
            "boolean_all",
            title=_text("Все условия выполнены", "All conditions are met", "Se cumplen todas las condiciones"),
            description=_text("Возвращает да, только если выполнены все заданные условия.", "Returns yes only when every condition is met.", "Devuelve sí solo cuando se cumplen todas las condiciones."),
            input_rule="binary_or_explicit_conditions",
            output_scale_rule="binary",
            required_configuration=["conditions"],
        ),
        _operation(
            "boolean_any",
            title=_text("Выполнено хотя бы одно условие", "Any condition is met", "Se cumple alguna condición"),
            description=_text("Возвращает да, если выполнено хотя бы одно условие.", "Returns yes when at least one condition is met.", "Devuelve sí cuando se cumple al menos una condición."),
            input_rule="binary_or_explicit_conditions",
            output_scale_rule="binary",
            required_configuration=["conditions"],
        ),
        _operation(
            "validated_composite",
            title=_text("Рассчитать валидированную составную шкалу", "Validated composite score", "Puntuación compuesta validada"),
            description=_text(
                "Объединяет пункты только по отдельному зарегистрированному правилу шкалы, включая обратное кодирование и пропуски.",
                "Combines items only through a registered scale rule including reverse coding and missing-data handling.",
                "Combina ítems solo mediante una regla registrada que incluye codificación inversa y datos ausentes.",
            ),
            input_rule="composite_capable_items",
            output_scale_rule="registered_composite_output",
            required_configuration=["composite_definition_id", "item_scoring", "missing_item_rule"],
            minimum_inputs=2,
        ),
        _operation(
            "registered_text_coding",
            title=_text("Применить зарегистрированное кодирование текста", "Registered text coding", "Codificación de texto registrada"),
            description=_text(
                "Создаёт категории или числовые признаки только по версионируемой схеме кодирования.",
                "Produces categories or numeric features only through a versioned coding scheme.",
                "Produce categorías o rasgos numéricos solo mediante un esquema versionado.",
            ),
            input_rule="text_only",
            output_scale_rule="coding_scheme_defined",
            required_configuration=["coding_scheme_id", "coding_scheme_version"],
        ),
        _operation(
            "change_from_baseline",
            title=_text("Изменение относительно исходного измерения", "Change from baseline", "Cambio desde la medición inicial"),
            description=_text("Сравнивает повторное измерение с явно выбранным исходным.", "Compares a repeated measurement with an explicit baseline.", "Compara una medición repetida con una línea base explícita."),
            input_rule="interval_or_ratio",
            output_scale_rule="difference_scale",
            required_configuration=["baseline_rule"],
            temporal_requirement="repeated_measurements",
        ),
        _operation(
            "slope_over_time",
            title=_text("Скорость изменения во времени", "Slope over time", "Pendiente temporal"),
            description=_text("Оценивает изменение числовой величины на единицу времени.", "Estimates numeric change per unit of time.", "Estima el cambio numérico por unidad de tiempo."),
            input_rule="interval_or_ratio",
            output_scale_rule="rate",
            required_configuration=["time_unit", "minimum_observations"],
            temporal_requirement="ordered_repeated_measurements",
        ),
        _operation(
            "registered_calculator",
            title=_text("Зарегистрированный калькулятор", "Registered calculator", "Calculadora registrada"),
            description=_text(
                "Использует отдельный версионируемый алгоритм с собственной проверкой входов и результата.",
                "Uses a separately versioned algorithm with its own input and output validation.",
                "Usa un algoritmo versionado con validación propia de entradas y resultado.",
            ),
            input_rule="calculator_contract_defined",
            output_scale_rule="calculator_contract_defined",
            required_configuration=["calculator_id", "calculator_version"],
        ),
    ]
}


def _binding_scale(binding: dict) -> dict | None:
    return get_scale_definition(binding.get("scale_type"))


def _all(bindings: list[dict], predicate) -> bool:
    return bool(bindings) and all(predicate(_binding_scale(binding)) for binding in bindings)


def _is_categorical(scale: dict | None) -> bool:
    return bool(scale) and scale.get("measurement_level") in {"nominal", "ordinal"}


def _is_ordered(scale: dict | None) -> bool:
    return bool(scale) and (
        scale.get("measurement_level") in {"ordinal", "interval", "ratio"}
        or "rank_based" in scale.get("statistical_capabilities", [])
    )


def _is_metric(scale: dict | None) -> bool:
    return bool(scale) and scale.get("measurement_level") in {"interval", "ratio"}


def _is_ratio(scale: dict | None) -> bool:
    return bool(scale) and scale.get("measurement_level") == "ratio"


def _is_text(scale: dict | None) -> bool:
    return bool(scale) and scale.get("value_structure") == "text"


def _evaluate_input_rule(operation: dict, bindings: list[dict]) -> tuple[bool, list[str]]:
    count = len(bindings)
    reasons = []
    minimum = operation["minimum_inputs"]
    maximum = operation["maximum_inputs"]
    if count < minimum:
        reasons.append("NOT_ENOUGH_SELECTED_QUESTIONS")
    if maximum is not None and count > maximum:
        reasons.append("TOO_MANY_SELECTED_QUESTIONS")
    missing_scale = [
        binding.get("question_code")
        for binding in bindings
        if _binding_scale(binding) is None
    ]
    if (
        missing_scale
        and operation["input_rule"]
        != "calculator_contract_defined"
    ):
        reasons.append("REGISTERED_QUESTION_SCALE_REQUIRED")

    rule = operation["input_rule"]
    compatible = not reasons
    if compatible and rule == "single_supported_value":
        compatible = count == 1 and not _is_text(_binding_scale(bindings[0]))
    elif compatible and rule == "categorical_or_ordered":
        compatible = _all(bindings, _is_categorical)
    elif compatible and rule == "condition_comparable":
        compatible = _all(bindings, lambda scale: scale is not None and scale.get("value_structure") not in {"file_reference", "image", "structured"})
    elif compatible and rule == "multiple_choice_response":
        compatible = count == 1 and str(bindings[0].get("response_type") or "") in {
            "multi_select", "multiple_choice", "checkbox",
        }
    elif compatible and rule == "ordered_or_numeric":
        compatible = _all(bindings, _is_ordered)
    elif compatible and rule == "interval_or_ratio":
        compatible = _all(bindings, _is_metric)
    elif compatible and rule == "ratio_only":
        compatible = _all(bindings, _is_ratio)
    elif compatible and rule == "additive_ratio_or_validated_composite":
        compatible = _all(bindings, _is_ratio)
    elif compatible and rule == "binary_or_explicit_conditions":
        compatible = _all(bindings, lambda scale: bool(scale) and scale.get("numeric_nature") == "binary") or bool(bindings)
    elif compatible and rule == "composite_capable_items":
        compatible = count >= 2 and _all(
            bindings,
            lambda scale: bool(scale) and scale.get("scale_code") in {"likert", "ordinal", "interval", "ratio"},
        )
    elif compatible and rule == "text_only":
        compatible = _all(bindings, _is_text)
    elif compatible and rule == "calculator_contract_defined":
        compatible = bool(bindings)

    if not compatible and not reasons:
        reasons.append("SELECTED_QUESTION_SCALES_INCOMPATIBLE")
    return compatible, reasons


def build_compatible_calculation_options(
    question_bindings: list[dict],
    *,
    repeated_measurements: bool = False,
    ordered_measurements: bool = False,
) -> dict:
    options = []
    for operation in CALCULATION_OPERATIONS.values():
        compatible, reasons = _evaluate_input_rule(operation, question_bindings)
        temporal_requirement = operation["temporal_requirement"]
        if compatible and temporal_requirement in {"repeated_measurements", "ordered_repeated_measurements"} and not repeated_measurements:
            compatible = False
            reasons.append("REPEATED_MEASUREMENTS_REQUIRED")
        if compatible and temporal_requirement == "ordered_repeated_measurements" and not ordered_measurements:
            compatible = False
            reasons.append("ORDERED_MEASUREMENTS_REQUIRED")
        options.append({
            **deepcopy(operation),
            "compatible": compatible,
            "incompatibility_reasons": reasons,
        })
    return {
        "ok": True,
        "registry": {
            "schema_version": PARAMETER_CALCULATION_REGISTRY_SCHEMA_VERSION,
            "definition_schema_version": PARAMETER_CALCULATION_DEFINITION_SCHEMA_VERSION,
        },
        "selected_question_count": len(question_bindings),
        "options": options,
    }


def get_calculation_operation(operation_id: Any) -> dict | None:
    operation = CALCULATION_OPERATIONS.get(str(operation_id or "").strip())
    return deepcopy(operation) if operation is not None else None


def validate_calculation_selection(
    *,
    operation_id: str,
    question_bindings: list[dict],
    configuration: dict | None,
    repeated_measurements: bool,
    ordered_measurements: bool,
    output_scale_type: str | None = None,
) -> dict:
    operation = get_calculation_operation(operation_id)
    if operation is None:
        return {"valid": False, "errors": [{"code": "CALCULATION_OPERATION_NOT_REGISTERED"}]}
    options = build_compatible_calculation_options(
        question_bindings,
        repeated_measurements=repeated_measurements,
        ordered_measurements=ordered_measurements,
    )
    selected = next(item for item in options["options"] if item["operation_id"] == operation_id)
    errors = []
    if not selected["compatible"]:
        errors.append({
            "code": "CALCULATION_OPERATION_INCOMPATIBLE",
            "reasons": selected["incompatibility_reasons"],
        })
    configuration = configuration or {}
    for field in operation["required_configuration"]:
        if configuration.get(field) in (None, "", []):
            errors.append({
                "code": "CALCULATION_CONFIGURATION_REQUIRED",
                "field": field,
            })
    output_rule = operation["output_scale_rule"]
    exact_output_scales = {"binary", "count", "proportion", "rate"}
    if output_rule in exact_output_scales and output_scale_type != output_rule:
        errors.append({
            "code": "CALCULATION_OUTPUT_SCALE_MISMATCH",
            "expected_scale_type": output_rule,
            "actual_scale_type": output_scale_type,
        })
    if output_rule.startswith("inherit"):
        input_scales = {
            binding.get("scale_type") for binding in question_bindings
            if binding.get("scale_type")
        }
        if len(input_scales) == 1:
            expected_scale = next(iter(input_scales))
            if output_scale_type != expected_scale:
                errors.append({
                    "code": "CALCULATION_OUTPUT_SCALE_MISMATCH",
                    "expected_scale_type": expected_scale,
                    "actual_scale_type": output_scale_type,
                })
    return {"valid": not errors, "errors": errors, "operation": selected}
