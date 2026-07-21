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


# Registered Standard Representation

## Core Principle

Every standard representation is a registered scientific object.

Representations are not generated ad hoc.

Every representation has a stable scientific contract.

Only registered representations may be constructed automatically.

---

## Representation Object

Each registered representation must define:

- representation_id
- representation_name
- scientific_purpose
- representation_category
- builder_id
- builder_version

---

## Scientific Compatibility

Each representation explicitly declares:

- supported_source_categories
- supported_data_types
- supported_measurement_scales
- supported_dataset_structures
- supported_observation_units

Only compatible representations may be constructed.

---

## Required Inputs

Each representation declares:

- required Prepared Domain Output sections;
- required metadata;
- required quality level;
- required coverage level;
- required calibration state.

Construction must fail if required inputs are unavailable.

---

## Output Contract

Every representation declares its output contract.

The output contract specifies:

- representation schema;
- produced scientific object;
- preserved provenance;
- preserved uncertainty;
- preserved quality metadata.

Representations must never silently discard scientific metadata.

---

## Scientific Limitations

Each representation explicitly documents:

- assumptions;
- limitations;
- unsupported situations;
- incompatible analysis families.

Scientific limitations are part of the representation contract.

---

## Versioning

Representations are versioned independently.

Updating one representation must not modify any other registered representation.

Historical studies remain reproducible by referencing the original representation version.

---

## Final Principle

The registry defines what standard scientific representations exist.

The Standard Representation Builder decides which of them are compatible with the current Prepared Domain Output.

The Representation Builder constructs the selected representation.



# Standard Representation Families

## Purpose

Standard Representations are organized into scientific families.

A family groups representations that serve the same scientific purpose.

Families simplify registration, discovery, compatibility checking, and future extension.

---

## Core Principle

Every registered Standard Representation belongs to one Representation Family.

Families classify scientific representations.

Families do not perform analysis.

Families do not define statistical methods.

---

## Initial Representation Families

### Observation Representations

Represent the collected observations.

Examples:

- Observation Table
- Participant Table
- Session Table
- Event Table

---

### Measurement Representations

Represent measured values.

Examples:

- Item Response Table
- Scale Value Table
- Domain Value Table
- Feature Table

---

### Structural Representations

Represent relationships within the dataset.

Examples:

- Matrix Representation
- Paired Dataset
- Repeated Measurement Dataset
- Longitudinal Dataset
- Hierarchical Dataset

---

### Signal Representations

Represent continuous recorded signals.

Examples:

- Time Series
- Signal Window Dataset
- Spectral Dataset
- Frequency Representation

---

### Image Representations

Represent imaging data.

Examples:

- Image Dataset
- Image Feature Dataset
- Segmentation Dataset

---

### Spatial Representations

Represent spatial measurements.

Examples:

- Coordinate Dataset
- Region Dataset
- Trajectory Dataset

---

### Derived Representations

Represent values derived during standard preparation without performing scientific interpretation.

Examples:

- Delta Dataset
- Difference Dataset
- Standardized Dataset
- Normalized Dataset

---

## Future Extension

New Representation Families may be registered without modifying the architecture.

---

## Final Principle

Representation Families organize scientific data representations.

Individual Representation Builders remain independent LEGO components.


# Measurement Representation Family

## Purpose

Measurement Representations prepare measured values for standard scientific analysis.

They represent what was measured, without performing statistical analysis or scientific interpretation.

---

## Core Principle

Measurement Representations preserve the meaning of the original measurement.

They may restructure prepared data into standard scientific formats, but they must not change what the measurement means.

---

## Initial Measurement Representations

### Item Response Representation

Purpose:

Represent individual item/question responses.

Used for:

- item-level descriptive statistics;
- item-level correlations;
- item-level missingness review;
- item-level quality review.

Must preserve:

- item_id;
- participant_id;
- session_id;
- response value;
- measurement scale;
- answer type;
- missing/skipped/not applicable status;
- provenance.

---

### Scale Value Representation

Purpose:

Represent values grouped by registered scales.

Used for:

- scale-level descriptive statistics;
- reliability analysis;
- scale correlations;
- group comparison by scale.

Must preserve:

- scale_id;
- scale_definition;
- item membership;
- scoring rule reference;
- participant_id;
- session_id;
- computed or prepared scale value;
- coverage;
- quality flags;
- provenance.

---

### Domain Value Representation

Purpose:

Represent values grouped by scientific domains.

Used for:

- domain-level descriptive statistics;
- domain correlations;
- domain comparison;
- domain-level longitudinal analysis.

Must preserve:

- domain_id;
- domain_definition;
- source items or features;
- aggregation rule reference;
- participant_id;
- session_id;
- domain value;
- coverage;
- quality flags;
- provenance.

---

### Feature Representation

Purpose:

Represent extracted or prepared features from non-questionnaire data.

Used for:

- sensor feature analysis;
- signal feature analysis;
- image feature analysis;
- model input preparation.

Must preserve:

- feature_id;
- feature_name;
- feature_type;
- source_signal_or_image_reference;
- extraction_rule_reference;
- unit;
- time window or spatial region if applicable;
- quality flags;
- provenance.

---

## Forbidden

Measurement Representations must not:

- perform hypothesis testing;
- infer missing values;
- hide skipped data;
- erase measurement scale;
- erase source item/feature references;
- erase quality or coverage metadata;
- perform scientific interpretation.

---

## Final Principle

Measurement Representations make measured values usable for standard analysis.

They do not analyze the values.


# Tabular and Matrix Representation Family

## Purpose

Tabular and Matrix Representations transform prepared measurement values into standard rectangular structures required by many scientific methods.

They do not analyze data.

They define how observations, variables, sessions, items, domains, features, or time windows are arranged.

---

## Core Principle

A table or matrix is a scientific representation, not an analysis result.

The representation must preserve:

- row meaning;
- column meaning;
- observation unit;
- variable identity;
- measurement scale;
- missing value status;
- provenance;
- quality;
- coverage.

---

## Initial Tabular and Matrix Representations

### Wide Observation Table

Purpose:

Represent one observation unit per row and multiple variables per columns.

Used for:

- descriptive statistics;
- correlation analysis;
- regression preparation;
- group comparison preparation;
- export to statistical packages.

Must define:

- row unit;
- column variables;
- participant/session linkage;
- missing value encoding;
- variable metadata;
- provenance.

---

### Long Observation Table

Purpose:

Represent one measured value per row.

Used for:

- repeated measures;
- longitudinal preparation;
- mixed models preparation;
- item-level analysis;
- event-level analysis.

Must define:

- participant_id;
- session_id;
- variable_id;
- value;
- time reference if available;
- measurement scale;
- value status;
- provenance.

---

### Response Matrix

Purpose:

Represent participants or sessions by item/question/feature columns.

Used for:

- item correlation;
- reliability preparation;
- factor analysis preparation;
- clustering preparation.

Must preserve:

- item identifiers;
- response values;
- measurement scales;
- response status;
- missingness;
- item metadata;
- provenance.

---

### Correlation Input Matrix

Purpose:

Represent variables in a form suitable for standard correlation procedures.

Used for:

- Pearson-compatible inputs;
- Spearman-compatible inputs;
- Kendall-compatible inputs;
- item-level dependency review;
- scale-level dependency review.

Must declare:

- variable set;
- measurement scales;
- allowed correlation families;
- excluded variables;
- exclusion reasons;
- missing data policy;
- provenance.

---

### Feature Matrix

Purpose:

Represent extracted features as variables.

Used for:

- sensor feature analysis;
- image feature analysis;
- model input preparation;
- clustering preparation;
- dimensionality reduction preparation.

Must preserve:

- feature identifiers;
- feature extraction rules;
- units;
- source windows or regions;
- quality flags;
- provenance.

---

## Forbidden

Tabular and Matrix Representations must not:

- calculate correlations;
- calculate regression;
- calculate factors;
- perform clustering;
- impute missing values unless explicitly represented as a separate registered imputation representation;
- erase row/column meaning;
- mix incompatible observation units silently.

---

## Final Principle

Tabular and Matrix Representations arrange prepared values into scientifically valid rectangular forms.

They prepare data structures for later analysis.

They are not analysis.