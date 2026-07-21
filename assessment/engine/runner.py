from assessment.engine.renderer import get_renderer


class AssessmentRunner:

    def prepare_item(self, item: dict) -> dict:
        return {
            "item": item,
            "renderer": get_renderer(item),
        }