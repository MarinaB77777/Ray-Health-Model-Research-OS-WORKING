# assessment/mappings/resource_level_maps.py

NOT_ENOUGH_DATA = "NOT_ENOUGH_DATA"


def score_to_level(score):
    if score is None:
        return NOT_ENOUGH_DATA

    if score <= 1:
        return "0-1"

    if score < 2.5:
        return "2"

    if score < 3.5:
        return "3"

    if score < 4.5:
        return "4"

    return "5"


LEVEL_MAPS = {
    "goal": {
        "0-1": {
            "resource_state": "Цели выполняют организующую функцию поведения.",
            "vulnerable_functions": [],
            "preserved_functions": [
                "goal_clarity",
                "goal_commitment",
                "future_oriented_cognition",
                "prioritization",
                "goal_directed_behavior",
                "goal_adjustment_capacity",
            ],
            "candidate_mechanisms": [],
        },
        "2": {
            "resource_state": "Появляются первые признаки рассогласования между целями и повседневными действиями.",
            "vulnerable_functions": [
                "future_oriented_cognition",
                "prioritization",
                "goal_maintenance",
            ],
            "preserved_functions": [
                "goal_clarity",
                "basic_planning",
            ],
            "behavioral_consequences": [
                "short_term_task_displacement",
                "attention_shift_to_near_needs",
            ],
            "decision_consequences": [
                "short_term_bias",
                "weaker_long_term_alignment",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
            ],
        },
        "3": {
            "resource_state": "Цели начинают хуже удерживать поведение во времени.",
            "vulnerable_functions": [
                "goal_commitment",
                "goal_directed_behavior",
                "goal_maintenance",
                "goal_shielding",
                "conflict_resolution_between_goals",
                "prioritization",
            ],
            "preserved_functions": [
                "basic_goal_understanding",
            ],
            "behavioral_consequences": [
                "delayed_important_actions",
                "direction_switching",
                "implementation_inconsistency",
                "unfinished_projects",
            ],
            "decision_consequences": [
                "comfort_over_long_term_direction",
                "reduced_sequence_of_goal_actions",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
                "LearningFailure",
            ],
        },
        "4": {
            "resource_state": "Организующая функция целей становится выраженно менее устойчивой.",
            "vulnerable_functions": [
                "prioritization",
                "value_consistent_behavior",
                "goal_adjustment_capacity",
                "persistence",
                "goal_commitment",
                "delay_of_gratification",
            ],
            "preserved_functions": [
                "knowledge",
                "reasoning",
                "emotionally_significant_goals",
            ],
            "behavioral_consequences": [
                "goal_conflict_growth",
                "cyclic_movement_and_abandonment",
                "difficulty_stopping_ineffective_path",
                "difficulty_changing_goal_strategy",
            ],
            "decision_consequences": [
                "current_circumstances_dominate_priorities",
                "ineffective_goal_persistence",
                "delayed_choice_between_competing_directions",
            ],
            "candidate_mechanisms": [
                "CommitmentTrap",
                "LearningFailure",
                "DecisionDegradation",
            ],
        },
        "5": {
            "resource_state": "Будущее перестаёт выполнять роль устойчивого организующего центра поведения.",
            "vulnerable_functions": [
                "goal_clarity",
                "goal_directed_behavior",
                "goal_maintenance",
                "prioritization",
                "goal_adjustment_capacity",
                "self_concordance",
                "adaptive_disengagement_reengagement",
            ],
            "preserved_functions": [
                "separate_desires",
                "short_term_motives",
                "some_cognitive_functions",
            ],
            "behavioral_consequences": [
                "fragmented_behavior",
                "chronic_incompletion",
                "constant_direction_switching",
                "avoidance_of_choice",
                "loss_of_direction",
            ],
            "decision_consequences": [
                "reactive_decisions",
                "short_term_inconsistent_choices",
                "loss_of_strategic_direction",
                "prolonged_ineffective_action",
            ],
            "candidate_mechanisms": [
                "CommitmentTrap",
                "LearningFailure",
                "OptionSpaceCollapse",
                "DecisionDegradation",
            ],
        },
    },

    "psychological": {
        "0-1": {
            "resource_state": "Психологическая саморегуляция сохранна.",
            "vulnerable_functions": [],
            "preserved_functions": [
                "learning",
                "behavior_correction",
                "feedback_use",
                "basic_cognitive_functions",
            ],
            "candidate_mechanisms": [],
        },
        "2": {
            "resource_state": "Лёгкое снижение устойчивости под стрессом.",
            "vulnerable_functions": [
                "emotion_regulation",
            ],
            "preserved_functions": [
                "working_memory",
                "reasoning",
                "basic_analysis",
            ],
            "behavioral_consequences": [
                "higher_reactivity_to_stressors",
            ],
            "decision_consequences": [
                "emotion_influenced_decisions",
                "relief_seeking_choices",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
            ],
        },
        "3": {
            "resource_state": "Умеренное снижение способности выдерживать психологический дискомфорт.",
            "vulnerable_functions": [
                "emotion_regulation",
                "distress_tolerance",
            ],
            "preserved_functions": [
                "basic_intellectual_abilities",
            ],
            "behavioral_consequences": [
                "avoidance_growth",
                "difficulty_tolerating_uncertainty",
                "difficulty_tolerating_waiting",
                "difficulty_tolerating_frustration",
            ],
            "decision_consequences": [
                "ending_discomfort_over_effective_solution",
                "avoidant_decisions",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
                "OptionSpaceCollapse",
            ],
        },
        "4": {
            "resource_state": "Выраженное снижение психологической гибкости.",
            "vulnerable_functions": [
                "psychological_flexibility",
                "intolerance_of_uncertainty",
            ],
            "preserved_functions": [
                "knowledge",
                "memory",
                "intelligence",
            ],
            "behavioral_consequences": [
                "difficulty_adapting_behavior",
                "need_to_reduce_uncertainty_fast",
            ],
            "decision_consequences": [
                "premature_fixation",
                "ineffective_strategy_continuation",
                "certainty_seeking_at_any_cost",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
                "LearningFailure",
                "CommitmentTrap",
            ],
        },
        "5": {
            "resource_state": "Критическое снижение психологической саморегуляции.",
            "vulnerable_functions": [
                "self_regulation",
                "behavioral_control",
                "feedback_utilization",
                "goal_directed_behavior",
            ],
            "preserved_functions": [
                "separate_cognitive_functions",
            ],
            "behavioral_consequences": [
                "reduced_feedback_use",
                "reduced_error_correction",
                "difficulty_sustaining_long_term_goals",
            ],
            "decision_consequences": [
                "reactive_decisions",
                "repetition_of_ineffective_actions",
                "problem_scenario_maintenance",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
                "LearningFailure",
                "CommitmentTrap",
                "NegativeSpiral",
            ],
        },
    },

    "social": {
        "0-1": {
            "resource_state": "Автономность оценки сохранна.",
            "vulnerable_functions": [],
            "preserved_functions": [
                "autonomous_regulation",
                "perceived_agency",
                "self_efficacy",
                "independent_judgment",
                "self_concordance",
            ],
            "candidate_mechanisms": [],
        },
        "2": {
            "resource_state": "Появляется лёгкое снижение автономности оценки.",
            "vulnerable_functions": [
                "autonomous_regulation",
                "perceived_agency",
            ],
            "preserved_functions": [
                "own_wishes_awareness",
                "distinguishing_own_and_others_opinion",
            ],
            "behavioral_consequences": [
                "increased_social_checking",
            ],
            "decision_consequences": [
                "socially_safer_choice_bias",
                "approval_or_conflict_avoidance_bias",
            ],
            "candidate_mechanisms": [
                "OptionSpaceCollapse",
            ],
        },
        "3": {
            "resource_state": "Социальное давление или ожидания начинают заметно влиять на поведение.",
            "vulnerable_functions": [
                "self_efficacy",
                "perceived_competence",
                "independent_judgment",
                "option_generation",
            ],
            "preserved_functions": [
                "basic_reasoning",
                "situation_understanding",
            ],
            "behavioral_consequences": [
                "options_rejected_due_to_social_reaction",
                "difficulty_defending_position",
            ],
            "decision_consequences": [
                "reduced_effective_option_space",
            ],
            "candidate_mechanisms": [
                "OptionSpaceCollapse",
                "DecisionDegradation",
            ],
        },
        "4": {
            "resource_state": "Собственная оценка ситуации становится менее устойчивой под влиянием внешнего мнения.",
            "vulnerable_functions": [
                "independent_risk_evaluation",
                "autonomy_of_judgment",
                "resistance_to_conformity_pressure",
            ],
            "preserved_functions": [
                "knowledge",
                "experience",
                "logical_reasoning",
            ],
            "behavioral_consequences": [
                "risk_underestimation_when_others_dismiss_risk",
                "risk_overestimation_when_group_is_anxious",
                "external_opinion_becomes_primary",
            ],
            "decision_consequences": [
                "social_calibration_of_decisions",
                "weaker_independent_risk_check",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
                "OptionSpaceCollapse",
            ],
        },
        "5": {
            "resource_state": "Автономная система выбора выраженно ослаблена.",
            "vulnerable_functions": [
                "perceived_agency",
                "autonomous_regulation",
                "self_concordance",
                "independent_judgment",
                "perceived_option_availability",
            ],
            "preserved_functions": [
                "facts_understanding",
                "memory",
                "reasoning",
            ],
            "behavioral_consequences": [
                "external_expectation_dependence",
                "fear_of_conflict",
                "difficulty_searching_alternatives",
                "difficulty_defending_priorities",
            ],
            "decision_consequences": [
                "objective_options_feel_unavailable",
                "external_agreement_over_own_goals",
            ],
            "candidate_mechanisms": [
                "OptionSpaceCollapse",
                "DecisionDegradation",
                "CommitmentTrap",
            ],
        },
    },

    "cognitive": {
        "0-1": {
            "resource_state": "Когнитивная обработка выглядит сохранной.",
            "vulnerable_functions": [],
            "preserved_functions": [
                "executive_functions",
                "cognitive_flexibility",
                "working_memory_updating",
                "inhibitory_control",
                "metacognitive_monitoring",
                "reflective_reasoning",
            ],
            "candidate_mechanisms": [],
        },
        "2": {
            "resource_state": "Появляются лёгкие затруднения в выделении главного и удержании нескольких версий ситуации.",
            "vulnerable_functions": [
                "salience_selection",
                "sustained_attention",
                "hypothesis_generation",
                "early_cognitive_control",
            ],
            "preserved_functions": [
                "basic_understanding",
                "reasoning",
            ],
            "behavioral_consequences": [
                "emotionally_salient_details_capture_attention",
                "important_signals_noticed_later",
            ],
            "decision_consequences": [
                "decision_based_on_incomplete_initial_model",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
            ],
        },
        "3": {
            "resource_state": "Сложная обработка информации требует заметно больше усилий.",
            "vulnerable_functions": [
                "working_memory",
                "evidence_integration",
                "belief_updating",
                "executive_attention",
                "cognitive_flexibility",
            ],
            "preserved_functions": [
                "intelligence",
                "knowledge",
                "experience",
            ],
            "behavioral_consequences": [
                "need_to_simplify_situation",
                "difficulty_holding_multiple_conditions",
            ],
            "decision_consequences": [
                "reduced_alternatives",
                "reduced_checks",
                "reduced_conflicting_data_integration",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
                "OptionSpaceCollapse",
            ],
        },
        "4": {
            "resource_state": "Выраженно снижается гибкость обработки и контроль вывода.",
            "vulnerable_functions": [
                "cognitive_flexibility",
                "inhibitory_control",
                "metacognitive_monitoring",
                "reflective_reasoning",
                "strategy_switching",
            ],
            "preserved_functions": [
                "knowledge",
                "logical_explanation_capacity",
            ],
            "behavioral_consequences": [
                "premature_fixation",
                "resistance_to_new_information",
                "old_plan_continuation",
                "reduced_self_checking",
            ],
            "decision_consequences": [
                "early_closure",
                "contradiction_ignoring",
                "continuing_ineffective_strategy",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
                "LearningFailure",
                "CommitmentTrap",
            ],
        },
        "5": {
            "resource_state": "Когнитивный ресурс становится серьёзным ограничителем траектории.",
            "vulnerable_functions": [
                "executive_control",
                "belief_updating",
                "error_monitoring",
                "metacognitive_regulation",
                "flexible_problem_solving",
                "feedback_use",
            ],
            "preserved_functions": [
                "separate_knowledge",
                "memory",
                "intelligence",
                "experience",
            ],
            "behavioral_consequences": [
                "reduced_error_detection",
                "reduced_feedback_use",
                "difficulty_returning_to_alternative_explanations",
                "prolonged_ineffective_strategy",
            ],
            "decision_consequences": [
                "trajectory_worsening_decisions",
                "reduced_correction_of_decision_errors",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
                "LearningFailure",
                "DualFailure",
            ],
        },
    },

    "physical": {
        "0-1": {
            "resource_state": "Физический ресурс не выглядит ограничивающим фактором.",
            "vulnerable_functions": [],
            "preserved_functions": [
                "attention",
                "working_memory",
                "processing_speed",
                "executive_functions",
                "self_control",
            ],
            "candidate_mechanisms": [],
        },
        "2": {
            "resource_state": "Появляется лёгкий дефицит сна, восстановления или общей энергии.",
            "vulnerable_functions": [
                "vigilance",
                "sustained_attention",
                "alertness",
                "reaction_time",
                "lapses_of_attention",
            ],
            "preserved_functions": [
                "basic_thinking",
                "knowledge",
                "logic",
                "decision_capacity",
            ],
            "behavioral_consequences": [
                "missed_details",
                "missed_environmental_changes",
                "attention_lapses",
            ],
            "decision_consequences": [
                "decision_based_on_incomplete_input",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
            ],
        },
        "3": {
            "resource_state": "Физического ресурса недостаточно для устойчивой сложной обработки информации в течение длительного времени.",
            "vulnerable_functions": [
                "working_memory",
                "processing_speed",
                "executive_attention",
                "cognitive_efficiency",
            ],
            "preserved_functions": [
                "general_reasoning",
            ],
            "behavioral_consequences": [
                "difficulty_holding_multiple_conditions",
                "increased_cost_of_habitual_actions",
            ],
            "decision_consequences": [
                "simplified_situation_model",
                "reduced_number_of_factors_considered",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
                "ResourceExhaustion",
            ],
        },
        "4": {
            "resource_state": "Поддержание контроля и сложной регуляции требует значительных усилий.",
            "vulnerable_functions": [
                "executive_functions",
                "inhibitory_control",
                "cognitive_control",
                "adaptive_problem_solving",
                "risk_evaluation",
                "judgment",
            ],
            "preserved_functions": [
                "basic_knowledge",
                "experience",
            ],
            "behavioral_consequences": [
                "difficulty_inhibiting_automatic_reactions",
                "difficulty_changing_course_after_new_information",
                "difficulty_holding_long_term_goals_under_load",
            ],
            "decision_consequences": [
                "preference_for_familiar_or_simple_option",
                "reduced_complex_analysis",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
                "ResourceExhaustion",
                "DualFailure",
            ],
        },
        "5": {
            "resource_state": "Физическое истощение становится серьёзным ограничителем функционирования.",
            "vulnerable_functions": [
                "error_monitoring",
                "feedback_processing",
                "self_control",
                "complex_decision_making",
            ],
            "preserved_functions": [
                "separate_skills",
                "knowledge",
            ],
            "behavioral_consequences": [
                "reduced_error_detection",
                "reduced_correction_after_failure",
                "reduced_use_of_new_information",
            ],
            "decision_consequences": [
                "cascade_errors",
                "reduced_course_correction",
            ],
            "candidate_mechanisms": [
                "DecisionDegradation",
                "ResourceExhaustion",
                "LearningFailure",
                "DualFailure",
            ],
        },
    },

    "pep": {
        "0-1": {
            "resource_state": "Неопределённость не воспринимается автоматически как угроза.",
            "vulnerable_functions": [],
            "preserved_functions": [
                "risk_detection",
                "adaptive_uncertainty_processing",
            ],
            "candidate_mechanisms": [],
        },
        "2": {
            "resource_state": "Появляется умеренная настороженность по отношению к неожиданным событиям.",
            "vulnerable_functions": [
                "threat_appraisal",
                "uncertainty_evaluation",
            ],
            "preserved_functions": [
                "positive_and_negative_scenario_consideration",
            ],
            "behavioral_consequences": [
                "increased_risk_accounting",
            ],
            "decision_consequences": [
                "cautious_decisions_in_unfamiliar_situations",
            ],
            "candidate_mechanisms": [
                "OptionSpaceCollapse",
            ],
        },
        "3": {
            "resource_state": "Неожиданные события чаще воспринимаются как источник потенциальных проблем.",
            "vulnerable_functions": [
                "future_expectancy",
                "uncertainty_tolerance",
                "anticipatory_appraisal",
            ],
            "preserved_functions": [
                "adaptation_capacity",
            ],
            "behavioral_consequences": [
                "negative_consequences_expected_early",
            ],
            "decision_consequences": [
                "preference_for_predictable_options",
            ],
            "candidate_mechanisms": [
                "OptionSpaceCollapse",
                "DecisionDegradation",
            ],
        },
        "4": {
            "resource_state": "Формируется устойчивая склонность ожидать ухудшения после неожиданных событий.",
            "vulnerable_functions": [
                "expectancy_bias",
                "uncertainty_processing",
                "threat_anticipation",
            ],
            "preserved_functions": [
                "logical_thinking",
                "knowledge",
            ],
            "behavioral_consequences": [
                "risk_overweighting",
                "opportunities_underweighting",
            ],
            "decision_consequences": [
                "useful_action_avoidance_due_to_expected_negative_outcome",
                "subjective_option_narrowing",
            ],
            "candidate_mechanisms": [
                "OptionSpaceCollapse",
                "DecisionDegradation",
            ],
        },
        "5": {
            "resource_state": "Неожиданности воспринимаются как вероятный источник каскада новых проблем.",
            "vulnerable_functions": [
                "future_expectancy",
                "perceived_controllability",
                "adaptive_uncertainty_processing",
            ],
            "preserved_functions": [
                "separate_successful_adaptations",
            ],
            "behavioral_consequences": [
                "threat_prevention_orientation",
                "difficulty_integrating_successful_adaptation",
            ],
            "decision_consequences": [
                "negative_scenario_overestimation",
                "refusal_of_potentially_useful_options",
                "option_space_collapse_amplification",
            ],
            "candidate_mechanisms": [
                "OptionSpaceCollapse",
                "NegativeSpiral",
                "DecisionDegradation",
            ],
        },
    },

    "recovery": {
        "0-1": {
            "resource_state": "Восстановление после нагрузки происходит относительно быстро.",
            "vulnerable_functions": [],
            "preserved_functions": [
                "return_to_baseline_functioning",
                "adaptive_recovery",
            ],
            "candidate_mechanisms": [],
        },
        "2": {
            "resource_state": "Восстановление сохранно, но начинает требовать больше времени.",
            "vulnerable_functions": [
                "recovery_efficiency",
            ],
            "preserved_functions": [
                "most_cognitive_and_emotional_functions",
            ],
            "behavioral_consequences": [
                "residual_fatigue_after_intense_periods",
            ],
            "decision_consequences": [
                "temporary_lower_analysis_quality_before_recovery",
            ],
            "candidate_mechanisms": [
                "RecoveryMismatch",
            ],
        },
        "3": {
            "resource_state": "Скорость восстановления заметно снижается.",
            "vulnerable_functions": [
                "resilience",
                "restoration_capacity",
                "cumulative_recovery_processes",
            ],
            "preserved_functions": [
                "recovery_possible_but_costly",
            ],
            "behavioral_consequences": [
                "fatigue_accumulation",
                "longer_aftereffects_of_load",
            ],
            "decision_consequences": [
                "decisions_during_incomplete_recovery",
                "simplified_strategies",
                "premature_completion_of_complex_tasks",
            ],
            "candidate_mechanisms": [
                "RecoveryMismatch",
                "ResourceExhaustion",
                "DecisionDegradation",
            ],
        },
        "4": {
            "resource_state": "Даже после отдыха часть последствий нагрузки сохраняется.",
            "vulnerable_functions": [
                "adaptive_recovery",
                "stress_recovery_systems",
                "resilience_mechanisms",
            ],
            "preserved_functions": [
                "temporary_partial_recovery",
            ],
            "behavioral_consequences": [
                "chronic_fatigue_risk",
                "symptom_accumulation",
                "long_recovery_after_loads",
            ],
            "decision_consequences": [
                "decisions_under_hidden_exhaustion",
            ],
            "candidate_mechanisms": [
                "RecoveryMismatch",
                "ResourceExhaustion",
                "DualFailure",
            ],
        },
        "5": {
            "resource_state": "Снижение нагрузки перестаёт приводить к ожидаемому улучшению состояния.",
            "vulnerable_functions": [
                "restoration_capacity",
                "recovery_regulation",
                "resilience_systems",
                "long_term_adaptation_to_load",
            ],
            "preserved_functions": [
                "separate_periods_of_improvement",
            ],
            "behavioral_consequences": [
                "load_accumulates_faster_than_recovery",
                "stable_exhaustion_risk",
            ],
            "decision_consequences": [
                "systematic_errors_from_accumulated_recovery_deficit",
            ],
            "candidate_mechanisms": [
                "RecoveryMismatch",
                "ResourceExhaustion",
                "NegativeSpiral",
                "DualFailure",
            ],
        },
    },
}


def get_level_profile(domain, score):
    level = score_to_level(score)

    if level == NOT_ENOUGH_DATA:
        return {
            "domain": domain,
            "level": NOT_ENOUGH_DATA,
            "status": NOT_ENOUGH_DATA,
            "score": None,
            "resource_state": None,
            "vulnerable_functions": [],
            "preserved_functions": [],
            "behavioral_consequences": [],
            "decision_consequences": [],
            "candidate_mechanisms": [],
            "reason": f"{domain}_score_missing",
        }

    profile = LEVEL_MAPS.get(domain, {}).get(level)

    if profile is None:
        return {
            "domain": domain,
            "level": level,
            "status": NOT_ENOUGH_DATA,
            "score": score,
            "resource_state": None,
            "vulnerable_functions": [],
            "preserved_functions": [],
            "behavioral_consequences": [],
            "decision_consequences": [],
            "candidate_mechanisms": [],
            "reason": f"{domain}_level_profile_missing",
        }

    result = dict(profile)
    result["domain"] = domain
    result["level"] = level
    result["score"] = score
    result["status"] = "AVAILABLE"
    result.setdefault("behavioral_consequences", [])
    result.setdefault("decision_consequences", [])
    result.setdefault("candidate_mechanisms", [])
    result.setdefault("vulnerable_functions", [])
    result.setdefault("preserved_functions", [])
    return result


def build_level_profiles(domain_scores):
    return {
        domain: get_level_profile(domain, score)
        for domain, score in domain_scores.items()
    }