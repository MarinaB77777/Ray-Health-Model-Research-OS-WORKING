# Domain Data Preparation Contract

## Core Principle

Raw domain data must not enter Analyzer Constructor directly.

Every domain must first produce Prepared Domain Output.

## Required Flow

Raw Domain Data  
→ Domain Data Preparation  
→ Prepared Domain Output  
→ Analyzer Constructor

## Preparation Blocks

Domain Data Preparation consists of three required blocks:

1. Common Metadata Block
2. Domain Data Structure Block
3. Normalization and Handoff Block

## 1. Common Metadata Block

Common for all domains:

- data_source_path
- domain_id
- source_type
- participant_id
- session_id
- study_id
- collection_started_at
- collection_finished_at
- global_time_reference
- provenance
- permission_status
- raw_data_included

## 2. Domain Data Structure Block

Domain-specific structure definition.

Examples:

Questionnaire:
- question_id
- question_type
- answer_type
- scale
- score_direction
- domain
- family
- active/status

Sensor:
- signal_type
- unit
- sampling_rate
- device_id
- calibration_reference
- time_axis
- artifact_rules

## 3. Normalization and Handoff Block

Defines:

- normalization rules
- quality rules
- coverage rules
- skipped / invalid data rules
- prepared payload
- save target
- handoff format

## Output

The output is Prepared Domain Output.

Prepared Domain Output must contain:

1. common scientific metadata;
2. domain-specific prepared payload.

Common metadata does not mean common payload.

## Forbidden

Domain Data Preparation must not:

- perform analysis;
- build mechanisms;
- build forecasts;
- infer missing data;
- treat missing data as zero;
- mix domains;
- require another domain to exist.

## Final Invariant

Analyzer Constructor receives only Prepared Domain Output, never raw domain data.

## Prepared Domain Output Schema

:::writing{variant=“document” id=“70482”}

Prepared Domain Output Schema

Prepared Domain Output is the only valid input for Analyzer Constructor.

Every Prepared Domain Output must contain the following top-level sections:

schema_version
prepared_output_id
domain_id
source_type
study_id
session_id
participant_id
collection_metadata
data_reference
provenance
quality
coverage
calibration
prepared_payload
handoff
raw_data_included

1. schema_version

Identifies the schema version of the Prepared Domain Output.

Example:

prepared-domain-output-1

2. prepared_output_id

Stable identifier of this prepared output object.

3. domain_id

Domain that produced the prepared output.

Examples:

questionnaire
sensor
game
eeg
pupillogram
interview
standard_method

4. source_type

Type of original source.

Examples:

self_report
time_series
signal
image
event_log
text
structured_record

5. study_id

Study or assessment identifier.

6. session_id

Collection session identifier.

7. participant_id

Pseudonymous participant identifier.

No full name is stored here.

8. collection_metadata

Must contain:

collection_started_at
collection_finished_at
global_time_reference
timezone
collection_context

9. data_reference

Must contain:

data_source_path
storage_type
data_format
data_checksum

Raw data may be referenced, but does not need to be embedded.

10. provenance

Must contain:

created_by
created_at
preparation_version
model_version
software_version
source_version

11. quality

Must contain:

quality_status
quality_score
quality_flags
invalid_items
skipped_items
not_scorable_items

12. coverage

Must contain:

coverage_score
expected_item_count
available_item_count
used_item_count
missing_item_count

13. calibration

Must contain:

calibration_required
calibration_available
calibration_reference_id
calibration_confidence
calibration_freshness
context_match

If calibration is not applicable, it must be explicitly marked as not applicable.

14. prepared_payload

Domain-specific prepared data.

Examples:

Questionnaire:

domain_scores
family_scores
item_scores

Sensor:

signal_features
artifact_summary
window_features

Game:

event_features
choice_features
timing_features

Common metadata does not mean common payload.

15. handoff

Must contain:

handoff_ready
handoff_target
allowed_analysis_types
blocked_analysis_types
handoff_notes

16. raw_data_included

Boolean.

Default must be:

false

Raw data should not be included unless explicitly allowed.

Final rule:

Prepared Domain Output must preserve uncertainty, provenance, quality, coverage and calibration state.

It must not pretend that unavailable data exists.

Prepared Output Builder Block Contract

Domain Data Preparation is assembled from blocks.

Each block must have:
 • block_id
 • block_type
 • input_contract
 • output_contract
 • responsibility
 • forbidden_responsibility
 • required_fields
 • optional_fields
 • not_enough_data_rules
 • not_applicable_rules
 • provenance_requirements

⸻

Block 1. Common Metadata Block

Responsibility:

Collect common metadata required for every domain.

Input:
 • raw domain source reference
 • session context
 • participant reference
 • study reference
 • collection time metadata
 • permission metadata

Output:
 • collection_metadata
 • data_reference
 • participant_id
 • session_id
 • study_id
 • domain_id
 • source_type
 • provenance base

Must not:
 • score data
 • normalize values
 • interpret meaning
 • build analysis output

⸻

Block 2. Domain Data Structure Block

Responsibility:

Describe the structure of domain data.

Input:
 • domain definition
 • raw data schema
 • item/question/signal/event definitions

Output:
 • domain_structure
 • item_structure
 • measurement_structure
 • scale_or_unit_structure
 • expected_item_count
 • required_item_rules

Must not:
 • compute final analysis
 • infer missing items
 • replace unknown values
 • mix with another domain

⸻

Block 3. Calibration / Reference Block

Responsibility:

Define what the data is interpreted relative to.

Input:
 • calibration references
 • baseline references
 • normative references
 • context references

Output:
 • calibration
 • reference_basis
 • calibration_required
 • calibration_available
 • calibration_confidence
 • context_match

Must not:
 • fabricate calibration
 • treat missing baseline as normal
 • convert weak calibration into certainty

⸻

Block 4. Quality and Coverage Block

Responsibility:

Describe whether the prepared data is usable.

Input:
 • domain_structure
 • available data
 • invalid/skipped/artifact rules

Output:
 • quality
 • coverage
 • skipped_items
 • invalid_items
 • not_scorable_items
 • missing_item_count

Must not:
 • treat missing as zero
 • treat missing as negative result
 • hide insufficient data

⸻

Block 5. Normalization Block

Responsibility:

Transform valid raw/domain values into prepared comparable values.

Input:
 • valid domain data
 • scale/unit rules
 • calibration/reference rules
 • normalization rules

Output:
 • normalized_values
 • normalized_units
 • normalization_method
 • normalization_warnings

Must not:
 • invent missing values
 • perform scientific interpretation
 • build mechanisms
 • build forecast

⸻

Block 6. Prepared Payload Block

Responsibility:

Build the domain-specific prepared payload.

Input:
 • normalized values
 • domain structure
 • quality
 • coverage
 • calibration

Output:
 • prepared_payload

Examples:

Questionnaire:
 • item_scores
 • domain_scores
 • family_scores

Sensor:
 • signal_features
 • artifact_summary
 • window_features

Game:
 • event_features
 • choice_features
 • timing_features

Must not:
 • replace common metadata
 • erase uncertainty
 • compute downstream analysis

⸻

Block 7. Handoff Block

Responsibility:

Prepare the object for Analyzer Constructor.

Input:
 • common metadata
 • quality
 • coverage
 • calibration
 • prepared_payload

Output:
 • handoff
 • handoff_ready
 • allowed_analysis_types
 • blocked_analysis_types
 • handoff_notes

Must not:
 • force readiness
 • hide blocked analysis
 • allow raw data to bypass preparation
 • allow analysis without sufficient prepared output

⸻

Final Builder Rule

Prepared Output Builder is complete only when:
 • common metadata exists;
 • domain structure exists;
 • quality and coverage are explicit;
 • calibration/reference state is explicit;
 • normalized or prepared values are available;
 • prepared_payload exists;
 • handoff state is explicit.

If any required part is missing, the output must be marked as not ready for analysis.

# Block 2 — Data Description Builder

## Purpose

The Data Description Builder constructs the second block of the Prepared Domain Output.

Its purpose is to produce a complete scientific description of the collected data before any preprocessing, calibration, normalization or analysis.

The builder describes the collected data.

It does not interpret the collected data.

---

## Builder Principle

The Data Description Builder is a configurable constructor.

It is assembled from reusable scientific description components.

The builder itself is domain-independent.

Questionnaires, sensors, laboratory devices, games, imaging systems and future data sources are supported by selecting and assembling appropriate description components.

The builder architecture must not require modification when new source categories are introduced.

---

## Source Category

Every Data Description Block begins with the selection of a Source Category.

The Source Category determines which Component Panel becomes available.

Examples of Source Categories include:

- Questionnaire
- Video Camera
- Thermal Camera
- Eye Tracker
- ECG
- EEG
- EMG
- PPG
- Accelerometer
- Gyroscope
- GPS
- Audio Recorder
- Laboratory Device
- Imaging Device

Additional Source Categories may be introduced without modifying the builder architecture.

---

## Component Panels

Each Source Category owns its own Component Panel.

A Component Panel is a collection of reusable scientific description components applicable only to that category.

A Component Panel defines:

- required components;
- optional components;
- validation rules;
- compatibility rules.

Different Source Categories expose different Component Panels.

---

## Component Selection

The researcher assembles the Data Description Block by selecting description components from the Component Panel of the selected Source Category.

The resulting Data Description Block therefore depends on the selected Source Category and selected Components.

No fixed universal Data Description structure exists.

The builder remains extensible through Component Panels.

---

## Category-Specific Requirements

Each Source Category defines its own required scientific description components.

Examples include:

Questionnaire

- question type
- scale
- answer status
- transition logic

Video Camera

- spatial resolution
- temporal resolution
- sensor matrix
- exposure
- color space

EEG

- channel configuration
- sampling frequency
- reference configuration
- electrode configuration

Thermal Camera

- spatial resolution
- temporal resolution
- temperature resolution
- spectral range

The required description components are determined only by the selected Source Category.

---

## Builder Output

The Data Description Builder produces one complete Data Description Block.

This block becomes Block 2 of the Prepared Domain Output.

The output is ready for the next preparation stage.

---

## Forbidden

The Data Description Builder must not:

- preprocess data;
- calibrate data;
- normalize data;
- calculate derived variables;
- calculate scores;
- calculate trends;
- perform scientific interpretation;
- perform analysis;
- estimate missing values.

---

## Final Invariant

The Data Description Builder constructs a complete scientific description of collected data using reusable category-specific components.

It describes the data.

It does not process the data.
Я специально не включил сюда:

наследование компонентов;
реестр устройств;
подключение приборов;
конкретные модели устройств.


Почему? Потому что это уже следующий уровень архитектуры (Registry/Assets), а этот раздел описывает только конструктор второго кубика. Если сейчас добавить туда реестр устройств, мы смешаем конструктор, каталог научных объектов и систему регистрации оборудования. Это уже будет нарушение разделения ответственности, которое мы сами же проводим во всей архитектуре.

Block 3 — Questionnaire Data Preparation Builder

Purpose

The Questionnaire Data Preparation Builder constructs the preparation pipeline that transforms questionnaire responses into a scientifically valid representation for downstream analysis.

The builder does not interpret questionnaire results.

The builder prepares questionnaire data according to the declared measurement properties of each question.

⸻

Builder Principle

The Questionnaire Data Preparation Builder is itself a configurable constructor.

The builder automatically derives the initial preparation pipeline from the configuration created in Block 2.

Researchers configure preparation policies rather than individual mathematical transformations.

⸻

Input

The builder automatically receives from Block 2:
 • Question Identifier
 • Question Block
 • Question Type
 • Measurement Scale
 • Scale Definition
 • Scale Labels
 • Scale Range
 • Response Value
 • Response Status
 • Transition Logic
 • Session Information

No information is entered again.

⸻

Preparation Profile Builder

Each question automatically receives a Preparation Profile determined by its Measurement Scale.

Examples:

Nominal Profile

Ordinal Profile

Interval Profile

Ratio Profile

Likert Item Profile

Binary Profile

Registered Questionnaire Profile

Researchers may select another registered profile only when scientifically justified.

⸻

Representation Builder

The builder determines how questionnaire data will be represented after preparation.

Examples include:

Categorical Representation

Ordered Categorical Representation

Interval Numeric Representation

Ratio Numeric Representation

Longitudinal Representation

The selected representation must remain compatible with the declared Measurement Scale.

⸻

Missing Data Builder

The builder defines how missing questionnaire responses are represented.

Possible representations include:

Missing

Skipped

Not Applicable

Refused

Unknown

Incomplete Session

Missing responses must never be silently converted into valid questionnaire values.

⸻

Validation Builder

Validation is determined automatically from the selected Question Type and Measurement Scale.

Validation may include:
 • allowed values;
 • allowed categories;
 • scale boundaries;
 • response type validation;
 • transition validation;
 • completeness validation.

Validation must never change participant responses.

⸻

Longitudinal Builder

If multiple questionnaire sessions exist, the builder defines how responses are prepared for longitudinal analysis.

Examples:

Current Session Only

Independent Sessions

Linked Sessions

Time Series Representation

Session Sequence

Time Interval Representation

The builder prepares longitudinal structure.

It does not perform longitudinal analysis.

⸻

Provenance Builder

Every preparation step must remain traceable.

Preparation metadata should include:
 • preparation profile;
 • profile version;
 • preparation timestamp;
 • preparation rules applied;
 • validation results;
 • transformation history.

⸻

Output

The Questionnaire Data Preparation Builder produces questionnaire data represented in the scientifically appropriate format for the declared Measurement Scale.

The output is ready for domain analysis.

The builder does not perform scientific analysis.

⸻

Forbidden

The Questionnaire Data Preparation Builder must not:
 • calculate questionnaire scores;
 • calculate domain scores;
 • calculate psychological resources;
 • calculate health indicators;
 • perform statistical analysis;
 • interpret participant responses;
 • change the declared Measurement Scale;
 • promote one Measurement Scale into another without an explicitly registered scientific preparation profile.

⸻

Final Invariants
 • Preparation follows the declared Measurement Scale.
 • Preparation follows the declared Question Type.
 • Scientific preparation rules are transparent and reproducible.
 • Raw questionnaire responses remain preserved.
 • Prepared questionnaire data are analysis-ready but are not analysis results.
 • Preparation does not perform interpretation.

⸻

# Block 3 — Questionnaire Data Preparation Builder
добавляем новый раздел.



# Block 3 — Sensor Data Preparation Builder

## Purpose

The Sensor Data Preparation Builder constructs the preparation pipeline that transforms raw sensor measurements into scientifically valid, analysis-ready sensor representations.

The builder prepares sensor data.

The builder does not interpret sensor data.

The builder does not perform scientific analysis.

The builder preserves raw measurements.

---

## Builder Principle

The Sensor Data Preparation Builder is a configurable constructor.

The initial preparation pipeline is automatically derived from:

- Sensor Category;
- Measurement Type;
- Measurement Characteristics;
- Recording Characteristics;
- Component configuration defined in Block 2.

Researchers configure preparation policies rather than individual preprocessing algorithms.

---

# Input

The builder automatically receives from Block 2:

- Source Category;
- Sensor Category;
- Measurement Type;
- Measurement Units;
- Sampling Characteristics;
- Spatial Characteristics;
- Temporal Characteristics;
- Device Characteristics;
- Recording Characteristics;
- Acquisition Conditions;
- Session Information.

No information is entered again.

---

# Preparation Profile Builder

Each registered Sensor Category automatically selects its own Preparation Profile.

Examples include:

- Video Camera Preparation Profile;
- Thermal Camera Preparation Profile;
- Eye Tracker Preparation Profile;
- ECG Preparation Profile;
- EEG Preparation Profile;
- EMG Preparation Profile;
- PPG Preparation Profile;
- Accelerometer Preparation Profile;
- Gyroscope Preparation Profile;
- Microphone Preparation Profile;
- Laboratory Device Preparation Profile.

Preparation Profiles define:

- required preparation stages;
- optional preparation stages;
- validation rules;
- compatible reference systems;
- supported output representations.

Researchers may select another registered profile only when scientifically justified.

---

# Reference Builder

Sensor measurements may optionally be represented relative to a selected Reference.

Reference selection is independent of scientific interpretation.

Reference selection does not modify raw measurements.

Available Reference Types may include:

- No Reference;
- Device Calibration;
- Personal Baseline;
- Population Reference;
- Clinical Reference;
- Environmental Reference;
- Experimental Baseline;
- Registered Custom Reference.

Every selected Reference should define:

- reference identifier;
- reference type;
- reference source;
- reference validity;
- reference timestamp;
- reference quality;
- reference confidence.

---

# Representation Builder

After Reference selection, the builder prepares the sensor representation.

Available representations may include:

- Raw Measurement;
- Difference from Reference;
- Percent Difference;
- Standardized Difference;
- Normalized Representation;
- Reference Category;
- Multi-layer Representation.

Multiple representations may be generated simultaneously.

The selected representation must preserve scientific traceability.

---

# Quality Builder

The builder prepares recording quality descriptors.

Quality preparation may include:

- recording completeness;
- missing segments;
- dropped samples;
- synchronization quality;
- acquisition consistency;
- sensor integrity;
- acquisition metadata validation;
- artifact markers.

Quality preparation does not evaluate physiological meaning.

---

# Calibration Builder

The builder prepares calibration metadata.

Calibration preparation may include:

- calibration identifier;
- calibration timestamp;
- calibration validity;
- calibration freshness;
- calibration confidence;
- baseline availability;
- baseline quality.

Calibration preparation does not perform calibration interpretation.

---

# Longitudinal Builder

If repeated recordings exist, the builder prepares longitudinal representation.

Available preparation modes may include:

- Current Recording Only;
- Independent Recordings;
- Linked Recordings;
- Recording Sequence;
- Time Series Representation;
- Session Order;
- Time Interval Representation.

The builder prepares longitudinal structure.

The builder does not perform longitudinal analysis.

---

# Provenance Builder

Every preparation step must remain reproducible.

Preparation metadata should include:

- preparation profile;
- preparation profile version;
- preparation timestamp;
- selected reference;
- representation type;
- validation results;
- preparation history.

---

# Output

The Sensor Data Preparation Builder produces sensor data represented in a scientifically reproducible form for downstream analysis.

The output may simultaneously contain:

- raw measurements;
- reference information;
- prepared representation;
- quality descriptors;
- calibration metadata;
- provenance metadata.

Prepared sensor data are analysis-ready.

Prepared sensor data are not analysis results.

---

# Forbidden

The Sensor Data Preparation Builder must not:

- estimate physiological state;
- estimate psychological state;
- estimate readiness;
- estimate fatigue;
- estimate stress;
- estimate disease;
- estimate diagnosis;
- calculate health scores;
- calculate resource scores;
- calculate domain scores;
- perform forecasting;
- perform scientific interpretation;
- perform scientific analysis.

---

# Final Invariants

Preparation follows the declared Sensor Category.

Preparation follows the declared Measurement Characteristics.

Preparation follows the selected Reference.

Raw measurements remain preserved.

Reference selection never changes raw measurements.

Prepared representations remain reproducible.

Prepared sensor data are analysis-ready but are not analysis results.

Deviation from Reference is not scientific interpretation.

Deviation from Reference is not diagnosis.

Deviation from Reference is not psychophysical conclusion.

Preparation does not perform interpretation.