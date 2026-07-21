from assessment.studies.decision_under_uncertainty.service import (
    DecisionUnderUncertaintyService,
)


def has_analysis_for_study(study_id: str | None) -> bool:
    return study_id in {
        "decision_under_uncertainty",
    }


def run_registered_analysis(
    *,
    study_id: str | None,
    answers: dict,
) -> dict | None:
    if study_id == "decision_under_uncertainty":
        service = DecisionUnderUncertaintyService()
        return {
            "result_type": "decision_under_uncertainty_analysis",
            "study_id": study_id,
            "answers_count": len(answers or {}),
            "analysis": service.process_completed_block(answers or {}),
            "next_questions": [],
            "uncertainty": {
                "status": "computed",
                "reason": None,
            },
        }

    return None