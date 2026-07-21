class DUScoring:

    def calculate(self, answers: dict) -> dict:
        return {
            "lifestyle_uncertainty": answers.get("DU1"),
            "observed_experience": answers.get("DU2"),
            "external_confirmation": answers.get("DU3"),
            "experience_context": answers.get("DU4"),
        }