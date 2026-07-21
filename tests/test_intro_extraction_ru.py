from model_engine.interview_extraction_ru import (
    extract_intro_blocks_from_text,
    merge_intro_knowledge,
)


def test_extracts_main_activity_and_person_context_from_one_message():
    result = extract_intro_blocks_from_text(
        "Я работаю преподавателем биологии."
    )

    assert "main_activity" in result
    assert "person_context" in result
    assert result["main_activity"]["confidence"] == 0.7
    assert result["person_context"]["confidence"] == 0.7


def test_extracts_life_phase_and_current_concerns_from_problem_message():
    result = extract_intro_blocks_from_text(
        "Сейчас у меня сложный период, много проблем и непонятно что дальше."
    )

    assert result["life_phase"]["value"] == "problem_or_difficult_phase"
    assert "current_concerns" in result


def test_extracts_positive_life_phase():
    result = extract_intro_blocks_from_text(
        "Сейчас всё довольно спокойно и стабильно."
    )

    assert result["life_phase"]["value"] == "positive_or_stable_phase"
    assert "current_concerns" not in result


def test_merge_keeps_higher_confidence_value():
    current = {
        "main_activity": {
            "value": "вроде связан с наукой",
            "confidence": 0.5,
        }
    }

    extracted = {
        "main_activity": {
            "value": "Я работаю преподавателем биологии.",
            "confidence": 0.7,
        }
    }

    merged = merge_intro_knowledge(current, extracted)

    assert merged["main_activity"]["value"] == (
        "Я работаю преподавателем биологии."
    )
    assert merged["main_activity"]["confidence"] == 0.7