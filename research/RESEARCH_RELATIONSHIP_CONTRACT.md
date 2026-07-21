# Research Relationship Contract v1

## Purpose

This document defines how research entities are connected.

The platform is built as a scientific graph.

Research Objects do not exist independently.

They are connected through explicit relationships.

Relationships are first-class scientific entities.

---

# Design Principle

Everything is connected.

Relationships are stored explicitly.

No hidden dependencies.

No implicit assumptions.

---

# Supported Relationship Types

A relationship may connect any registered entities.

Supported relationships include:

depends_on

derived_from

computed_from

supports

contradicts

explains

predicts

requires

validates

invalidates

correlates_with

causes_candidate

mediates

moderates

belongs_to

part_of

generated_by

measured_by

observed_by

replicates

extends

replaces

future_extension

---

# Relationship Identity

Each relationship has:

relationship_id

relationship_type

source_entity

target_entity

version

active

created_at

updated_at

owner

---

# Owner

Relationships may be created by

researcher

ray

validation

system

Owner never implies correctness.

---

# Scientific Metadata

Every relationship may contain

description

scientific_reason

confidence

evidence

limitations

notes

---

# Confidence

Relationship confidence is stored separately.

Possible confidence sources

expert_defined

statistical

replicated

ray_discovery

external_publication

manual_review

combined

---

# Validation

Relationships may be

candidate

approved

validated

rejected

archived

---

# Human Rule

Researcher-created relationships become immediately available inside Human Research.

Ray-created relationships remain Discovery Candidates until approved.

---

# Scientific Graph

The platform represents research as a graph.

Example

Question

↓

Derived Variable

↓

Model Parameter

↓

Mechanism

↓

Forecast

↓

Scientific Conclusion

Every edge is an explicit Relationship.

---

# Query Support

Relationships must support queries such as

"What depends on StressBurden?"

"Which hypotheses use Pressure?"

"Which mechanisms influence ForecastRisk?"

"What variables support this hypothesis?"

"What discoveries contradict this mechanism?"

---

# Future Compatibility

The relationship model must support

graph databases

knowledge graphs

causal discovery

Bayesian networks

future reasoning engines

without structural changes.