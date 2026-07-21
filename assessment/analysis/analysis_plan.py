from assessment.analysis.analyzers.prepared_output import (
    add_prepared_output,
)
from assessment.analysis.analysis_plan import (
    build_analysis_plan,
)

def build_analysis_plan(
    assessment_id: str,
) -> list:
    return [
        add_prepared_output,
    ]