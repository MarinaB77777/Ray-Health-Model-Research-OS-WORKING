from model_engine.intro_dialogue_ru import (
    build_intro_dialogue_reply,
)


def test_intro_transition_only_on_first_turn():
    status = {
        "complete": False,
        "next_block": "expectations_from_ray",
    }

    first_reply = build_intro_dialogue_reply(
        status=status,
        turn_index=0,
    )

    later_reply = build_intro_dialogue_reply(
        status=status,
        turn_index=1,
    )

    assert "Хотел бы тебе помочь" in first_reply["message"]
    assert "Хотел бы тебе помочь" not in later_reply["message"]
    assert later_reply["status"] == "question"