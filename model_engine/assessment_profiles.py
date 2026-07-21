ASSESSMENT_PROFILES = {
    "resource_exhaustion": {
        "title": "Истощение ресурсов",
        "legacy_formula_blocks": {
            "physical_resource": {
                "questions": ["T1", "T2", "T3", "T4", "B3", "B4"],
                "formula": "R_phys",
                "level_table": "physical_resource",
            },
            "psychological_resource": {
                "questions": ["M1", "M2", "M3", "M4"],
                "formula": "R_psych",
                "level_table": "psychological_resource",
            },
            "goal_resource": {
                "questions": ["G1", "G2", "G3"],
                "formula": "R_goal",
                "level_table": "goal_resource",
            },
            "social_resource": {
                "questions": ["C1", "C2", "C3"],
                "formula": "R_social",
                "level_table": "social_autonomy_resource",
            },
            "financial_resource": {
                "questions": ["F1", "F2", "F3", "F4"],
                "formula": "R_fin",
                "level_table": "financial_resource",
            },
            "meaning_resource": {
                "questions": ["P1", "P2", "P3"],
                "formula": "R_spiritual",
                "level_table": "meaning_resource",
            },
        },
        "new_mechanism_blocks": {
            "recovery": {
                "questions": ["RE1", "RE2", "V3", "V4"],
                "status": "ORIENTING_BY_LEVEL_TABLE",
                "level_table": "recovery_resource",
            },
            "pep": {
                "questions": ["PEP1"],
                "status": "ORIENTING_BY_LEVEL_TABLE",
                "level_table": "pep",
            },
        },
        "critical_gate": ["K23", "K24"],
    },

    "decision_making": {
        "title": "Принятие решений",
        "legacy_formula_blocks": {
            "goal_resource": {
                "questions": ["G1", "G2", "G3"],
                "formula": "R_goal",
                "level_table": "goal_resource",
            },
            "physical_resource_check": {
                "questions": ["T1", "T2", "T3", "T4"],
                "formula": "R_phys",
                "purpose": "secondary_cognitive_pathway_check",
            },
            "psychological_resource_check": {
                "questions": ["M1", "M2", "M3", "M4"],
                "formula": "R_psych",
                "purpose": "secondary_cognitive_pathway_check",
            },
        },
        "new_mechanism_blocks": {
            "cognitive_resource": {
                "questions": [
                    "KCog1", "KCog2", "KCog3",
                    "KCog4", "KCog5", "KCog6", "KCog7",
                ],
                "status": "ORIENTING_BY_LEVEL_TABLE",
                "level_table": "cognitive_resource",
            },
            "learning_failure": {
                "questions": ["DR1", "DR2", "DR3"],
                "status": "ORIENTING_MECHANISM",
            },
            "commitment_trap": {
                "questions": ["DR4", "G13", "PV3"],
                "status": "ORIENTING_MECHANISM",
            },
            "decision_degradation": {
                "questions": ["DR5", "DR6", "DR7", "MT1", "MT2", "MT3", "MT4"],
                "status": "ORIENTING_MECHANISM",
            },
            "option_space_collapse": {
                "questions": ["G9", "G9a", "Q3", "Q9", "FR1", "SR1"],
                "status": "ORIENTING_MECHANISM",
            },
        },
        "critical_gate": ["K23", "K24"],
    },

    "problem_trajectory": {
        "title": "Траектория проблемы",
        "legacy_formula_blocks": {
            "load_pressure_proxy": {
                "questions": [
                    "B8", "B9",
                    "D7", "D8", "D9", "D10",
                    "D11a", "D11b", "D11c", "D11d",
                    "D12", "D13",
                    "E1", "E1a", "E1b", "E1c", "E1d",
                    "E2", "E2a", "E2b", "E2c",
                    "E3", "E3a", "E3b", "E3c",
                    "E4", "E4a", "E4b", "E4c",
                    "E5", "E6",
                    "E7", "E7a", "E7b", "E7c",
                ],
                "formula": "Pressure_proxy / L_external",
                "status": "ORIENTING_PROXY",
            },
            "resource_deficit": {
                "questions": [
                    "T1", "T2", "T3", "T4",
                    "M1", "M2", "M3", "M4",
                    "G1", "G2", "G3",
                    "C1", "C2", "C3",
                    "F1", "F2", "F3", "F4",
                    "P1", "P2", "P3",
                ],
                "formula": "R",
            },
        },
        "new_mechanism_blocks": {
            "problem_context": {
                "questions": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10"],
                "status": "ORIENTING_TRAJECTORY_CONTEXT",
            },
            "velocity_recovery": {
                "questions": ["V1", "V2", "V3", "V4", "RE1", "RE2"],
                "status": "ORIENTING_BY_LEVEL_TABLE",
            },
            "commitment_and_values": {
                "questions": ["PV1", "PV2", "PV3", "PV4", "PV5", "PV6", "PV6a", "PV6b"],
                "status": "ORIENTING_MECHANISM",
            },
            "decision_patterns": {
                "questions": ["DR1", "DR2", "DR3", "DR4", "DR5", "DR6", "DR7"],
                "status": "ORIENTING_MECHANISM",
            },
            "pep": {
                "questions": ["PEP1"],
                "status": "ORIENTING_BY_LEVEL_TABLE",
                "level_table": "pep",
            },
        },
        "critical_gate": ["K23", "K24"],
    },
}
