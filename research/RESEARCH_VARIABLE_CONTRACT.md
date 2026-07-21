# Research Variable Contract v1

## Purpose

This document defines the universal variable model used throughout the research platform.

Every statistical analysis, hypothesis, discovery, validation, mechanism, forecast and publication operates on Variables.

Variables are independent from questionnaires.

Questions are only one possible source of variables.

---

# Principle

Question ≠ Variable

Model Parameter ≠ Variable

Sensor ≠ Variable

Game Event ≠ Variable

Everything above becomes a Variable only after being defined.

---

# Variable Identity

Every variable must have:

id

name

display_name

description

version

active

---

# Variable Source

A variable always has exactly one primary source.

Allowed source types:

QUESTION

QUESTION_GROUP

QUESTIONNAIRE

MODEL_PARAMETER

MODEL_MECHANISM

MODEL_STATE

GAME

GAME_EVENT

SENSOR

SENSOR_FEATURE

TIMELINE

EVENT

FORECAST

SUMMARY

MANUAL

CUSTOM

DERIVED

---

# Source Reference

Each variable stores

source_type

source_id

study_id

question_code

assessment_id

if applicable.

---

# Variable Role

A variable may play different roles depending on the study.

Possible roles:

predictor

outcome

mediator

moderator

control

grouping

filter

derived

validation_only

exploratory

The same variable may have different roles in different studies.

---

# Variable Data Types

Supported data types

numeric

integer

float

boolean

categorical

ordinal

text

datetime

duration

vector

time_series

event

distribution

probability

---

# Variable Scale

Supported scales

nominal

ordinal

interval

ratio

binary

continuous

discrete

---

# Missing Values

Unknown values are first-class values.

Allowed states

known

unknown

not_collected

not_applicable

estimated

derived

invalid

Missing data must never be silently converted to zero.

---

# Variable Provenance

Every variable stores

who created it

how it was created

whether it was manually defined

whether it was derived

which computation created it

which version created it

---

# Derived Variables

Variables may be computed.

Example

StressBurden

TrajectoryRisk

ResourceDeficit

Pressure

ForecastRisk

They remain Variables.

Their provenance must record the computation.

---

# Statistical Compatibility

Every variable may declare

recommended statistical methods

supported transformations

normalization

standardization

expected distributions

validation requirements

---

# Discovery Compatibility

Ray Discovery may use every Variable.

Ray may create candidate variables.

Candidate variables require researcher approval before becoming official variables.

---

# Future Compatibility

Variables must remain compatible with

Questionnaires

Games

Sensors

Psychophysical Model

Forecast Model

Research Dashboard

Validation System

Knowledge Base

Future Research Modules

without changing this contract.