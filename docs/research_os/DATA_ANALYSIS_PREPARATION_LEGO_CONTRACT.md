# Data Analysis Preparation Lego Contract

## Core idea

We save data in a rich scientific form so that later we do not have to guess what the data are.

The first cube is the refrigerator label: it preserves the complete identity, origin, measurement context, structure, quality, coverage, calibration, permissions, provenance, and prepared payload of the collected data.

The next stage does not rediscover whether the data are questionnaire answers, sensor signals, event logs, images, or time series. It reads the preserved scientific description and decides what must be done before analysis and which analysis routes are possible.

The practical rule is simple:

Data are stored once with an exhaustive scientific label. Later processing must use that label, not infer blindly from raw values.

---

# 1. Why the first cube exists

The first cube exists so that every incoming domain dataset becomes a scientifically traceable prepared data object.

It answers:

- what data were collected;
- where they came from;
- which domain produced them;
- which instrument or source generated them;
- which participant/session/study they belong to;
- when they were collected;
- which global time reference they use;
- what source path and storage format they have;
- whether raw data are included or only referenced;
- what quality, coverage and calibration state they have;
- what is allowed to be done with them;
- whether they are ready to be handed to the next processing stage.

The first cube is not an analysis cube.

It does not decide which statistical method to use.
It does not build mechanisms.
It does not forecast.
It does not interpret participant state.
It does not calculate research conclusions.

Its role is to make sure that the data enter the system with enough scientific context that future processing does not become guesswork.

---

# 2. Data are not naked values

A value is not enough.

The number `4` means nothing by itself.

It may be:

- a Likert response;
- an ordinal rank;
- a score on a 0–5 risk scale;
- a count;
- a category code;
- a sensor amplitude;
- a time point;
- a frame index;
- a calibration label.

Therefore, storing only values is scientifically unsafe.

Every value must be stored with enough metadata to know what kind of value it is and what operations are scientifically allowed.

The chocolate analogy:

If we put chocolate in the refrigerator, we do not later inspect a brown object and guess what it is. We already know:

- it is chocolate;
- what type it is;
- how much it weighs;
- whether it has nuts;
- when it expires;
- how it should be handled.

The same applies to data.

When data are stored, their scientific identity must travel with them.

---

# 3. First cube output

The first cube produces a Prepared Domain Output.

Prepared Domain Output must preserve at least:

- schema_version;
- prepared_output_id;
- domain_id;
- source_type;
- study_id;
- session_id;
- participant_id;
- collection_metadata;
- data_reference;
- provenance;
- permission_status;
- quality;
- coverage;
- calibration;
- handoff;
- prepared_payload;
- raw_data_included.

It may also include or reference a data description section containing the scientific description of the data structure and measurement properties.

This description can include, depending on source category:

For questionnaires:

- question identifiers;
- question types;
- answer types;
- measurement scales;
- scale ranges;
- scale labels;
- score directions;
- required/optional status;
- active/inactive status;
- branching or transition logic;
- domain/family tags;
- item-level metadata.

For sensors:

- signal type;
- unit;
- sampling rate;
- temporal resolution;
- spatial resolution if applicable;
- device identifier;
- calibration reference;
- baseline reference;
- acquisition conditions;
- artifact rules;
- time axis;
- synchronization reference.

For games:

- event types;
- choice types;
- timing fields;
- sequence rules;
- trial structure;
- decision options;
- interaction logs;
- state transitions.

For images/video:

- spatial resolution;
- temporal resolution;
- color space;
- frame rate;
- sensor/camera metadata;
- segmentation or annotation reference;
- image acquisition context.

The exact content is domain-specific. The invariant is that the first cube must preserve the scientific description necessary for downstream processing.

---

# 4. The next cube: analysis preparation, not blind data guessing

After the first cube, the system should not ask:

"What are these values?"

It should ask:

"Given this known data object, what must be done to make it suitable for the intended analyses?"

This is the role of the next cube.

It uses two sources:

1. The preserved scientific description from the first cube.
2. The actual received payload or dataset.

The first source tells what the data are supposed to be.
The second source tells what actually arrived.

Both are needed.

Examples:

- The first cube may say a question is ordinal Likert 0–5.
- The actual payload may show some responses are missing.

- The first cube may say a sensor signal has 100 Hz sampling rate.
- The actual dataset may show dropped samples and noisy windows.

- The first cube may say a game logs event sequences.
- The actual payload may show that some trials were skipped.

The next cube must combine declared scientific description with actual dataset condition.

---

# 5. There is not one universal preparation

This is the key architectural correction.

Data preparation is not one universal operation.

The required preparation depends on:

- source category;
- data type;
- measurement scale;
- structure of observations;
- quality state;
- coverage state;
- calibration state;
- intended analysis family;
- whether the analysis is standard, dependency-oriented, longitudinal, delta-based, signal-based, image-based, or author-specific.

Therefore, one dataset may require multiple preparation routes.

A questionnaire dataset may need:

- preparation for descriptive statistics;
- preparation for item-level correlations;
- preparation for dependency analysis between specific answers;
- preparation for score aggregation;
- preparation for delta calculation;
- preparation for longitudinal comparison;
- preparation for author-defined model variables;
- preparation for missing-data aware analysis;
- preparation for export.

A sensor dataset may need:

- artifact detection;
- noise cleaning;
- filtering;
- normalization;
- calibration checking;
- baseline alignment;
- segmentation;
- feature extraction;
- synchronization with global time;
- windowing;
- quality exclusion rules.

A game dataset may need:

- event ordering;
- choice extraction;
- timing feature construction;
- reversal detection;
- sequence segmentation;
- state transition reconstruction;
- missing event checks;
- derived behavioral variables.

The system must therefore support multiple preparation branches from the same Prepared Domain Output.

---

# 6. Wrapper removal principle

The chocolate cannot be eaten until the wrapper is removed.

In data terms, before analysis, each source type may require source-appropriate preparation.

For questionnaires, the wrapper may be:

- raw answer format;
- category labels;
- missing/skipped/not applicable answers;
- reverse-coded items;
- branching effects;
- multiple-response encoding;
- scale direction;
- item-to-domain mapping.

For sensors, the wrapper may be:

- noise;
- artifacts;
- dropped samples;
- unsynchronized timestamps;
- uncalibrated signal values;
- device-specific units;
- baseline mismatch;
- invalid windows.

For images/video, the wrapper may be:

- frame extraction;
- segmentation masks;
- color normalization;
- resolution handling;
- artifact detection;
- missing frames;
- camera metadata alignment.

For games, the wrapper may be:

- raw event logs;
- duplicated events;
- incomplete sequences;
- timing jitter;
- state reconstruction;
- action-to-variable mapping.

Removing the wrapper is not analysis. It is preparation for analysis.

---

# 7. Analysis routes and preparation routes

The next cube should not produce a single prepared dataset.

It should produce preparation routes.

A route is a structured preparation plan for a specific analysis family or analysis purpose.

Examples:

## Questionnaire descriptive route

Purpose:

Prepare questionnaire answers for descriptive summaries.

May require:

- validate allowed values;
- preserve ordinal scale;
- count missing responses;
- compute response frequencies;
- prepare medians/percentiles if allowed;
- avoid invalid arithmetic means where scale does not allow them.

## Questionnaire item-correlation route

Purpose:

Prepare item-level answers for correlation/dependency analysis.

May require:

- align participants by item responses;
- include only comparable items;
- handle missing item pairs;
- choose correlation family according to scale;
- preserve ordinal/nominal distinction;
- block invalid item pairs.

## Questionnaire delta route

Purpose:

Prepare repeated or paired questionnaire data for delta calculation.

May require:

- verify same participant or same unit;
- verify comparable time points;
- verify same item/scale version;
- align global time references;
- calculate difference only when measurement scale supports it;
- preserve uncertainty if scale or timing mismatch exists.

## Sensor signal route

Purpose:

Prepare sensor signals for feature extraction or time-series analysis.

May require:

- verify sampling rate;
- check dropped samples;
- remove artifacts;
- filter noise;
- normalize signal;
- segment windows;
- align to global time reference;
- compute signal quality flags.

## Game event route

Purpose:

Prepare event logs for behavioral or sequence analysis.

May require:

- sort events by synchronized timestamp;
- reconstruct trial/session sequence;
- detect skipped or impossible transitions;
- extract choices;
- compute timing features;
- preserve reversals and hesitation markers.

---

# 8. Standard analysis is not the only goal

Questionnaire preparation must not be limited to standard scoring or descriptive statistics.

A research platform must also support:

- item-level dependency studies;
- correlations between specific questions;
- correlations between questionnaire items and sensor variables;
- longitudinal item changes;
- delta calculations;
- comparison of domains across time;
- custom derived variables;
- author-defined scores;
- mechanism-specific variables;
- validation of question usefulness;
- weak/redundant question detection;
- cross-domain relationships.

Therefore, questionnaire data must preserve item-level structure.

It is not enough to store only final domain scores.

The platform must support both:

1. Standard questionnaire analysis.
2. Research analysis of the questionnaire as a data source.

These are different preparation routes.

---

# 9. Relationship between Cube 1 and later preparation

Cube 1 stores what is known.

Later preparation reads what is known and decides what to do.

Cube 1 must not perform all future preparations in advance.

It must preserve enough information so that future preparations are possible.

For example:

- It should preserve item-level answers and item-level metadata.
- It should preserve scale and question type.
- It should preserve time reference.
- It should preserve missing/skipped/not applicable states.
- It should preserve calibration and quality context.
- It should preserve whether raw data are included or referenced.

Later preparation can then build routes without guessing.

---

# 10. Separation of responsibilities

## Cube 1: Data Preservation and Scientific Description

Responsible for:

- identity;
- source;
- metadata;
- data reference;
- provenance;
- permissions;
- data description;
- quality;
- coverage;
- calibration;
- prepared payload;
- handoff readiness.

Forbidden:

- choosing analysis methods;
- interpreting results;
- building mechanisms;
- forecasting;
- converting missing values into valid values;
- hiding uncertainty.

## Preparation Route Constructor

Responsible for:

- reading Prepared Domain Output;
- reading actual payload/dataset condition;
- identifying which preparation routes are needed;
- building source-appropriate preparation plans;
- preserving method-specific requirements;
- blocking impossible or scientifically invalid preparations.

Forbidden:

- interpreting participant state;
- producing conclusions;
- pretending invalid data are valid;
- forcing one universal preparation for all analyses.

## Analyzer Constructor

Responsible for:

- receiving prepared analysis-ready inputs;
- assembling analysis blocks;
- running selected or configured analysis methods;
- preserving assumptions, warnings, and limitations.

Forbidden:

- processing raw sensor signals directly;
- scoring raw questionnaires directly without preparation route;
- ignoring quality/calibration/coverage;
- silently using methods not allowed for the data type/scale/structure.

---

# 11. Practical architecture

The correct flow is:

Raw domain data

→ Cube 1: Prepared Domain Output

→ Analysis Preparation Planning

→ One or more preparation routes

→ Prepared analysis-specific inputs

→ Analyzer Constructor

→ Analysis Result

This means:

Prepared Domain Output is not the final analysis input for every possible analysis.

It is the authoritative scientific data object from which analysis-specific inputs are built.

---

# 12. Multiple preparation outputs

A single Prepared Domain Output may produce multiple downstream prepared inputs.

Example:

Questionnaire Prepared Domain Output

may produce:

- descriptive_prepared_input;
- item_correlation_prepared_input;
- domain_score_prepared_input;
- delta_prepared_input;
- longitudinal_prepared_input;
- author_model_prepared_input.

Sensor Prepared Domain Output

may produce:

- cleaned_signal_input;
- normalized_signal_input;
- window_feature_input;
- event_aligned_signal_input;
- baseline_relative_input;
- artifact_summary_input.

Game Prepared Domain Output

may produce:

- event_sequence_input;
- choice_feature_input;
- timing_feature_input;
- transition_matrix_input;
- behavioral_pattern_input.

Each output must state:

- source prepared_output_id;
- preparation_route_id;
- preparation_purpose;
- applied_steps;
- skipped_steps;
- blocked_steps;
- quality_after_preparation;
- coverage_after_preparation;
- remaining limitations;
- assumptions;
- allowed downstream analyses.

---

# 13. Scientific restrictions

The system must never assume that because a value is numeric, all numeric analysis is valid.

Numeric encoding does not automatically mean interval or ratio scale.

A Likert value may be stored as `1`, `2`, `3`, `4`, `5`, but the scientific meaning may be ordinal.

Therefore:

- arithmetic mean may be allowed only if justified by the chosen analytic convention;
- Pearson correlation must not be used blindly for ordinal data;
- delta calculation must not be done if the scale does not support meaningful subtraction;
- categorical codes must not be treated as continuous quantities;
- missing values must not be treated as zero;
- skipped and not applicable must not be collapsed silently;
- sensor noise removal must not erase meaningful signal without trace;
- calibration absence must not be treated as normal calibration.

---

# 14. What this solves

This architecture prevents:

- raw data entering analysis directly;
- repeated guessing of data type;
- loss of item-level questionnaire information;
- invalid statistical methods;
- one-size-fits-all preparation;
- sensor data being analyzed before cleaning/noise handling;
- questionnaire data being reduced too early to scores;
- missing data being converted to false values;
- future analyses being blocked because the original scientific context was lost.

It allows:

- standard analysis;
- custom author analysis;
- dependency analysis;
- item-level correlations;
- delta calculations;
- longitudinal analysis;
- sensor feature extraction;
- cross-domain analysis;
- validation studies;
- future analysis methods without changing the original stored data contract.

---

# 15. Final invariant

The first cube preserves the chocolate with its label.

The preparation route constructor removes the wrapper differently depending on what will be cooked.

The analyzer eats only properly prepared chocolate.

In scientific terms:

Prepared Domain Output preserves complete scientific data identity and context.

Preparation routes transform that preserved data object into analysis-specific inputs.

Analyzer Constructor performs analysis only on inputs prepared for the selected method.

There is no universal preparation.

There is no raw-data shortcut.

There is no guessing when the data were already saved with their scientific description.
