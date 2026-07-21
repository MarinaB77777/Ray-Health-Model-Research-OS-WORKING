class ForecastEngine:

    def run(self, analysis: dict, forecaster) -> dict:
        return forecaster.build(analysis)