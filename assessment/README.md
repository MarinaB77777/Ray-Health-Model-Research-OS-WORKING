

Assessment Platform Architecture — Checkpoint v1

Assessment Platform
│
├── Assessment Engine
│   ├── runner.py
│   ├── renderer.py
│   ├── pipeline.py
│   ├── scoring_engine.py
│   ├── analysis_engine.py
│   ├── forecast_engine.py
│   └── summary_engine.py
│
├── registry.py
│       (legacy assessments)
│
├── study_registry.py
│       (new modular studies)
│
└── studies/




Архитектурные принципы



1.


Assessment Engine не знает исследования.

Он знает только
study_id




2.


Каждое исследование полностью живет в своей папке.
study/
    metadata.py
    questions_*.py
    routing.py
    scoring.py
    analysis.py
    forecast.py
    summary.py
    service.py




3.


Pipeline универсальный.
Answers

↓

Scoring

↓

Analysis

↓

Forecast

↓

Summary




4.


Summary никогда не получает ответы участника.

Только Forecast.




5.


Question — частный случай Assessment Item.

В будущем поддерживаются
Question
Game
Image
Video
Sensor
Camera
Instruction
VR
Reaction Test
Drag&Drop




6.


Study описывает исследование.

Assessment Engine выполняет исследование.




7.


Добавление нового исследования не требует изменения Engine.

Достаточно:
создать папку исследования

↓

зарегистрировать Study




8.


Legacy registry сохраняется.

Новая архитектура развивается параллельно без поломки существующей системы.




Следующий этап

Study
      │
      ├── Metadata
      ├── Item Provider
      ├── Routing
      ├── Pipeline
      ├── Analysis
      ├── Forecast
      └── Summary


Я бы ввёл для проекта правило:

Ни один новый модуль исследования не имеет права обращаться напрямую к движку.

То есть:

исследование не импортирует ScoringEngine, AnalysisEngine, ForecastEngine и т.д.;
оно описывает только свои metadata, items, routing, scoring, analysis, forecast, summary;
всё остальное делает AssessmentPipeline.

