from pilot_account.service import PilotAccountService
from pilot_session.agreement import build_session_agreement_record
from pilot_session.service import PilotSessionService


class PilotSessionStartFlow:
    def __init__(
        self,
        account_service: PilotAccountService,
        session_service: PilotSessionService,
    ):
        self.account_service = account_service
        self.session_service = session_service

    def start_session_after_agreement(
        self,
        account_id: str,
        consent_record: dict,
        study_id: str | None = None,
        participant_role: str = "participant",
    ) -> dict | None:
        account = self.account_service.get_account(account_id)

        if account is None:
            return None

        agreement = build_session_agreement_record(
            participant_id=account.participant_id,
            consent_record=consent_record,
        )

        session = self.session_service.create_session_from_agreement(
            agreement_record=agreement,
            subject_link_id=account.subject_link_id,
            study_id=study_id,
            participant_role=participant_role,
        )
        result = {
            "account": account,
            "agreement": agreement,
            "session": session,
        }


        return result