
Domain Data Identity Contract



Version


1.0 (Draft)

Status: Architecture Draft




Purpose


This document defines the mandatory identity contract for every domain data source within Research OS.

Its purpose is to guarantee that every collected dataset can be uniquely identified regardless of:

scientific domain;
acquisition technology;
collection method;
storage format;
analysis pipeline;
future system extensions.


The contract provides a universal identity layer that precedes all domain-specific preprocessing, preparation and analysis.




Architectural Position


The Domain Data Identity layer is the first mandatory layer after data acquisition.
Domain Data Source
        ↓
Domain Data Identity
        ↓
Domain-Specific Preparation
        ↓
Prepared Domain Output
        ↓
Domain Analysis
        ↓
Cross-Domain Analysis
        ↓
Research Analysis
Identity precedes preparation.

Preparation precedes analysis.

Analysis never creates or modifies source identity.




Scope


This contract applies to every domain capable of producing scientific data.

Examples include:

questionnaires;
sensors;
wearable devices;
laboratory devices;
games;
behavioral tasks;
VR / AR environments;
simulations;
imported datasets;
imaging systems;
signal acquisition systems;
future scientific domains.


No domain is exempt.




Core Principle


Every collected dataset must have exactly one identity.

Identity must remain stable throughout the entire scientific lifecycle.

Identity must not depend on:

preprocessing;
normalization;
analysis;
storage technology;
scientific interpretation.


Identity exists before all of them.




Responsibilities


The Domain Data Identity layer is responsible for:

uniquely identifying the collected data;
identifying its owner;
identifying its acquisition session;
identifying its domain;
identifying its acquisition method;
identifying its temporal position;
identifying its physical or logical origin.


It is not responsible for interpreting data.




Mandatory Fields



source_instance_id


Unique identifier of this specific data acquisition instance.

This identifier uniquely represents one collected source.

Examples:

questionnaire completion;
continuous sensor recording window;
VR session;
game execution;
imported recording;
laboratory measurement.


Every acquisition instance has exactly one source_instance_id.




session_id


Identifier of the acquisition session.

The session groups acquisition events belonging to the same research session.

A session may contain multiple source instances.

Example:

One participant session may include:

questionnaire;
HR sensor;
eye tracker;
VR task;
reaction-time game.


Each has its own source_instance_id.

All may share one session_id.




participant_id


Anonymous participant identifier.

Personally identifying information must remain outside this contract.




domain_id


Scientific domain responsible for producing the data.

Examples:

questionnaire
sensor
game
vr
laboratory
imaging
standard_method


Future domains may be added.




source_type


Describes the acquisition technology or interaction type.

Examples:

self_report
wearable_device
laboratory_device
interactive_task
vr_device
imported_dataset
simulation





data_structure_type


Describes the structural organization of the collected data.

Examples:

question_bank
time_series
event_log
signal_stream
image_sequence
video_sequence
tabular_measurements
structured_document


This field describes structure only.

It does not describe scientific meaning.




data_source_path


Logical or physical location of the original source.

The path must remain stable enough to preserve provenance.




collection_started_at


Timestamp indicating acquisition start.




collection_finished_at


Timestamp indicating acquisition completion.

Continuous acquisition windows must preserve both timestamps.




global_time_reference


Shared synchronized timeline identifier used across the research project.

This field enables later:

cross-domain synchronization;
temporal alignment;
multimodal analysis;
longitudinal analysis.


Global Time Reference remains mandatory even when only one domain exists.




Identity Invariants


The identity layer guarantees uniqueness across:

participant;
acquisition session;
acquisition instance;
scientific domain;
acquisition method;
temporal interval;
source location.


No two acquisition instances may share the same complete identity.




Identity Does Not Include


The identity layer must not contain:

scientific conclusions;
normalized values;
prepared outputs;
calculated parameters;
model predictions;
resource scores;
burden scores;
forecasts;
diagnoses;
interpretation.


Identity exists independently from scientific analysis.




Relationship to Domain Independence


Identity is domain-independent.

The same identity contract applies equally to:

questionnaires;
sensors;
games;
VR;
laboratory methods;
future scientific domains.


The contract introduces no dependency between domains.




Relationship to Prepared Domain Output


Prepared Domain Output references Domain Data Identity.

Prepared Domain Output does not redefine identity.

Prepared Domain Output may add:

preprocessing;
normalization;
validation;
domain metadata.


Identity remains unchanged.




Scientific Traceability


Every scientific observation must remain traceable back to exactly one Domain Data Identity.

Traceability must survive:

preprocessing;
export;
synchronization;
analysis;
publication.


Identity is never regenerated downstream.




Extensibility


Future domains may introduce additional identity metadata.

Additional fields must not modify or redefine the mandatory identity fields defined by this contract.




Final Principle


Domain Data Identity establishes the scientific identity of collected data.

It answers only one question:

“What exact acquisition instance produced these data?”

It does not answer:

what the data mean;
whether the data are valid;
how the data should be interpreted;
what conclusions may be drawn.


Those responsibilities belong to subsequent preparation and analysis layers.


:::writing{variant=“document” id=“52864”}


Questionnaire Data Description Block



Purpose


Questionnaire Data Description Block describes one questionnaire completion before normalization and analysis.

It answers:

What questionnaire was completed?

Which version was used?

Which questions were shown?

Which block each question belongs to?

Which answer scale was used?

Which answer was given?

How did the participant move between questions?

This block does not normalize answers and does not perform analysis.




Required Level 1: Questionnaire Completion


Each questionnaire completion must include:

questionnaire_id
questionnaire_version
questionnaire_completion_id
attempt_number
attempt_started_at
attempt_finished_at
previous_attempt_id
time_since_previous_attempt


If this is the first completion:

previous_attempt_id = null
time_since_previous_attempt = null


If the same questionnaire is completed multiple times, later preparation blocks may use these fields to build time-dependent comparisons.

This block stores the time relationship but does not calculate trajectory, trend, velocity or forecast.




Required Level 2: Question Records


Each question record must include:

question_block
question_number_in_block
question_id
question_version
question_type
scale
answer
answer_status
transition





question_block


Human-readable block of questions.

Examples:

physical_resource
cognitive_resource
psychological_resource
goal_resource
social_resource
financial_resource
recovery
pressure
markers





question_number_in_block


Number of the question inside its block.

This is not enough by itself to identify the question globally.




question_id


Unique identifier of the question.

Recommended pattern:
question_block + question_number_in_block
Example:
physical_resource_1




question_version


Version of the question text and meaning.

If the question changes scientifically, the version must change.




question_type


Type of question.

Examples:

single_choice
multiple_choice
numeric
likert
visual_analog_scale
text
ranking
date
time
duration


Question type is not the same as scale.




scale


Scale used to capture the answer.

Must include, when applicable:

scale_type
min
max
step
labels
direction
unit


Examples:
0–5 numeric scale
1–7 Likert scale
0–10 visual analog scale
yes/no categorical scale
free text




answer


Raw answer as given by the participant within the scale.

This is not yet normalized.




answer_status


Allowed values include:

ANSWERED
ANSWER_MISSING
SKIPPED_BY_LOGIC
NOT_APPLICABLE
REFUSED
INVALID_FORMAT
OUT_OF_RANGE
NOT_SCORABLE


Missing answer must not be treated as zero.




transition


Defines how participant moved after this question.

Sequential transition:
transition_type = sequential
next_question_id = ...
Conditional transition:
transition_type = conditional
condition = ...
next_question_id = ...
Terminal transition:
transition_type = terminal
next_question_id = null
If questionnaire navigation is not strictly sequential, transition logic must be explicitly preserved.




Scale-Dependent Preparation Rule


This block only records question type, scale and answer.

It does not decide how to normalize or score the answer.

The next preparation block chooses the correct processing path based on:

question_type
scale
answer_status
questionnaire_version
question_version
previous_attempt_id
time_since_previous_attempt





Forbidden


Questionnaire Data Description Block must not:

normalize answers;
score answers;
calculate domain scores;
calculate resource levels;
infer missing answers;
replace missing values with zero;
calculate trends;
calculate trajectory;
perform analysis.





Final Invariant


Questionnaire Data Description Block preserves the scientific structure of the questionnaire completion.

It prepares the data for normalization but does not interpret the data.
:::


