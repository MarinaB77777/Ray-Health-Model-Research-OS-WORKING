# Model Parameters System — Architecture, Locations, and Usage Guide

**Status:** working architecture after separation of questionnaires/answers from model calculations  
**Scope:** all calculation models, all current and future calculated parameters  
**Purpose:** one reference file for finding, understanding, creating, storing, retrieving, and using model parameters without mixing them with questionnaires or answers

---

## 1. Core principle

Questions and answers are one independent data layer.

Calculated model parameters are another independent data layer.

They may be connected through provenance, because answers can be used as model inputs, but they are not the same entity and must not be stored or analyzed as if they were the same.

```text
QUESTION DEFINITIONS
        ↓
ANSWER RECORDS
```

This layer contains collected participant data.

Separately:

```text
MODEL INPUT CONTRACT
        ↓
MODEL CALCULATION RUN
        ↓
CALCULATION RESULT
        ↓
CALCULATED PARAMETER RECORDS
```

This layer contains model outputs.

The relationship:

```text
answer records → prepared model input → calculated parameter records
```

is only a documented calculation provenance path.

It does not mean:

- that a parameter belongs to a questionnaire;
- that an answer is a model parameter;
- that a questionnaire should automatically run a model;
- that `study_id` should select a model;
- that calculated parameters should be stored inside answer records;
- that parameters should be read from `ParticipantSession.raw_engine_result`.

---

## 2. Non-negotiable architectural invariants

### 2.1 Questions and answers

Any question may be used in any questionnaire, in any order.

Question identity is stable and independent of the questionnaire where it was shown.

Answers are stored and researched as answer observations.

Question and answer analysis must work independently of all model calculations.

### 2.2 Models and parameters

There may be many models.

Each model may have:

- its own `model_id`;
- multiple `model_version` values;
- multiple `calculation_version` values;
- its own `input_contract_version`;
- its own parameter definitions;
- new parameters added later;
- parameters removed, deprecated, disabled, or versioned later.

A model is never selected by questionnaire ID or study ID.

A model calculation is an explicit operation.

A model parameter is identified in context by at least:

```text
model_id
parameter_id
parameter_definition_version
```

`parameter_code` alone is not globally unique across all models.

### 2.3 Unknown and incomplete data

```text
Unknown ≠ 0
Not enough data ≠ no calculation
Not enough data ≠ no parameter records
```

A calculation run may have status:

```text
NOT_ENOUGH_DATA
```

and still contain many valid calculated parameter records.

Each parameter has its own calculation status.

Example:

```text
ModelCalculationRun: NOT_ENOUGH_DATA
├── Current State: calculated
├── Pressure Proxy: calculated
├── State Risk: not_enough_data
└── Trajectory Risk: not_enough_data
```

### 2.4 No automatic questionnaire execution

A questionnaire does not automatically run a model.

The current Health Model adapter explicitly declares:

```text
automatic_questionnaire_execution = False
```

Input preparation is a separate process that creates a model input contract from selected permissible source data.

---

## 3. Main entities

## 3.1 Question definition

Defines a question independently of any questionnaire.

Expected identity:

```text
question_uuid
question_code
question_version
scale metadata
response metadata
```

Question definitions are not model parameter definitions.

## 3.2 Answer record

Represents one submitted answer observation.

Typical identity and provenance:

```text
answer_record_id
submission_id
question_uuid
question_code
participant_id / subject_link_id
session_id
study_id
answer_value
answer_value_type
observation time
```

Answer records are analyzed separately through questionnaire analysis pipelines.

## 3.3 Model definition registration

A calculation model is registered as executable code with:

```text
model_id
model_version
calculation_version
input_contract_version
build_input
validate_input
calculate
build_parameter_records
parameter_definition_provider
supported_input_source_types
```

Location:

```text
research/model_registry.py
```

Main class:

```python
RegisteredCalculationModel
```

Main functions:

```python
register_calculation_model(...)
get_registered_calculation_model(...)
list_registered_calculation_models(...)
clear_registered_calculation_models(...)
```

## 3.4 Model parameter definition

A parameter definition describes what a model output means.

It is not a measured value.

Current Health Model location:

```text
research/analyses/health_model/model_parameter_registry.py
```

Important functions:

```python
list_model_parameter_definitions(...)
get_model_parameter_definition(...)
validate_model_parameter_definition(...)
save_custom_model_parameter_definition(...)
build_model_parameter_registry(...)
```

Built-in definitions are currently stored in:

```python
BUILT_IN_MODEL_PARAMETER_DEFINITIONS
```

Custom definitions created later by a constructor are stored in:

```text
data/model_parameter_definitions.json
```

The current Health Model registry contains 35 valid definitions.

### Definition identity

```text
parameter_id
parameter_code
definition_version
model_id
calculation_version
```

### Definition metadata

A definition may include:

```text
title
parameter_role
parameter_kind
value_type
scale_type
value_schema
missing_semantics
score_direction
calculation.value_path
calculation.status_path
research.available
research.allowed_analysis_roles
status
definition_source
```

## 3.5 Model calculation input reference

Represents one source used to create a model input.

Location:

```text
research/model_calculation_schemas.py
```

Class:

```python
ModelCalculationInputReference
```

Supported source examples:

```text
questionnaire_answer
sensor_measurement
manual_measurement
prepared_domain_output
previous_model_parameter
verified_external_record
imported_file
```

Important fields:

```text
input_reference_id
source_type
source_record_type
source_record_id
source_session_id
source_submission_id
participant_id
subject_link_id
study_id
domain_id
observation_time
global_time_reference
selected_variable_codes
selected_record_ids
provenance
```

The reference documents where inputs came from. It does not change the entity type of the result.

## 3.6 Model calculation run

Represents one explicit execution of one model version.

Location:

```text
research/model_calculation_schemas.py
```

Class:

```python
ModelCalculationRun
```

Statuses:

```text
CREATED
INPUT_READY
RUNNING
COMPLETED
NOT_ENOUGH_DATA
BLOCKED
FAILED
INVALIDATED
```

Important fields:

```text
calculation_run_id
model_id
model_version
calculation_version
input_contract_version
status

created_at
updated_at
started_at
completed_at
invalidated_at

participant_id
subject_link_id

calculation_scope
observation_unit

input_references
input_snapshot
input_quality
input_validation

calculation_result
parameter_records
parameter_record_count

uncertainty
warnings
reason_codes
provenance

invalidated
invalidation_reason
failure
```

## 3.7 Calculated parameter record

Represents one parameter value produced in one calculation run.

Current record builder for Health Model:

```text
research/analyses/health_model/model_parameter_extractor.py
```

Main function:

```python
build_health_model_parameter_records(...)
```

Current schema:

```text
health-model-parameter-record-2
```

Important fields:

```text
parameter_record_id
schema_version
registry_schema_version
record_type

calculation_run_id

parameter_id
parameter_code
parameter_definition_version
parameter_definition_source

title
parameter_role
parameter_kind

parameter_value
parameter_value_type
runtime_value_type
scale_type
value_schema
score_direction

calculation_status
raw_calculation_status
value_path
status_path
value_path_found
status_path_found
value_validation
reason_codes

model_id
model_version
calculator_id
calculation_version

study_id
session_id
source_session_id
participant_id
subject_link_id

observation_time
observation_time_source
created_at

research_available
allowed_analysis_roles
source_mode
input_reference_ids
```

---

## 4. Supported parameter formats

The architecture must not assume that every model parameter is a float.

Supported `parameter_kind` values:

```text
scalar
binary
categorical
ordinal
vector
time_series
distribution
interval
structured
```

### 4.1 Scalar

Single numeric value.

Examples:

```text
Current State
Stress Burden
Pressure Proxy
Resource Deficit
Delta
```

Possible scales:

```text
continuous
count
ratio
interval
percentage
probability
duration
```

### 4.2 Binary

Boolean calculated state.

Examples:

```text
critical_status.is_critical
forecast_allowed
critical_override_applied
```

Binary values are not automatically treated as continuous measurements.

### 4.3 Categorical

One unordered category.

Example:

```text
PREVENTIVE_WINDOW
HIDDEN_FACTOR_MODE
DIAGNOSTIC_MODE
```

Allowed values must be defined explicitly.

### 4.4 Ordinal

Ordered categories.

Example:

```text
low
moderate
high
critical
```

The order must be stored explicitly in `ordered_values`.

### 4.5 Vector

A fixed set of named components.

Examples:

```text
resource deficit domain vector
pressure profile
mechanism score vector
```

Component schema must be versioned.

### 4.6 Time series

A sequence of values over time.

Examples:

```text
Current State trajectory
resource trajectory
sensor-derived trajectory
```

Observation time and global time reference are mandatory.

### 4.7 Distribution

A calculated distribution.

Examples:

```text
posterior distribution
bootstrap distribution
uncertainty distribution
```

Its schema may contain parameters, quantiles, or a sample.

### 4.8 Interval

A bounded estimate.

Example:

```json
{
  "lower": 2.1,
  "upper": 3.4,
  "level": 0.95
}
```

### 4.9 Structured

A complex output that cannot honestly be reduced to one number.

Examples:

```text
forecast result
mechanism state
constellation result
readiness conclusion
```

Structured values must not automatically enter standard pairwise statistical analysis.

---

## 5. Where the current implementation is located

## 5.1 Generic multi-model architecture

### Model calculation schemas

```text
research/model_calculation_schemas.py
```

Contains:

```text
ModelCalculationStatus
ModelCalculationInputReference
ModelCalculationRun
validate_model_calculation_run
```

### Persistent calculation store

```text
research/model_calculation_store.py
```

Contains:

```python
ModelCalculationPersistentStore
```

Capabilities:

```text
save/get/list calculation runs
filter by model/version/status/participant/source session
list parameter records
filter parameter records
invalidate calculation runs
persistent JSON serialization
atomic temporary-file replacement
```

### Model registry

```text
research/model_registry.py
```

Contains:

```text
RegisteredCalculationModel
register_calculation_model
get_registered_calculation_model
list_registered_calculation_models
```

### Calculation service

```text
research/model_calculation_service.py
```

Contains:

```python
ModelCalculationService
```

Main methods:

```python
create_run(...)
run_calculation(...)
get_run(...)
list_runs(...)
list_parameter_records(...)
```

The service performs:

```text
resolve registered model
build model input
validate input
run calculator
build parameter records
attach run identity
save complete or partial result
preserve NOT_ENOUGH_DATA results
```

## 5.2 Health Model implementation

### Calculator

```text
research/analyses/health_model/v61_calculator.py
```

Main function:

```python
calculate_health_model_v61(...)
```

### Health Model adapter

```text
research/analyses/health_model/model_adapter.py
```

Contains:

```text
HEALTH_MODEL_ID = health_model_v6_1
HEALTH_MODEL_VERSION = 6.1
HEALTH_MODEL_CALCULATION_VERSION = 1
HEALTH_MODEL_INPUT_CONTRACT_VERSION = health-model-v61-input-1
```

Main functions:

```python
build_health_model_input(...)
validate_health_model_input(...)
calculate_registered_health_model(...)
build_registered_health_model_parameter_records(...)
list_health_model_parameter_definitions(...)
build_registered_health_model(...)
register_health_model(...)
```

The adapter:

- accepts a preassembled input contract;
- does not search questionnaires;
- does not search question banks;
- does not use `study_id` to decide execution;
- does not automatically execute after answer collection;
- produces independent calculation runs and parameter records.

### Parameter definition registry

```text
research/analyses/health_model/model_parameter_registry.py
```

### Parameter extractor

```text
research/analyses/health_model/model_parameter_extractor.py
```

### Existing legacy catalog and analysis code

```text
research/analyses/health_model/model_parameter_catalog.py
research/analyses/health_model/model_parameter_dependency_builder.py
research/analyses/health_model/model_parameter_pair_dataset.py
research/analyses/health_model/model_parameter_analysis_check.py
```

These files were originally built around parameter records stored inside pilot/research snapshots.

They must be progressively switched to use:

```text
ModelCalculationPersistentStore.list_parameter_records(...)
```

as the authoritative source.

---

## 6. Current verified behavior

The following has been tested successfully.

### Registry validation

```text
definition_count: 35
invalid_count: 0
```

### Extractor

For a test input:

```text
record_count: 35
calculated: 32
not_enough_data: 3
invalid: 0
```

### Generic persistent store

A test run was:

```text
saved
reloaded from JSON
found by calculation_run_id
```

### Generic model registry

A test model was:

```text
registered
retrieved by model/version/calculation version
listed with source types
```

### Generic calculation service

A test model completed:

```text
status: COMPLETED
parameter_count: 1
parameter_value: 8
calculation_run_id attached: True
```

### Health Model full independent calculation

Verified result:

```text
run_status: NOT_ENOUGH_DATA
parameter_record_count: 35
stored_run_restored: True
stored_parameter_count: 35

parameter_status_counts:
    calculated: 32
    not_enough_data: 3

all_records_have_run_id: True
all_records_have_model_id: True

current_state_value: 2.3117679621826097
```

This confirms:

```text
NOT_ENOUGH_DATA does not discard available parameters.
```

---

## 7. How to use model parameters

## 7.1 Retrieve all registered models

Use:

```python
from research.model_registry import (
    list_registered_calculation_models,
)

models = list_registered_calculation_models()
```

Use this for:

- model selection UI;
- model constructor/catalog UI;
- validating available model versions;
- displaying parameter definition counts;
- selecting a model for an explicit calculation.

## 7.2 Retrieve parameter definitions for a model

For Health Model:

```python
from research.analyses.health_model.model_parameter_registry import (
    list_model_parameter_definitions,
)

definitions = list_model_parameter_definitions(
    include_inactive=False,
)
```

Use definitions for:

- UI labels;
- parameter type and scale;
- valid ranges;
- allowed categories;
- score direction;
- analysis role eligibility;
- constructor editing;
- validation;
- choosing compatible statistical methods.

Never infer these from Python runtime value type.

## 7.3 Create an explicit model calculation run

```python
run = service.create_run(
    model_id="health_model_v6_1",
    model_version="6.1",
    calculation_version="1",
    participant_id="participant-id",
    subject_link_id="subject-id",
    input_snapshot=model_input_contract,
    input_references=[...],
)
```

`input_snapshot` must already follow the model input contract.

Do not pass a questionnaire object as if it were a model input contract.

## 7.4 Run the calculation

```python
completed = service.run_calculation(
    run.calculation_run_id
)
```

Possible run statuses include:

```text
COMPLETED
NOT_ENOUGH_DATA
FAILED
INVALIDATED
```

Always inspect both:

```text
run.status
individual parameter calculation_status
```

## 7.5 Retrieve parameter records

```python
records = store.list_parameter_records(
    model_id="health_model_v6_1",
    parameter_code=(
        "current_state.current_state_final"
    ),
    subject_link_id="subject-id",
    calculation_status="calculated",
)
```

Supported filters include:

```text
model_id
parameter_id
parameter_code
calculation_run_id
participant_id
subject_link_id
calculation_status
include_invalidated_runs
```

## 7.6 Cross-participant research

For analysis across participants:

```text
one parameter
→ latest or explicitly selected eligible calculation per participant
→ one observation per participant
```

Repeated calculations must never be silently treated as independent participants.

Required explicit policy examples:

```text
reject_repeated
latest
earliest
specific calculation run selection
```

## 7.7 Within-participant trajectory

For trajectory analysis:

```text
one participant
→ repeated comparable calculation runs
→ ordered by observation_time
```

Requirements:

```text
same model_id
compatible model_version/calculation_version
same parameter definition version or explicit harmonization
valid observation time
stable participant identity
comparable input contract
```

Do not mix incompatible versions silently.

## 7.8 Parameter-to-parameter statistical analysis

Before selecting a statistical method, use definition metadata:

```text
parameter_kind
value_type
scale_type
value_schema
observation_unit
analysis_scope
allowed_analysis_roles
```

Do not select a method using only:

```text
Python type
```

Structured, distribution, vector, interval, and time-series parameters need dedicated analytical handling.

## 7.9 Forecasting and trajectories

A forecast must be built from calculation runs and parameter trajectories, not from questionnaire identity.

Possible chain:

```text
calculation runs
→ parameter time series
→ dynamics / velocity / persistence
→ mechanism calculation
→ constellation analysis
→ structural forecast
```

Forecast permission and forecast output remain separate parameters or structured outputs.

---

## 8. Adding a new model

To add a new executable model:

1. Create its calculator.
2. Define its input contract.
3. Create an input builder.
4. Create input validation.
5. Create parameter definitions.
6. Create a parameter record builder.
7. Create a model adapter.
8. Register it through `register_calculation_model`.
9. Test a complete calculation run.
10. Expose it through the common API.

Example adapter responsibilities:

```text
build_input
validate_input
calculate
build_parameter_records
parameter_definition_provider
```

Do not add model-specific branching to `ParticipantSession`.

Do not add:

```python
if session.study_id == "new_model":
```

as model orchestration.

---

## 9. Adding a new parameter

A new parameter must first be added as a definition.

Required minimum:

```text
parameter_id
parameter_code
definition_version
title
parameter_role
parameter_kind
value_type
scale_type
value_schema
missing_semantics
calculation.value_path or registered calculation rule
model_id
calculation_version
research availability
allowed analysis roles
status
```

Then:

1. Validate the definition.
2. Activate it.
3. Update the model calculation result if the output does not yet exist.
4. Ensure the parameter record builder can extract or calculate it.
5. Test calculated, missing, invalid, and not-applicable cases.
6. Preserve old definition versions for old records.

A changed scientific meaning requires a new definition version.

Do not silently rewrite old parameter records with a new definition.

---

## 10. Future parameter constructor

The parameter constructor should create and edit parameter definitions, not arbitrary hidden JSON keys.

It must support:

```text
stable parameter UUID
model selection
parameter code
multilingual title
definition version
parameter kind
value type
scale type
numeric range
unit
allowed categories
ordinal order
vector components
structured schema
missing-data semantics
score direction
calculation binding
calculation version
research availability
allowed analysis roles
validation
draft/active/deprecated/disabled status
```

The constructor must not execute arbitrary unreviewed Python code.

Executable model logic must remain registered code.

A safe future formula builder may exist only through validated, versioned, bounded operations.

---

## 11. Persistent storage

The generic calculation store is:

```text
research/model_calculation_store.py
```

The application-level instance should later use `rc_config.data_path(...)` or the project’s accepted persistent data path abstraction.

Recommended logical storage filename:

```text
data/model_calculation_runs.json
```

or under configured persistent root:

```text
model_calculations/model_calculation_runs.json
```

The exact final path must be selected when wiring into `main.py`.

Do not store new authoritative parameter records in:

```text
data/pilot_sessions.json
ParticipantSession.raw_engine_result
research_records.json questionnaire snapshots
```

Legacy records may remain readable during migration, but they are not the target architecture.

---

## 12. API that should exist

The following common API is the intended direction.

### Model catalog

```text
GET /research/models
```

Returns registered models and versions.

### Model parameter definitions

```text
GET /research/models/{model_id}/parameters
```

Returns definitions, including inactive definitions when explicitly requested.

### Create calculation run

```text
POST /research/model-calculations
```

Request contains:

```text
model_id
model_version
calculation_version
participant identity
input snapshot
input references
provenance
```

### Execute calculation

```text
POST /research/model-calculations/{calculation_run_id}/run
```

### Read calculation run

```text
GET /research/model-calculations/{calculation_run_id}
```

### List runs

```text
GET /research/model-calculations
```

Filters:

```text
model_id
version
status
participant
subject link
source session
```

### List parameter records

```text
GET /research/model-parameters/records
```

Filters:

```text
model_id
parameter_id
parameter_code
calculation_run_id
participant
subject link
calculation_status
```

### Parameter measurement catalog

```text
GET /research/model-parameter-measurements
```

This endpoint must ultimately read from the generic calculation store, not pilot sessions.

---

## 13. Data Explorer behavior

The Data Explorer should have two distinct modes.

## 13.1 Across participants

Left panel:

```text
model
→ parameter
→ latest eligible value for each participant
```

Right panel:

```text
choose another parameter
→ pair values by participant
→ form dataset
→ validate method
→ run analysis
```

## 13.2 Within participant

Left panel:

```text
participant
→ calculation runs ordered by time
→ available parameter trajectories
```

Right panel:

```text
choose parameters
→ inspect trajectory
→ analyze dynamics
→ later build forecast
```

Question/answer mode remains separate:

```text
question
→ answers from participants
→ question-to-question analysis
```

No mixing in one hidden data structure.

---

## 14. Legacy code and migration warnings

The following old behavior is architecturally incorrect as an authoritative path:

```python
if session.study_id == "health_model":
    ...
    result["research_calculated_parameter_records"] = ...
```

Location:

```text
pilot_session/service.py
```

It currently mixes:

```text
answer collection
model selection
model execution
parameter storage
```

This block should later be removed or converted into an explicit compatibility bridge after the common calculation API is wired.

Do not remove it blindly before:

- application-level calculation store exists;
- model registration happens at startup;
- calculation API exists;
- current participant-facing behavior is reviewed;
- legacy data migration policy is agreed.

---

## 15. Immediate next implementation steps

1. Inspect `main.py` store initialization.
2. Create one application-level `ModelCalculationPersistentStore`.
3. Create one application-level `ModelCalculationService`.
4. Register Health Model at application startup.
5. Add common model and calculation endpoints.
6. Change model parameter measurement endpoint to read only from calculation runs.
7. Run one persistent Health Model calculation through the API.
8. Confirm 35 parameter records appear after server restart.
9. Update parameter catalog/dependency/dataset builders to consume generic records.
10. Update Data Explorer.
11. Remove or isolate legacy model execution from `PilotSessionService`.
12. Add constructor API for parameter definitions.
13. Generalize the current Health Model-specific parameter registry into a multi-model definition store without breaking existing imports.

---

## 16. Quick “where do I look?” index

### I need the definition of a parameter

```text
research/analyses/health_model/model_parameter_registry.py
```

### I need the value of a calculated parameter

```text
ModelCalculationPersistentStore.list_parameter_records(...)
```

### I need to understand one calculation run

```text
research/model_calculation_schemas.py
ModelCalculationRun
```

### I need to run a model

```text
research/model_calculation_service.py
ModelCalculationService
```

### I need to register a new model

```text
research/model_registry.py
register_calculation_model(...)
```

### I need Health Model integration

```text
research/analyses/health_model/model_adapter.py
```

### I need Health Model formulas

```text
research/analyses/health_model/v61_calculator.py
```

### I need Health Model parameter records

```text
research/analyses/health_model/model_parameter_extractor.py
```

### I need persistent calculation storage

```text
research/model_calculation_store.py
```

### I need old parameter statistical dataset logic

```text
research/analyses/health_model/model_parameter_pair_dataset.py
```

### I need old dependency/method selection logic

```text
research/analyses/health_model/model_parameter_dependency_builder.py
```

### I need to find the current architectural mixing to remove later

```text
pilot_session/service.py
run_session(...)
```

---

## 17. Final rule

Whenever model parameters are needed for analysis, visualization, trajectory, forecast, comparison, export, or another model:

```text
read parameter definitions from the model parameter registry
read parameter observations from model calculation runs
respect model/version/definition/calculation identity
respect per-parameter calculation status
respect observation time and participant identity
never reconstruct scientific metadata from Python value types
never use questionnaire identity as model identity
never treat missing data as zero
```
