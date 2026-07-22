from __future__ import annotations

from pathlib import Path
from typing import Any

from external_ai.service import ExternalAIGateway

from .actions import RayActionStore
from .audit import RayAuditLog
from .context import RayContextResolver
from .contracts import (
    MemoryScope,
    RayActionProposal,
    RayResponse,
    RayRole,
)
from .evidence import EvidenceRegistry
from .learning import LearningCandidate, LearningRegistry
from .localization import localized
from .memory import MemoryRecord, RayMemoryStore


class RayColleagueService:
    """Governed, deterministic colleague foundation shared by two isolated roles."""

    def __init__(
        self,
        data_dir: str | Path = "data",
        *,
        external_ai_gateway: ExternalAIGateway | None = None,
    ) -> None:
        base = Path(data_dir)
        self.contexts = RayContextResolver()
        self.memory = RayMemoryStore(base / "ray_colleague_memory.json")
        self.learning = LearningRegistry(base / "ray_colleague_learning.json")
        self.evidence = EvidenceRegistry(base / "ray_colleague_evidence.json")
        self.actions = RayActionStore(base / "ray_colleague_actions.json")
        self.audit = RayAuditLog(base / "ray_colleague_audit.jsonl")
        self.external_ai_gateway = external_ai_gateway

    def contract(self) -> dict[str, Any]:
        result = self.contexts.contract()
        result.update(
            {
                "response_contract": "ray-colleague-response-1",
                "memory_contract": "ray-colleague-memory-1",
                "learning_contract": "ray-colleague-learning-1",
                "evidence_contract": "ray-colleague-evidence-1",
                "learning_statuses": ["draft", "trial", "active", "rejected"],
                "action_rule": "proposal_requires_explicit_confirmation",
                "external_ai_rule": "separate_filtered_artifact_never_automatic_truth_memory_or_authority",
            }
        )
        return result

    def respond(
        self,
        *,
        role: RayRole,
        owner_id: str,
        page_id: str,
        language: str,
        message: str,
        session_id: str | None = None,
        project_id: str | None = None,
        study_id: str | None = None,
        entity_refs: list[str] | None = None,
        selection: dict[str, Any] | None = None,
        requested_action: str | None = None,
    ) -> dict[str, Any]:
        context = self.contexts.resolve(
            role=role,
            owner_id=owner_id,
            page_id=page_id,
            language=language,
            session_id=session_id,
            project_id=project_id,
            study_id=study_id,
            entity_refs=entity_refs,
            selection=selection,
        )
        clean_message = message.strip()
        questions, unresolved = self._questions_for(context)
        if not clean_message:
            questions.insert(0, localized(context.language, "need_message"))
            unresolved.insert(0, "user_intent")

        intro_key = (
            "research_intro"
            if role == RayRole.RESEARCH_COLLEAGUE
            else "participant_intro"
        )
        response = RayResponse(
            role=role,
            page_id=page_id,
            language=context.language,
            message=localized(context.language, intro_key),
            clarification_questions=questions,
            next_steps=self._next_steps(context, unresolved),
            unresolved=unresolved,
        )

        # Participant messages are research-session data. They must remain in
        # the local participant-guide path and must never be forwarded as raw
        # prompts to an external provider. The external gateway is currently
        # an explicitly researcher-scoped information tool only.
        if (
            clean_message
            and role == RayRole.RESEARCH_COLLEAGUE
            and self.external_ai_gateway is not None
        ):
            external_result = self.external_ai_gateway.ask(
                account_id=owner_id,
                role=role.value,
                message=clean_message,
                language=context.language.value,
            )
            artifact = external_result.to_dict()
            response.external_information.append(artifact)
            if external_result.status == "received" and external_result.content:
                response.message = (
                    localized(context.language, "external_information")
                    + "\n\n"
                    + external_result.content
                )
            elif external_result.status not in {"not_configured"}:
                response.message = (
                    response.message
                    + "\n\n"
                    + localized(context.language, "external_unavailable")
                    + f" [{external_result.error_code or external_result.status}]"
                )
                response.unresolved.append("external_ai_response")

        if requested_action:
            proposal = self._build_action(context, requested_action, clean_message)
            if proposal:
                response.action_proposals.append(proposal)
                self.actions.add(
                    proposal,
                    role=role,
                    owner_id=owner_id,
                    page_id=page_id,
                )

        result = response.to_dict()
        self.audit.record(
            event_type="ray_response_created",
            role=role,
            owner_id=owner_id,
            page_id=page_id,
            request_id=response.request_id,
            status="completed",
            details={
                "unresolved_count": len(unresolved),
                "proposal_count": len(response.action_proposals),
                "language": context.language.value,
                "external_ai_status": (
                    response.external_information[0]["status"]
                    if response.external_information
                    else "not_requested"
                ),
            },
        )
        return result

    def remember(
        self,
        *,
        role: RayRole,
        owner_id: str,
        scope: str,
        summary: str,
        provenance: dict[str, Any],
        retention_reason: str,
        project_id: str | None = None,
        session_id: str | None = None,
        expires_at: str | None = None,
    ) -> dict[str, Any]:
        record = MemoryRecord(
            role=role,
            owner_id=owner_id,
            scope=MemoryScope(scope),
            summary=summary,
            provenance=provenance,
            retention_reason=retention_reason,
            project_id=project_id,
            session_id=session_id,
            expires_at=expires_at,
        )
        return self.memory.add(record)

    def submit_feedback(self, **payload: Any) -> dict[str, Any]:
        candidate = LearningCandidate(**payload)
        return self.learning.add(candidate)

    def confirm_action(
        self,
        action_id: str,
        *,
        role: RayRole,
        owner_id: str,
    ) -> dict[str, Any]:
        action = self.actions.confirm(action_id, role=role, owner_id=owner_id)
        self.audit.record(
            event_type="ray_action_confirmed",
            role=role,
            owner_id=owner_id,
            page_id=action["page_id"],
            request_id=action_id,
            status="confirmed",
            details={"action_type": action["action_type"]},
        )
        return action

    @staticmethod
    def _has(selection: dict[str, Any], *keys: str) -> bool:
        return any(selection.get(key) not in (None, "", [], {}) for key in keys)

    def _questions_for(self, context) -> tuple[list[str], list[str]]:
        selection = context.selection
        questions: list[str] = []
        unresolved: list[str] = []

        def require(condition: bool, code: str, text_key: str) -> None:
            if not condition:
                unresolved.append(code)
                questions.append(localized(context.language, text_key))

        if context.page_id == "evidence_review":
            plan = selection.get("review_plan") or {}
            readiness = selection.get("validation") or plan.get("readiness") or {}
            eligibility = plan.get("eligibility") or {}
            search = plan.get("search") or {}
            screening = plan.get("screening") or {}
            extraction = plan.get("extraction") or {}
            appraisal = plan.get("appraisal") or {}
            synthesis = plan.get("synthesis") or {}
            acquisition = plan.get("evidence_acquisition_plan") or {}
            selected_items = (
                selection.get("selected_catalog_items")
                or acquisition.get("selected_catalog_items")
                or []
            )
            require(
                self._has(plan, "review_question") and self._has(plan, "review_type"),
                "evidence_review_question_scope",
                "evidence_review_question_scope",
            )
            require(
                self._has(eligibility, "inclusion_criteria") and self._has(eligibility, "exclusion_criteria"),
                "evidence_review_eligibility",
                "evidence_review_eligibility",
            )
            require(
                bool(search.get("sources"))
                and all(item.get("planned_query") for item in search.get("sources", []) if isinstance(item, dict)),
                "evidence_review_search",
                "evidence_review_search",
            )
            require(
                self._has(screening, "screening_process")
                and self._has(screening, "exclusion_reason_policy")
                and bool(extraction.get("data_items")),
                "evidence_review_selection_extraction",
                "evidence_review_selection_extraction",
            )
            require(
                bool(appraisal.get("approach_ids")),
                "evidence_review_appraisal",
                "evidence_review_appraisal",
            )
            require(
                bool(selected_items),
                "evidence_review_acquisition",
                "evidence_review_acquisition",
            )
            require(
                bool(synthesis.get("approach_ids")) and self._has(synthesis, "compatibility_rule"),
                "evidence_review_synthesis",
                "evidence_review_synthesis",
            )
            require(
                self._has(plan, "contradictory_evidence_rule")
                and self._has(plan, "claim_decision_rule"),
                "evidence_review_claim_rules",
                "evidence_review_claim_rules",
            )
            for issue in readiness.get("issues") or []:
                code = f"protocol:{issue}"
                if code not in unresolved:
                    unresolved.append(code)
        elif context.page_id == "model_parameter_constructor":
            require(
                self._has(selection, "name", "preliminary_definition"),
                "preliminary_definition",
                "name_definition",
            )
            require(
                self._has(selection, "question_refs", "measurement_source_refs"),
                "measurement_binding",
                "measurement",
            )
            require(
                self._has(selection, "calculation_rule", "formula_id"),
                "calculation_rule",
                "calculation",
            )
            require(
                self._has(selection, "time_reference", "temporal_scale"),
                "time_binding",
                "time",
            )
        elif context.page_id == "research_lab":
            require(self._has(selection, "basis_items"), "hypothesis_basis", "hypothesis_basis")
            require(self._has(selection, "variable_roles"), "hypothesis_variables", "hypothesis_variables")
            require(self._has(selection, "formal_statement"), "formal_statement", "hypothesis_statement")
            require(self._has(selection, "falsification_criteria"), "falsification_criteria", "hypothesis_falsification")
            require(self._has(selection, "time_relation"), "time_relation", "hypothesis_time")
            require(self._has(selection, "planned_analysis"), "planned_analysis", "hypothesis_analysis")
            if selection.get("hypothesis_mode") == "technical_quantitative":
                roles = selection.get("variable_roles") or []
                sensor_plan = selection.get("sensor_validation") or {}
                sensor_sources = sensor_plan.get("data_sources") or []
                require(
                    any(item.get("role") in {"predictor", "mediator", "moderator"} for item in roles if isinstance(item, dict)),
                    "technical_predictor",
                    "hypothesis_predictor",
                )
                require(
                    selection.get("model_family") not in {None, "", "unspecified"},
                    "technical_model_family",
                    "hypothesis_model_family",
                )
                if selection.get("time_axis_included"):
                    require(
                        any(item.get("source_role") == "time_axis" for item in sensor_sources if isinstance(item, dict)),
                        "technical_time_contract",
                        "hypothesis_time_variable",
                    )
                require(
                    any(item.get("source_role") == "sensor_candidate" for item in sensor_sources if isinstance(item, dict)),
                    "sensor_candidate_source",
                    "sensor_candidate_source",
                )
                require(
                    any(item.get("source_role") in {"criterion_reference", "questionnaire_anchor", "physical_state_anchor", "model_parameter_anchor", "event_annotation"} for item in sensor_sources if isinstance(item, dict)),
                    "sensor_anchor_source",
                    "sensor_anchor_source",
                )
                require(
                    self._has(sensor_plan, "pairing_strategy") and self._has(sensor_plan, "observation_unit", "independence_unit"),
                    "sensor_pairing_contract",
                    "sensor_pairing_contract",
                )
                require(
                    self._has(sensor_plan, "selected_method_ids"),
                    "sensor_validation_method",
                    "sensor_validation_method",
                )
                if sensor_plan.get("validation_aim") == "sensor_questionnaire_discrepancy":
                    require(
                        self._has(sensor_plan, "discrepancy_metric") and self._has(sensor_plan, "harmonization_rule"),
                        "sensor_discrepancy_definition",
                        "sensor_discrepancy_definition",
                    )
            elif selection.get("hypothesis_mode") == "humanities_qualitative":
                inquiry = selection.get("qualitative_inquiry") or {}
                sources = inquiry.get("evidence_sources") or []
                require(
                    self._has(inquiry, "research_question"),
                    "qualitative_research_question",
                    "qualitative_research_question",
                )
                require(
                    any(item.get("evidence_role") == "empirical_material" for item in sources if isinstance(item, dict)),
                    "qualitative_empirical_material",
                    "qualitative_empirical_material",
                )
                require(
                    self._has(inquiry, "selected_method_ids"),
                    "qualitative_method",
                    "qualitative_method",
                )
                require(
                    self._has(inquiry, "disconfirming_evidence_rule"),
                    "qualitative_disconfirmation",
                    "qualitative_disconfirmation",
                )
                require(
                    self._has(inquiry, "trustworthiness_strategy_ids"),
                    "qualitative_trustworthiness",
                    "qualitative_trustworthiness",
                )
        elif context.page_id == "data_preparation":
            require(
                self._has(selection, "model_id", "dataset_id", "result_set_id"),
                "data_source",
                "data_source",
            )
            require(
                self._has(selection, "observation_unit", "sample_design"),
                "observation_unit",
                "data_shape",
            )
            require(
                self._has(selection, "analysis_method_id"),
                "analysis_method",
                "method",
            )
            require(
                self._has(selection, "time_reference", "time_slice"),
                "time_alignment",
                "time",
            )
        elif context.page_id == "data_editor":
            require(self._has(selection, "source_type", "detected_format"), "input_format", "input_format")
            require(self._has(selection, "quality_profile"), "quality_profile", "quality_profile")
            require(self._has(selection, "normalization_candidates", "selected_operations"), "normalization_choice", "normalization_choice")
            require(self._has(selection, "time_reference", "time_field"), "time_alignment", "time")
        elif context.page_id == "measurement_setup":
            require(self._has(selection, "connector_type"), "connector_type", "device_type")
            require(self._has(selection, "manufacturer", "product_name", "title"), "device_identity", "device_identity")
            require(self._has(selection, "permission_state", "status"), "permission_state", "permission_state")
            require(self._has(selection, "measurement_goal", "measurement_type"), "measurement_goal", "measurement_goal")
        elif context.page_id == "model_training":
            require(self._has(selection, "source_folder"), "source_folder", "training_source_folder")
            require(self._has(selection, "mask_folder"), "mask_folder", "training_mask_folder")
            require(self._has(selection, "output_folder"), "output_folder", "training_output_folder")
            require(self._has(selection, "task_type"), "task_type", "training_task")
            require(self._has(selection, "independence_unit", "group_regex"), "independence_unit", "training_independence")
        elif context.page_id == "fiji_integration":
            require(self._has(selection, "installation", "launcher_path"), "fiji_installation", "fiji_installation")
            require(self._has(selection, "input_path", "image"), "image_input", "image_input")
            require(self._has(selection, "operations", "active_command"), "processing_intent", "processing_intent")
            require(self._has(selection, "time_reference", "frame_time_binding"), "time_alignment", "time")
            require(self._has(selection, "output_path", "processing_run_id"), "output_contract", "output_contract")
        elif context.page_id == "scientific_results":
            require(
                self._has(selection, "calculation_run_id", "analysis_result_id"),
                "result_provenance",
                "result_trace",
            )
            require(
                self._has(selection, "quality_summary", "limitations"),
                "quality_limitations",
                "quality",
            )
            require(
                self._has(selection, "evidence_ids"),
                "scientific_sources",
                "sources",
            )
        elif context.role == RayRole.RESEARCH_COLLEAGUE:
            require(
                bool(context.project_id or context.study_id or context.entity_refs),
                "project_context",
                "project",
            )

        return questions, unresolved

    @staticmethod
    def _next_steps(context, unresolved: list[str]) -> list[str]:
        if unresolved:
            return [localized(context.language, "complete_missing")]
        return [
            localized(context.language, "complete_review"),
            localized(context.language, "confirm_before_write"),
        ]

    @staticmethod
    def _build_action(
        context,
        requested_action: str,
        message: str,
    ) -> RayActionProposal | None:
        allowed = {
            "track_open_question": "action_question",
            "track_project_decision": "action_decision",
            "track_research_risk": "action_risk",
        }
        if requested_action not in context.allowed_capabilities:
            raise PermissionError("REQUESTED_ACTION_NOT_ALLOWED_IN_CONTEXT")
        if requested_action not in allowed:
            return None
        if not message:
            raise ValueError("ACTION_CONTENT_REQUIRED")
        return RayActionProposal(
            action_type=requested_action,
            label=localized(context.language, allowed[requested_action]),
            payload={
                "text": message,
                "project_id": context.project_id,
                "study_id": context.study_id,
                "page_id": context.page_id,
            },
        )
