# Research Study Contract v1

## Purpose

This document defines the universal structure of every research study supported by the platform.

Studies are independent from questionnaires.

A study may use questionnaires, games, sensors, psychophysical model outputs, derived variables, timelines, external datasets, or combinations of them.

---

# Study Identity

Every study has:

study_id

title

description

version

author

created_at

updated_at

active

---

# Scientific Goal

Every study must define:

Primary research question

Secondary questions

Scientific purpose

Expected contribution

Limitations

---

# Participants

A study defines:

target population

inclusion criteria

exclusion criteria

minimum sample size

recommended sample size

---

# Variables

A study never stores raw questions.

Instead it references Variables.

Variables are classified as:

Independent

Dependent

Mediator

Moderator

Control

Grouping

Exploratory

Derived

Validation only

---

# Research Objects

A study may contain:

Research Hypotheses

Discovery Candidates

Mechanism Candidates

Derived Parameters

Statistical Models

Validation Reports

Scientific Conclusions

All follow the Research Object Contract.

---

# Data Sources

A study may combine data from:

Questionnaires

Games

Sensors

Psychophysical Engine

Timeline

Manual measurements

External datasets

Future sources

---

# Statistical Plan

Each study defines:

planned analyses

required assumptions

effect size expectations

confidence thresholds

multiple comparison correction

validation strategy

replication strategy

---

# Ray Discovery

Ray Discovery may analyze the same variables.

Ray suggestions remain outside the study until approved.

Study integrity must never depend on Ray suggestions.

---

# Outputs

Each completed study may produce:

Statistical results

Validated hypotheses

Rejected hypotheses

Discovery review list

Research report

Publication dataset

Knowledge base updates

---

# Versioning

Studies are immutable after publication.

New scientific versions create new study versions.

Historical reproducibility must always be preserved.

---

# Core Principle

Studies orchestrate research.

Variables provide measurable information.

Research Objects represent scientific entities.

Validation determines scientific confidence.

Knowledge Base stores only validated knowledge.