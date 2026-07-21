class SummaryEngine:

    def run(self, forecast: dict, summarizer) -> dict:
        return summarizer.build(forecast)