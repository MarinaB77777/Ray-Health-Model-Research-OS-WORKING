from assessment.studies.decision_under_uncertainty.metadata import STUDY_METADATA

from assessment.studies.decision_under_uncertainty.scoring import DUScoring
from assessment.studies.decision_under_uncertainty.analysis import DUAnalysis
from assessment.studies.decision_under_uncertainty.forecast import DUForecast
from assessment.studies.decision_under_uncertainty.summary import DUSummary
from assessment.studies.decision_under_uncertainty.hypotheses import DUHypotheses


STUDY_REGISTRY = {
    "decision_under_uncertainty": {
        "metadata": STUDY_METADATA,
        "scoring": DUScoring,
        "analysis": DUAnalysis,
        "forecast": DUForecast,
        "summary": DUSummary,
        "active": True,
        "hypotheses": DUHypotheses,
    },
}


def get_study_definition(study_id: str):
    study = STUDY_REGISTRY.get(study_id)

    if not study or not study.get("active"):
        return None

    return study