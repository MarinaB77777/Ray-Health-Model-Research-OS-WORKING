from .schemas import (
    ProposedAction,
    GovernanceContext,
    GovernanceVerdict,
)

from .rules import governance_check


class GovernanceService:

    """
    Thin service wrapper.

    GovernanceService:
    - receives proposed action + context
    - calls governance rules
    - returns one GovernanceVerdict

    It does NOT:
    - execute actions
    - modify Runtime state
    - contact humans
    - perform reasoning
    - write memory directly
    """

    def check(
        self,
        action: ProposedAction,
        context: GovernanceContext,
    ) -> GovernanceVerdict:

        return governance_check(
            action=action,
            context=context,
        )