def get_renderer(item: dict) -> str:
    item_type = item.get("item_type", "question")

    mapping = {
        "question": "question_renderer",
        "game": "game_renderer",
        "sensor": "sensor_renderer",
        "image": "image_renderer",
        "video": "video_renderer",
        "instruction": "instruction_renderer",
        "timer": "timer_renderer",
        "pause": "pause_renderer",
        "vr": "vr_renderer",
    }

    return mapping.get(item_type, "question_renderer")