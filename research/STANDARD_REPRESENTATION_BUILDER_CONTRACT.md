# Standard Representation Builder Contract

## Purpose

The Standard Representation Builder constructs scientifically accepted data representations required for standard analytical methods.

The builder does not perform analysis.

The builder does not select analytical methods.

The builder prepares standard scientific representations of already prepared data.

---

# Core Principle

Prepared Domain Output is not modified.

The builder creates one or more standard representations derived from the Prepared Domain Output.

These representations become reusable scientific objects.

Each representation is independent.

Multiple representations may coexist simultaneously.

---

# Input

The Standard Representation Builder receives:

- Prepared Domain Output;
- data description;
- quality metadata;
- coverage metadata;
- calibration metadata;
- provenance metadata;
- handoff metadata.

No raw domain data may enter the builder.

---

# Builder Principle

The Standard Representation Builder is itself a LEGO constructor.

It consists of independent Representation Builders.

Each Representation Builder produces one standard scientific representation.

Representations are reusable.

Representations are analysis-independent.

---

# Builder Architecture

Prepared Domain Output

↓

Standard Representation Builder

↓

Representation Builders

↓

Standard Representations

The Standard Representation Builder never performs statistical analysis.

---

# Representation Builders

Each Representation Builder has one responsibility.

Examples include:

- Tabular Representation Builder
- Matrix Representation Builder
- Frequency Representation Builder
- Paired Data Builder
- Repeated Measurement Builder
- Longitudinal Builder
- Time Series Builder
- Signal Window Builder
- Image Dataset Builder

Additional Representation Builders may be added without changing the architecture.

---

# Representation Independence

Each Representation Builder operates independently.

One representation must not require another representation to exist.

Builders may execute independently or simultaneously.

---

# Output

Each Representation Builder produces one Standard Representation Object.

Multiple Standard Representation Objects may be produced from one Prepared Domain Output.

These objects become available for downstream standard scientific analysis.

No analysis is performed.

---

# Forbidden

The Standard Representation Builder must not:

- perform statistical analysis;
- perform scientific interpretation;
- calculate hypothesis tests;
- calculate significance;
- estimate effect sizes;
- construct conclusions;
- modify Prepared Domain Output;
- remove uncertainty;
- replace provenance.

---

# Final Principle

The Standard Representation Builder prepares scientifically accepted representations of prepared data.

It prepares the data.

It does not analyze the data.

# Standard Representation Registry

## Purpose

The Standard Representation Registry defines all registered standard scientific representations supported by the platform.

The registry does not build representations.

The registry describes available Representation Builders.

---

## Registry Principle

Every Standard Representation Builder must be registered.

Only registered Representation Builders may be used by the Standard Representation Builder.

Registration guarantees:

- reproducibility;
- scientific traceability;
- version control;
- compatibility checking;
- future extensibility.

---

## Representation Registration

Each registered representation must contain:

- representation_id
- representation_name
- representation_category
- supported_source_categories
- supported_measurement_scales
- supported_data_types
- supported_dataset_structures
- required_inputs
- optional_inputs
- output_contract
- builder_version
- scientific_description
- limitations

---

## Categories

Representations may belong to categories such as:

- Tabular
- Matrix
- Frequency
- Longitudinal
- Repeated Measurements
- Time Series
- Signal
- Image
- Spatial
- Network
- Event
- Derived

Additional categories may be added without modifying the architecture.

---

## Compatibility

Each Representation Builder explicitly declares:

- compatible source categories;
- compatible data types;
- compatible measurement scales;
- compatible dataset structures.

The Standard Representation Builder selects only compatible builders.

---

## Final Principle

The registry describes available scientific representations.

The constructor assembles them.

The Representation Builders construct them.