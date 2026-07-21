# Research Object Contract v1

## Purpose

This document defines the universal object model for every entity produced, analyzed, discovered, validated, or archived by the research platform.

Every research entity must be represented as a Research Object.

Research Objects are independent from any specific study, questionnaire, game, model, sensor, or statistical method.

This contract is intended to remain stable as the platform grows.

---

# Design Principles

Research Objects represent scientific knowledge candidates.

They are not limited to hypotheses.

Different object types follow one common lifecycle while preserving their own metadata.

---

# Object Types

Supported object types include:

- Research Hypothesis
- Discovery Candidate
- Mechanism Candidate
- Statistical Model
- Derived Parameter
- Question Candidate
- Variable Definition
- Research Dataset
- Validation Report
- Scientific Conclusion

Additional types may be added without changing the contract.

---

# Owners

Every Research Object has exactly one creator.

Allowed owners:

- researcher
- ray

Owner determines who initiated the object.

Owner does NOT determine scientific validity.

---

# Research Object Lifecycle

draft

↓

candidate

↓

needs_review

↓

approved

↓

validated

↓

published

↓

archived

Objects may also become

rejected

at any stage.

---

# Human Authority

Researcher-created objects become active immediately inside the Human Research Contour.

Ray-created objects remain inside the Discovery Contour until explicitly accepted by a researcher.

Automatic promotion is forbidden.

---

# Required Fields

Every Research Object must contain:

id

object_type

owner

status

title

description

study_id

created_at

updated_at

version

---

# Scientific Metadata

Every Research Object should support:

research_question

variables

analysis_methods

assumptions

limitations

expected_direction

notes

---

# Evidence

Research Objects never exist without evidence.

Evidence may include:

- questionnaire responses
- computed model parameters
- psychophysical mechanisms
- game variables
- sensor variables
- timeline events
- statistical outputs
- external validated datasets

Evidence remains linked to the object throughout its lifecycle.

---

# Validation Metadata

Validation information is stored separately from the object logic.

Examples:

replication status

cross-validation

population coverage

sample size

confidence interval

effect size

statistical significance

time stability

external validation

---

# Publication Rule

Only validated Research Objects may become scientific conclusions.

Discovery Candidates are never published directly.

---

# Separation Principle

Human Research

↓

creates formal scientific knowledge

Ray Discovery

↓

creates possible scientific ideas

Validation

↓

decides whether evidence is sufficient

Knowledge Base

↓

stores only validated knowledge

---

# Future Compatibility

This contract must remain compatible with:

Questionnaires

Games

Sensors

Psychophysical Model

Forecast Engine

Ray Discovery Engine

Research Dashboard

Publication System

External Statistical Packages

Future AI-assisted research modules

without structural changes.