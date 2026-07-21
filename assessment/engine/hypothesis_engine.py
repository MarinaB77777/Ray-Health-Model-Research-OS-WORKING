class HypothesisEngine:

    def run(self, scores: dict, hypothesis_builder):
        return hypothesis_builder.build(scores)