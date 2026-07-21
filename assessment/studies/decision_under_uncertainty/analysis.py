class DUAnalysis:

    def analyze(self, hypotheses_result: dict) -> dict:
        hypotheses = hypotheses_result.get("hypotheses", [])

        primary = None

        if hypotheses:
            primary = max(
                hypotheses,
                key=lambda item: item.get("confidence", 0)
            )

        return {
            "analysis_type": "hypothesis_based_initial_analysis",
            "hypotheses": hypotheses,
            "primary_hypothesis": primary,
            "needs_more_data": True,
        }