from assessment.analysis.runners.spearman import run_spearman_correlation
from assessment.analysis.runners.pearson import run_pearson_correlation
from assessment.analysis.runners.mann_whitney import run_mann_whitney_u
from assessment.analysis.runners.kruskal_wallis import (
    run_kruskal_wallis,
)
from assessment.analysis.runners.fisher_exact import run_fisher_exact
from assessment.analysis.runners.chi_square import run_chi_square

RUNNER_MAP = {
    "spearman_correlation": run_spearman_correlation,
    "pearson_correlation": run_pearson_correlation,
    "mann_whitney_u": run_mann_whitney_u,
    "kruskal_wallis": run_kruskal_wallis,
    "fisher_exact": run_fisher_exact,
    "chi_square": run_chi_square,
}


def run_statistical_method(
    *,
    study_id: str,
    left_question_code: str,
    right_question_code: str,
    method_id: str,
    answer_records: list[dict],
) -> dict:
    runner = RUNNER_MAP.get(method_id)

    if runner is None:
        return {
            "ok": False,
            "status": "runner_not_available",
            "method_id": method_id,
        }

    return runner(
        study_id=study_id,
        left_question_code=left_question_code,
        right_question_code=right_question_code,
        answer_records=answer_records,
    )