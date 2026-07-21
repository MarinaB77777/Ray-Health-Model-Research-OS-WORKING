from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from research.repository import OBJECT_STORE_LOCK, load_objects, save_objects


PROJECT_SCHEMA_VERSION = "research-project-workspace-1"
PROJECT_BLOCK_SCHEMA_VERSION = "research-project-block-1"
PROJECT_ENTITY_LINK_SCHEMA_VERSION = "research-project-entity-link-1"
PROJECT_TIME_CONTRACT_VERSION = "research-project-time-1"
SUPPORTED_LANGUAGES = frozenset({"ru", "en", "es"})
PROJECT_STATUSES = frozenset({"draft", "trial", "active"})
BLOCK_LIFECYCLES = frozenset({"connected", "disconnected"})


class ProjectWorkspaceError(Exception):
    def __init__(self, code: str, status_code: int = 422) -> None:
        super().__init__(code)
        self.code = code
        self.status_code = status_code


def utc_iso() -> str:
    return datetime.now(UTC).isoformat()


def _text(value: Any, code: str, *, required: bool = False, maximum: int = 20000) -> str:
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise ProjectWorkspaceError(code)
    normalized = value.strip()
    if required and not normalized:
        raise ProjectWorkspaceError(code)
    if len(normalized) > maximum:
        raise ProjectWorkspaceError(f"{code}_TOO_LONG")
    return normalized


def _language(value: str | None) -> str:
    language = (value or "ru").strip().lower()
    if language not in SUPPORTED_LANGUAGES:
        raise ProjectWorkspaceError("PROJECT_LANGUAGE_UNSUPPORTED")
    return language


def _timezone(value: str | None) -> str:
    candidate = (value or "UTC").strip()
    try:
        ZoneInfo(candidate)
    except ZoneInfoNotFoundError as exc:
        raise ProjectWorkspaceError("PROJECT_TIMEZONE_INVALID") from exc
    return candidate


def _labels(ru: str, en: str, es: str) -> dict[str, str]:
    return {"ru": ru, "en": en, "es": es}


def _field(code: str, field_type: str, ru: str, en: str, es: str, *, required: bool = False) -> dict[str, Any]:
    return {
        "code": code,
        "field_type": field_type,
        "label": _labels(ru, en, es),
        "required": required,
    }


def _action(code: str, kind: str, ru: str, en: str, es: str, *, route: str | None = None,
            capability: str | None = None) -> dict[str, Any]:
    action = {"code": code, "kind": kind, "label": _labels(ru, en, es)}
    if route:
        action["route"] = route
    if capability:
        action["capability"] = capability
    return action


BLOCK_CATALOG: dict[str, dict[str, Any]] = {
    "introduction": {
        "label": _labels("Введение", "Introduction", "Introducción"),
        "purpose": _labels("Научный контекст, актуальность и границы проекта.", "Scientific context, rationale and project scope.", "Contexto científico, justificación y alcance del proyecto."),
        "cardinality": "single",
        "fields": [
            _field("background", "long_text", "Научный контекст", "Scientific background", "Contexto científico"),
            _field("rationale", "long_text", "Почему исследование необходимо", "Research rationale", "Justificación del estudio"),
            _field("scope", "long_text", "Границы исследования", "Study scope", "Alcance del estudio"),
            _field("source_notes", "evidence_links", "Подтверждённые источники", "Verified sources", "Fuentes verificadas"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить введение", "Save introduction", "Guardar introducción"),
            _action("request_scientific_review", "ray_external", "Попросить Рэя подготовить научный обзор", "Ask Ray for a scientific review", "Pedir a Ray una revisión científica", capability="external_scientific_ai"),
            _action("open_sources", "route", "Настроить научные источники", "Configure scientific sources", "Configurar fuentes científicas", route="/ray-settings"),
        ],
    },
    "scientific_context": {
        "label": _labels("Научные основания", "Scientific foundations", "Fundamentos científicos"),
        "purpose": _labels("Проверяемые положения, пробелы и противоречия литературы.", "Testable claims, evidence gaps and contradictions.", "Afirmaciones verificables, vacíos y contradicciones."),
        "cardinality": "single",
        "fields": [
            _field("established_findings", "long_text", "Установленные результаты", "Established findings", "Hallazgos establecidos"),
            _field("evidence_gaps", "long_text", "Пробелы в доказательствах", "Evidence gaps", "Vacíos de evidencia"),
            _field("contradictions", "long_text", "Противоречия", "Contradictions", "Contradicciones"),
            _field("evidence_links", "evidence_links", "Связанные источники", "Linked evidence", "Evidencia vinculada"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить основания", "Save foundations", "Guardar fundamentos"),
            _action("verify_claims", "ray_external", "Проверить утверждения по источникам", "Verify claims against sources", "Verificar afirmaciones con fuentes", capability="external_scientific_ai"),
        ],
    },
    "hypotheses": {
        "label": _labels("Гипотезы", "Hypotheses", "Hipótesis"),
        "purpose": _labels("Фальсифицируемые гипотезы, основания и критерии проверки.", "Falsifiable hypotheses, rationale and test criteria.", "Hipótesis falsables, fundamentos y criterios de prueba."),
        "cardinality": "multiple",
        "fields": [
            _field("hypothesis", "long_text", "Рабочая формулировка гипотезы", "Working hypothesis statement", "Formulación de trabajo de la hipótesis"),
            _field("basis", "long_text", "Научное основание", "Scientific basis", "Base científica"),
            _field("predictions", "long_text", "Проверяемые предсказания", "Testable predictions", "Predicciones comprobables"),
            _field("falsification_criteria", "long_text", "Критерии опровержения", "Falsification criteria", "Criterios de falsación"),
            _field("hypothesis_versions", "entity_links", "Структурированные версии гипотезы", "Structured hypothesis versions", "Versiones estructuradas de la hipótesis"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить гипотезу", "Save hypothesis", "Guardar hipótesis"),
            _action("open_hypothesis_lab", "route", "Открыть лабораторию гипотез", "Open hypothesis laboratory", "Abrir laboratorio de hipótesis", route="/research-lab"),
            _action("search_prior_hypotheses", "ray_external", "Найти проверку сходных гипотез", "Find tests of similar hypotheses", "Buscar pruebas de hipótesis similares", capability="external_scientific_ai"),
            _action("open_parameter_constructor", "route", "Создать измеряемый параметр", "Create a measurable parameter", "Crear un parámetro medible", route="/model-parameter-constructor?mode=parameter"),
        ],
    },
    "variables_mechanisms": {
        "label": _labels("Параметры и механизмы", "Parameters and mechanisms", "Parámetros y mecanismos"),
        "purpose": _labels("Связь гипотез с измеряемыми параметрами и механизмами модели.", "Connect hypotheses to measurable parameters and model mechanisms.", "Conectar hipótesis con parámetros y mecanismos medibles."),
        "cardinality": "single",
        "fields": [
            _field("constructs", "entity_links", "Исследуемые конструкты", "Study constructs", "Constructos del estudio"),
            _field("parameter_links", "entity_links", "Параметры модели", "Model parameters", "Parámetros del modelo"),
            _field("mechanism_links", "entity_links", "Механизмы модели", "Model mechanisms", "Mecanismos del modelo"),
            _field("relationship_notes", "long_text", "Предполагаемые связи", "Expected relationships", "Relaciones esperadas"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить связи", "Save relationships", "Guardar relaciones"),
            _action("open_parameter_editor", "route", "Открыть редактор параметров", "Open parameter editor", "Abrir editor de parámetros", route="/parameter-editor"),
            _action("open_mechanism_editor", "route", "Открыть редактор механизмов", "Open mechanism editor", "Abrir editor de mecanismos", route="/mechanism-editor"),
        ],
    },
    "study_design": {
        "label": _labels("Дизайн исследования", "Study design", "Diseño del estudio"),
        "purpose": _labels("Популяция, выборка, сравнения, смещения и протокол.", "Population, sampling, comparisons, bias and protocol.", "Población, muestreo, comparaciones, sesgos y protocolo."),
        "cardinality": "single",
        "fields": [
            _field("design_type", "choice", "Тип дизайна", "Design type", "Tipo de diseño"),
            _field("population", "long_text", "Целевая популяция", "Target population", "Población objetivo"),
            _field("sampling", "long_text", "Выборка и расчёт объёма", "Sampling and sample-size rationale", "Muestreo y justificación del tamaño"),
            _field("comparisons", "long_text", "Сравнения и контроль", "Comparisons and controls", "Comparaciones y controles"),
            _field("bias_control", "long_text", "Контроль смещений", "Bias control", "Control de sesgos"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить дизайн", "Save design", "Guardar diseño"),
            _action("open_analysis_builder", "route", "Открыть конструктор анализа", "Open analysis builder", "Abrir constructor de análisis", route="/analysis-builder"),
        ],
    },
    "experimental_setup": {
        "label": _labels("Экспериментальная установка", "Experimental setup", "Configuración experimental"),
        "purpose": _labels("Оборудование, сенсоры, игры, камеры и синхронизация времени.", "Equipment, sensors, games, cameras and time synchronization.", "Equipos, sensores, juegos, cámaras y sincronización temporal."),
        "cardinality": "multiple",
        "fields": [
            _field("setup_description", "long_text", "Описание установки", "Setup description", "Descripción de la configuración"),
            _field("instrument_links", "entity_links", "Подключённые инструменты", "Connected instruments", "Instrumentos conectados"),
            _field("calibration", "long_text", "Калибровка и контроль качества", "Calibration and quality control", "Calibración y control de calidad"),
            _field("time_synchronization", "long_text", "Синхронизация с единым временем", "Global time synchronization", "Sincronización con el tiempo global", required=True),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить установку", "Save setup", "Guardar configuración"),
            _action("connect_sensors", "route", "Подключить сенсоры и приборы", "Connect sensors and devices", "Conectar sensores y dispositivos", route="/measurement-setup"),
            _action("open_fiji_integration", "route", "Подключить Fiji для изображений и видео", "Connect Fiji for images and video", "Conectar Fiji para imágenes y vídeo", route="/fiji-integration"),
            _action("prepare_sensor_data", "route", "Настроить подготовку данных", "Configure data preparation", "Configurar preparación de datos", route="/data-editor"),
        ],
    },
    "measurement_plan": {
        "label": _labels("План измерений", "Measurement plan", "Plan de medición"),
        "purpose": _labels("Что, чем, когда и в каких временных срезах измеряется.", "What is measured, how, when and at which time points.", "Qué se mide, cómo, cuándo y en qué momentos."),
        "cardinality": "single",
        "fields": [
            _field("measurement_targets", "entity_links", "Измеряемые параметры", "Measurement targets", "Objetivos de medición"),
            _field("questionnaire_links", "entity_links", "Вопросы и опросники", "Questions and questionnaires", "Preguntas y cuestionarios"),
            _field("schedule", "long_text", "Временные срезы и расписание", "Time points and schedule", "Momentos y calendario", required=True),
            _field("missingness_plan", "long_text", "Обработка пропусков", "Missing-data plan", "Plan de datos faltantes"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить план измерений", "Save measurement plan", "Guardar plan de medición"),
            _action("open_question_editor", "route", "Выбрать или создать вопросы", "Select or create questions", "Seleccionar o crear preguntas", route="/question-editor"),
            _action("open_parameter_editor", "route", "Выбрать параметры", "Select parameters", "Seleccionar parámetros", route="/parameter-editor"),
        ],
    },
    "data_analysis": {
        "label": _labels("Данные и статистический анализ", "Data and statistical analysis", "Datos y análisis estadístico"),
        "purpose": _labels("Подготовка данных, методы, допущения и критерии решений.", "Data preparation, methods, assumptions and decision criteria.", "Preparación de datos, métodos, supuestos y criterios."),
        "cardinality": "single",
        "fields": [
            _field("data_sources", "entity_links", "Источники данных", "Data sources", "Fuentes de datos"),
            _field("preparation_plan", "long_text", "Подготовка и контроль данных", "Preparation and quality control", "Preparación y control de calidad"),
            _field("statistical_methods", "entity_links", "Статистические методы", "Statistical methods", "Métodos estadísticos"),
            _field("assumptions", "long_text", "Допущения и диагностика", "Assumptions and diagnostics", "Supuestos y diagnósticos"),
            _field("decision_rules", "long_text", "Критерии решений", "Decision rules", "Criterios de decisión"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить план анализа", "Save analysis plan", "Guardar plan de análisis"),
            _action("open_data_explorer", "route", "Открыть исследование данных", "Open data explorer", "Abrir explorador de datos", route="/data-preparation"),
            _action("open_analysis_builder", "route", "Настроить статистический анализ", "Configure statistical analysis", "Configurar análisis estadístico", route="/analysis-builder"),
        ],
    },
    "results": {
        "label": _labels("Результаты", "Results", "Resultados"),
        "purpose": _labels("Результаты анализов, оценки неопределённости и проверка гипотез.", "Analysis results, uncertainty estimates and hypothesis tests.", "Resultados, incertidumbre y pruebas de hipótesis."),
        "cardinality": "multiple",
        "fields": [
            _field("result_links", "entity_links", "Связанные результаты", "Linked results", "Resultados vinculados"),
            _field("primary_findings", "long_text", "Основные результаты", "Primary findings", "Hallazgos principales"),
            _field("uncertainty", "long_text", "Неопределённость и устойчивость", "Uncertainty and robustness", "Incertidumbre y robustez"),
            _field("hypothesis_outcomes", "long_text", "Итоги проверки гипотез", "Hypothesis outcomes", "Resultados de las hipótesis"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить результаты", "Save results", "Guardar resultados"),
            _action("open_scientific_results", "route", "Открыть научные результаты", "Open scientific results", "Abrir resultados científicos", route="/scientific-results"),
        ],
    },
    "discussion": {
        "label": _labels("Обсуждение и ограничения", "Discussion and limitations", "Discusión y limitaciones"),
        "purpose": _labels("Интерпретация, альтернативные объяснения, ограничения и переносимость.", "Interpretation, alternatives, limitations and generalizability.", "Interpretación, alternativas, limitaciones y generalización."),
        "cardinality": "single",
        "fields": [
            _field("interpretation", "long_text", "Интерпретация", "Interpretation", "Interpretación"),
            _field("alternative_explanations", "long_text", "Альтернативные объяснения", "Alternative explanations", "Explicaciones alternativas"),
            _field("limitations", "long_text", "Ограничения", "Limitations", "Limitaciones"),
            _field("generalizability", "long_text", "Переносимость результатов", "Generalizability", "Generalización"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить обсуждение", "Save discussion", "Guardar discusión"),
            _action("compare_with_evidence", "ray_external", "Сопоставить с научными источниками", "Compare with scientific evidence", "Comparar con evidencia científica", capability="external_scientific_ai"),
        ],
    },
    "bibliography_citations": {
        "label": _labels("Ссылки и библиография", "Citations and bibliography", "Citas y bibliografía"),
        "purpose": _labels(
            "Структурированные источники, проверка обязательных полей и воспроизводимое форматирование под журнал или другой адрес назначения.",
            "Structured sources, required-field validation and reproducible formatting for a journal or another destination.",
            "Fuentes estructuradas, validación y formato reproducible para una revista u otro destino.",
        ),
        "cardinality": "multiple",
        "fields": [
            _field("source_links", "entity_links", "Зарегистрированные источники", "Registered sources", "Fuentes registradas"),
            _field("target_destination", "long_text", "Журнал или место подачи", "Target journal or destination", "Revista o destino"),
            _field("style_rationale", "long_text", "Требуемый стиль и источник требований", "Required style and source of instructions", "Estilo requerido y fuente de instrucciones"),
            _field("bibliography_versions", "entity_links", "Сохранённые версии библиографии", "Saved bibliography versions", "Versiones guardadas"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить блок библиографии", "Save bibliography block", "Guardar bloque bibliográfico"),
            _action("open_citation_workspace", "route", "Сформировать и проверить ссылки", "Format and validate references", "Formatear y validar referencias", route="/citation-workspace"),
        ],
    },
    "sources_corpus": {
        "label": _labels("Источники, корпус и архив", "Sources, corpus and archive", "Fuentes, corpus y archivo"),
        "purpose": _labels("Критерии отбора, происхождение, критика источников и структура корпуса.", "Selection criteria, provenance, source criticism and corpus structure.", "Criterios de selección, procedencia, crítica de fuentes y estructura del corpus."),
        "cardinality": "multiple",
        "profiles": ["humanities_qualitative", "mixed_methods", "interdisciplinary"],
        "fields": [
            _field("source_scope", "long_text", "Границы и состав корпуса", "Corpus scope and composition", "Alcance y composición del corpus"),
            _field("selection_criteria", "long_text", "Критерии включения и исключения", "Inclusion and exclusion criteria", "Criterios de inclusión y exclusión"),
            _field("provenance", "long_text", "Происхождение и контекст источников", "Source provenance and context", "Procedencia y contexto de las fuentes"),
            _field("source_criticism", "long_text", "Критика и ограничения источников", "Source criticism and limitations", "Crítica y limitaciones de las fuentes"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить описание корпуса", "Save corpus description", "Guardar descripción del corpus"),
            _action("request_source_map", "ray_external", "Попросить Рэя построить карту источников", "Ask Ray to map the sources", "Pedir a Ray un mapa de fuentes", capability="external_scientific_ai"),
        ],
    },
    "interviews_observation": {
        "label": _labels("Интервью и наблюдение", "Interviews and observation", "Entrevistas y observación"),
        "purpose": _labels("Гайд, процедура, контекст, рефлексивность и насыщение данных.", "Guide, procedure, context, reflexivity and data saturation.", "Guía, procedimiento, contexto, reflexividad y saturación."),
        "cardinality": "multiple",
        "profiles": ["humanities_qualitative", "mixed_methods", "interdisciplinary"],
        "fields": [
            _field("method", "choice", "Метод получения материала", "Material collection method", "Método de obtención"),
            _field("guide", "long_text", "Гайд интервью или наблюдения", "Interview or observation guide", "Guía de entrevista u observación"),
            _field("context_protocol", "long_text", "Контекст и протокол проведения", "Context and procedure", "Contexto y procedimiento"),
            _field("reflexivity", "long_text", "Позиция исследователя и рефлексивность", "Researcher position and reflexivity", "Posición del investigador y reflexividad"),
            _field("saturation", "long_text", "Критерий насыщения", "Saturation criterion", "Criterio de saturación"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить протокол", "Save protocol", "Guardar protocolo"),
            _action("open_question_editor", "route", "Создать вопросы интервью", "Create interview questions", "Crear preguntas de entrevista", route="/question-editor"),
        ],
    },
    "qualitative_analysis": {
        "label": _labels("Качественный анализ", "Qualitative analysis", "Análisis cualitativo"),
        "purpose": _labels("Кодирование, категории, интерпретация, согласованность и аудиторский след.", "Coding, categories, interpretation, agreement and audit trail.", "Codificación, categorías, interpretación, concordancia y auditoría."),
        "cardinality": "multiple",
        "profiles": ["humanities_qualitative", "mixed_methods", "interdisciplinary"],
        "fields": [
            _field("analytic_approach", "choice", "Подход к анализу", "Analytic approach", "Enfoque analítico"),
            _field("coding_framework", "long_text", "Схема кодирования", "Coding framework", "Marco de codificación"),
            _field("interpretive_procedure", "long_text", "Процедура интерпретации", "Interpretive procedure", "Procedimiento interpretativo"),
            _field("agreement_strategy", "long_text", "Согласованность кодирования", "Coding agreement strategy", "Estrategia de concordancia"),
            _field("audit_trail", "long_text", "Аудиторский след и мемо", "Audit trail and memos", "Rastro de auditoría y memos"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить план качественного анализа", "Save qualitative analysis plan", "Guardar plan cualitativo"),
            _action("open_data_editor", "route", "Открыть редактор материалов", "Open material editor", "Abrir editor de materiales", route="/data-editor"),
        ],
    },
    "signal_processing": {
        "label": _labels("Обработка сигналов", "Signal processing", "Procesamiento de señales"),
        "purpose": _labels("Частота дискретизации, фильтрация, артефакты, признаки и проверка качества.", "Sampling, filtering, artifacts, features and quality validation.", "Muestreo, filtrado, artefactos, características y calidad."),
        "cardinality": "multiple",
        "profiles": ["quantitative_technical", "mixed_methods", "interdisciplinary"],
        "fields": [
            _field("signal_sources", "entity_links", "Источники сигналов", "Signal sources", "Fuentes de señal"),
            _field("sampling", "long_text", "Дискретизация и временная привязка", "Sampling and time binding", "Muestreo y referencia temporal", required=True),
            _field("filtering", "long_text", "Фильтрация и удаление артефактов", "Filtering and artifact removal", "Filtrado y eliminación de artefactos"),
            _field("feature_extraction", "long_text", "Извлечение признаков", "Feature extraction", "Extracción de características"),
            _field("quality_metrics", "long_text", "Метрики качества", "Quality metrics", "Métricas de calidad"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить обработку сигналов", "Save signal-processing plan", "Guardar procesamiento"),
            _action("open_sensor_data_editor", "route", "Открыть редактор данных сенсоров", "Open sensor data editor", "Abrir editor de sensores", route="/data-editor"),
        ],
    },
    "image_processing_fiji": {
        "label": _labels("Обработка изображений в Fiji", "Fiji image processing", "Procesamiento de imágenes con Fiji"),
        "purpose": _labels(
            "Воспроизводимая интерактивная и пакетная обработка изображений с журналом операций, происхождением и привязкой ко времени.",
            "Reproducible interactive and batch image processing with operation logs, provenance and time binding.",
            "Procesamiento reproducible interactivo y por lotes con registro, procedencia y referencia temporal.",
        ),
        "cardinality": "multiple",
        "profiles": ["quantitative_technical", "mixed_methods", "interdisciplinary"],
        "fields": [
            _field("input_datasets", "entity_links", "Исходные изображения, видео и стеки", "Source images, videos and stacks", "Imágenes, vídeos y pilas de origen"),
            _field("pipeline_definition", "long_text", "Научное основание и последовательность обработки", "Scientific rationale and processing sequence", "Fundamento científico y secuencia de procesamiento"),
            _field("time_binding", "long_text", "Привязка кадров к единому времени", "Frame binding to global time", "Vinculación de fotogramas al tiempo global"),
            _field("processing_runs", "entity_links", "Версии запусков обработки", "Processing run versions", "Versiones de ejecuciones"),
            _field("output_datasets", "entity_links", "Стандартные выходные наборы данных", "Standard output datasets", "Conjuntos de salida estándar"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить блок Fiji", "Save Fiji block", "Guardar bloque Fiji"),
            _action("open_fiji_integration", "route", "Подключить Fiji и настроить обработку", "Connect Fiji and configure processing", "Conectar Fiji y configurar procesamiento", route="/fiji-integration"),
            _action("open_data_editor", "route", "Проверить выходные данные", "Inspect output data", "Inspeccionar datos de salida", route="/data-editor"),
            _action("open_model_training", "route", "Передать данные в обучение модели", "Send data to model training", "Enviar datos al entrenamiento", route="/model-training"),
        ],
    },
    "computational_pipeline": {
        "label": _labels("Вычислительный процесс", "Computational pipeline", "Proceso computacional"),
        "purpose": _labels("Версии данных и кода, окружение, вычисления, проверки и воспроизводимость.", "Data/code versions, environment, computation, checks and reproducibility.", "Versiones, entorno, cálculos, verificaciones y reproducibilidad."),
        "cardinality": "multiple",
        "profiles": ["quantitative_technical", "mixed_methods", "interdisciplinary"],
        "fields": [
            _field("inputs", "entity_links", "Стандартные входные данные", "Standard inputs", "Entradas estándar"),
            _field("pipeline_steps", "long_text", "Шаги вычислительного процесса", "Pipeline steps", "Pasos del proceso"),
            _field("environment", "long_text", "Окружение и зависимости", "Environment and dependencies", "Entorno y dependencias"),
            _field("validation_checks", "long_text", "Автоматические проверки", "Automated checks", "Verificaciones automáticas"),
            _field("outputs", "entity_links", "Стандартные выходные данные", "Standard outputs", "Salidas estándar"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить вычислительный процесс", "Save computational pipeline", "Guardar proceso computacional"),
            _action("open_data_editor", "route", "Открыть преобразование данных", "Open data transformation", "Abrir transformación de datos", route="/data-editor"),
            _action("open_fiji_integration", "route", "Открыть воспроизводимую обработку в Fiji", "Open reproducible Fiji processing", "Abrir procesamiento reproducible en Fiji", route="/fiji-integration"),
            _action("open_analysis_builder", "route", "Открыть конструктор анализа", "Open analysis builder", "Abrir constructor de análisis", route="/analysis-builder"),
        ],
    },
    "model_training": {
        "label": _labels("Обучение модели", "Model training", "Entrenamiento del modelo"),
        "purpose": _labels(
            "Версионированное обучение модели по стандартным входам и эталонной разметке с независимой проверкой.",
            "Versioned model training from standard inputs and reference labels with independent evaluation.",
            "Entrenamiento versionado con entradas estándar, etiquetas de referencia y evaluación independiente.",
        ),
        "cardinality": "multiple",
        "profiles": ["quantitative_technical", "mixed_methods", "interdisciplinary"],
        "fields": [
            _field("training_inputs", "entity_links", "Набор исходных данных", "Training input dataset", "Datos de entrada"),
            _field("reference_labels", "entity_links", "Эталонная разметка", "Reference labels", "Etiquetas de referencia"),
            _field("task_definition", "long_text", "Что должна предсказывать модель", "Model prediction target", "Objetivo de predicción"),
            _field("independence_unit", "long_text", "Единица независимого разделения", "Independent split unit", "Unidad de división independiente"),
            _field("training_run_links", "entity_links", "Версии запусков и моделей", "Training runs and model versions", "Ejecuciones y versiones del modelo"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить блок обучения", "Save training block", "Guardar bloque de entrenamiento"),
            _action("open_model_training", "route", "Настроить и запустить обучение", "Configure and run training", "Configurar y ejecutar entrenamiento", route="/model-training"),
            _action("open_data_editor", "route", "Проверить входные данные", "Inspect input data", "Inspeccionar datos", route="/data-editor"),
        ],
    },
    "simulation_modeling": {
        "label": _labels("Моделирование и симуляция", "Modeling and simulation", "Modelado y simulación"),
        "purpose": _labels("Модель, параметры, начальные условия, сценарии, чувствительность и валидация.", "Model, parameters, initial conditions, scenarios, sensitivity and validation.", "Modelo, parámetros, condiciones, escenarios, sensibilidad y validación."),
        "cardinality": "multiple",
        "profiles": ["quantitative_technical", "mixed_methods", "interdisciplinary"],
        "fields": [
            _field("model_definition", "long_text", "Определение модели", "Model definition", "Definición del modelo"),
            _field("parameter_links", "entity_links", "Параметры и механизмы", "Parameters and mechanisms", "Parámetros y mecanismos"),
            _field("initial_conditions", "long_text", "Начальные и граничные условия", "Initial and boundary conditions", "Condiciones iniciales y de contorno"),
            _field("scenarios", "long_text", "Сценарии", "Scenarios", "Escenarios"),
            _field("sensitivity_validation", "long_text", "Чувствительность и валидация", "Sensitivity and validation", "Sensibilidad y validación"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить модель", "Save model", "Guardar modelo"),
            _action("open_logic_editor", "route", "Открыть редактор логики модели", "Open model logic editor", "Abrir editor de lógica", route="/model-logic-editor"),
            _action("open_mechanism_editor", "route", "Открыть редактор механизмов", "Open mechanism editor", "Abrir editor de mecanismos", route="/mechanism-editor"),
        ],
    },
    "probabilistic_inference": {
        "label": _labels("Вероятностное моделирование и вывод", "Probabilistic modeling and inference", "Modelado e inferencia probabilística"),
        "purpose": _labels("Вероятностная модель, априорные основания, неопределённость, диагностика и прогностическая проверка.", "Probability model, prior rationale, uncertainty, diagnostics and predictive checking.", "Modelo probabilístico, fundamentos previos, incertidumbre, diagnóstico y comprobación predictiva."),
        "cardinality": "multiple",
        "profiles": ["quantitative_technical", "mixed_methods", "interdisciplinary"],
        "fields": [
            _field("estimand", "long_text", "Что именно оценивается", "Target estimand", "Cantidad objetivo", required=True),
            _field("method_links", "entity_links", "Выбранные вероятностные методы", "Selected probabilistic methods", "Métodos probabilísticos seleccionados"),
            _field("prior_rationale", "long_text", "Основание априорных распределений", "Prior-distribution rationale", "Fundamento de distribuciones previas"),
            _field("likelihood_model", "long_text", "Модель данных и функция правдоподобия", "Data and likelihood model", "Modelo de datos y verosimilitud"),
            _field("temporal_dependence", "long_text", "Временная и внутригрупповая зависимость", "Temporal and within-group dependence", "Dependencia temporal e intragrupal"),
            _field("diagnostic_plan", "long_text", "Диагностика, чувствительность и прогностическая проверка", "Diagnostics, sensitivity and predictive checks", "Diagnóstico, sensibilidad y comprobaciones predictivas"),
            _field("decision_rule", "long_text", "Правило научного решения", "Scientific decision rule", "Regla de decisión científica"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить вероятностный план", "Save probabilistic plan", "Guardar plan probabilístico"),
            _action("open_probabilistic_methods", "route", "Выбрать и выполнить вероятностный метод", "Select and run a probabilistic method", "Seleccionar y ejecutar un método probabilístico", route="/probabilistic-methods"),
            _action("open_data_explorer", "route", "Проверить данные и временную структуру", "Check data and temporal structure", "Comprobar datos y estructura temporal", route="/data-preparation"),
        ],
    },
    "ethics_governance": {
        "label": _labels("Этика и управление", "Ethics and governance", "Ética y gobernanza"),
        "purpose": _labels("Согласие, риски, доступ, приватность и воспроизводимость.", "Consent, risk, access, privacy and reproducibility.", "Consentimiento, riesgos, acceso, privacidad y reproducibilidad."),
        "cardinality": "single",
        "fields": [
            _field("ethics_requirements", "long_text", "Этические требования", "Ethics requirements", "Requisitos éticos"),
            _field("consent_plan", "long_text", "Информированное согласие", "Informed consent plan", "Plan de consentimiento informado"),
            _field("data_governance", "long_text", "Доступ и управление данными", "Data access and governance", "Acceso y gobernanza de datos"),
            _field("reproducibility", "long_text", "Воспроизводимость и аудит", "Reproducibility and audit", "Reproducibilidad y auditoría"),
        ],
        "actions": [
            _action("save_block", "save", "Сохранить требования", "Save requirements", "Guardar requisitos"),
            _action("open_consent", "route", "Открыть текущий контур согласия", "Open the current consent workflow", "Abrir el flujo de consentimiento actual", route="/assessment"),
        ],
    },
}


# A project block connects versioned scientific objects through typed ports.  The
# text fields remain available for reasoning and interpretation; they are never
# used as substitutes for an actual registry connection.
ENTITY_FIELD_ACCEPTS: dict[tuple[str, str], list[str]] = {
    ("hypotheses", "hypothesis_versions"): ["hypothesis"],
    ("variables_mechanisms", "constructs"): ["observable_marker", "model_parameter"],
    ("variables_mechanisms", "parameter_links"): ["model_parameter"],
    ("variables_mechanisms", "mechanism_links"): ["mechanism"],
    ("experimental_setup", "instrument_links"): ["measurement_instrument"],
    ("measurement_plan", "measurement_targets"): ["model_parameter", "observable_marker"],
    ("measurement_plan", "questionnaire_links"): ["question", "question_bank"],
    ("data_analysis", "data_sources"): ["measurement_dataset", "questionnaire_result", "parameter_result"],
    ("data_analysis", "statistical_methods"): ["probabilistic_method", "analysis_method"],
    ("results", "result_links"): ["analysis_result", "parameter_result", "hypothesis_result"],
    ("signal_processing", "signal_sources"): ["measurement_instrument", "measurement_dataset"],
    ("image_processing_fiji", "input_datasets"): ["measurement_dataset"],
    ("image_processing_fiji", "processing_runs"): ["image_processing_run"],
    ("image_processing_fiji", "output_datasets"): ["measurement_dataset"],
    ("computational_pipeline", "inputs"): ["measurement_dataset", "questionnaire_result", "parameter_result"],
    ("computational_pipeline", "outputs"): ["analysis_result", "parameter_result", "measurement_dataset"],
    ("model_training", "training_inputs"): ["measurement_dataset"],
    ("model_training", "reference_labels"): ["measurement_dataset"],
    ("model_training", "training_run_links"): ["model_training_run", "trained_model"],
    ("bibliography_citations", "source_links"): ["scientific_source", "citation_record"],
    ("bibliography_citations", "bibliography_versions"): ["citation_collection"],
    ("model_integration", "parameter_links"): ["model_parameter", "mechanism"],
    ("probabilistic_methods", "method_links"): ["probabilistic_method"],
}


# Navigation metadata is deliberately separate from scientific block definitions:
# a block keeps its complete contract while the toolbox can reorganize it without
# migrating project data or changing identifiers.
BLOCK_NAVIGATION: dict[str, tuple[str, str, int]] = {
    "introduction": ("foundations", "common", 10),
    "scientific_context": ("foundations", "common", 20),
    "hypotheses": ("foundations", "common", 30),
    "ethics_governance": ("foundations", "common", 40),
    "variables_mechanisms": ("design", "common", 10),
    "study_design": ("design", "common", 20),
    "measurement_plan": ("design", "common", 30),
    "experimental_setup": ("setup_acquisition", "common", 10),
    "sources_corpus": ("setup_acquisition", "humanities", 20),
    "interviews_observation": ("setup_acquisition", "humanities", 30),
    "signal_processing": ("data_preparation", "technical", 10),
    "image_processing_fiji": ("data_preparation", "technical", 20),
    "computational_pipeline": ("data_preparation", "technical", 30),
    "data_analysis": ("analysis_modeling", "common", 10),
    "qualitative_analysis": ("analysis_modeling", "humanities", 20),
    "probabilistic_inference": ("analysis_modeling", "technical", 30),
    "simulation_modeling": ("analysis_modeling", "technical", 40),
    "model_training": ("analysis_modeling", "technical", 50),
    "results": ("results_interpretation", "common", 10),
    "discussion": ("results_interpretation", "common", 20),
    "bibliography_citations": ("results_interpretation", "common", 30),
}

NAVIGATION_STAGES: dict[str, dict[str, Any]] = {
    "foundations": {"order": 10, "label": _labels("Научные основания", "Scientific foundations", "Fundamentos científicos")},
    "design": {"order": 20, "label": _labels("Проектирование исследования", "Study design", "Diseño del estudio")},
    "setup_acquisition": {"order": 30, "label": _labels("Установка и получение материала", "Setup and data acquisition", "Configuración y obtención de datos")},
    "data_preparation": {"order": 40, "label": _labels("Подготовка и преобразование данных", "Data preparation and transformation", "Preparación y transformación de datos")},
    "analysis_modeling": {"order": 50, "label": _labels("Анализ и моделирование", "Analysis and modeling", "Análisis y modelado")},
    "results_interpretation": {"order": 60, "label": _labels("Результаты и интерпретация", "Results and interpretation", "Resultados e interpretación")},
}

NAVIGATION_TRACKS: dict[str, dict[str, Any]] = {
    "common": {"order": 10, "label": _labels("Общее научное ядро", "Common scientific core", "Núcleo científico común")},
    "technical": {"order": 20, "label": _labels("Технические методы", "Technical methods", "Métodos técnicos")},
    "humanities": {"order": 30, "label": _labels("Гуманитарные и качественные методы", "Humanities and qualitative methods", "Métodos humanísticos y cualitativos")},
}


def block_catalog(language: str = "ru", research_profiles: list[str] | None = None) -> dict[str, Any]:
    lang = _language(language)
    selected_profiles = {str(item) for item in (research_profiles or [])}
    broad_profile = bool(selected_profiles & {"mixed_methods", "interdisciplinary"})
    blocks = []
    for code, definition in BLOCK_CATALOG.items():
        item = deepcopy(definition)
        item["code"] = code
        item["label"] = item["label"][lang]
        item["purpose"] = item["purpose"][lang]
        recommended_for = set(item.get("profiles") or [])
        item["recommended"] = bool(selected_profiles) and (
            broad_profile or not recommended_for or bool(selected_profiles & recommended_for)
        )
        stage_code, track_code, block_order = BLOCK_NAVIGATION.get(code, ("design", "common", 999))
        stage = NAVIGATION_STAGES[stage_code]
        track = NAVIGATION_TRACKS[track_code]
        item["navigation"] = {
            "schema_version": "research-project-block-navigation-1",
            "stage_code": stage_code,
            "stage_label": stage["label"][lang],
            "stage_order": stage["order"],
            "track_code": track_code,
            "track_label": track["label"][lang],
            "track_order": track["order"],
            "block_order": block_order,
        }
        for field in item["fields"]:
            field["label"] = field["label"][lang]
            accepted = ENTITY_FIELD_ACCEPTS.get((code, field["code"]))
            if accepted:
                field["connection_spec"] = {
                    "schema_version": "research-project-port-1",
                    "accepted_entity_types": accepted,
                    "cardinality": "many",
                    "version_binding": "exact_registered_version",
                    "status_policy": "draft_trial_active_visible_status_preserved",
                    "time_contract_required_for_measurements": True,
                }
        for action in item["actions"]:
            action["label"] = action["label"][lang]
            if action["kind"] == "ray_external":
                action["available"] = False
                action["unavailable_reason"] = "EXTERNAL_SCIENTIFIC_AI_NOT_CONNECTED_UNTIL_POST_PILOT"
            else:
                action["available"] = True
        blocks.append(item)
    return {
        "schema_version": PROJECT_BLOCK_SCHEMA_VERSION,
        "language": lang,
        "navigation_schema_version": "research-project-block-navigation-1",
        "stages": [
            {"code": code, "label": value["label"][lang], "order": value["order"]}
            for code, value in sorted(NAVIGATION_STAGES.items(), key=lambda pair: pair[1]["order"])
        ],
        "tracks": [
            {"code": code, "label": value["label"][lang], "order": value["order"]}
            for code, value in sorted(NAVIGATION_TRACKS.items(), key=lambda pair: pair[1]["order"])
        ],
        "blocks": blocks,
    }


def _event(event_type: str, actor_account_id: str, **details: Any) -> dict[str, Any]:
    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "actor_account_id": actor_account_id,
        "occurred_at": utc_iso(),
        "details": details,
    }


def _project_index(objects: list[dict[str, Any]], project_id: str, owner: str) -> int:
    for index, item in enumerate(objects):
        if item.get("id") == project_id and item.get("object_type") == "project":
            if item.get("owner") != owner:
                raise ProjectWorkspaceError("PROJECT_ACCESS_DENIED", 403)
            return index
    raise ProjectWorkspaceError("PROJECT_NOT_FOUND", 404)


def project_compatibility(project: dict[str, Any]) -> dict[str, Any]:
    if project.get("schema_version") == PROJECT_SCHEMA_VERSION and isinstance(project.get("blocks"), list):
        return {"status": "compatible", "requires_rework": False}
    return {
        "status": "legacy_requires_explicit_migration",
        "requires_rework": True,
        "reason": "PROJECT_PRECEDES_MODULAR_WORKSPACE_CONTRACT",
        "legacy_content_preserved": True,
    }


def create_project(*, owner: str, authorship: dict[str, Any], title: str,
                   research_question: str = "", goal: str = "", language: str = "ru",
                   display_timezone: str = "UTC") -> dict[str, Any]:
    title = _text(title, "PROJECT_TITLE_REQUIRED", required=True, maximum=300)
    research_question = _text(research_question, "PROJECT_RESEARCH_QUESTION_INVALID")
    goal = _text(goal, "PROJECT_GOAL_INVALID")
    lang = _language(language)
    timezone = _timezone(display_timezone)
    timestamp = utc_iso()
    project_id = str(uuid4())
    project = {
        "id": project_id,
        "object_type": "project",
        "schema_version": PROJECT_SCHEMA_VERSION,
        "version": 1,
        "owner": owner,
        "status": "draft",
        "title": title,
        "description": goal,
        "research_question": research_question,
        "language": lang,
        "authorship": deepcopy(authorship),
        "global_time_contract": {
            "contract_version": PROJECT_TIME_CONTRACT_VERSION,
            "axis": "UTC",
            "scale_type": "datetime",
            "display_timezone": timezone,
            "event_clock_source": "server_utc",
            "measurement_synchronization_status": "not_configured",
        },
        "blocks": [],
        "block_order": [],
        "active_block_id": None,
        "created_at": timestamp,
        "updated_at": timestamp,
        "audit_log": [_event("project_created", owner, schema_version=PROJECT_SCHEMA_VERSION)],
        "validation": {
            "status": "draft_incomplete" if not research_question else "draft_not_validated",
            "issues": ([{"field": "research_question", "code": "SCIENTIFIC_QUESTION_NOT_YET_DEFINED"}]
                       if not research_question else []),
        },
    }
    with OBJECT_STORE_LOCK:
        objects = load_objects()
        objects.append(project)
        save_objects(objects)
    return deepcopy(project)


def list_projects(owner: str) -> list[dict[str, Any]]:
    projects = []
    for item in load_objects():
        if item.get("object_type") != "project" or item.get("owner") != owner:
            continue
        copy = deepcopy(item)
        copy["workspace_compatibility"] = project_compatibility(copy)
        projects.append(copy)
    return projects


def get_project(project_id: str, owner: str) -> dict[str, Any]:
    objects = load_objects()
    project = deepcopy(objects[_project_index(objects, project_id, owner)])
    project["workspace_compatibility"] = project_compatibility(project)
    return project


def update_project(project_id: str, owner: str, changes: dict[str, Any]) -> dict[str, Any]:
    allowed = {"title", "description", "research_question", "language", "status", "active_block_id"}
    unknown = set(changes) - allowed
    if unknown:
        raise ProjectWorkspaceError("PROJECT_UPDATE_FIELDS_UNSUPPORTED:" + ",".join(sorted(unknown)))
    with OBJECT_STORE_LOCK:
        objects = load_objects()
        index = _project_index(objects, project_id, owner)
        project = deepcopy(objects[index])
        if project_compatibility(project)["requires_rework"]:
            raise ProjectWorkspaceError("LEGACY_PROJECT_REQUIRES_EXPLICIT_MIGRATION", 409)
        if "title" in changes:
            project["title"] = _text(changes["title"], "PROJECT_TITLE_REQUIRED", required=True, maximum=300)
        if "description" in changes:
            project["description"] = _text(changes["description"], "PROJECT_GOAL_INVALID")
        if "research_question" in changes:
            project["research_question"] = _text(changes["research_question"], "PROJECT_RESEARCH_QUESTION_INVALID")
        if "language" in changes:
            project["language"] = _language(changes["language"])
        if "status" in changes:
            status = str(changes["status"]).lower()
            if status not in PROJECT_STATUSES:
                raise ProjectWorkspaceError("PROJECT_STATUS_UNSUPPORTED")
            project["status"] = status
        if "active_block_id" in changes:
            block_id = changes["active_block_id"]
            if block_id is not None and not any(block.get("block_id") == block_id and block.get("lifecycle") == "connected" for block in project["blocks"]):
                raise ProjectWorkspaceError("ACTIVE_PROJECT_BLOCK_NOT_CONNECTED")
            project["active_block_id"] = block_id
        project["version"] = int(project.get("version") or 0) + 1
        project["updated_at"] = utc_iso()
        project.setdefault("audit_log", []).append(_event("project_updated", owner, fields=sorted(changes)))
        objects[index] = project
        save_objects(objects)
    return deepcopy(project)


def connect_block(project_id: str, owner: str, block_type: str) -> dict[str, Any]:
    definition = BLOCK_CATALOG.get(block_type)
    if definition is None:
        raise ProjectWorkspaceError("PROJECT_BLOCK_TYPE_UNSUPPORTED")
    with OBJECT_STORE_LOCK:
        objects = load_objects()
        index = _project_index(objects, project_id, owner)
        project = deepcopy(objects[index])
        if project_compatibility(project)["requires_rework"]:
            raise ProjectWorkspaceError("LEGACY_PROJECT_REQUIRES_EXPLICIT_MIGRATION", 409)
        connected = [item for item in project["blocks"] if item.get("block_type") == block_type and item.get("lifecycle") == "connected"]
        if definition["cardinality"] == "single" and connected:
            project["active_block_id"] = connected[0]["block_id"]
            project["updated_at"] = utc_iso()
            objects[index] = project
            save_objects(objects)
            return deepcopy(project)
        timestamp = utc_iso()
        block_id = str(uuid4())
        block = {
            "block_id": block_id,
            "schema_version": PROJECT_BLOCK_SCHEMA_VERSION,
            "block_type": block_type,
            "revision": 1,
            "lifecycle": "connected",
            "content": {
                field["code"]: ([] if field["field_type"] in {"entity_links", "evidence_links"} else "")
                for field in definition["fields"]
            },
            "entity_links": [],
            "evidence_links": [],
            "connected_at": timestamp,
            "updated_at": timestamp,
            "validation": {"valid": False, "issues": [{"code": "BLOCK_NOT_REVIEWED"}]},
        }
        project["blocks"].append(block)
        project["block_order"].append(block_id)
        project["active_block_id"] = block_id
        project["version"] += 1
        project["updated_at"] = timestamp
        project["audit_log"].append(_event("project_block_connected", owner, block_id=block_id, block_type=block_type))
        objects[index] = project
        save_objects(objects)
    return deepcopy(project)


def connect_entity(
    project_id: str,
    owner: str,
    block_id: str,
    *,
    field_code: str,
    entity: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(entity, dict):
        raise ProjectWorkspaceError("PROJECT_ENTITY_REFERENCE_MUST_BE_OBJECT")
    with OBJECT_STORE_LOCK:
        objects = load_objects()
        index = _project_index(objects, project_id, owner)
        project = deepcopy(objects[index])
        if project_compatibility(project)["requires_rework"]:
            raise ProjectWorkspaceError("LEGACY_PROJECT_REQUIRES_EXPLICIT_MIGRATION", 409)
        block = next((item for item in project["blocks"] if item.get("block_id") == block_id), None)
        if block is None:
            raise ProjectWorkspaceError("PROJECT_BLOCK_NOT_FOUND", 404)
        if block.get("lifecycle") != "connected":
            raise ProjectWorkspaceError("PROJECT_BLOCK_IS_DISCONNECTED", 409)
        accepted = ENTITY_FIELD_ACCEPTS.get((block["block_type"], field_code))
        if not accepted:
            raise ProjectWorkspaceError("PROJECT_BLOCK_FIELD_IS_NOT_A_CONNECTION_PORT")
        entity_type = _text(entity.get("entity_type"), "PROJECT_ENTITY_TYPE_REQUIRED", required=True, maximum=80)
        if entity_type not in accepted:
            raise ProjectWorkspaceError("PROJECT_ENTITY_TYPE_INCOMPATIBLE_WITH_PORT")
        registry_id = _text(entity.get("registry_id"), "PROJECT_ENTITY_REGISTRY_ID_REQUIRED", required=True, maximum=500)
        version = entity.get("version")
        if version in (None, ""):
            raise ProjectWorkspaceError("PROJECT_ENTITY_VERSION_REQUIRED")
        status = _text(entity.get("status"), "PROJECT_ENTITY_STATUS_REQUIRED", required=True, maximum=40)
        display_name = _text(entity.get("display_name"), "PROJECT_ENTITY_DISPLAY_NAME_REQUIRED", required=True, maximum=500)
        reference_key = f"{entity_type}:{registry_id}:{version}"
        existing = next((item for item in block.get("entity_links", []) if item.get("reference_key") == reference_key and item.get("field_code") == field_code and item.get("lifecycle") == "connected"), None)
        if existing is None:
            now = utc_iso()
            reference = {
                "schema_version": PROJECT_ENTITY_LINK_SCHEMA_VERSION,
                "link_id": str(uuid4()),
                "reference_key": reference_key,
                "field_code": field_code,
                "entity_type": entity_type,
                "registry_id": registry_id,
                "version": deepcopy(version),
                "status": status,
                "display_name": display_name,
                "source_schema_version": entity.get("source_schema_version"),
                "source_route": entity.get("source_route"),
                "time_contract": deepcopy(entity.get("time_contract")),
                "lifecycle": "connected",
                "connected_at": now,
                "connected_by": owner,
            }
            block.setdefault("entity_links", []).append(reference)
            block.setdefault("content", {})[field_code] = [
                item["link_id"] for item in block["entity_links"]
                if item.get("field_code") == field_code and item.get("lifecycle") == "connected"
            ]
            block["revision"] = int(block.get("revision") or 0) + 1
            block["updated_at"] = now
            project["version"] += 1
            project["updated_at"] = now
            project["active_block_id"] = block_id
            project["audit_log"].append(_event("project_entity_connected", owner, block_id=block_id, field_code=field_code, reference_key=reference_key))
            objects[index] = project
            save_objects(objects)
    return deepcopy(project)


def disconnect_entity(project_id: str, owner: str, block_id: str, link_id: str) -> dict[str, Any]:
    with OBJECT_STORE_LOCK:
        objects = load_objects()
        index = _project_index(objects, project_id, owner)
        project = deepcopy(objects[index])
        block = next((item for item in project.get("blocks", []) if item.get("block_id") == block_id), None)
        if block is None:
            raise ProjectWorkspaceError("PROJECT_BLOCK_NOT_FOUND", 404)
        link = next((item for item in block.get("entity_links", []) if item.get("link_id") == link_id), None)
        if link is None:
            raise ProjectWorkspaceError("PROJECT_ENTITY_LINK_NOT_FOUND", 404)
        if link.get("lifecycle") == "connected":
            now = utc_iso()
            link["lifecycle"] = "disconnected"
            link["disconnected_at"] = now
            link["disconnected_by"] = owner
            field_code = link["field_code"]
            block.setdefault("content", {})[field_code] = [
                item["link_id"] for item in block["entity_links"]
                if item.get("field_code") == field_code and item.get("lifecycle") == "connected"
            ]
            block["revision"] = int(block.get("revision") or 0) + 1
            block["updated_at"] = now
            project["version"] += 1
            project["updated_at"] = now
            project["audit_log"].append(_event("project_entity_disconnected_reference_preserved", owner, block_id=block_id, link_id=link_id))
            objects[index] = project
            save_objects(objects)
    return deepcopy(project)


def update_block(project_id: str, owner: str, block_id: str, content: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(content, dict):
        raise ProjectWorkspaceError("PROJECT_BLOCK_CONTENT_MUST_BE_OBJECT")
    with OBJECT_STORE_LOCK:
        objects = load_objects()
        index = _project_index(objects, project_id, owner)
        project = deepcopy(objects[index])
        if project_compatibility(project)["requires_rework"]:
            raise ProjectWorkspaceError("LEGACY_PROJECT_REQUIRES_EXPLICIT_MIGRATION", 409)
        block = next((item for item in project["blocks"] if item.get("block_id") == block_id), None)
        if block is None:
            raise ProjectWorkspaceError("PROJECT_BLOCK_NOT_FOUND", 404)
        if block.get("lifecycle") != "connected":
            raise ProjectWorkspaceError("PROJECT_BLOCK_IS_DISCONNECTED", 409)
        definition = BLOCK_CATALOG[block["block_type"]]
        fields = {field["code"]: field for field in definition["fields"]}
        unknown = set(content) - set(fields)
        if unknown:
            raise ProjectWorkspaceError("PROJECT_BLOCK_FIELDS_UNSUPPORTED:" + ",".join(sorted(unknown)))
        normalized = dict(block.get("content") or {})
        for code, value in content.items():
            if isinstance(value, list):
                if not all(isinstance(item, str) for item in value):
                    raise ProjectWorkspaceError("PROJECT_BLOCK_LIST_VALUES_MUST_BE_TEXT")
                normalized[code] = [item.strip() for item in value if item.strip()]
            else:
                normalized[code] = _text(value, f"PROJECT_BLOCK_FIELD_INVALID:{code}")
        issues = []
        for field in definition["fields"]:
            if field.get("required") and not normalized.get(field["code"]):
                issues.append({"field": field["code"], "code": "REQUIRED_BLOCK_FIELD_EMPTY"})
        block["content"] = normalized
        block["revision"] = int(block.get("revision") or 0) + 1
        block["updated_at"] = utc_iso()
        block["validation"] = {"valid": not issues, "issues": issues}
        project["active_block_id"] = block_id
        project["version"] += 1
        project["updated_at"] = block["updated_at"]
        project["audit_log"].append(_event("project_block_updated", owner, block_id=block_id, revision=block["revision"]))
        objects[index] = project
        save_objects(objects)
    return deepcopy(project)


def disconnect_block(project_id: str, owner: str, block_id: str) -> dict[str, Any]:
    with OBJECT_STORE_LOCK:
        objects = load_objects()
        index = _project_index(objects, project_id, owner)
        project = deepcopy(objects[index])
        if project_compatibility(project)["requires_rework"]:
            raise ProjectWorkspaceError("LEGACY_PROJECT_REQUIRES_EXPLICIT_MIGRATION", 409)
        block = next((item for item in project["blocks"] if item.get("block_id") == block_id), None)
        if block is None:
            raise ProjectWorkspaceError("PROJECT_BLOCK_NOT_FOUND", 404)
        block["lifecycle"] = "disconnected"
        block["disconnected_at"] = utc_iso()
        block["revision"] = int(block.get("revision") or 0) + 1
        if project.get("active_block_id") == block_id:
            project["active_block_id"] = next((item["block_id"] for item in project["blocks"] if item.get("lifecycle") == "connected" and item.get("block_id") != block_id), None)
        project["version"] += 1
        project["updated_at"] = block["disconnected_at"]
        project["audit_log"].append(_event("project_block_disconnected_content_preserved", owner, block_id=block_id))
        objects[index] = project
        save_objects(objects)
    return deepcopy(project)
