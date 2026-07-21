from assessment.analysis.statistics.grouping import (
    subject_id_from_record,
)


def collect_contingency_table(
    *,
    answer_records: list[dict],
    left_question_code: str,
    right_question_code: str,
) -> dict:
    by_subject = {}

    for record in answer_records:
        subject_id = subject_id_from_record(record)
        question_code = record.get("question_code")

        if not subject_id:
            continue

        if question_code not in {left_question_code, right_question_code}:
            continue

        by_subject.setdefault(subject_id, {})[question_code] = record.get("answer_value")

    paired_values = []
    left_values = []
    right_values = []

    for answers in by_subject.values():
        left_value = answers.get(left_question_code)
        right_value = answers.get(right_question_code)

        if (
            left_value is None
            or left_value == ""
            or right_value is None
            or right_value == ""
        ):
            continue

        left_key = str(left_value)
        right_key = str(right_value)

        paired_values.append((left_key, right_key))
        left_values.append(left_key)
        right_values.append(right_key)

    row_categories = sorted(set(left_values))
    column_categories = sorted(set(right_values))

    table = [
        [0 for _ in column_categories]
        for _ in row_categories
    ]

    row_index = {
        category: index
        for index, category in enumerate(row_categories)
    }

    column_index = {
        category: index
        for index, category in enumerate(column_categories)
    }

    for left_key, right_key in paired_values:
        table[row_index[left_key]][column_index[right_key]] += 1

    return {
        "row_categories": row_categories,
        "column_categories": column_categories,
        "table": table,
        "sample_size": len(paired_values),
        "row_count": len(row_categories),
        "column_count": len(column_categories),
    }


def is_two_by_two_table(contingency: dict) -> bool:
    return (
        contingency.get("row_count") == 2
        and contingency.get("column_count") == 2
    )