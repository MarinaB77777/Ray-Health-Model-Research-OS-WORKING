Pilot Session MVP Contract



Purpose


This document defines the minimum executable Pilot Session MVP layer for the university pilot version of the psychophysical readiness system.

The purpose of this layer is:

bounded participant/session orchestration;
bounded session persistence;
operational integration around /run;
research-safe snapshot handling;
explainable session state handling.


This document defines:

ParticipantSession structure;
SessionStatus lifecycle;
minimum persistence requirements;
required service functions;
export boundaries;
anti-drift rules;
test requirements.


This document does NOT:

redefine psychophysical calculations;
redefine Runtime architecture;
redefine Governance;
introduce Analyst behavior;
introduce Projection Layer;
introduce autonomous Runtime;
introduce hidden personalization;
introduce longitudinal profiling.





Pilot Session MVP Position


Pilot Session MVP operates as:

participant/session lifecycle shell
+
bounded persistence layer
+
integration layer around /run

The Pilot Session layer:

creates participant sessions;
stores submitted answers;
calls the psychophysical engine;
stores engine-produced result snapshots;
stores engine-produced acquisition request snapshots;
stores engine-produced clarification question snapshots;
stores public output snapshots;
exposes bounded exports.


The Pilot Session layer does NOT:

reinterpret engine results;
recalculate stress;
recalculate uncertainty;
modify forecast logic;
coordinate acquisition retries;
schedule clarification loops;
manage unresolved states as Runtime authority;
invent psychological meaning;
act as Analyst;
act as Runtime;
act as Governance;
create autonomous behavior.





Core Invariants


The Pilot Session layer preserves:

uncertainty visibility;
anti-fabrication behavior;
bounded operational scope;
public/internal output separation;
anti-profiling boundaries.


Core invariants:

session layer ≠ engine;
session layer ≠ Runtime;
session layer ≠ Governance;
session layer ≠ Analyst;
session persistence ≠ participant model;
stored snapshot ≠ recalculation authority;
stored uncertainty ≠ resolved uncertainty;
stored contradiction ≠ contradiction resolved;
export ≠ unrestricted disclosure;
stored result ≠ medical truth;
participant flow ≠ psychological authority;
session persistence ≠ longitudinal profiling authority.


The engine is the authoritative producer of bounded psychophysical computation results within its scope.




ParticipantSession Structure



Minimum Required Fields

ParticipantSession:
    session_id: str
    participant_id: str

    status: SessionStatus

    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]

    answers: dict

    engine_version: str
    engine_snapshot_schema_version: str
    public_output_schema_version: str
    export_schema_version: str

    raw_engine_result: dict
    public_output: dict

    next_question_snapshots: list
    acquisition_request_snapshots: dict

    uncertainty_snapshot: dict

    export_generated: bool
    export_policy_version: str
    invalidated: bool
    invalidation_reason: Optional[str]

MVP Debt Notice


raw_engine_result: dict is accepted only as a temporary MVP snapshot format.

It must not become:

hidden schema authority;
dumping ground;
implicit Runtime contract;
public export source without filtering;
cross-session profiling source.


Future versions should migrate toward:

explicit EngineSnapshot schema;
versioned internal contract;
separated internal/public persistence objects;
replay-safe audit metadata.





Participant Identity Boundary


participant_id is a research/pilot identifier.

It must not automatically imply:

real-world identity;
longitudinal profile;
psychological model;
cross-session behavioral inference;
hidden participant memory.


Any future identity mapping, re-identification, or cross-session linking must be governed by a separate research data contract.




SessionStatus Enum

SessionStatus:
    CREATED
    ANSWERS_RECEIVED
    RUN_COMPLETED
    WAITING_FOR_INPUT
    PARTIAL_RESULT
    EXPORT_READY
    EXPORT_BLOCKED
    RUN_FAILED
    INVALIDATED
    CLOSED

Minimum Allowed Transitions

CREATED → ANSWERS_RECEIVED
ANSWERS_RECEIVED → RUN_COMPLETED
ANSWERS_RECEIVED → RUN_FAILED
RUN_COMPLETED → WAITING_FOR_INPUT
RUN_COMPLETED → PARTIAL_RESULT
RUN_COMPLETED → EXPORT_READY
RUN_COMPLETED → EXPORT_BLOCKED
WAITING_FOR_INPUT → ANSWERS_RECEIVED
PARTIAL_RESULT → EXPORT_READY
EXPORT_READY → CLOSED
EXPORT_BLOCKED → CLOSED
RUN_FAILED → CLOSED
CLOSED → INVALIDATED
Rules:

direct invalid transitions are forbidden;
CLOSED means operationally closed, not epistemically final;
closed sessions must not be modified as ordinary active sessions;
audit-safe metadata updates and invalidation are allowed only through explicit service functions;
INVALIDATED marks that a stored session/export should no longer be treated as valid.





Stored Engine Snapshot


The session layer stores:

full raw engine result snapshot;
public output snapshot;
uncertainty snapshot;
next question snapshots;
acquisition request snapshots.


The session layer must NOT recalculate:

stress;
forecast;
uncertainty;
warnings;
public reasons;
domain summaries;
readiness state.


Engine-produced acquisition requests are stored only as snapshots.

They must NOT become:

session-owned queue;
retry schedule;
unresolved-state authority;
acquisition lifecycle owner;
hidden coordination mechanism.


Engine-produced next questions are stored only as snapshots.

They must NOT become:

adaptive dialogue memory;
behavioral profiling source;
cross-session optimization signal;
hidden personalization mechanism.





Public Output Boundary


Participant-facing output is based on:
result["output"]
This includes:

summary_text;
result_level;
forecast visibility;
domain_summary;
public warnings;
public reasons;
next_questions;
public uncertainty fields.


The public export must NOT expose:

internal Runtime state;
hidden governance metadata;
internal debug traces;
internal reasoning structures;
raw engine internals;
derived profiling;
cross-session hidden scoring.


Stored public output is not automatically an eternal valid export artifact.

Exports must carry:

export_schema_version;
export_policy_version;
generated_at;
session_id;
participant_id;
uncertainty state at generation time.





Research-Safe Persistence Boundary


For this MVP, research-safe persistence means:

store only session-scoped pilot data;
preserve uncertainty rather than smoothing it;
avoid hidden participant modeling;
avoid cross-session profiling;
avoid automatic identity enrichment;
avoid autonomous follow-up behavior;
preserve public/internal separation.


Research-safe persistence does NOT mean:

unrestricted retention;
unrestricted analytics;
hidden longitudinal modeling;
behavioral prediction;
psychological profiling;
medical record creation.


Retention duration, deletion policy, anonymization rules, and re-identification rules belong to the separate research data contract.




Required Service Functions


Minimum required functions:
create_session()
submit_answers()
run_session()
generate_export()
close_session()
invalidate_session()
get_session()
Rules:

run_session() calls run_engine_logic();
run_session() stores snapshots, not interpretations;
generate_export() uses stored public output plus current export policy boundary;
close_session() marks operational closure;
invalidate_session() marks a session/export as no longer valid;
closed sessions are not editable through ordinary lifecycle functions;
session service must not coordinate acquisition;
session service must not schedule clarification;
session service must not perform retry orchestration.





Export Boundaries


Export is:

bounded;
research-safe;
uncertainty-aware;
participant-readable when intended for participant view.


Export is NOT:

medical diagnosis;
psychiatric interpretation;
unrestricted profiling;
hidden behavioral analysis;
Runtime state dump;
raw internal debug artifact.


Research export and participant-facing export are different export modes and must not be silently merged.




Test Requirements


Before backend integration:

Required tests:

session schema tests;
lifecycle transition tests;
invalid transition tests;
persistence tests;
engine integration snapshot tests;
export boundary tests;
invalidation tests;
anti-mini-runtime tests.


All tests must pass before:

endpoint integration;
Render deployment;
pilot usage.





Immediate Implementation Scope


The immediate implementation target is:
pilot_session/
├── __init__.py
├── schemas.py
├── store.py
├── service.py
└── export.py
and:
tests/
├── test_pilot_session_schemas.py
├── test_pilot_session_store.py
├── test_pilot_session_service.py
└── test_pilot_session_export.py
This MVP implementation must remain within the bounded scope defined in this document.

The MVP may evolve through:
- bounded schema refinement;
- additional governed sensor integrations;
- additional bounded acquisition sources;
- additional participant-safe export modes;
- additional operational profiles;
- safety improvements;
- implementation hardening;
- explicit versioned contracts;
- bounded extensibility mechanisms.

The MVP must NOT silently evolve into:
- autonomous Runtime authority;
- hidden longitudinal profiling;
- unrestricted adaptive personalization;
- hidden psychological interpretation;
- unrestricted orchestration expansion;
- ungoverned analytical subsystems.
