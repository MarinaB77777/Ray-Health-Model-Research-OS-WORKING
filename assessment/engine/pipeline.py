from assessment.engine.scoring_engine import ScoringEngine
from assessment.engine.hypothesis_engine import HypothesisEngine
from assessment.engine.analysis_engine import AnalysisEngine
from assessment.engine.forecast_engine import ForecastEngine
from assessment.engine.summary_engine import SummaryEngine
from assessment.study_registry import get_study_definition


class AssessmentPipeline:

    def __init__(self):
        self.scoring_engine = ScoringEngine()
        self.hypothesis_engine = HypothesisEngine()
        self.analysis_engine = AnalysisEngine()
        self.forecast_engine = ForecastEngine()
        self.summary_engine = SummaryEngine()

    def run(self, study_id: str, answers: dict) -> dict:
        study = get_study_definition(study_id)

        if study is None:
            raise ValueError(f"Unknown or inactive study: {study_id}")

        scorer = study["scoring"]()
        hypothesis_builder = study["hypotheses"]()
        analyzer = study["analysis"]()
        forecaster = study["forecast"]()
        summarizer = study["summary"]()

        scores = self.scoring_engine.run(answers, scorer)
        hypotheses = self.hypothesis_engine.run(scores, hypothesis_builder)
        analysis = self.analysis_engine.run(hypotheses, analyzer)
        forecast = self.forecast_engine.run(analysis, forecaster)
        summary = self.summary_engine.run(forecast, summarizer)

        return {
            "scores": scores,
            "hypotheses": hypotheses,
            "analysis": analysis,
            "forecast": forecast,
            "summary": summary,
        }