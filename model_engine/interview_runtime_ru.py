from model_engine.interview_extraction_ru import (
    extract_intro_blocks_from_text,
    merge_intro_knowledge,
)
from model_engine.interview_logic_ru import (
    get_intro_status,
)
from model_engine.intro_dialogue_ru import build_intro_dialogue_reply

def run_intro_turn(
    message: str,
    current_knowledge: dict = None,
) -> dict:
    if current_knowledge is None:
        current_knowledge = {}

    extracted_blocks = extract_intro_blocks_from_text(message)

    updated_knowledge = merge_intro_knowledge(
        current_knowledge=current_knowledge,
        extracted_blocks=extracted_blocks,
    )

    status = get_intro_status(updated_knowledge)
    ray_reply = build_intro_dialogue_reply(
        status=status,
        turn_index=len(current_knowledge),
    )
    return {
        "goal": "intro",
        "message": message,
        "extracted_blocks": extracted_blocks,
        "knowledge": updated_knowledge,
        "status": status,
        "ray": ray_reply,
    }


