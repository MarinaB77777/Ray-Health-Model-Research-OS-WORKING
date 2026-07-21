# Analyzer Constructor Boundary

## Core Principle

Analyzer Constructor does not start from raw data.

Analyzer Constructor starts from Prepared Domain Output.

Raw domain data must first pass through domain-specific preparation.

---

## Boundary Rule

Raw Questionnaire Data  
≠  
Raw Sensor Data

Raw Sensor Data  
≠  
Raw EEG Data

Raw Game Data  
≠  
Raw Interview Data

Therefore raw data cannot be the universal input of Analyzer Constructor.

---

## Required Separation

The architecture must separate:

1. Domain Preparation Constructor
2. Analyzer Constructor

---

## Domain Preparation Constructor

Domain Preparation Constructor is responsible for transforming raw domain data into Prepared Domain Output.

Examples:

Questionnaire:

raw answers  
→ validation  
→ scoring  
→ mapping  
→ quality flags  
→ Prepared Questionnaire Output

Sensor:

raw signal  
→ artifact detection  
→ cleaning  
→ calibration check  
→ segmentation  
→ feature extraction  
→ synchronization  
→ quality flags  
→ Prepared Sensor Output

---

## Analyzer Constructor

Analyzer Constructor receives Prepared Domain Output only.

It builds analysis structures from analysis-ready domain outputs.

Analyzer Constructor must not:

- process raw sensor signals;
- score raw questionnaires directly;
- perform domain-specific cleaning;
- perform calibration;
- infer missing preparation;
- treat raw data as analysis-ready.

---

## Prepared Domain Output Rule

Prepared Domain Output is the contract between domain preparation and analysis.

Prepared Domain Output contains:

1. common scientific metadata;
2. domain-specific prepared payload.

Common metadata does not mean common payload.

---

## Architecture Consequence

Analyzer Constructor may operate across domains only after each domain has produced its own Prepared Domain Output.

Cross-domain analysis may combine Prepared Domain Outputs.

Cross-domain analysis must not require raw domain data.

---

## Final Invariant

Domain-specific raw data is prepared inside the domain.

Analyzer Constructor operates only on prepared, validated, provenance-preserving, analysis-ready domain outputs.