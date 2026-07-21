
# Research Statistical Methods Contract v1

## Purpose

This document defines how statistical methods are described, selected, executed, and interpreted inside the research platform.

Statistics must support both:

1. Human Research Contour
2. Ray Discovery Contour

but the authority of the result depends on the contour.

---

# Core Principle

Statistical result ≠ scientific truth.

A statistical result may support, weaken, or contradict a Research Object.

It does not automatically validate it.

---

# Method Categories

Supported method categories include:

- descriptive statistics
- correlation
- group comparison
- regression
- classification
- clustering
- dimensionality reduction
- factor analysis
- Bayesian analysis
- time-series analysis
- survival analysis
- nonlinear analysis
- machine learning feature importance
- validation analysis
- replication analysis

---

# Method Definition

Each statistical method must define:

method_id

name

category

description

input_variable_types

minimum_sample_size

assumptions

limitations

output_metrics

suitable_for

not_suitable_for

---

# Human Research Use

In Human Research, statistical methods are selected by the researcher before analysis whenever possible.

The study must record:

planned methods

primary analysis

secondary analysis

correction strategy

validation strategy

interpretation rules

---

# Ray Discovery Use

Ray may run exploratory statistical searches.

Ray may suggest:

- possible dependency
- possible nonlinear relation
- possible cluster
- possible weak question
- possible redundant variable
- possible derived parameter
- possible mechanism candidate

Ray results must be marked as exploratory.

They require human review before becoming formal research hypotheses.

---

# Multiple Comparisons

Exploratory analysis may test many combinations.

Therefore it must record:

number_of_tests

correction_method

false_discovery_risk

exploratory_status

No exploratory result may be treated as confirmed without validation.

---

# Output Contract

Every statistical result must contain:

result_id

method_id

variables

sample_size

effect_size

confidence_interval

p_value

adjusted_p_value

model_quality

assumptions_checked

limitations

created_by

created_at

contour

---

# Interpretation Rule

Statistics can say:

- association detected
- difference detected
- prediction improved
- cluster detected
- no sufficient evidence
- result unstable
- not enough data

Statistics must not say:

- cause proven
- diagnosis confirmed
- person has trait
- mechanism is true

---

# Validation Rule

A statistical result becomes stronger only through:

replication

cross-validation

time stability

population stability

external validation

mechanism consistency

---

# Storage Rule

Raw statistical outputs belong to the research layer.

Participant-facing summaries may only receive safe, interpreted, uncertainty-aware conclusions.

---

# Future Compatibility

This contract must remain compatible with:

Researcher Dashboard

Ray Discovery Lab

Validation Lab

Knowledge Base

Psychophysical Model

Sensor Data

Games

Longitudinal Data

External statistical libraries

