from assessment.engine.pipeline import AssessmentPipeline


class DecisionUnderUncertaintyService:

    def __init__(self):
        self.pipeline = AssessmentPipeline()

    def process_completed_block(self, answers: dict) -> dict:
        return self.pipeline.run(
            study_id="decision_under_uncertainty",
            answers=answers,
        )