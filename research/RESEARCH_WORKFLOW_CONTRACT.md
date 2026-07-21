# Research Workflow Contract v1

## Purpose

This document defines the lifecycle of every research activity performed inside the platform.

The workflow is identical regardless of whether the study is created by a human researcher or whether a discovery originates from Ray.

The difference is authority, not workflow.

---

# Phase 1. Research Design

Possible initiators:

Researcher

Ray Discovery

Human researcher creates formal studies.

Ray creates Discovery Candidates.

---

# Phase 2. Variable Selection

Variables are selected.

Variables may originate from:

Questionnaires

Games

Sensors

Psychophysical Model

Timeline

External datasets

Derived variables

Future data sources

Variables remain references.

Data is not copied.

---

# Phase 3. Statistical Plan

Analysis methods are selected.

Possible methods include:

Descriptive

Correlation

Regression

Classification

Bayesian

Time Series

Clustering

Factor Analysis

Machine Learning

Custom methods

Human Research chooses methods manually.

Ray Discovery may choose exploratory methods automatically.

---

# Phase 4. Data Collection

Data enters the study.

Collection status:

planned

collecting

completed

insufficient

invalid

cancelled

Data provenance must always be preserved.

---

# Phase 5. Analysis

Analysis produces statistical outputs.

Outputs may support

weaken

contradict

or fail to evaluate

Research Objects.

Analysis never produces scientific truth.

---

# Phase 6. Interpretation

Interpretation differs by contour.

Human Research:

researcher interprets results.

Ray Discovery:

Ray generates candidate explanations.

Candidate explanations require researcher review.

---

# Phase 7. Validation

Validation may include

replication

cross-validation

time stability

population stability

external validation

mechanism consistency

Validation updates confidence.

Validation never changes historical raw results.

---

# Phase 8. Knowledge Integration

Validated Research Objects may update the Knowledge Base.

Rejected objects remain archived.

Discovery Candidates remain in Discovery unless promoted.

---

# Workflow Invariants

No statistical output bypasses validation.

No Ray Discovery bypasses researcher approval.

No validated knowledge bypasses evidence.

Historical analyses remain reproducible.

Research versions remain immutable.

---

# Future Compatibility

The workflow must support:

single-session studies

longitudinal studies

sensor studies

game studies

adaptive studies

multicenter studies

future AI-assisted studies

without changing this lifecycle.