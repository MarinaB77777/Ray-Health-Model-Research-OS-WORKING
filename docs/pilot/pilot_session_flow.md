# Pilot Session Flow

## Purpose


This document defines the operational participant/session flow for the university pilot version of the psychophysical readiness system.

The purpose of this flow is:

bounded psychophysical assessment;
readiness-oriented interaction;
uncertainty-aware clarification;
explainable operational outputs;
research-safe session handling.


This document defines:

participant lifecycle;
session lifecycle;
clarification flow;
acquisition flow;
readiness evaluation flow;
output generation boundaries.


This document does NOT:

define medical diagnosis;
define psychiatric truth;
define unrestricted profiling;
define autonomous Runtime behavior;
define Inner Core behavior.


The pilot operates within bounded research-session scope.

The pilot does not establish:

continuous human-state authority;
continuous behavioral surveillance;
persistent psychological interpretation outside active session boundaries.





Pilot Scope


Pilot v1 includes:

bounded Base Ray
+
psychophysical/readiness subsystem
+
governed operational interaction

Pilot v1 excludes:

Inner Core;
Projection Layer;
autonomous Runtime;
unrestricted learning;
deep adaptive memory;
Domain Rays;
hidden personalization.





Core Principles



Operational Principles


The pilot preserves:

uncertainty visibility;
contradiction legitimacy;
bounded clarification;
operational explainability;
anti-fabrication behavior.


Core invariants:

NOT_ENOUGH_DATA = valid state
Unknown ≠ 0
contradiction ≠ failure
clarification ≠ diagnosis
assessment ≠ diagnosis
prediction ≠ certainty
forecast ≠ deterministic human prediction
readiness ≠ medical truth
silence ≠ confirmation
participant uncertainty ≠ invalid participation





Human Protection Principles


The pilot must NOT:

psychologically profile participants;
infer hidden identity;
fabricate conclusions;
force coherence;
silently escalate authority;
simulate medical certainty.





Participant Lifecycle



High-Level Flow

participant registered
→ consent
→ session started
→ questionnaire flow
→ acquisition requests
→ readiness evaluation
→ clarification loop
→ result generation
→ research export
→ session closed
Pilot interaction and longitudinal observation must remain:

bounded;
uncertainty-aware;
non-coercive;
consent-aware;
operationally scoped.


Core invariants:

longitudinal observation ≠ unrestricted participant surveillance
session closure ≠ epistemic completion
research export ≠ Runtime continuation





Participant Creation



Participant ID


Each participant receives:

participant_id;
pilot-scoped identifier.


The pilot should avoid:

unnecessary personally identifying information;
unrestricted identity linkage.





Consent Phase



Consent Required


Before session start:

participant must receive pilot explanation;
participant must receive boundary explanation;
participant must receive uncertainty explanation;
participant must confirm participation consent.





Consent Boundaries


Consent does NOT imply:

medical diagnosis;
psychological ownership;
unrestricted data reuse;
unrestricted learning;
unrestricted memory retention.


Participants may:

pause participation;
skip questions;
terminate participation;


without forced completion pressure.




Session Lifecycle



Session States

CREATED
CONSENT_PENDING
READY
ACTIVE
WAITING_FOR_INPUT
ANALYZING
CLARIFICATION_REQUIRED
RESULT_READY
EXPORTED
CLOSED




Session State Meanings



CREATED


Session object initialized.

No participant interaction yet.




CONSENT_PENDING


Waiting for participant consent.

Core invariant:

consent pending
≠ readiness evaluation permission

No readiness evaluation allowed.




READY


Consent completed.

Session may begin.




ACTIVE


Participant actively interacting with questionnaire/acquisition flow.




WAITING_FOR_INPUT


System awaiting:

participant response;
clarification;
acquisition data;
questionnaire continuation.


Core invariants:

WAITING ≠ abandoned
WAITING ≠ resolved





ANALYZING


Psychophysical engine processing:

answers;
readiness;
uncertainty;
consistency;
acquisition gaps.





CLARIFICATION_REQUIRED


Additional clarification needed because of:

contradiction;
insufficient coverage;
uncertainty;
incomplete readiness state.


Core invariants:

clarification ≠ diagnosis
clarification ≠ deception detection





RESULT_READY


Bounded operational output prepared.

Core invariant:

result generation
≠ certainty

Result generation does NOT imply:

diagnosis;
complete understanding.





EXPORTED


Research-safe export completed.




CLOSED


Session lifecycle completed.

Core invariant:

closed session
≠ permanent truth




Questionnaire Flow



Initial Questionnaire


The initial questionnaire gathers:

B context;
D activity/load;
E external pressure;
resource indicators;
K_self markers;
uncertainty-relevant gaps.





Activity-First Routing


The pilot uses:

activity-first interpretation;
operational Human Profiles;
contextual clarification routing.


Core invariant:

activity-first routing
≠ participant identity determination

Profiles remain:

probabilistic;
revisable;
non-authoritative.





Human Profiles


Current operational baseline profiles include:

Academic / Analytical;
Field / Operational;
Household / Coordination;
Student / Learning.


Profiles are:

contextual operational heuristics;
not diagnoses;
not identity labels;
not authority sources.


Core invariant:

profile hint
≠ verified reality




Acquisition Flow



Acquisition Requests


The system may request:

additional questionnaire answers;
clarification;
context;
sensor input (future-compatible);
calibration-related input (future-compatible).


Core invariant:

acquisition request
≠ acquisition success




Acquisition Boundaries


The pilot does NOT assume:

unavailable data;
hidden context;
inferred truth from silence.


Missing data remains:

visible;
uncertainty-relevant;
operationally important.





Clarification Flow



Clarification Legitimacy


Clarifications may occur when:

contradiction detected;
uncertainty too high;
readiness incomplete;
context insufficient.





Clarification Principles


Clarification must remain:

bounded;
respectful;
uncertainty-aware;
interruption-aware.


Clarification must NOT become:

interrogation;
coercion;
hidden profiling;
forced interpretation.


Clarification may remain incomplete when operational uncertainty remains acceptable.

Participant refusal to answer clarification requests is valid.

Missing clarification must preserve uncertainty, not force inferred interpretation.

Core invariants:

clarification pressure ≠ improved research quality
clarification refusal ≠ participant non-cooperation





Readiness Evaluation



Readiness Purpose


Readiness evaluation estimates:

operational strain;
overload likelihood;
recovery degradation;
uncertainty level;
consistency level.


Readiness evaluation does NOT determine:

psychiatric diagnosis;
moral truth;
hidden intention;
deception.


Analyzer evaluates operational consistency and readiness signals, not medical or psychiatric truth.




Readiness Outputs


Outputs may include:

readiness score/state;
uncertainty level;
warnings;
clarification requests;
next_questions;
operational recommendations.


Core invariant:

operational output
≠ definitive psychological truth




Forecast Boundaries


Forecasts are allowed only when:

coverage sufficient;
uncertainty acceptable;
consistency acceptable;
no critical block present.


Forecast may be blocked when:

insufficient coverage;
contradiction unresolved;
hidden-factor risk;
uncertainty too high.


Core invariant:

blocked forecast
≠ system failure




Result Generation



Public Output


Participant-visible outputs may include:

operational summary;
uncertainty visibility;
bounded recommendations;
clarification suggestions;
overload warnings.





Result Boundaries


Results must remain:

bounded;
uncertainty-aware;
non-diagnostic;
operational.


Core invariant:

result generation
≠ medical conclusion




Research Export



Export Scope


Research exports may include:

anonymized participant_id;
session_id;
timestamps;
readiness outputs;
uncertainty states;
warnings;
questionnaire responses.





Export Restrictions


Research exports must NOT include:

Inner Core;
unrestricted dialogue history;
hidden identity reconstruction;
raw psychological profiling;
unrestricted behavioral inference.


Research export must preserve:

uncertainty visibility;
participant consent boundaries;
bounded interpretation semantics.


Core invariant:

research export
≠ unrestricted truth export




Session Closure



Closure Rules


Session closure:

finalizes operational flow;
finalizes export eligibility;
freezes session lifecycle state.


Session closure does NOT:

finalize participant identity;
define permanent readiness truth;
authorize unrestricted retention.


Core invariants:

session closure ≠ epistemic completion
partial closure ≠ failed session
unresolved closure ≠ solved state





Pilot Architectural Position


The university pilot is:

bounded operational psychophysical readiness system

with:

explainable outputs;
uncertainty visibility;
governed interaction;
anti-fabrication principles;
bounded Runtime behavior.


The pilot is NOT:

AGI;
autonomous therapist;
unrestricted adaptive AI;
psychological authority system.

