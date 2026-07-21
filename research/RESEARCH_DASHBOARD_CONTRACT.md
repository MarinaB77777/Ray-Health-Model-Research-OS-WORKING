# Research Dashboard Contract v1

## Purpose

The Research Dashboard is the primary workspace for researchers.

It provides access to every research object, study, dataset, variable, discovery, validation result, publication, and knowledge object.

The dashboard never accesses implementation directly.

Everything displayed comes from registered Research Objects and Entity Registry.

---

# Dashboard Sections

The dashboard consists of independent modules.

Modules may be enabled or disabled without affecting other modules.

---

## Home

Overview

Recent activity

Research notifications

Pending approvals

Running analyses

Ray Discovery notifications

Validation status

---

## Studies

Create study

Open study

Duplicate study

Archive study

Study versions

Study reports

---

## Variables

Browse variables

Search variables

Create derived variable

Variable dictionary

Variable relationships

Variable usage

---

## Research Objects

Browse all objects

Filter by type

Filter by owner

Filter by study

Search

Version history

Relationships

---

## Human Research

Research hypotheses

Research questions

Statistical plans

Experiments

Drafts

Publications

---

## Ray Discovery

Discovery candidates

Pattern search

Mechanism candidates

Question suggestions

Derived parameter suggestions

Weak question detection

Unexpected dependencies

Required sample estimation

---

## Validation Lab

Replication

Cross-validation

Population stability

Time stability

Evidence review

Confidence updates

Publication readiness

---

## Statistical Analysis

Run analysis

Saved analyses

Statistical history

Comparison

Visualizations

Method library

---

## Entity Registry

Questions

Questionnaires

Games

Sensors

Mechanisms

Model Parameters

Forecast Parameters

Timeline Events

Custom Entities

---

## Dataset Manager

Participant datasets

Research datasets

Filters

Exports

Snapshots

Version history

---

## Knowledge Base

Validated hypotheses

Validated mechanisms

Accepted variables

Scientific conclusions

Rejected findings

Archived research

---

## Publications

Draft manuscripts

Figures

Tables

Exports

Supplementary material

Publication history

---

## Administration

Permissions

Researchers

Discovery Agents

Audit log

Governance

Version management

---

# Navigation Principle

Every screen must allow navigation to related Research Objects.

No dead ends.

Every object can be explored.

---

# Search

Global search must work across

Studies

Variables

Research Objects

Mechanisms

Questions

Forecasts

Datasets

Validation

Knowledge

---

# Visualization

Dashboard supports

tables

graphs

timelines

knowledge graph

dependency graph

statistical plots

network graphs

heatmaps

future visualization modules

---

# Future Compatibility

Dashboard architecture must support future modules without redesign.

Modules communicate through contracts.

Modules never communicate through implementation.