QUESTIONNAIRE_FLOW_SCHEMA_VERSION = "questionnaire-flow-1"


def _flow_node(
    question_code: str,
    next_code: str | None = None,
    condition: dict | None = None,
) -> dict:
    return {
        "question_code": question_code,
        "next_code": next_code,
        "condition": condition,
    }


def build_linear_flow(
    question_codes: list[str],
) -> dict:
    nodes = []

    for index, question_code in enumerate(question_codes):
        next_code = (
            question_codes[index + 1]
            if index + 1 < len(question_codes)
            else None
        )

        nodes.append(
            _flow_node(
                question_code=question_code,
                next_code=next_code,
            )
        )

    return {
        "schema_version": QUESTIONNAIRE_FLOW_SCHEMA_VERSION,
        "flow_type": "linear",
        "nodes": nodes,
    }


def build_execution_path(
    flow: dict,
    answers: dict,
) -> dict:
    nodes = flow.get("nodes", [])
    visited_question_codes = []

    for node in nodes:
        question_code = node.get("question_code")
        if question_code is None:
            continue

        visited_question_codes.append(question_code)

    return {
        "schema_version": QUESTIONNAIRE_FLOW_SCHEMA_VERSION,
        "flow_type": flow.get("flow_type"),
        "visited_question_codes": visited_question_codes,
        "sequence_signature": ">".join(visited_question_codes),
        "answers_follow_flow": all(
            question_code in answers
            for question_code in visited_question_codes
        ),
    }