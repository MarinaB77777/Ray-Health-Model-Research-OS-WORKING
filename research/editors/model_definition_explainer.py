from __future__ import annotations

from copy import deepcopy
from typing import Any

from research.editors.model_entity_classification import enrich_model_entity


EXPLANATION_SCHEMA_VERSION = "ray-model-definition-explanation-1"
SUPPORTED_LANGUAGES = {"ru", "en", "es"}


TEXT = {
    "ru": {
        "no_definition": "Научное определение пока не зарегистрировано.",
        "current_output": "Система сейчас формирует результат «{title}».",
        "calculator": "Результат берётся из калькулятора {calculator}, версия {version}, по пути {path}.",
        "formula": "Зарегистрированное правило расчёта: {formula}.",
        "no_formula": "Точная формула и её вычислительные входы в реестре не описаны; Рэй не подменяет их догадкой.",
        "scale": "Результат имеет шкалу «{scale}» и тип значения «{value_type}»{range}.",
        "time": "Каждое измерение привязано к единому времени; режим агрегации: {aggregation}{window}.",
        "missing": "При недостаточности данных применяется правило «{rule}».",
        "inputs": "Зарегистрированные входы: {inputs}.",
        "no_inputs": "Входы расчёта в текущем контракте не перечислены.",
        "what": "Что считается сейчас",
        "how": "Как считается сейчас",
        "known": "Что подтверждено контрактом",
        "gaps": "Что необходимо определить",
    },
    "en": {
        "no_definition": "A scientific construct definition has not yet been registered.",
        "current_output": "The system currently produces the result “{title}”.",
        "calculator": "The result is read from calculator {calculator}, version {version}, at path {path}.",
        "formula": "Registered calculation rule: {formula}.",
        "no_formula": "The exact formula and computational inputs are not described in the registry; Ray does not replace them with a guess.",
        "scale": "The result uses the “{scale}” scale and value type “{value_type}”{range}.",
        "time": "Every measurement is linked to the common time reference; aggregation: {aggregation}{window}.",
        "missing": "When data are insufficient, the rule “{rule}” is applied.",
        "inputs": "Registered inputs: {inputs}.",
        "no_inputs": "Calculation inputs are not listed in the current contract.",
        "what": "What is calculated now",
        "how": "How it is calculated now",
        "known": "What the contract confirms",
        "gaps": "What still needs to be defined",
    },
    "es": {
        "no_definition": "Todavía no se ha registrado una definición científica del constructo.",
        "current_output": "Actualmente el sistema produce el resultado «{title}».",
        "calculator": "El resultado se obtiene de la calculadora {calculator}, versión {version}, en la ruta {path}.",
        "formula": "Regla de cálculo registrada: {formula}.",
        "no_formula": "La fórmula exacta y sus entradas computacionales no están descritas en el registro; Ray no las sustituye por una conjetura.",
        "scale": "El resultado usa la escala «{scale}» y el tipo de valor «{value_type}»{range}.",
        "time": "Cada medición está vinculada a la referencia temporal común; agregación: {aggregation}{window}.",
        "missing": "Cuando los datos son insuficientes se aplica la regla «{rule}».",
        "inputs": "Entradas registradas: {inputs}.",
        "no_inputs": "Las entradas del cálculo no figuran en el contrato actual.",
        "what": "Qué se calcula ahora",
        "how": "Cómo se calcula ahora",
        "known": "Qué confirma el contrato",
        "gaps": "Qué falta por definir",
    },
}


HUMAN_CODES = {
    "existing_calculator_output": {"ru": "готовый результат зарегистрированного калькулятора", "en": "registered calculator output", "es": "resultado de una calculadora registrada"},
    "single_observation": {"ru": "одно наблюдение", "en": "single observation", "es": "una observación"},
    "not_enough_data": {"ru": "недостаточно данных", "en": "not enough data", "es": "datos insuficientes"},
    "binary": {"ru": "два состояния", "en": "two-state", "es": "dos estados"},
    "nominal": {"ru": "категории без порядка", "en": "unordered categories", "es": "categorías sin orden"},
    "ordinal": {"ru": "упорядоченные уровни", "en": "ordered levels", "es": "niveles ordenados"},
    "continuous": {"ru": "непрерывная числовая", "en": "continuous numeric", "es": "numérica continua"},
    "structured": {"ru": "составной структурированный результат", "en": "structured composite result", "es": "resultado compuesto estructurado"},
}


def localized(value: Any, lang: str, fallback: str = "") -> str:
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("en") or value.get("ru") or value.get("es") or fallback)
    return str(value if value not in (None, "") else fallback)


def human_code(value: Any, lang: str) -> str:
    code = str(value or "").strip()
    if code in HUMAN_CODES:
        return HUMAN_CODES[code][lang]
    return code.replace("_", " ").replace(".", " → ") if code else "—"


def _registered_inputs(definition: dict, lang: str) -> list[str]:
    values: list[str] = []
    for mapping in definition.get("question_input_mappings") or []:
        if not isinstance(mapping, dict):
            continue
        label = localized(mapping.get("title"), lang) or mapping.get("question_code") or mapping.get("input_code")
        if label:
            values.append(str(label))
    calculation = definition.get("calculation_design") or {}
    for component in calculation.get("components") or []:
        if isinstance(component, dict):
            label = localized(component.get("title"), lang) or component.get("parameter_code") or component.get("component_code")
        else:
            label = component
        if label and str(label) not in values:
            values.append(str(label))
    return values


def _formula(definition: dict) -> str:
    design = definition.get("calculation_design") or {}
    expression = design.get("expression")
    if isinstance(expression, dict):
        return str(expression.get("human_readable") or expression.get("expression") or expression.get("formula") or "").strip()
    return str(expression or definition.get("formula") or "").strip()


def explain_model_definition(definition: dict, lang: str = "ru") -> dict:
    lang = lang if lang in SUPPORTED_LANGUAGES else "ru"
    t = TEXT[lang]
    entity = enrich_model_entity(definition)
    title = localized(entity.get("title"), lang, entity.get("parameter_code") or "—")
    meaning = entity.get("meaning") or {}
    construct = localized(meaning.get("construct_definition"), lang)
    represented = localized(meaning.get("what_is_represented"), lang)
    calculation = entity.get("calculation") or {}
    design = entity.get("calculation_design") or {}
    temporal = entity.get("temporal_design") or {}
    missing_rule = (design.get("missing_data_rule") or {}).get("on_insufficient_data")
    scale = (entity.get("output_scale") or {}).get("scale_type") or entity.get("scale_type")
    value_schema = entity.get("value_schema") or {}
    value_type = (entity.get("output_scale") or {}).get("value_type") or entity.get("value_type")
    minimum, maximum, unit = value_schema.get("minimum"), value_schema.get("maximum"), value_schema.get("unit")
    range_text = ""
    if minimum is not None or maximum is not None or unit:
        range_text = f" ({minimum if minimum is not None else '…'}–{maximum if maximum is not None else '…'}{(' ' + str(unit)) if unit else ''})"
    formula = _formula(entity)
    inputs = _registered_inputs(entity, lang)
    path = calculation.get("value_path")
    calculator = calculation.get("calculator_id") or calculation.get("model_id")
    calc_version = calculation.get("calculation_version") or "—"
    window = temporal.get("time_window") or {}
    window_text = ""
    if window.get("value") is not None:
        window_text = f", {window.get('value')} {human_code(window.get('unit'), lang)}"

    what_parts = [t["current_output"].format(title=title)]
    if construct:
        what_parts.append(construct)
    elif represented:
        what_parts.append(represented)
    else:
        what_parts.append(t["no_definition"])
    what_parts.append(t["scale"].format(scale=human_code(scale, lang), value_type=human_code(value_type, lang), range=range_text))

    how_parts = []
    if formula:
        how_parts.append(t["formula"].format(formula=formula))
    elif calculator and path:
        how_parts.append(t["calculator"].format(calculator=calculator, version=calc_version, path=human_code(path, lang)))
        how_parts.append(t["no_formula"])
    else:
        how_parts.append(t["no_formula"])
    how_parts.append(t["inputs"].format(inputs=", ".join(inputs)) if inputs else t["no_inputs"])
    how_parts.append(t["time"].format(aggregation=human_code(temporal.get("aggregation"), lang), window=window_text))
    if missing_rule:
        how_parts.append(t["missing"].format(rule=human_code(missing_rule, lang)))

    missing_fields = []
    if not construct:
        missing_fields.append("meaning.construct_definition")
    if not represented:
        missing_fields.append("meaning.what_is_represented")
    if not inputs:
        missing_fields.append("calculation_design.components_or_question_inputs")
    if not formula:
        missing_fields.append("calculation_design.expression")
    if not scale:
        missing_fields.append("output_scale")
    if not temporal:
        missing_fields.append("temporal_design")

    if not missing_fields:
        completeness = "complete"
    elif calculator and path and scale and temporal:
        completeness = "trace_only"
    else:
        completeness = "partial"

    classification = entity["entity_classification"]
    ray_statement = "\n\n".join((f"{t['what']}:\n" + " ".join(what_parts), f"{t['how']}:\n" + " ".join(how_parts)))
    return {
        "schema_version": EXPLANATION_SCHEMA_VERSION,
        "language": lang,
        "parameter_code": entity.get("parameter_code"),
        "definition_version": entity.get("definition_version"),
        "entity_classification": classification,
        "title": title,
        "what_is_calculated": " ".join(what_parts),
        "how_it_is_calculated": " ".join(how_parts),
        "ray_statement": ray_statement,
        "completeness": completeness,
        "missing_fields": missing_fields,
        "contract_evidence": {
            "calculator_id": calculator,
            "calculation_version": calc_version,
            "value_path": path,
            "scale_type": scale,
            "temporal_contract_present": bool(temporal),
            "formula_registered": bool(formula),
            "registered_inputs": deepcopy(inputs),
        },
        "draft_seed": {
            "construct_definition": construct,
            "what_is_represented": represented,
            "current_implementation_note": ray_statement,
            "requires_human_scientific_review": True,
        },
    }
