research/ANALYZER_CONSTRUCTOR_LEGO_CONTRACT.md

Начинаем с верхнего уровня:

# Analyzer Constructor LEGO Contract

## Core Principle

Analyzer Constructor does not analyze raw data.

Analyzer Constructor receives Prepared Domain Output and builds analyzers that can work with these prepared data.

Prepared Domain Output is the stable scientific data contract.

Analyzer Constructor is the LEGO assembly layer for analysis.

---

## Input

Analyzer Constructor receives one or more Prepared Domain Outputs.

Each Prepared Domain Output must already contain:

- domain identity;
- source identity;
- participant/session/study identity;
- collection metadata;
- data reference;
- provenance;
- permissions;
- quality;
- coverage;
- calibration;
- prepared payload;
- handoff state;
- raw_data_included flag.

Analyzer Constructor must not reconstruct these fields.

---

## Purpose

Analyzer Constructor answers the question:

Which analyzers can be connected to these prepared data, and what preparation does each selected analyzer require?

---

## Analyzer Constructor Responsibilities

Analyzer Constructor must:

1. read Prepared Domain Output;
2. verify that the output is eligible for analysis;
3. determine which analyzer types can accept the data;
4. build an Analyzer Object for each selected analysis task;
5. attach the required preparation pipeline for that analyzer;
6. preserve provenance, uncertainty, quality, coverage, and calibration state;
7. block analysis when required data, permission, quality, calibration, or coverage is insufficient.

---

## Forbidden Responsibilities

Analyzer Constructor must not:

- process raw data;
- clean sensor signals directly;
- normalize raw values directly;
- score raw questionnaires directly;
- infer missing preparation;
- fabricate missing variables;
- treat missing data as zero;
- ignore calibration state;
- ignore quality or coverage;
- perform final scientific interpretation;
- build conclusions directly.

---

## Key Distinction

Prepared Domain Output describes what the data are.

Analyzer Constructor decides what can be done with those data.

Preparation Pipeline prepares data for one selected analysis task.

Analyzer executes the analysis.

---

## LEGO Principle

There is no single universal preparation pipeline.

The same Prepared Domain Output may support many different analyzers.

Each analyzer may require its own preparation pipeline.

Example:

Prepared Questionnaire Output may support:

- descriptive statistics analyzer;
- question-level correlation analyzer;
- scale correlation analyzer;
- delta analyzer;
- reliability analyzer;
- factor analysis analyzer;
- longitudinal analyzer;
- author model analyzer.

Prepared Sensor Output may support:

- artifact-cleaned signal analyzer;
- normalized signal analyzer;
- window feature analyzer;
- time-series analyzer;
- synchronization analyzer;
- frequency-domain analyzer;
- author physiological model analyzer.

Each analyzer receives the same Prepared Domain Output, but builds a different preparation route.

---

## Final Invariant

Analyzer Constructor connects analyzers to prepared data.

It does not make data become something they are not.

It does not erase uncertainty.

It does not bypass preparation.

It does not bypass scientific constraints.


# Analyzer Constructor Internal LEGO Architecture

Analyzer Constructor is itself a configurable constructor.

It is assembled from independent LEGO builders.

Each builder has one responsibility.

Builders communicate only through explicit contracts.

No builder performs the responsibility of another builder.

---

# Builder Sequence

Prepared Domain Output

↓

Analyzer Eligibility Builder

↓

Analysis Target Builder

↓

Analysis Capability Builder

↓

Preparation Pipeline Builder

↓

Analyzer Object Builder

↓

Analyzer Object

---

# Builder Responsibilities

## 1. Analyzer Eligibility Builder

Purpose

Determine whether analysis is allowed.

Checks include:

- handoff_ready;
- permission status;
- quality requirements;
- coverage requirements;
- calibration requirements;
- required Prepared Domain Output sections.

Output

Analysis eligibility state.

This builder does not choose analyzers.

---

## 2. Analysis Target Builder

Purpose

Determine which scientific analysis tasks may be performed.

Examples

- descriptive statistics;
- correlation analysis;
- reliability analysis;
- factor analysis;
- longitudinal analysis;
- mixed models;
- survival analysis;
- Bayesian analysis;
- author analysis.

Output

List of available analysis targets.

This builder does not select statistical methods.

---

## 3. Analysis Capability Builder

Purpose

Determine which analysis methods are scientifically compatible with the prepared data.

Examples

Allowed:

- Spearman correlation;
- Pearson correlation;
- Mann–Whitney;
- Mixed Effects Model.

Forbidden:

- methods requiring interval variables;
- methods requiring independent observations;
- methods requiring repeated measurements.

Output

Analysis capability profile.

This builder does not prepare data.

---

## 4. Preparation Pipeline Builder

Purpose

Construct the preparation pipeline required by one selected analysis target.

The pipeline depends on:

- Prepared Domain Output;
- selected analysis target;
- selected analysis method.

Different analyzers may construct different preparation pipelines from the same Prepared Domain Output.

This builder does not perform analysis.

---

## 5. Analyzer Object Builder

Purpose

Construct the Analyzer Object.

The Analyzer Object becomes the executable scientific analysis unit.

The builder attaches:

- analysis target;
- selected methods;
- preparation pipeline;
- provenance;
- constraints;
- uncertainty.

The builder does not execute the analyzer.

---

# Final Principle

Each builder performs exactly one scientific responsibility.

The Analyzer Constructor is therefore a LEGO constructor composed of reusable scientific builders.



# Standard vs Author Analyzers

Analyzer Constructor must separate standard analysis methods from author-defined analyzers.

Standard analyzers are based on generally accepted statistical or methodological procedures.

Author analyzers are based on registered custom scientific models, formulas, mappings, mechanisms, or domain-specific rules.

Standard analyzers may be shown automatically when compatible with Prepared Domain Output.

Author analyzers may be shown only when their model contract is registered and compatible with the Prepared Domain Output.

Standard analyzer availability does not imply author analyzer availability.

Author analyzer availability does not replace standard analysis capability.

Both may use the same Prepared Domain Output, but they must remain separate analysis contours.

# Standard and Author Preparation

The platform separates preparation for standard scientific analysis from preparation for author-defined analysis.

These preparation paths have different purposes.

---

## Standard Scientific Preparation

Purpose

Represent prepared data in scientifically accepted forms required by standard analytical methods.

The preparation follows established methodological requirements.

Examples include:

- categorical representation;
- ordinal representation;
- interval representation;
- ratio representation;
- contingency tables;
- paired observations;
- repeated measurements;
- longitudinal datasets;
- analysis matrices.

Standard preparation produces analysis-ready representations required by accepted scientific methods.

The researcher does not construct these representations manually.

The platform prepares them automatically when compatible with the Prepared Domain Output.

---

## Author Preparation

Purpose

Provide scientifically valid data representations that may be useful for author-defined analysis.

The platform does not assume which representation the researcher will use.

Instead, it exposes possible prepared representations supported by the available data.

Examples include:

- question-level responses;
- domain-level values;
- family-level values;
- response matrices;
- delta representations;
- session differences;
- longitudinal trajectories;
- derived variables;
- custom aggregations;
- registered preparation templates.

These representations are not analyses.

They are reusable LEGO building blocks for constructing author-defined analyzers.

The researcher selects which prepared representations become part of an author analyzer.

---

## Core Principle

Standard preparation answers:

"How should these data be represented for standard scientific methods?"

Author preparation answers:

"What scientifically valid representations can be constructed from these data?"

These responsibilities must remain separate.

Standard preparation follows established methodology.

Author preparation supports scientific creativity without modifying the original Prepared Domain Output.