class DUSummary:

    def build(self, forecast: dict) -> dict:
        return {
            "title": "Предварительный результат",
            "message": forecast.get("message"),
            "confidence": "Предварительная оценка по первому блоку. Для более точного вывода нужен следующий блок исследования.",
        }