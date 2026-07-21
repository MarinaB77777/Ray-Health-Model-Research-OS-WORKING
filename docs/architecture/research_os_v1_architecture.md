# Research OS v1 Architecture

Version: 1.0 (Draft)

Status: Architecture Draft

---

# 1. Purpose

## 1.1 Mission

Research OS is a universal scientific research platform designed to support the complete lifecycle of research projects independent of scientific discipline.

The platform provides a common architecture for planning, conducting, validating, documenting, reproducing and publishing research while allowing domain-specific scientific modules to be connected without changing the platform core.

Research OS is not a health model.

Research OS is not a psychology platform.

Research OS is not a statistics package.

Research OS is the operating environment in which scientific research is performed.

---

## 1.2 Goals

Research OS is designed to:

- organize complete research projects;
- support interdisciplinary research;
- separate scientific knowledge from implementation;
- provide reproducible research workflows;
- integrate heterogeneous scientific assets;
- maintain scientific traceability;
- support collaboration between researchers;
- support AI-assisted scientific work without replacing scientific responsibility.

---

## 1.3 Non-goals

Research OS does not define:

- domain mathematical models;
- statistical algorithms;
- medical conclusions;
- scientific truth.

Scientific models, algorithms and domain knowledge are external modules connected to the platform.

---

# 2. Scope

Research OS manages scientific work.

The platform may include:

- research projects;
- protocols;
- hypotheses;
- experiments;
- questionnaires;
- sensors;
- laboratory devices;
- datasets;
- analysis pipelines;
- statistical methods;
- AI collaboration;
- validation workflows;
- publications;
- knowledge management.

Research OS does not restrict the scientific discipline.

The same architecture must support psychology, medicine, physics, biology, engineering and future scientific domains.

---

# 3. Scientific Architecture Principles

## 3.1 Scientific Neutrality

Research OS never assumes a scientific discipline.

The platform does not distinguish between psychology, medicine, physics, engineering, biology or any future scientific domain.

Scientific disciplines are implemented as domain modules connected to the common platform.

The platform core remains discipline-independent.

---

## 3.2 Separation of Scientific Knowledge and Platform

Research OS manages scientific work.

Research OS does not define scientific knowledge.

Domain knowledge belongs to domain modules.

Scientific models remain independent from the platform.

The platform must remain usable even when completely different scientific models are connected.

---

## 3.3 Scientific Traceability

Every scientific object must have traceable origin.

Every hypothesis, dataset, experiment, result, analysis, conclusion and publication must preserve its provenance.

Research OS must always answer:

- where did this originate?
- how was it produced?
- which version was used?
- who created it?
- which evidence supports it?

Traceability is mandatory.

---

## 3.4 Scientific Reproducibility

Every completed research process should be reproducible whenever possible.

The platform should preserve sufficient information to reproduce:

- datasets;
- preprocessing;
- experimental configuration;
- software versions;
- model versions;
- statistical methods;
- analysis configuration.

Reproducibility is a design objective of the platform.

---

## 3.5 Evidence Before Conclusion

Research OS never treats hypotheses as knowledge.

Evidence precedes validation.

Validation precedes accepted knowledge.

Accepted knowledge precedes publication.

Scientific conclusions are produced only after sufficient supporting evidence.

---

## 3.6 No Fabrication

Research OS must never fabricate scientific reality.

If data is missing, insufficient, unavailable, contradictory, outdated, unverified or outside the system boundary, the platform must explicitly mark this state instead of filling the gap with assumptions.

Unknown remains unknown.

Not collected remains not collected.

Not measured remains not measured.

Not validated remains not validated.

The platform must never invent:

- observations;
- measurements;
- participant data;
- sensor data;
- device readings;
- experimental outcomes;
- statistical significance;
- correlations;
- causal explanations;
- mechanisms;
- validation results;
- scientific conclusions.

When the system does not know, it must ask for clarification, request additional data, mark the result as insufficient, or stop the process.

Scientific accuracy has priority over completeness.

A missing answer is better than a fabricated answer.

Only scientifically defined methods may be used to support scientific claims.

Unsupported claims must remain hypotheses, questions, assumptions, or unknowns.

---

## 3.7 Human Scientific Responsibility

Scientific responsibility always belongs to the human researcher.

Research OS assists scientific work.

Research OS never replaces scientific judgement.

AI systems may propose, critique, organize or analyze.

Final scientific responsibility remains with the human investigator.

---

## 3.8 Interdisciplinary Design

A research project may combine arbitrary scientific domains.

Questionnaires,
sensors,
laboratory devices,
mathematical models,
images,
time series,
games,
AI collaboration,
and future scientific modules
may coexist within the same research project.

The platform architecture must never assume a single scientific discipline.

4. Research OS Laws

# 4. Research OS Laws

The following laws define non-negotiable architectural constraints of Research OS.

Every subsystem, module, workflow, AI component, scientific model and future extension must comply with these laws.

Violation of a Research OS Law is considered an architectural defect.

---

## Law #1 — Scientific Process over Scientific Truth

Research OS never determines scientific truth.

Research OS manages the scientific process by which scientific knowledge is investigated, validated and documented.

Scientific conclusions belong to scientific evidence and human judgement, not to the platform itself.

---

## Law #2 — No Fabrication

Research OS must never fabricate scientific reality.

If information is unavailable, missing, contradictory, uncertain or outside system boundaries, the platform must preserve that state explicitly.

Unknown remains unknown.

Not measured remains not measured.

Not collected remains not collected.

Not validated remains not validated.

The platform must never invent:

- observations;
- measurements;
- participant data;
- sensor values;
- device readings;
- experimental outcomes;
- statistical significance;
- causal explanations;
- mechanisms;
- scientific conclusions.

When information is insufficient, the platform must:

- request additional information;
- recommend additional measurements;
- recommend additional experiments;
- explicitly mark insufficient evidence;
- or stop the scientific process.

Scientific accuracy always has priority over apparent completeness.

---

## Law #3 — Evidence Before Conclusion

No scientific conclusion may exist without explicit supporting evidence.

Evidence must precede:

- interpretation;
- validation;
- accepted knowledge;
- publication.

Hypotheses are not evidence.

Correlation is not causation.

Candidate findings are not validated knowledge.

---

## Law #4 — Honest Uncertainty

Research OS must preserve uncertainty rather than hide it.

Whenever certainty is not scientifically justified, uncertainty must remain explicitly represented.

Unknown remains unknown.

Estimated remains estimated.

Hypothesized remains hypothesized.

Candidate patterns remain candidate patterns until validated.

Confidence is metadata.

Confidence never replaces evidence.

---

## Law #5 — Ask Instead of Assume

When required information is unavailable, the platform must never silently replace missing knowledge with assumptions.

The preferred order is:

1. obtain missing information;
2. request clarification;
3. recommend additional measurements;
4. recommend additional experiments;
5. explicitly mark uncertainty.

Assumptions must always be identified as assumptions.

---

## Law #6 — Scientific Methods Only

Scientific claims may only be supported using scientifically defined methods.

Research OS must distinguish between:

- observation;
- hypothesis;
- assumption;
- experiment;
- statistical result;
- interpretation;
- validated knowledge.

These categories are never interchangeable.

---

## Law #7 — Human Scientific Responsibility

Scientific responsibility always belongs to the human researcher.

Research OS assists scientific work.

AI systems may:

- organize;
- critique;
- suggest;
- analyse;
- document.

AI systems must never replace scientific responsibility.

---

## Law #8 — Single Source of Truth

Every scientific entity has exactly one authoritative source.

Projects reference scientific assets.

Projects do not own scientific definitions.

Registries define scientific entities.

Projects use them.

---

## Law #9 — Reproducibility

Every scientific result should be reproducible whenever technically possible.

Research OS should preserve sufficient information to reproduce the scientific workflow.

---

## Law #10 — Extensibility Without Core Modification

New scientific domains must extend the platform without modifying the Research OS core.

Scientific disciplines are plugins.

The platform core remains discipline-independent.

If a choice exists between a complete answer and a scientifically honest answer, Research OS always chooses the scientifically honest answer.

## Law #12 — Applications Extend the Core

Research OS core must remain independent from administrative, financial, procurement, publication-formatting and regulatory workflows.

Such capabilities are implemented as applications connected to the core, not as core concepts.

Examples of future Research OS applications include:

- Grant Manager;
- Publication Manager;
- Procurement Manager;
- Inventory Manager;
- Budget Manager;
- Ethics / IRB Manager;
- Laboratory Operations Manager;
- Teaching / Course Manager.

These applications may reference Projects, Assets, Processes, Teams, Results and Publications.

They must not redefine core entities.

They must not change scientific evidence.

They must not bypass Research OS Laws.

---

## Law #13 — Independent Workspace

Workspace ownership must not depend on a university, institution or administrative structure.

A Workspace may belong to:

- an independent researcher;
- a research group;
- a laboratory;
- a startup;
- a company;
- a university group;
- an international consortium.

Institutional administration may be integrated as an external application or permission layer, but it must not control the scientific core by default.

Research OS is designed to support independent scientific work.

## 5.2 Project

### Purpose

A Project is the primary scientific container within Research OS.

A Project represents one coherent scientific initiative conducted within a Workspace.

Projects organize scientific work.

Projects do not define scientific knowledge.

---

### Responsibilities

A Project is responsible for:

- defining research objectives;
- organizing research protocols;
- grouping hypotheses;
- managing experiments;
- collecting datasets;
- organizing analyses;
- coordinating validation;
- tracking scientific progress;
- organizing publications;
- maintaining project history.

A Project coordinates scientific work.

A Project does not perform scientific work.

---

### Does Not

A Project does not:

- execute experiments;
- perform statistical calculations;
- define scientific entities;
- own registry definitions;
- determine scientific truth;
- replace scientific evidence.

---

### Owns

A Project owns:

- Protocols
- Hypotheses
- Experiments
- Analyses
- Results
- Validation Records
- Publications
- Project Notes
- Project Timeline

These objects exist only within the Project.

---

### References

A Project references shared scientific assets.

Examples include:

- Questions
- Sensors
- Devices
- Mechanisms
- Parameters
- Models
- Datasets
- Statistical Methods
- Literature
- External Repositories

Referenced assets remain owned by their registries.

Projects never duplicate scientific definitions.

---

### Team

Every Project contains a Research Team.

Team members may include:

- Principal Investigator
- Researchers
- Collaborators
- Statisticians
- Reviewers
- AI Colleague

Membership defines participation.

Scientific responsibility remains human.

---

### Modules

Projects activate only the modules they require.

Examples:

- Questionnaires
- Sensors
- Devices
- Imaging
- Signal Processing
- Health Model
- PupillAI
- Statistics
- Forecast
- Validation
- Publications

The platform core does not require any specific module.

---

### Lifecycle

A Project progresses through independent scientific stages.

Typical lifecycle:

Draft

↓

Planning

↓

Protocol Approved

↓

Data Collection

↓

Analysis

↓

Validation

↓

Publication Preparation

↓

Published

↓

Archived

Stages may iterate.

Scientific work is rarely linear.

## 5.3 Asset

### Purpose

An Asset represents any reusable scientific resource that may participate in one or more research projects.

Assets are independent scientific objects.

Assets may exist before, during or after a Project.

Projects consume Assets.

Projects do not define Assets.

---

### Responsibilities

Assets provide reusable scientific resources.

Examples include:

- Questions
- Questionnaires
- Sensors
- Devices
- Laboratory Equipment
- Games
- Simulations
- VR / AR Scenarios
- Digital Twins
- LLM Prompts
- AI Interaction Protocols
- Images
- Videos
- Audio
- Signals
- Time Series
- Models
- Parameters
- Mechanisms
- Formulas
- Algorithms
- Datasets
- Statistical Methods
- Publications
- Literature
- Protocol Templates
- Experiment Templates
- Calibration Procedures
- Measurement Procedures

Assets are reusable.

Assets are versionable.

Assets are independently managed.

---

### Does Not

An Asset does not:

- own Projects;
- execute scientific processes;
- perform analyses;
- determine conclusions;
- replace evidence.

Assets describe scientific resources.

---

### Ownership

Every Asset has exactly one authoritative owner.

Ownership may belong to:

- a Registry;
- a Workspace;
- an external repository.

Projects reference Assets.

Projects do not duplicate Assets.

---

### Versioning

Assets may evolve over time.

Every Asset version must preserve:

- identifier;
- version;
- author;
- creation date;
- modification history;
- compatibility information.

Historical versions remain reproducible.

---

### Relationships

Assets may be referenced by:

- Projects;
- Experiments;
- Protocols;
- Analyses;
- Publications;
- Knowledge Objects.

Multiple Projects may reference the same Asset.


### Digital and Interactive Assets

Research OS must support non-traditional scientific Assets.

Examples include:

- simulation environments;
- VR / AR experimental scenarios;
- digital twins;
- LLM prompts;
- AI interaction protocols;
- interactive behavioral tasks;
- synthetic experiment environments.

These Assets are scientific resources only if they are explicitly defined, versioned, traceable and reproducible.

A simulation result is not evidence unless the simulation configuration, assumptions, parameters and validation status are preserved.

An LLM output is not evidence by itself.

AI-generated material must be marked as AI-generated and must not be treated as observed reality unless independently verified.

VR / AR scenarios must preserve scenario version, timing, stimuli, interaction logs and measurement rules.

---

### Lifecycle

Draft

↓

Reviewed

↓

Approved

↓

Published

↓

Deprecated

↓

Archived

Historical versions remain available.

---

### Invariants

Every Asset has a stable identifier.

Assets remain independent of Projects.

Projects reference Assets rather than copying them.

Assets are reusable across Workspaces whenever permissions allow.

---

### Extensibility

New Asset types may be introduced without modifying existing Asset architecture.

Scientific disciplines define Asset specializations rather than replacing the Asset model.



---

### Invariants

A Project belongs to exactly one Workspace.

A Project never owns scientific registries.

A Project references shared Assets.

A Project preserves complete scientific history.

Deleting a Project must never silently delete shared scientific assets.

Scientific evidence remains traceable throughout the Project lifecycle.

---

### Extensibility

Projects support arbitrary future scientific modules, workflows and applications without modification of Project architecture.

## 5.4 Hypothesis

### Purpose

A Hypothesis represents a scientifically testable proposition within a Project.

A Hypothesis defines a question to be investigated.

A Hypothesis is never scientific evidence.

A Hypothesis is never scientific knowledge.

---

### Responsibilities

A Hypothesis is responsible for defining:

- the scientific question;
- the expected relationship;
- the variables involved;
- the proposed mechanisms;
- the planned validation methods;
- the expected evidence.

A Hypothesis defines what is being investigated.

It does not define the outcome.

---

### Does Not

A Hypothesis does not:

- prove itself;
- execute experiments;
- perform statistical analyses;
- generate conclusions;
- become knowledge automatically.

---

### References

A Hypothesis may reference:

- Questions;
- Parameters;
- Mechanisms;
- Models;
- Assets;
- Datasets;
- Literature;
- Previous hypotheses;
- Publications.

Referenced scientific objects remain independent.

---

### Evidence

Evidence is collected independently from the Hypothesis.

Evidence may support,
contradict,
partially support,
or remain insufficient to evaluate the Hypothesis.

Evidence never changes historical hypothesis definitions.

---

### Validation

Every Hypothesis must define, before investigation whenever possible:

- validation criteria;
- statistical methods;
- acceptance criteria;
- rejection criteria;
- stopping criteria;
- required evidence.

Changing validation criteria after observing results must remain traceable.

---

### Lifecycle

Draft

↓

Proposed

↓

Approved for Investigation

↓

Evidence Collection

↓

Analysis

↓

Validation

↓

Supported

or

Rejected

or

Inconclusive

or

Archived

Support is never equivalent to proof.

## 5.5 Protocol

### Purpose

A Protocol defines how scientific work will be conducted.

A Protocol describes the complete execution methodology of a scientific investigation.

Protocols ensure scientific reproducibility.

Protocols do not contain scientific conclusions.

---

### Responsibilities

A Protocol defines the scientific execution plan.

The Protocol may describe:

- study design;
- experimental methodology;
- questionnaires;
- measurement procedures;
- laboratory procedures;
- sensor configuration;
- device configuration;
- calibration procedures;
- participant workflow;
- simulation configuration;
- VR / AR scenarios;
- AI interaction procedures;
- data acquisition;
- preprocessing;
- quality control;
- statistical analysis plan;
- validation procedures;
- stopping criteria;
- safety procedures;
- ethical requirements.

---

### Does Not

A Protocol does not:

- contain scientific evidence;
- contain experimental results;
- validate hypotheses;
- produce conclusions;
- replace scientific judgement.

---

### References

A Protocol references scientific Assets.

Examples include:

- Questions
- Questionnaires
- Sensors
- Devices
- Laboratory Equipment
- Models
- Parameters
- Mechanisms
- Simulations
- VR / AR Scenarios
- Statistical Methods
- Calibration Procedures
- Measurement Procedures

Protocols reference Assets.

Protocols do not redefine Assets.

---

### Versioning

Protocols are versioned.

Changes remain completely traceable.

Historical protocol versions remain reproducible.

Projects always reference the protocol version actually used.

---

### Lifecycle

Draft

↓

Internal Review

↓

Approved

↓

Active

↓

Completed

↓

Archived

---

### Invariants

Protocols are immutable once approved.

Protocol revisions create new versions.

Experiments always reference exactly one protocol version.

Scientific results remain linked to the protocol under which they were obtained.

---

### Extensibility

Scientific domains may extend Protocols with discipline-specific sections.

The Protocol architecture remains independent of any scientific discipline.

---

### Invariants

A Hypothesis belongs to exactly one Project.

A Hypothesis remains immutable after approval.

Revisions create new versions.

Historical hypotheses remain preserved.

Negative results remain part of scientific history.

Rejected hypotheses are not deleted.

---

### Extensibility

Future scientific domains may extend Hypotheses with domain-specific metadata without modifying the core Hypothesis architecture.

# 17. Applications

## Purpose

Applications extend Research OS with specialized capabilities while keeping the platform core independent from administrative, scientific and organizational workflows.

Applications consume Core Entities.

Applications never redefine Core Entities.

Applications never bypass Research OS Laws.

---

## Principles

Applications are optional.

Research OS remains fully functional without any specific Application.

Applications may be installed, removed or replaced independently.

Applications communicate with the Core only through public contracts.

---

## Examples

Examples of Applications include:

- AI Documentation Assistant
- Publication Manager
- Grant Manager
- Procurement Manager
- Inventory Manager
- Laboratory Operations
- Statistics Studio
- Visualization Studio
- Ethics / IRB Manager
- Teaching Manager
- Collaboration Manager

Future Applications may be introduced without modification of the Research OS Core.

---

## AI Documentation Assistant

The AI Documentation Assistant supports researchers by automatically assembling scientific documentation from information already available within a Project.

The researcher should never be required to enter the same information multiple times.

The assistant may generate:

- research protocols;
- methodology sections;
- equipment descriptions;
- sensor configurations;
- questionnaire descriptions;
- statistical methods;
- calibration summaries;
- project documentation;
- publication drafts.

The assistant always preserves links to original project data.

Automatically generated documentation remains editable by the researcher.

---

## Missing Information

If required information is unavailable, the assistant must never invent it.

Instead, the assistant shall:

- identify missing information;
- request clarification;
- recommend additional documentation;
- clearly indicate incomplete sections.

Incomplete documentation is preferable to fabricated documentation.

---

## Traceability

Every automatically generated document must preserve traceability.

Each generated section should reference its source whenever possible.

Researchers must always be able to determine where every generated statement originated.

---

## Extensibility

New Applications may be added without changing the architecture of Research OS.

Applications may integrate with future scientific disciplines, external services and organizational workflows while preserving Core integrity.

10. Experiment

## Purpose

An Experiment represents a single execution of a scientific investigation within a Project.

An Experiment performs scientific work.

An Experiment produces scientific observations.

An Experiment does not produce scientific conclusions.

---

## Responsibilities

An Experiment is responsible for executing a defined scientific procedure.

An Experiment may include:

- participant sessions;
- laboratory measurements;
- questionnaires;
- sensor acquisition;
- device acquisition;
- simulations;
- imaging;
- behavioral tasks;
- data collection;
- calibration activities;
- quality control procedures.

---

## Does Not

An Experiment does not:

- define hypotheses;
- define scientific Assets;
- validate scientific knowledge;
- perform publication.

---

## References

An Experiment may reference:

- Project;
- Hypotheses;
- Assets;
- Datasets;
- Models;
- Protocols (optional);
- Devices;
- Sensors;
- AI Applications.

Referenced objects remain independent.

---

## Results

An Experiment produces:

- observations;
- measurements;
- datasets;
- logs;
- metadata.

Scientific conclusions are produced later during Analysis.

---

## Lifecycle

Planned

↓

Prepared

↓

Running

↓

Completed

↓

Validated

↓

Archived

Cancelled experiments remain part of project history.

---

## Invariants

Every Experiment belongs to exactly one Project.

Every observation remains traceable to the Experiment that produced it.

Raw observations remain immutable.

Corrections never overwrite original observations.

---

## Extensibility

Scientific disciplines may extend Experiments with discipline-specific execution details.

The Experiment architecture remains discipline-independent.

# 11. Dataset

## Purpose

A Dataset represents a structured collection of scientific observations produced, imported or derived during research.

A Dataset is a scientific object.

A Dataset is not a storage format.

---

## Responsibilities

A Dataset is responsible for preserving scientific observations together with sufficient metadata for interpretation, validation and reuse.

Datasets may contain:

- participant responses;
- sensor recordings;
- laboratory measurements;
- device outputs;
- images;
- videos;
- audio;
- physiological signals;
- simulation outputs;
- derived measurements;
- calculated parameters.

---

## Does Not

A Dataset does not:

- define scientific hypotheses;
- define scientific Assets;
- determine scientific conclusions;
- replace statistical analysis.

---

## Sources

Datasets may originate from:

- Experiments;
- imported external data;
- scientific repositories;
- simulations;
- laboratory instruments;
- questionnaires;
- sensors;
- AI-assisted preprocessing;
- manually verified scientific observations.

The origin of every Dataset must remain traceable.

---

## Metadata

Every Dataset should preserve sufficient metadata for scientific interpretation.

Examples include:

- source;
- acquisition time;
- acquisition method;
- software version;
- model version;
- device version;
- preprocessing history;
- quality indicators;
- permissions;
- provenance.

---

## Storage Independence

A Dataset is independent from its storage format.

The same Dataset may be represented as:

- SQL;
- CSV;
- JSON;
- Parquet;
- HDF5;
- Images;
- Video;
- Binary sensor files;
- Future storage technologies.

Storage technology does not define the Dataset.

---

## Versioning

Datasets are versioned.

Original observations remain preserved.

Derived datasets reference their parent datasets.

Every transformation remains traceable.

---

## Lifecycle

Created

↓

Validated

↓

Used

↓

Referenced

↓

Archived

Deletion must follow explicit retention policies.

---

## Invariants

Every Dataset has a stable identifier.

Every Dataset preserves provenance.

Raw observations remain immutable.

Derived datasets never overwrite source datasets.

Every Dataset remains traceable to its origin.

---

## Extensibility

Scientific domains may extend Dataset metadata while preserving the common Dataset architecture.

FINAL

Файл:
docs/architecture/research_os/21_architecture_map.md
# 21. Research OS Architecture Map

## Purpose

This document defines the one-page architecture map of Research OS.

It shows the stable system layers, core entities, applications, extension points and non-negotiable boundaries.

Research OS is not a health model, not an AI product, not a statistics package and not an administrative system.

Research OS is the operating environment for scientific work.

---

## Architecture Map

```text
WORKSPACE
│
├── Research Team
│   ├── Human Researcher
│   ├── Collaborators
│   ├── Reviewers
│   └── AI Colleague / Ray
│
├── Shared Scientific Assets
│   ├── Questions / Questionnaires
│   ├── Sensors / Devices / Laboratory Equipment
│   ├── Models / Parameters / Mechanisms / Formulas
│   ├── Datasets / Signals / Images / Videos
│   ├── Simulations / VR / AR / Digital Twins
│   ├── LLM Prompts / AI Interaction Protocols
│   ├── Statistical Methods
│   └── Literature / Publications / Templates
│
├── Projects
│   │
│   └── Project
│       ├── Research Goals
│       ├── Hypotheses
│       ├── Experiments / Investigations
│       ├── Data / Results
│       ├── Analyses
│       ├── Validation
│       ├── Knowledge
│       └── Publications
│
├── Applications
│   ├── AI Documentation Assistant
│   ├── Publication Manager
│   ├── Grant Manager
│   ├── Procurement / Inventory
│   ├── Laboratory Operations
│   ├── Statistics Studio
│   ├── Visualization Studio
│   └── Ethics / IRB / Compliance
│
└── Core Laws
    ├── No Fabrication
    ├── Evidence Before Conclusion
    ├── Honest Uncertainty
    ├── Human Scientific Responsibility
    ├── Single Source of Truth
    ├── Progressive Complexity
    ├── Passive Documentation
    └── Capture Once




Core Boundary


Research OS Core contains only universal scientific concepts:

Workspace
Project
Asset
Team
Hypothesis
Experiment / Investigation
Dataset / Result
Analysis
Validation
Knowledge
Publication


The Core does not contain:

grants;
procurement;
inventory;
university administration;
publication formatting;
country-specific regulation;
domain-specific scientific models;
mandatory protocol bureaucracy.


Those belong to Applications or domain modules.




Applications Boundary


Applications extend the Core.

Applications may support funding, publication, procurement, documentation, statistics, laboratory management and compliance.

Applications may reference Core entities.

Applications must not redefine Core entities.

Applications must not alter scientific evidence.

Applications must not bypass Research OS Laws.




Protocol Position


Protocol is not mandatory workflow bureaucracy.

Protocol is an attachable scientific documentation form.

It may be generated automatically from project activity when needed.

Ray / AI Documentation Assistant may prepare protocol drafts from existing project data.

Missing information must be marked or requested.

Nothing may be invented.




Researcher Experience Principle


Research OS must support work first.

The system must not force unnecessary administrative structure before scientific work can proceed.

Small work remains lightweight.

Complex work may progressively attach advanced structures, documentation, validation, procurement, grants or compliance.

The researcher should not repeat information already known to the system.




Extension Points


Research OS supports extension through:

new Asset types;
new Applications;
new domain modules;
new scientific workflows;
new devices and sensors;
new statistical methods;
new AI collaboration modes;
new publication and grant systems.


Extensions must connect to the Core without changing Core concepts.




Architecture Invariant


If a choice exists between a complete-looking system and a scientifically honest system, Research OS always chooses scientific honesty.

No data means no conclusion.

Unknown means ask, measure, mark unknown or stop.

Hypothesis remains hypothesis until tested by scientific methods.

