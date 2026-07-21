from assessment.engine.pipeline import AssessmentPipeline
from assessment.studies.decision_under_uncertainty.scoring import DUScoring
from assessment.studies.decision_under_uncertainty.analysis import DUAnalysis
from assessment.studies.decision_under_uncertainty.forecast import DUForecast
from assessment.studies.decision_under_uncertainty.summary import DUSummary


class DecisionUnderUncertaintyService:

    def __init__(self):
        self.pipeline = AssessmentPipeline()

    def process_completed_block(self, answers: dict) -> dict:
        return self.pipeline.run(
            answers=answers,
            scorer=DUScoring(),
            analyzer=DUAnalysis(),
            forecaster=DUForecast(),
            summarizer=DUSummary(),
        )