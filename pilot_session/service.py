from datetime import UTC, datetime
from uuid import uuid4
from assessment.analysis.analyzer import analyze_assessment
from assessment.analysis.analysis_registry import (
    run_registered_analysis,
)
from assessment.registry import get_assessment
from assessment.prepared_output import build_prepared_assessment_output
from assessment.question_banks.loader import load_question_bank
from question_banks import get_question_bank
from assessment.mappings.health_model_v61_mapping import (
    build_health_model_v61_domain_scores,
)

from model_engine.run_engine import run_engine_logic
from research.analyses.health_model.model_parameter_extractor import (
    build_health_model_parameter_records,
)
from research.analyses.health_model.v61_calculator import (
    calculate_health_model_v61,
)
from assessment.mappings.health_model_v61_calculator_input import (
    build_health_model_v61_calculator_input,
)
from assessment.mappings.health_model_v61_parameter_registry import (
    build_health_model_input_from_uuid_answers,
)
from assessment.mappings.health_model_v61_required_inputs import (
    build_health_model_v61_input_coverage,
)
from assessment.mappings.health_model_v61_parameter_registry import (
    build_health_model_input_from_uuid_answers,
    build_health_model_input_mapping_records,
)
from pilot_session.errors import (
    ExportBlockedError,
    InvalidStatusTransitionError,
    RunFailedError,
    SessionInvalidatedError,
    SessionNotFoundError,
)
from pilot_session.export import (
    generate_participant_export,
    generate_research_export,
)

from pilot_session.schemas import ParticipantSession, SessionStatus
from pilot_session.statuses import can_generate_export
from pilot_session.store import PilotSessionStore
from research.records_store import (
    save_research_record_from_export,
)


class PilotSessionService:
    def __init__(self, store: PilotSessionStore):
        self.store = store

    def _resolve_question_identity(
        self,
        question_code: str,
        language: str = "ru",
        study_id: str | None = None,
        domain_data_identity: dict | None = None,
    ) -> dict:
        bank_ids = []

        if domain_data_identity:
            data_source_path = domain_data_identity.get("data_source_path")
            if data_source_path:
                bank_ids.append(data_source_path)

        if study_id:
            bank_ids.append(study_id)

        bank_ids.append("health_model")

        seen = set()
        for bank_id in bank_ids:
            if not bank_id or bank_id in seen:
                continue

            seen.add(bank_id)

            question_bank = load_question_bank(
                bank_id=bank_id,
                lang=language,
            )

            question = question_bank.get(question_code)

            if question:
                return {
                    "question_id": question.get("question_id"),
                    "question_uuid": question.get("question_id"),
                    "question_bank_id": bank_id,
                    "question_bank_code": question.get("code", question_code),
                    "question_block": question.get("block"),
                    "question_family": question.get("family"),
                    "question_domain": question.get("domain"),
                    "question_version": question.get("version"),
                    "scale_type": question.get("scale_type"),
                    "score_direction": question.get("score_direction"),
                }

        return {
            "question_id": None,
            "question_uuid": None,
            "question_bank_id": None,
            "question_bank_code": question_code,
            "question_block": None,
            "question_family": None,
            "question_domain": None,
            "question_version": None,
            "scale_type": None,
            "score_direction": None,
        }

    def create_session(self, participant_id: str) -> ParticipantSession:
        session = ParticipantSession(
            session_id=str(uuid4()),
            participant_id=participant_id,
        )

        self.store.save(session)
        return session
    def create_session_from_agreement(
        self,
        agreement_record: dict,
        subject_link_id: str | None = None,
        study_id: str | None = None,
        participant_role: str | None = None,
        synchronization_reference: str | None = None,
    ) -> ParticipantSession:
        if agreement_record.get("collection_allowed") is not True:
            raise InvalidStatusTransitionError(
                "Session cannot be created without accepted agreement"
            )

        signed_at = agreement_record.get("signed_at")

        session = ParticipantSession(
            session_id=str(uuid4()),
            participant_id=agreement_record["participant_id"],
            subject_link_id=subject_link_id,
            study_id=study_id,
            participant_role=participant_role,
            synchronization_reference=synchronization_reference,
            agreement_id=agreement_record["agreement_id"],
            agreement_version=agreement_record["agreement_version"],
            agreement_signed_at=(
                datetime.fromisoformat(signed_at)
                if signed_at is not None
                else None
            ),
            collection_agreement_status=agreement_record["agreement_status"],
        )

        self.store.save(session)
        return session

    def submit_answers(
        self,
        session_id: str,
        answers: dict,
        domain_data_identity: dict | None = None,
    ) -> ParticipantSession:
        session = self.store.get(session_id)

        if session is None:
            raise SessionNotFoundError(
                "Session not found"
            )

        if session.status != SessionStatus.CREATED:
            raise InvalidStatusTransitionError(
                "Invalid session status transition"
            )

        if session.invalidated:
            raise SessionInvalidatedError(
                "Session is invalidated"
            )

        created_at = datetime.now(UTC).isoformat()
        submission_id = str(uuid4())
        next_revision = session.answer_revision_count + 1
        identity = dict(domain_data_identity or {})
        identity["session_id"] = session.session_id
        identity["participant_id"] = session.participant_id
        identity["subject_link_id"] = session.subject_link_id
        identity["study_id"] = session.study_id

        session.answers = answers

        if domain_data_identity is not None:
            session.domain_data_identity = domain_data_identity

        session.questionnaire_submissions.append({
            "submission_id": submission_id,
            "submission_type": "initial_answers",
            "created_at": created_at,
            "session_id": session.session_id,
            "participant_id": session.participant_id,
            "subject_link_id": session.subject_link_id,
            "study_id": session.study_id,
            "participant_role": session.participant_role,
            "synchronization_reference": session.synchronization_reference,
            "domain_data_identity": identity,
            "answers": answers,
            "answered_keys": list(answers.keys()),
            "answers_count": len(answers),
        })

        for question_code, answer_value in answers.items():
            question_identity = self._resolve_question_identity(
                question_code,
                study_id=session.study_id,
                domain_data_identity=identity,
            )
            session.research_answer_records.append({
                "answer_record_id": str(uuid4()),
                "submission_id": submission_id,
                "record_type": "questionnaire_answer",
                "created_at": created_at,
                "participant_id": session.participant_id,
                "subject_link_id": session.subject_link_id,
                "session_id": session.session_id,
                "study_id": session.study_id,
                "participant_role": session.participant_role,
                "synchronization_reference": session.synchronization_reference,
                "questionnaire_id": identity.get("questionnaire_id"),
                "questionnaire_version": identity.get("questionnaire_version"),
                "question_code": question_code,
                **question_identity,
                "answer_value": answer_value,
                "answer_value_type": type(answer_value).__name__,
                "answer_revision": next_revision,
                "source_mode": "questionnaire",
                "domain_data_identity": identity,
            })

        session.answer_revision_count += 1


        session.answer_merge_history.append({
            "type": "initial_answers",
            "answered_keys": list(answers.keys()),
            "answers_count_after_merge": len(session.answers),
            "created_at": datetime.now(UTC).isoformat(),
        })

        session.status = SessionStatus.ANSWERS_RECEIVED
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session

    def submit_followup_answers(
        self,
        session_id: str,
        answers: dict,
    ) -> ParticipantSession:
        session = self.store.get(session_id)

        if session is None:
            raise SessionNotFoundError(
                "Session not found"
            )

        if session.invalidated:
            raise SessionInvalidatedError(
                "Session is invalidated"
            )

        if session.status not in {
            SessionStatus.RUN_COMPLETED,
            SessionStatus.WAITING_FOR_INPUT,
            SessionStatus.PARTIAL_RESULT,
        }:
            raise InvalidStatusTransitionError(
                "Invalid session status transition"
            )

        previous_keys = set(session.answers.keys())

        session.answers.update(answers)

        new_keys = [
            key for key in answers.keys()
            if key not in previous_keys
        ]

        updated_keys = [
            key for key in answers.keys()
            if key in previous_keys
        ]
        
        created_at = datetime.now(UTC).isoformat()
        submission_id = str(uuid4())
        next_revision = session.answer_revision_count + 1
        identity = session.domain_data_identity or {}

        session.questionnaire_submissions.append({
            "submission_id": submission_id,
            "submission_type": "followup_answers",
            "created_at": created_at,
            "session_id": session.session_id,
            "participant_id": session.participant_id,
            "subject_link_id": session.subject_link_id,
            "study_id": session.study_id,
            "participant_role": session.participant_role,
            "synchronization_reference": session.synchronization_reference,
            "domain_data_identity": identity,
            "answers": answers,
            "answered_keys": list(answers.keys()),
            "answers_count": len(answers),
            "new_keys": new_keys,
            "updated_keys": updated_keys,
        })

        for question_code, answer_value in answers.items():
            question_identity = self._resolve_question_identity(
                question_code,
                study_id=session.study_id,
                domain_data_identity=identity,
            )
            session.research_answer_records.append({
                "answer_record_id": str(uuid4()),
                "submission_id": submission_id,
                "record_type": "questionnaire_answer",
                "created_at": created_at,
                "participant_id": session.participant_id,
                "subject_link_id": session.subject_link_id,
                "session_id": session.session_id,
                "study_id": session.study_id,
                "participant_role": session.participant_role,
                "synchronization_reference": session.synchronization_reference,
                "questionnaire_id": identity.get("questionnaire_id"),
                "questionnaire_version": identity.get("questionnaire_version"),
                "question_code": question_code,
                **question_identity,
                "answer_value": answer_value,
                "answer_value_type": type(answer_value).__name__,
                "answer_revision": next_revision,
                "source_mode": "ray_followup",
                "domain_data_identity": identity,
            })

        session.answer_revision_count += 1
        session.answer_merge_history.append({
            "type": "followup_answers",
            "answered_keys": list(answers.keys()),
            "new_keys": new_keys,
            "updated_keys": updated_keys,
            "answers_count_after_merge": len(session.answers),
            "created_at": datetime.now(UTC).isoformat(),
        })

        session.status = SessionStatus.ANSWERS_RECEIVED
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session

    def get_session(self, session_id: str) -> ParticipantSession:
        session = self.store.get(session_id)

        if session is None:
            raise SessionNotFoundError(
                "Session not found"
            )

        return session

    def run_session(self, session_id: str) -> ParticipantSession:
        session = self.store.get(session_id)

        if session is None:
            raise SessionNotFoundError(
                "Session not found"
            )

        if session.invalidated:
            raise SessionInvalidatedError(
                "Session is invalidated"
            )

        if session.status != SessionStatus.ANSWERS_RECEIVED:
            raise InvalidStatusTransitionError(
                "Invalid session status transition"
            )

        try:
            if session.study_id == "health_model":
                health_model_mapping = build_health_model_v61_domain_scores(
                    answers=session.answers or {},
                    question_bank=get_question_bank("ru"),
                )
                
                calculator_input = (
                    build_health_model_input_from_uuid_answers(
                        answers=session.answers or {},
                        question_bank=get_question_bank("ru"),
                    )
                )

                result = calculate_health_model_v61(
                    calculator_input
                )

                result["calculator_input"] = calculator_input

                result["question_parameter_mapping_records"] = (
                    build_health_model_input_mapping_records(
                        answers=session.answers or {},
                        question_bank=get_question_bank("ru"),
                    )
                )

                coverage = build_health_model_v61_input_coverage(
                    calculator_input
                )

                result["coverage"] = coverage
                result["missing_required_data"] = coverage["missing_required_data"]
                result["missing_critical_data"] = coverage["missing_critical_data"]

                if coverage["missing_critical_data"]:
                    result["forecast_allowed"] = False
                    result["readiness_status"] = "NOT_ENOUGH_DATA"
                
                result["research_calculated_parameter_records"] = (
                    build_health_model_parameter_records(
                        session_id=session.session_id,
                        participant_id=session.participant_id,
                        subject_link_id=session.subject_link_id,
                        study_id=session.study_id or "health_model",
                        analysis_output=result,
                        observation_time=session.updated_at,
                    )
                )
                
                result["questionnaire_mapping"] = health_model_mapping

            elif session.study_id in {"intro", "resource", "decision"}:
                assessment = get_assessment(
                    assessment_id=session.study_id,
                    question_bank=get_question_bank("ru"),
                )

                if assessment is None or assessment.get("ok") is False:
                    raise RunFailedError(
                        "Assessment not found or invalid"
                    )

                result = analyze_assessment(
                    assessment_id=session.study_id,
                    assessment=assessment,
                    answers=session.answers,
                )
  
                questions = assessment.get("questions", {})

                if isinstance(questions, list):
                    questions = {
                        q.get("code"): q
                        for q in questions
                        if q.get("code")
                    }

                prepared_output = build_prepared_assessment_output(
                    assessment_id=session.study_id,
                    question_bank=questions,
                    answers=session.answers,
                )

                result = run_engine_logic(session.answers)
            else:
                registered_result = run_registered_analysis(
                    study_id=session.study_id,
                    answers=session.answers or {},
                )

                if registered_result is not None:
                    result = registered_result
                else:
                    result = {
                        "result_type": "completed_questionnaire",
                        "study_id": session.study_id,
                        "answers_count": len(session.answers or {}),
                        "answers": session.answers,
                        "public_explanation": {
                            "title": "Анкета сохранена",
                            "message": "Ответы сохранены для исследовательского анализа.",
                            "confidence": "analysis_not_run_yet",
                        },
                        "next_questions": [],
                        "uncertainty": {
                            "status": "not_analyzed_yet",
                            "reason": "generic_questionnaire_saved_without_model_analysis",
                        },
                   
                    "next_questions": [],
                    "uncertainty": {
                        "status": "not_analyzed_yet",
                        "reason": "generic_questionnaire_saved_without_model_analysis",
                    },
                }

        except Exception as exc:
            print("=== RUN_SESSION FAILED ===")
            print(type(exc).__name__)
            print(str(exc))

            session.status = SessionStatus.RUN_FAILED
            session.updated_at = datetime.now(UTC)

            self.store.save(session)

            raise RunFailedError(
                "Session run failed"
            ) from exc

        session.run_count += 1
        session.run_history.append({
            "type": "engine_run",
            "run_number": session.run_count,
            "answers_count": len(session.answers),
            "next_questions_count": len(
                result.get("next_questions", [])
            ),
            "created_at": datetime.now(UTC).isoformat(),
        })

        session.raw_engine_result = result
        session.public_output = result.get(
            "public_explanation",
            result.get("pilot_public_output",
            result.get("output", {})),
        )
        session.next_question_snapshots = result.get(
            "next_questions",
            [],
        )

        session.acquisition_request_snapshots = result.get(
            "data_acquisition_requests",
            {},
        )

        session.uncertainty_snapshot = result.get(
            "uncertainty",
            {},
        )

        session.status = SessionStatus.RUN_COMPLETED
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session

    def generate_participant_export(self, session_id: str) -> dict:
        session = self.get_session(session_id)

        if not can_generate_export(session):
            raise ExportBlockedError(
                "Participant export generation blocked"
            )

        return generate_participant_export(session)


    def generate_research_export(self, session_id: str) -> dict:
        session = self.get_session(session_id)

        export = generate_research_export(session)

        save_research_record_from_export(export)

        return export

    def generate_export(self, session_id: str) -> dict:
        # Backward-compatible alias for participant export.
        # TODO: remove after legacy /export endpoint is deprecated.
        return self.generate_participant_export(session_id)

    def close_session(self, session_id: str) -> ParticipantSession:
        session = self.get_session(session_id)

        if session.invalidated:
            raise SessionInvalidatedError(
                "Session is invalidated"
            )

        if session.status == SessionStatus.CLOSED:
            return session

        if session.status not in {
            SessionStatus.RUN_COMPLETED,
            SessionStatus.EXPORT_READY,
            SessionStatus.EXPORT_BLOCKED,
            SessionStatus.RUN_FAILED,
        }:
            raise InvalidStatusTransitionError(
                "Invalid session status transition"
            )

        session.status = SessionStatus.CLOSED
        session.closed_at = datetime.now(UTC)
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session

    def invalidate_session(
        self,
        session_id: str,
        reason: str,
    ) -> ParticipantSession:
        session = self.get_session(session_id)

        session.status = SessionStatus.INVALIDATED
        session.invalidated = True
        session.invalidation_reason = reason
        session.updated_at = datetime.now(UTC)

        self.store.save(session)
        return session
