class AnalysisEngine:

    def run(self, scores: dict, analyzer) -> dict:
        return analyzer.analyze(scores)