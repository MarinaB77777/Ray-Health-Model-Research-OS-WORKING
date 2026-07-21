class DUForecast:

    def build(self, analysis: dict) -> dict:
        primary = analysis.get("primary_hypothesis")

        if not primary:
            return {
                "forecast_type": "hypothesis_based_du_forecast",
                "level": "not_enough_data",
                "message": "По первому блоку пока недостаточно данных для устойчивого предположения.",
                "confidence": "low_initial",
                "needs_more_data": True,
            }

        hypothesis_id = primary.get("id")
        confidence_value = primary.get("confidence", 0)

        if hypothesis_id == "adaptation_to_uncertainty":
            message = (
                "По первому блоку можно предположить, что в изменяющихся условиях "
                "способность ориентироваться и принимать решения в целом сохранена. "
                "Это пока гипотеза, а не окончательный вывод."
            )
        elif hypothesis_id == "external_confirmation_dependence":
            message = (
                "По первому блоку есть предварительный сигнал, что внешнее подтверждение "
                "может играть заметную роль в оценке успешности решений. "
                "Эту гипотезу нужно проверить следующими блоками."
            )
        elif hypothesis_id == "limited_personal_experience":
            message = (
                "По первому блоку может быть недостаточно признаков устойчивого личного опыта "
                "действий в неопределённых ситуациях. Требуется уточнение в следующих блоках."
            )
        else:
            message = "По первому блоку сформирована предварительная гипотеза, требующая уточнения."

        return {
            "forecast_type": "hypothesis_based_du_forecast",
            "primary_hypothesis": hypothesis_id,
            "confidence_value": confidence_value,
            "message": message,
            "confidence": "low_initial",
            "needs_more_data": analysis.get("needs_more_data", True),
        }