
# Research Contours Contract v1

## Purpose

This document separates two research contours:

1. Human Research Contour
2. Ray Discovery Contour

They must not be mixed.

---

# 1. Human Research Contour

## Owner

Human researcher.

## Purpose

Formal scientific research.

The human researcher defines:

- research question;
- hypothesis;
- independent variables;
- dependent variables;
- model parameters involved;
- mechanisms involved;
- statistical methods;
- interpretation rules;
- validation criteria.

## Rule

Ray must not silently create or modify Human Research hypotheses.

Ray may assist only as a tool.

---

# 2. Ray Discovery Contour

## Owner

Ray.

## Purpose

Exploratory discovery.

Ray may independently search for:

- correlations;
- nonlinear dependencies;
- clusters;
- unexpected patterns;
- possible new mechanisms;
- weak or redundant questions;
- useful derived parameters;
- cross-study dependencies.

## Rule

Ray-created objects are not formal research hypotheses.

They are Discovery Candidates.

They may become Human Research hypotheses only after human approval.

---

# 3. Shared Research Object Contract

Every research object must contain:

```python
{
    "id": "...",
    "object_type": "hypothesis | discovery_candidate | mechanism_candidate | question_candidate | parameter_candidate | statistical_model",
    "owner": "researcher | ray",
    "status": "draft | candidate | needs_review | approved | validated | rejected | archived",
    "research_question": "...",
    "variables": [],
    "analysis_methods": [],
    "evidence": [],
    "validation": {},
    "created_by": "researcher | ray",
    "approved_by_researcher": False
}




4. Variable Contract


A variable may come from:

question;
question group;
questionnaire;
game;
sensor;
model parameter;
model mechanism;
model state;
forecast;
timeline;
event;
manual input;
custom source.


Each variable must describe:
{
    "name": "...",
    "source_type": "...",
    "source_ref": "...",
    "role": "predictor | outcome | moderator | mediator | control | grouping",
    "data_type": "numeric | categorical | boolean | text | time_series | event"
}




5. Boundary Rule


Human Research and Ray Discovery may share data sources, but they do not share authority.

Researcher contour = formal hypothesis testing.

Ray contour = exploratory discovery.

Validation contour decides what becomes accepted knowledge.




6. Promotion Rule


Ray Discovery Candidate can become Human Research Hypothesis only by explicit human action:
ray_candidate
    ↓
needs_review
    ↓
approved_by_researcher
    ↓
research_hypothesis
No automatic promotion is allowed.
Сохрани именно сюда:

```text
research/RESEARCH_CONTOURS_CONTRACT.md
