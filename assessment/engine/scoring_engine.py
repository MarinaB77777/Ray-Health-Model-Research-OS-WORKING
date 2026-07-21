class ScoringEngine:

    def run(self, answers: dict, scorer) -> dict:
        return scorer.calculate(answers)