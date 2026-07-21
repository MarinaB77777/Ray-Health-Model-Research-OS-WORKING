# Research Entity Registry Contract v1

## Purpose

This document defines the universal registry of research entities available throughout the platform.

The Entity Registry serves as the source for researcher tools, Ray Discovery, statistical analyses, validation workflows, dashboards, APIs, and future external integrations.

Entities are selectable research components.

Research Objects reference Entities.

Variables reference Entities.

Studies reference Entities.

---

# Design Principle

Everything that can participate in research must exist as an Entity.

The researcher never selects raw implementation details.

The researcher selects registered Entities.

---

# Entity Categories

Supported categories include:

QUESTION

QUESTION_GROUP

QUESTIONNAIRE

GAME

GAME_EVENT

GAME_PARAMETER

SENSOR

SENSOR_CHANNEL

SENSOR_FEATURE

MODEL_PARAMETER

MODEL_MECHANISM

MODEL_STATE

MODEL_TRANSITION

FORECAST_PARAMETER

SUMMARY_PARAMETER

TIMELINE_EVENT

TIMELINE_INTERVAL

DERIVED_VARIABLE

RESEARCH_VARIABLE

STATISTICAL_MODEL

VALIDATION_RULE

CUSTOM_ENTITY

Future categories may be added without changing this contract.

---

# Entity Identity

Each entity must have:

entity_id

entity_type

display_name

description

version

active

owner

created_at

updated_at

---

# Entity Metadata

Every entity should describe:

scientific meaning

clinical meaning (if applicable)

research meaning

calculation source

dependencies

limitations

recommended use

forbidden use

---

# Relationships

Entities may reference other entities.

Examples:

Question

↓

Derived Variable

↓

Model Parameter

↓

Mechanism

↓

Forecast Parameter

↓

Research Variable

Relationships remain explicit.

No hidden dependencies.

---

# Registry Rules

Every selectable item in the researcher dashboard must come from the Entity Registry.

The dashboard must never build selections from source code.

---

# Research Compatibility

Entities may participate in:

Human Research

Ray Discovery

Validation

Knowledge Base

Forecast

Psychophysical Model

Games

Sensors

Questionnaires

---

# Versioning

Entity definitions are immutable.

Scientific updates create new versions.

Historical analyses continue referencing the original version.

---

# Future Compatibility

The registry must support:

manual registration

automatic registration

plugin registration

future model modules

future sensor modules

future statistical modules

without structural changes.