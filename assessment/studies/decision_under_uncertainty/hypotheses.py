class DUHypotheses:

    def build(self, scores: dict):

        hypotheses = []

        lifestyle = scores.get("lifestyle_uncertainty", 0)
        experience = scores.get("observed_experience", 0)
        confirmation = scores.get("external_confirmation", 0)

        if lifestyle >= 4:
            hypotheses.append({
                "id": "adaptation_to_uncertainty",
                "confidence": 0.60,
                "status": "candidate",
            })

        if confirmation >= 3:
            hypotheses.append({
                "id": "external_confirmation_dependence",
                "confidence": 0.45,
                "status": "candidate",
            })

        if experience <= 1:
            hypotheses.append({
                "id": "limited_personal_experience",
                "confidence": 0.40,
                "status": "candidate",
            })

        return {
            "hypotheses": hypotheses
        }