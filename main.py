import uuid
import json
import shutil
import os
from copy import deepcopy
from collections import defaultdict
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path
from typing import Any
import importlib.util
from pydantic import BaseModel, Field, SecretStr
from pilot_session.interview import (
    build_ray_next_question,
    build_ray_chat_response,
    parse_numeric_reply,
)
from fastapi.responses import HTMLResponse, FileResponse
from fastapi import FastAPI, HTTPException, Request, Response
from assessment.studies.decision_under_uncertainty.service import DecisionUnderUncertaintyService
from assessment.questionnaire_components import (
    list_question_types,
    list_response_types,
    list_scale_types,
    list_presentation_types,
    list_transition_types,
    normalize_question_type_id,
    normalize_response_type_id,
    normalize_scale_type_id,
    validate_question_measurement_contract,
)
from assessment.measurement.scale_registry import (
    build_scale_reference,
    get_scale_definition,
    get_scale_registry_contract,
    list_scale_definitions,
    scale_matches_requirement,
)
from assessment.analysis.analysis_method_registry import (
    EXECUTABLE_METHOD_IDS,
    METHODS,
)

from assessment.prepared_output import build_prepared_domain_output
from assessment.analysis.analysis_checker import (
    check_pair_analysis,
)
from assessment.analysis.run_statistical_method import (
    run_statistical_method,
)
from measurement_graph.connectors import discover_measurement_connectors
from measurement_graph.session import (
    create_measurement_session,
    mark_finished,
    mark_saved,
)
from measurement_graph.graph_builder import (
    build_measurement_graph_from_session,
)
from measurement_graph.storage import (
    save_measurement_graph,
)
from measurement_graph.time_contract import (
    normalize_measurement_time_reference,
    validate_measurement_time_reference,
)
from measurement_graph.instruments.session_runtime import (
    connect_instrument,
    disconnect_instrument,
    list_connected_instruments,
)

from model_engine.run_engine import run_engine_logic
from model_engine.intro_session_ru import (
    create_intro_session,
    process_intro_message,
)

from pilot_session.errors import PilotSessionError
from pilot_session.persistent_store import (
    PilotSessionPersistentStore,
)
from pilot_session.service import PilotSessionService
from pilot_account.persistent_store import PilotAccountPersistentStore
from pilot_account.service import PilotAccountService
from pilot_account.session_start_flow import PilotSessionStartFlow
from assessment.studies.decision_under_uncertainty import QUESTION_BANK
from assessment.studies.decision_under_uncertainty.router import get_next_question_code
from question_banks import get_question_bank
from assessment.registry import get_assessment, list_assessments
from assessment.services.result_service import ResultService
from research.lab_store import (
    account_deletion_impact,
    apply_account_deletion_disposition,
    create_research_object,
    list_research_objects,
)
from research.citations import build_citation_collection, citation_contract
from research.hypothesis_builder import build_hypothesis_definition, hypothesis_contract
from research.sensor_hypothesis import (
    build_sensor_validation_plan,
    compatible_sensor_methods,
    sensor_hypothesis_contract,
)
from research.qualitative_hypothesis import (
    build_qualitative_hypothesis_plan,
    build_qualitative_hypothesis_result,
    compatible_qualitative_methods,
    qualitative_hypothesis_contract,
)
from research.evidence_review import (
    EvidenceReviewError,
    build_plan as build_evidence_review_plan,
    contract as evidence_review_contract,
    list_reviews as list_evidence_reviews,
    save_review as save_evidence_review,
)
from research.researcher_accounts import (
    SESSION_COOKIE_NAME,
    SESSION_TTL_HOURS,
    ResearcherAccountError,
    ResearcherAccountService,
)
from research.repository import configure_object_store
from research.storage_paths import application_data_directory
from research.project_workspace import (
    ProjectWorkspaceError,
    block_catalog as project_block_catalog,
    connect_block as connect_project_block,
    connect_entity as connect_project_entity,
    create_project as create_modular_research_project,
    disconnect_block as disconnect_project_block,
    disconnect_entity as disconnect_project_entity,
    get_project as get_modular_research_project,
    list_projects as list_modular_research_projects,
    update_block as update_project_block,
    update_project as update_modular_research_project,
)
from research.model_training import (
    ModelTrainingError,
    build_colab_notebook,
    training_contract as model_training_contract,
)
from research.fiji_integration import (
    FijiIntegrationError,
    bridge_status as fiji_bridge_status,
    configure_installation as configure_fiji_installation,
    discover_installations as discover_fiji_installations,
    execute_pipeline as execute_fiji_pipeline,
    get_run as get_fiji_run,
    install_bridge as install_fiji_bridge,
    integration_contract as fiji_integration_contract,
    launch_fiji,
    record_bridge_event as record_fiji_bridge_event,
    remove_bridge as remove_fiji_bridge,
    validate_pipeline as validate_fiji_pipeline,
)
from research.probabilistic import (
    ProbabilisticMethodError,
    list_probabilistic_methods,
    run_probabilistic_method,
)
from research.records_store import (
    list_research_records,
    save_du_research_record,
)
from assessment.analysis.analysis_selector import (
    build_analysis_catalog,
)
from research.entity_registry import list_entities, list_hypothesis_entities
from research.analysis_runner import run_health_model_research_analysis
from research.analysis_store import load_analysis_results
from assessment.analysis.dependency_builder import (
    build_available_dependencies,
)
from research.analyses.health_model.level_map_analysis import (
    analyze_record_level_maps,
)
from research.public_output.health_model.participant_report import (
    build_participant_report,
)
from research.analyses.health_model.research_variable_registry import (
    list_health_model_research_variables,
)
from research.analyses.health_model.model_parameter_catalog import (
    build_available_model_parameter_catalog,
)
from research.analyses.health_model.model_parameter_dependency_builder import (
    build_available_model_parameter_dependencies,
    build_selected_model_parameter_pair_options,
)
from research.analyses.health_model.v61_calculator import (
    calculate_health_model_v61,
)
from research.analyses.health_model.model_parameter_pair_dataset import (
    build_model_parameter_pair_dataset,
    list_model_parameter_pair_participants,
    build_model_parameter_measurement_catalog,
)
from research.analyses.health_model.model_parameter_analysis_checker import (
    check_model_parameter_pair_analysis,
)
from research.analyses.health_model.parameter_calculation_registry import (
    build_compatible_calculation_options,
)
from research.analyses.health_model.observable_marker_registry import (
    delete_observable_marker_draft,
    list_observable_markers,
    transition_observable_marker,
    upsert_observable_marker_draft,
)
from research.model_calculation_store import (
    ModelCalculationPersistentStore,
)
from research.model_calculation_schemas import (
    ModelCalculationInputReference,
)
from research.model_calculation_service import (
    ModelCalculationService,
)
from research.model_registry import (
    list_registered_calculation_models,
)
from research.analyses.health_model.model_adapter import (
    register_health_model,
)
from research.analyses.health_model.model_parameter_registry import (
    build_model_parameter_registry,
    delete_custom_model_parameter_draft,
    get_model_parameter_definition,
    list_model_parameter_definitions as list_registered_parameter_definitions,
    transition_custom_model_parameter_definition,
    upsert_custom_model_parameter_draft,
)
from research.analyses.health_model.mechanism_registry import (
    delete_custom_mechanism_draft,
    get_mechanism,
    list_mechanism_definitions as list_registered_mechanism_definitions,
    transition_custom_mechanism_definition,
    upsert_custom_mechanism_draft,
)
from research.editors.audit import append_audit_event, list_audit_events
from research.editors.question_registry import (
    active_question_overlays,
    delete_question_draft,
    list_question_versions,
    transition_question_definition,
    upsert_question_draft,
)
from research.editors.question_bank_registry import (
    get_registered_question_bank,
    list_registered_question_banks,
    register_question_bank,
    rollback_question_bank_registration,
)
from research.editors.model_entity_classification import (
    LOGIC_ENTITY,
    MODEL_PARAMETER,
    enrich_model_entity,
    filter_model_entities,
)
from research.editors.model_definition_explainer import explain_model_definition
from research.editors.data_pipeline import (
    apply_transformation,
    build_transformation_run_dataset,
    get_transformation_run,
    list_transformation_runs,
    profile_records,
    list_recipes,
    transformation_contract,
    transform_records,
)
from research.editors.data_lifecycle import (
    assess_empty_session_purge,
    build_downstream_reference_index,
    purge_empty_session,
)
from ray_colleague import RayColleagueService, RayRole
from external_core import (
    DomainLifecycle,
    ExternalCoreService,
    SettingsStatus,
)
from external_ai import ConnectionScope, ExternalAIError, ExternalAIGateway
from pprint import pformat
from pathlib import Path

app = FastAPI()
register_health_model()
from fastapi.staticfiles import StaticFiles


store = PilotSessionPersistentStore(
    "data/pilot_sessions.json"
)

model_calculation_store = (
    ModelCalculationPersistentStore(
        "data/model_calculation_runs.json"
    )
)

model_calculation_service = (
    ModelCalculationService(
        model_calculation_store
    )
)

pilot_service = PilotSessionService(store)
account_store = PilotAccountPersistentStore(
    "data/pilot_accounts.json"
)

account_service = PilotAccountService(account_store)

session_start_flow = PilotSessionStartFlow(
    account_service=account_service,
    session_service=pilot_service,
)

intro_sessions = {}
result_service = ResultService()
external_core_service = ExternalCoreService("data")
researcher_account_service = ResearcherAccountService()
configure_object_store(application_data_directory() / "research_objects.json")


def _external_ai_effective_settings(
    role: str,
    account_id: str | None,
) -> dict[str, Any]:
    del account_id
    return external_core_service.effective(
        role=role,
        domain_id=ExternalCoreService.DOMAIN_SCOPE_ID,
    )


external_ai_gateway = ExternalAIGateway(
    application_data_directory(),
    settings_provider=_external_ai_effective_settings,
)
ray_colleague_service = RayColleagueService(
    "data",
    external_ai_gateway=external_ai_gateway,
)

class RayChatInput(BaseModel):
    message: str
    lang: str = "ru"

class IntroChatInput(BaseModel):
    message: str

class RayStartInput(BaseModel):
    participant_id: str = "ray_dialogue_user"
    lang: str = "ru"


class RayColleagueResearcherInput(BaseModel):
    researcher_id: str
    message: str = ""
    page_id: str = "research_workspace"
    lang: str = "ru"
    project_id: str | None = None
    study_id: str | None = None
    entity_refs: list[str] = Field(default_factory=list)
    selection: dict[str, Any] = Field(default_factory=dict)
    requested_action: str | None = None


class RayColleagueParticipantInput(BaseModel):
    participant_id: str
    session_id: str
    message: str = ""
    page_id: str = "pilot"
    lang: str = "ru"
    study_id: str | None = None
    entity_refs: list[str] = Field(default_factory=list)
    selection: dict[str, Any] = Field(default_factory=dict)


class RayColleagueMemoryInput(BaseModel):
    owner_id: str
    scope: str
    summary: str
    provenance: dict[str, Any]
    retention_reason: str
    project_id: str | None = None
    session_id: str | None = None
    expires_at: str | None = None


class RayColleagueFeedbackInput(BaseModel):
    role: str
    submitted_by: str
    target_type: str
    target_id: str
    feedback: str
    expected_behavior: str
    context_scope: str
    contains_participant_data: bool = False


class RayActionConfirmationInput(BaseModel):
    owner_id: str


class ExternalCoreTransitionInput(BaseModel):
    actor_id: str | None = None


class ExternalAIModelDiscoveryInput(BaseModel):
    provider_id: str
    credential: SecretStr


class ExternalAIConnectionInput(BaseModel):
    scope: str = "account"
    provider_id: str
    model: str
    credential: SecretStr


class ExternalAIPolicyInput(BaseModel):
    scope: str = "account"
    profile_id: str
    enabled: bool = True
    never_send_categories: list[str] = Field(default_factory=list)
    never_send_terms: list[str] = Field(default_factory=list)


class ExternalCoreSettingsDraftInput(BaseModel):
    layer: str
    scope_id: str
    created_by: str
    settings_id: str | None = None
    revision: int = 1
    parent_settings_id: str | None = None
    allowed_capabilities: list[str] | None = None
    allowed_data_classes: list[str] | None = None
    allowed_channels: list[str] | None = None
    allowed_languages: list[str] | None = None
    default_language: str | None = None
    allowed_memory_scopes: list[str] | None = None
    maximum_retention_days: int | None = None
    learning_enabled: bool | None = None
    allowed_learning_categories: list[str] | None = None
    human_confirmation_actions: list[str] = Field(default_factory=list)
    clarification_policy: str | None = None
    uncertainty_detail: str | None = None
    external_ai_mode: str | None = None
    notes: str | None = None


class CreatePilotAccountInput(BaseModel):
    preferred_language: str = "ru"
class ModelCalculationInputReferencePayload(
    BaseModel
):
    source_type: str
    source_record_type: str

    source_record_id: str | None = None
    source_session_id: str | None = None
    source_submission_id: str | None = None

    participant_id: str | None = None
    subject_link_id: str | None = None

    study_id: str | None = None
    domain_id: str | None = None

    observation_time: str | None = None
    global_time_reference: str | None = None

    selected_variable_codes: list[str] = []
    selected_record_ids: list[str] = []

    provenance: dict = {}


class CreateModelCalculationInput(BaseModel):
    model_id: str
    model_version: str
    calculation_version: str

    participant_id: str | None = None
    subject_link_id: str | None = None

    calculation_scope: str = "participant"
    observation_unit: str = "calculation_run"

    input_snapshot: dict
    input_references: list[
        ModelCalculationInputReferencePayload
    ] = []

    input_quality: dict = {}
    provenance: dict = {}
    
def serialize_model_calculation_run(
    run,
) -> dict:
    return {
        "calculation_run_id": (
            run.calculation_run_id
        ),
        "schema_version": (
            run.schema_version
        ),
        "status": run.status.value,

        "model_id": run.model_id,
        "model_version": (
            run.model_version
        ),
        "calculation_version": (
            run.calculation_version
        ),
        "input_contract_version": (
            run.input_contract_version
        ),

        "created_at": (
            run.created_at.isoformat()
        ),
        "updated_at": (
            run.updated_at.isoformat()
        ),
        "started_at": (
            run.started_at.isoformat()
            if run.started_at
            else None
        ),
        "completed_at": (
            run.completed_at.isoformat()
            if run.completed_at
            else None
        ),

        "participant_id": (
            run.participant_id
        ),
        "subject_link_id": (
            run.subject_link_id
        ),

        "calculation_scope": (
            run.calculation_scope
        ),
        "observation_unit": (
            run.observation_unit
        ),

        "input_references": [
            {
                "input_reference_id": (
                    reference.input_reference_id
                ),
                "schema_version": (
                    reference.schema_version
                ),
                "source_type": (
                    reference.source_type
                ),
                "source_record_type": (
                    reference.source_record_type
                ),
                "source_record_id": (
                    reference.source_record_id
                ),
                "source_session_id": (
                    reference.source_session_id
                ),
                "source_submission_id": (
                    reference.source_submission_id
                ),
                "participant_id": (
                    reference.participant_id
                ),
                "subject_link_id": (
                    reference.subject_link_id
                ),
                "study_id": (
                    reference.study_id
                ),
                "domain_id": (
                    reference.domain_id
                ),
                "observation_time": (
                    reference.observation_time
                ),
                "global_time_reference": (
                    reference.global_time_reference
                ),
                "selected_variable_codes": (
                    reference.selected_variable_codes
                ),
                "selected_record_ids": (
                    reference.selected_record_ids
                ),
                "provenance": (
                    reference.provenance
                ),
            }
            for reference
            in run.input_references
        ],

        "input_snapshot": (
            run.input_snapshot
        ),
        "input_quality": (
            run.input_quality
        ),
        "input_validation": (
            run.input_validation
        ),

        "calculation_result": (
            run.calculation_result
        ),
        "parameter_record_count": (
            run.parameter_record_count
        ),
        "parameter_records": (
            run.parameter_records
        ),

        "uncertainty": run.uncertainty,
        "warnings": run.warnings,
        "reason_codes": (
            run.reason_codes
        ),

        "provenance": run.provenance,

        "invalidated": (
            run.invalidated
        ),
        "invalidation_reason": (
            run.invalidation_reason
        ),
        "failure": run.failure,
    }
    
class DUCompletePayload(BaseModel):
    session_id: str
    answers: dict
    language: str = "ru"
    account_id: str | None = None
    domain_data_identity: dict | None = None

class StartSessionAfterAgreementInput(BaseModel):
    account_id: str
    consent_record: dict
    study_id: str | None = None
    participant_role: str = "participant"

class ResearchObjectPayload(BaseModel):
    object_type: str
    owner: str
    title: str
    description: str = ""
    status: str = "draft"
    variables: list = Field(default_factory=list)
    analysis_methods: list = Field(default_factory=list)
    research_question: str | None = None
    hypothesis_basis: str | None = None
    basis_notes: str | None = None


class CitationCollectionInput(BaseModel):
    title: str = "Bibliography"
    destination: str = ""
    style: str = "apa7"
    requirements_source: str = ""
    references: list[dict[str, Any]] = Field(default_factory=list)
    project_id: str | None = None
    block_id: str | None = None


class HypothesisDefinitionInput(BaseModel):
    definition: dict[str, Any]
    project_id: str | None = None
    block_id: str | None = None


class SensorMethodCompatibilityInput(BaseModel):
    validation_aim: str
    outcome_data_kind: str
    repeated_measurements: bool = False
    has_reference: bool = False


class SensorValidationPlanInput(BaseModel):
    plan: dict[str, Any]


class QualitativeMethodCompatibilityInput(BaseModel):
    inquiry_mode: str
    empirical_entity_types: list[str] = Field(default_factory=list)


class QualitativeHypothesisPlanInput(BaseModel):
    plan: dict[str, Any]


class QualitativeHypothesisResultInput(BaseModel):
    result: dict[str, Any]
    project_id: str | None = None


class EvidenceReviewInput(BaseModel):
    plan: dict[str, Any]
    status: str = "draft"
    language: str = "ru"
    project_id: str | None = None
    block_id: str | None = None
    review_id: str | None = None


class ResearcherRegistrationInput(BaseModel):
    login: str
    display_name: str
    password: str
    preferred_language: str = "ru"


class ResearcherLoginInput(BaseModel):
    login: str
    password: str


class ResearcherRecoveryInput(BaseModel):
    login: str
    recovery_code: str
    new_password: str


class ResearcherAccountDeletionInput(BaseModel):
    password: str
    confirmation: str
    delete_owned_drafts: bool = False


class ResearcherPreferencesInput(BaseModel):
    research_profiles: list[str]
    preferred_language: str | None = None


class ResearchProjectCreateInput(BaseModel):
    title: str
    research_question: str = ""
    goal: str = ""
    language: str = "ru"
    display_timezone: str = "UTC"


class ResearchProjectUpdateInput(BaseModel):
    changes: dict[str, Any]


class ResearchProjectBlockConnectInput(BaseModel):
    block_type: str


class ResearchProjectBlockUpdateInput(BaseModel):
    content: dict[str, Any]


class ResearchProjectEntityConnectInput(BaseModel):
    field_code: str
    entity: dict[str, Any]


class ModelTrainingNotebookInput(BaseModel):
    source_folder: str
    mask_folder: str
    output_folder: str
    language: str = "ru"
    task_type: str = "grayscale_binary_segmentation"
    pairing_strategy: str = "relative_path_and_normalized_stem"
    group_regex: str | None = None
    image_height: int = 256
    image_width: int = 256
    batch_size: int = 8
    epochs: int = 50
    seed: int = 20260719
    project_id: str | None = None
    block_id: str | None = None


class FijiInstallationInput(BaseModel):
    path: str


class FijiPipelineInput(BaseModel):
    input_path: str
    output_path: str
    operations: list[dict[str, Any]]
    apply_to_stack: bool = False
    time_reference: dict[str, Any] | None = None
    project_id: str | None = None
    block_id: str | None = None


class ProbabilisticAnalysisRunInput(BaseModel):
    method_id: str
    payload: dict[str, Any]
    project_id: str | None = None
    block_id: str | None = None

class QuestionBankSavePayload(BaseModel):
    language: str = "ru"
    source_file: str | None = None
    variable_name: str | None = None
    questions: list[dict]

class CreateQuestionBankPayload(BaseModel):
    bank_id: str
    title: str

class MeasurementGraphPayload(BaseModel):
    graph: dict

class PilotQuestionnaireBanksPayload(BaseModel):
    enabled_bank_ids: list[str]

class RunInput(BaseModel):
    answers: dict

class HealthModelV61RunInput(BaseModel):
    answers: dict

class RayAnswerInput(BaseModel):
    variable_code: str
    value: Any

class InvalidateSessionInput(BaseModel):
    reason: str

class SubmitAnswersInput(BaseModel):
    answers: dict
    domain_data_identity: dict | None = None

class CreateMeasurementInput(BaseModel):
    connector: dict
    measurement_type: str
    study_id: str | None = None
    participant_id: str | None = None
    session_id: str | None = None
    series_id: str | None = None
    series_position: int | None = None
    context: dict | None = None

class FinishMeasurementInput(BaseModel):
    measurement_session: dict
    raw_file_path: str | None = None
    original_file_name: str | None = None
    file_type: str | None = None
    checksum: str | None = None
    context: dict | None = None


class SaveMeasurementInput(BaseModel):
    measurement_graph: dict

class ConnectInstrumentInput(BaseModel):
    instrument_id: str
    connector: dict
    measurement_type: str
    study_id: str
    participant_id: str | None = None
    session_id: str | None = None
    context: dict | None = None


class TurnOffInstrumentInput(BaseModel):
    raw_file_path: str | None = None
    original_file_name: str | None = None
    file_type: str | None = None
    checksum: str | None = None

class AnalysisCheckInput(BaseModel):
    study_id: str
    left_question_code: str
    right_question_code: str
    method_id: str

class ParameterAnalysisCheckInput(BaseModel):
    model_id: str = "health_model_v6_1"
    study_id: str | None = None
    left_parameter_code: str
    right_parameter_code: str
    method_id: str
    analysis_scope: str = "CROSS_PARTICIPANT"
    repeated_measure_policy: str = "latest"
    participant_reference: str | None = None

class ModelParameterStatisticalRunInput(BaseModel):
    model_id: str = "health_model_v6_1"
    study_id: str | None = None
    left_parameter_code: str
    right_parameter_code: str
    method_id: str
    analysis_scope: str = "CROSS_PARTICIPANT"
    repeated_measure_policy: str = "latest"
    participant_reference: str | None = None

class ModelParameterDatasetInput(BaseModel):
    model_id: str = "health_model_v6_1"
    study_id: str | None = None
    left_parameter_code: str
    right_parameter_code: str
    analysis_scope: str = "CROSS_PARTICIPANT"
    repeated_measure_policy: str = "reject_repeated"
    participant_reference: str | None = None

class StatisticalAnalysisRunInput(BaseModel):
    study_id: str
    left_question_code: str
    right_question_code: str
    method_id: str


class QuestionnaireMultivariableAnalysisInput(BaseModel):
    project_id: str = "health_model_pilot"
    study_id: str | None = None
    questionnaire_id: str
    question_uuids: list[str]
    analysis_scope: str = "cross_participant"
    participant_reference: str | None = None
    pair_methods: dict[str, str] | None = None

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/pilot/accounts")
def create_pilot_account(data: CreatePilotAccountInput):
    account = account_service.create_account(
        preferred_language=data.preferred_language,
    )

    return {
        "ok": True,
        "account_id": account.account_id,
        "participant_id": account.participant_id,
        "subject_link_id": account.subject_link_id,
        "preferred_language": account.preferred_language,
        "status": account.status.value,
    }
@app.get("/pilot/accounts/{account_id}")
def get_pilot_account(account_id: str):
    account = account_service.get_account(account_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return {
        "ok": True,
        "account_id": account.account_id,
        "participant_id": account.participant_id,
        "subject_link_id": account.subject_link_id,
        "preferred_language": account.preferred_language,
        "status": account.status.value,
    }


@app.post("/pilot/accounts/start-session")
def start_session_after_agreement(
    data: StartSessionAfterAgreementInput,
):
    print("=== START SESSION ROUTE HIT ===")
    print(data)
    try:
        result = session_start_flow.start_session_after_agreement(
            account_id=data.account_id,
            consent_record=data.consent_record,
            study_id=data.study_id,
            participant_role=data.participant_role,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Account not found",
            )

        session = result["session"]
        agreement = result["agreement"]

        return {
            "ok": True,
            "account_id": data.account_id,
            "session_id": session.session_id,
            "participant_id": session.participant_id,
            "subject_link_id": session.subject_link_id,
            "agreement_id": agreement["agreement_id"],
            "agreement_status": agreement["agreement_status"],
            "collection_allowed": agreement["collection_allowed"],
            "status": session.status.value,
            "available_start_modes": [
                {
                    "mode": "ray_dialogue",
                    "label": "Диалог с Рэем",
                    "endpoint": f"/ray/chat/{session.session_id}",
                    "method": "POST",
                    "first_question": {
                        "status": "question",
                        "message": (
                            "Привет. Я Рэй. Давай начнём спокойно.\n\n"
                            "Первый вопрос: есть ли у тебя сейчас работа, учёба "
                            "или другая основная деятельность?\n\n"
                            "Ответь числом: 0 — нет, 1 — да."
                        ),
                        "awaiting_variable_code": "d0",
                        "expected_response_target": "answers.d0",
                    },
                },
                {
                    "mode": "questionnaire",
                    "label": "Ответы на вопросы анкеты",
                    "endpoint": (
                        f"/pilot/sessions/{session.session_id}/answers"
                    ),
                    "method": "POST",
                    "expected_payload": {
                        "answers": {
                            "d0": "0 or 1"
                        }
                    },
                },
            ],
        }

    except PilotSessionError as exc:
        print("=== START SESSION ERROR ===")
        print(exc.to_dict())

        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict(),
        )    

@app.post("/pilot/sessions/{session_id}/intro-chat")
def intro_chat(
    session_id: str,
    data: IntroChatInput,
):
    try:
        pilot_session = pilot_service.get_session(session_id)

        intro_session = intro_sessions.get(session_id)

        if intro_session is None:
            intro_session = create_intro_session(
                session_id=pilot_session.session_id,
                participant_id=pilot_session.participant_id,
                subject_link_id=pilot_session.subject_link_id,
                study_id=pilot_session.study_id or "pilot-study-1",
                participant_role=(
                    pilot_session.participant_role
                    or "participant"
                ),
                synchronization_reference=(
                    pilot_session.synchronization_reference
                ),
            )

        result = process_intro_message(
            session=intro_session,
            message=data.message,
        )

        intro_sessions[session_id] = result["session"]

        return {
            "ok": True,
            "session_id": session_id,
            "intro": result,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

def _raise_ray_colleague_http(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        status_code = 403
    elif isinstance(exc, KeyError):
        status_code = 404
    else:
        status_code = 422
    raise HTTPException(status_code=status_code, detail=str(exc)) from exc


def _raise_researcher_account_http(exc: ResearcherAccountError) -> None:
    raise HTTPException(status_code=exc.status_code, detail={"error": exc.code}) from exc


def _set_researcher_session_cookie(response: Response, token: str, request: Request) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_TTL_HOURS * 60 * 60,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        path="/",
    )


def _researcher_session(
    request: Request, *, require_csrf: bool = False
) -> dict[str, Any]:
    try:
        return researcher_account_service.require_session(
            request.cookies.get(SESSION_COOKIE_NAME),
            request.headers.get("x-csrf-token") if require_csrf else None,
        )
    except ResearcherAccountError as exc:
        _raise_researcher_account_http(exc)


def _platform_external_ai_admin(account_id: str) -> bool:
    configured = {
        item.strip()
        for item in os.environ.get(
            "RAY_PLATFORM_ADMIN_ACCOUNT_IDS",
            "",
        ).split(",")
        if item.strip()
    }
    return account_id in configured


def _raise_external_ai_http(exc: ExternalAIError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail={"error": exc.code},
    ) from exc


@app.get("/researcher/auth/contract")
def researcher_auth_contract():
    return {"ok": True, "contract": researcher_account_service.contract()}


@app.get("/researcher/auth/storage-status")
def researcher_auth_storage_status():
    return {"ok": True, "storage": researcher_account_service.storage_status()}


@app.post("/researcher/auth/migrate-legacy-store")
def migrate_legacy_researcher_account_store():
    try:
        return {"ok": True, **researcher_account_service.migrate_legacy_store("data")}
    except ResearcherAccountError as exc:
        _raise_researcher_account_http(exc)


@app.post("/researcher/auth/register")
def register_researcher_account(
    data: ResearcherRegistrationInput, request: Request, response: Response
):
    try:
        result = researcher_account_service.register_and_login(
            login=data.login,
            display_name=data.display_name,
            password=data.password,
            preferred_language=data.preferred_language,
        )
        _set_researcher_session_cookie(response, result.pop("session_token"), request)
        return {"ok": True, **result}
    except ResearcherAccountError as exc:
        _raise_researcher_account_http(exc)


@app.post("/researcher/auth/login")
def login_researcher_account(
    data: ResearcherLoginInput, request: Request, response: Response
):
    try:
        result = researcher_account_service.authenticate(
            login=data.login, password=data.password
        )
        _set_researcher_session_cookie(response, result.pop("session_token"), request)
        return {"ok": True, **result}
    except ResearcherAccountError as exc:
        _raise_researcher_account_http(exc)


@app.get("/researcher/auth/session")
def current_researcher_session(request: Request):
    try:
        result = researcher_account_service.rotate_csrf(
            request.cookies.get(SESSION_COOKIE_NAME)
        )
        result["active_sessions"] = researcher_account_service.list_sessions(
            result["account"]["account_id"]
        )
        return {"ok": True, **result}
    except ResearcherAccountError as exc:
        _raise_researcher_account_http(exc)


@app.post("/researcher/auth/logout")
def logout_researcher_account(request: Request, response: Response):
    try:
        researcher_account_service.logout(
            request.cookies.get(SESSION_COOKIE_NAME) or "",
            request.headers.get("x-csrf-token") or "",
        )
        response.delete_cookie(SESSION_COOKIE_NAME, path="/", samesite="strict")
        return {"ok": True, "status": "logged_out"}
    except ResearcherAccountError as exc:
        _raise_researcher_account_http(exc)


@app.post("/researcher/auth/sessions/revoke-others")
def revoke_other_researcher_sessions(request: Request):
    try:
        count = researcher_account_service.revoke_other_sessions(
            request.cookies.get(SESSION_COOKIE_NAME) or "",
            request.headers.get("x-csrf-token") or "",
        )
        return {"ok": True, "revoked_session_count": count}
    except ResearcherAccountError as exc:
        _raise_researcher_account_http(exc)


@app.post("/researcher/auth/recover")
def recover_researcher_account(data: ResearcherRecoveryInput):
    try:
        result = researcher_account_service.recover(
            login=data.login,
            recovery_code=data.recovery_code,
            new_password=data.new_password,
        )
        return {"ok": True, **result, "status": "password_changed_all_sessions_revoked"}
    except ResearcherAccountError as exc:
        _raise_researcher_account_http(exc)


@app.post("/researcher/account/preferences")
def update_researcher_preferences(data: ResearcherPreferencesInput, request: Request):
    context = _researcher_session(request, require_csrf=True)
    try:
        account = researcher_account_service.update_preferences(
            account_id=context["account"]["account_id"],
            research_profiles=data.research_profiles,
            preferred_language=data.preferred_language,
        )
        return {"ok": True, "account": account}
    except ResearcherAccountError as exc:
        _raise_researcher_account_http(exc)


@app.get("/researcher/account/deletion-preview")
def researcher_account_deletion_preview(request: Request):
    context = _researcher_session(request)
    account = context["account"]
    return {
        "ok": True,
        "account": account,
        "required_confirmation": f"DELETE {account['login']}",
        "research_objects": account_deletion_impact(account["account_id"]),
        "authorship_policy": "authorship_and_contribution_history_are_preserved",
        "trial_active_policy": "access_removed_authorship_preserved",
    }


@app.post("/researcher/account/delete")
def delete_researcher_account(
    data: ResearcherAccountDeletionInput, request: Request, response: Response
):
    context = _researcher_session(request, require_csrf=True)
    account_id = context["account"]["account_id"]
    try:
        verified = researcher_account_service.verify_deletion(
            account_id=account_id,
            password=data.password,
            confirmation=data.confirmation,
        )
        authorship = researcher_account_service.authorship_snapshot(account_id)
        disposition = apply_account_deletion_disposition(
            account_id,
            delete_owned_drafts=data.delete_owned_drafts,
            authorship_snapshot=authorship,
        )
        researcher_account_service.delete_verified_account(account_id)
        response.delete_cookie(SESSION_COOKIE_NAME, path="/", samesite="strict")
        return {
            "ok": True,
            "status": "account_deleted",
            "deleted_login": verified["login"],
            "research_object_disposition": disposition,
            "authorship": {
                **authorship,
                "account_link_status": "account_deleted_authorship_preserved",
            },
        }
    except ResearcherAccountError as exc:
        _raise_researcher_account_http(exc)


@app.get("/ray-colleague/contract")
def get_ray_colleague_contract():
    return {
        "ok": True,
        "contract": ray_colleague_service.contract(),
    }


@app.get("/external-core/contract")
def get_external_core_contract(request: Request):
    context = _researcher_session(request)
    contract = external_core_service.contract()
    connection = external_ai_gateway.registry.effective_connection(
        context["account"]["account_id"]
    )
    contract["external_ai_provider_registered"] = connection is not None
    return {"ok": True, "contract": contract}


@app.get("/external-core/settings")
def list_external_core_settings(request: Request):
    _researcher_session(request)
    return {"ok": True, "revisions": external_core_service.list_settings()}


@app.get("/external-core/settings/effective")
def get_effective_external_core_settings(
    request: Request,
    role: str,
    domain_id: str | None = None,
    project_id: str | None = None,
    session_id: str | None = None,
):
    _researcher_session(request)
    try:
        return {
            "ok": True,
            "settings": external_core_service.effective(
                role=role,
                domain_id=domain_id,
                project_id=project_id,
                session_id=session_id,
            ),
        }
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.post("/external-core/settings/drafts")
def create_external_core_settings_draft(
    data: ExternalCoreSettingsDraftInput,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    try:
        payload = data.model_dump(exclude_none=True) if hasattr(
            data, "model_dump"
        ) else data.dict(exclude_none=True)
        payload["created_by"] = context["account"]["account_id"]
        return {
            "ok": True,
            "revision": external_core_service.create_draft(payload),
        }
    except (ValueError, PermissionError, KeyError, TypeError) as exc:
        _raise_ray_colleague_http(exc)


@app.post(
    "/external-core/settings/{settings_id}/{revision}/transition/{target}"
)
def transition_external_core_settings(
    settings_id: str,
    revision: int,
    target: str,
    data: ExternalCoreTransitionInput,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    try:
        item = external_core_service.settings.transition(
            settings_id,
            revision,
            SettingsStatus(target),
            actor_id=context["account"]["account_id"],
        )
        return {"ok": True, "revision": item}
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.delete("/external-core/settings/{settings_id}/{revision}")
def delete_external_core_settings_draft(
    settings_id: str,
    revision: int,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    try:
        external_core_service.settings.delete_draft(
            settings_id,
            revision,
            actor_id=context["account"]["account_id"],
        )
        return {"ok": True, "status": "draft_deleted"}
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.get("/external-core/domains")
def list_external_core_domains(request: Request):
    _researcher_session(request)
    return {"ok": True, "domains": external_core_service.domains.list_all()}


@app.post("/external-core/domains/{domain_id}/transition/{target}")
def transition_external_core_domain(
    domain_id: str,
    target: str,
    data: ExternalCoreTransitionInput,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    try:
        item = external_core_service.domains.transition(
            domain_id,
            DomainLifecycle(target),
            actor_id=context["account"]["account_id"],
        )
        return {"ok": True, "domain": item}
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.post("/ray-colleague/researcher/respond")
def ray_colleague_researcher_respond(
    data: RayColleagueResearcherInput,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    try:
        response = ray_colleague_service.respond(
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id=context["account"]["account_id"],
            page_id=data.page_id,
            language=data.lang,
            message=data.message,
            project_id=data.project_id,
            study_id=data.study_id,
            entity_refs=data.entity_refs,
            selection=data.selection,
            requested_action=data.requested_action,
        )
        return {"ok": True, "response": response}
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.get("/external-ai/contract")
def get_external_ai_contract(request: Request):
    context = _researcher_session(request)
    account_id = context["account"]["account_id"]
    return {
        "ok": True,
        "contract": external_ai_gateway.contract(
            account_id=account_id,
            can_manage_platform=_platform_external_ai_admin(account_id),
        ),
    }


@app.post("/external-ai/providers/models")
def discover_external_ai_models(
    data: ExternalAIModelDiscoveryInput,
    request: Request,
):
    _researcher_session(request, require_csrf=True)
    try:
        return {
            "ok": True,
            "models": external_ai_gateway.list_models(
                data.provider_id,
                data.credential.get_secret_value(),
            ),
        }
    except ExternalAIError as exc:
        _raise_external_ai_http(exc)


@app.get("/external-ai/connections")
def list_external_ai_connections(request: Request):
    context = _researcher_session(request)
    return {
        "ok": True,
        **external_ai_gateway.list_connections(
            context["account"]["account_id"]
        ),
    }


@app.post("/external-ai/connections")
def create_external_ai_connection(
    data: ExternalAIConnectionInput,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    account_id = context["account"]["account_id"]
    try:
        connection = external_ai_gateway.connect(
            actor_account_id=account_id,
            scope=ConnectionScope(data.scope),
            provider_id=data.provider_id,
            model=data.model,
            credential=data.credential.get_secret_value(),
            can_manage_platform=_platform_external_ai_admin(account_id),
        )
        return {"ok": True, "connection": connection}
    except ValueError as exc:
        _raise_external_ai_http(
            ExternalAIError(str(exc), status_code=422)
        )
    except ExternalAIError as exc:
        _raise_external_ai_http(exc)


@app.delete("/external-ai/connections/{connection_id}")
def delete_external_ai_connection(
    connection_id: str,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    account_id = context["account"]["account_id"]
    try:
        external_ai_gateway.delete_connection(
            connection_id,
            actor_account_id=account_id,
            can_manage_platform=_platform_external_ai_admin(account_id),
        )
        return {"ok": True, "status": "connection_deleted"}
    except ExternalAIError as exc:
        _raise_external_ai_http(exc)


@app.get("/external-ai/policies")
def get_external_ai_policies(request: Request):
    context = _researcher_session(request)
    return {
        "ok": True,
        **external_ai_gateway.get_policies(
            context["account"]["account_id"]
        ),
    }


@app.put("/external-ai/policies")
def update_external_ai_policy(
    data: ExternalAIPolicyInput,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    account_id = context["account"]["account_id"]
    try:
        policy = external_ai_gateway.save_policy(
            actor_account_id=account_id,
            scope=ConnectionScope(data.scope),
            profile_id=data.profile_id,
            enabled=data.enabled,
            never_send_categories=data.never_send_categories,
            never_send_terms=data.never_send_terms,
            can_manage_platform=_platform_external_ai_admin(account_id),
        )
        return {"ok": True, "policy": policy}
    except ValueError as exc:
        _raise_external_ai_http(
            ExternalAIError(str(exc), status_code=422)
        )
    except ExternalAIError as exc:
        _raise_external_ai_http(exc)


@app.post("/ray-colleague/participant/respond")
def ray_colleague_participant_respond(
    data: RayColleagueParticipantInput,
):
    try:
        session = pilot_service.get_session(data.session_id)
        if session.participant_id != data.participant_id:
            raise PermissionError("PARTICIPANT_SESSION_OWNERSHIP_MISMATCH")
        response = ray_colleague_service.respond(
            role=RayRole.PARTICIPANT_GUIDE,
            owner_id=data.participant_id,
            page_id=data.page_id,
            language=data.lang,
            message=data.message,
            session_id=data.session_id,
            study_id=data.study_id,
            entity_refs=data.entity_refs,
            selection=data.selection,
        )
        return {"ok": True, "response": response}
    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        ) from exc
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.post("/ray-colleague/researcher/memory")
def create_ray_researcher_memory(
    data: RayColleagueMemoryInput,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    try:
        record = ray_colleague_service.remember(
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id=context["account"]["account_id"],
            scope=data.scope,
            summary=data.summary,
            provenance=data.provenance,
            retention_reason=data.retention_reason,
            project_id=data.project_id,
            session_id=data.session_id,
            expires_at=data.expires_at,
        )
        return {"ok": True, "record": record}
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.post("/ray-colleague/participant/memory")
def create_ray_participant_memory(
    data: RayColleagueMemoryInput,
):
    try:
        record = ray_colleague_service.remember(
            role=RayRole.PARTICIPANT_GUIDE,
            owner_id=data.owner_id,
            scope=data.scope,
            summary=data.summary,
            provenance=data.provenance,
            retention_reason=data.retention_reason,
            project_id=data.project_id,
            session_id=data.session_id,
            expires_at=data.expires_at,
        )
        return {"ok": True, "record": record}
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.get("/ray-colleague/researcher/memory/{researcher_id}")
def list_ray_researcher_memory(
    researcher_id: str,
    request: Request,
    project_id: str | None = None,
):
    context = _researcher_session(request)
    return {
        "ok": True,
        "records": ray_colleague_service.memory.list_for_owner(
            RayRole.RESEARCH_COLLEAGUE,
            context["account"]["account_id"],
            project_id=project_id,
        ),
    }


@app.get("/ray-colleague/participant/memory/{participant_id}")
def list_ray_participant_memory(
    participant_id: str,
    session_id: str,
):
    return {
        "ok": True,
        "records": ray_colleague_service.memory.list_for_owner(
            RayRole.PARTICIPANT_GUIDE,
            participant_id,
            session_id=session_id,
        ),
    }


@app.delete("/ray-colleague/researcher/memory/{record_id}")
def delete_ray_researcher_memory(
    record_id: str,
    researcher_id: str,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    try:
        record = ray_colleague_service.memory.delete(
            RayRole.RESEARCH_COLLEAGUE,
            context["account"]["account_id"],
            record_id,
        )
        return {"ok": True, "record": record}
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.delete("/ray-colleague/participant/memory/{record_id}")
def delete_ray_participant_memory(
    record_id: str,
    participant_id: str,
):
    try:
        record = ray_colleague_service.memory.delete(
            RayRole.PARTICIPANT_GUIDE,
            participant_id,
            record_id,
        )
        return {"ok": True, "record": record}
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.post("/ray-colleague/feedback")
def submit_ray_colleague_feedback(
    data: RayColleagueFeedbackInput,
):
    try:
        candidate = ray_colleague_service.submit_feedback(
            role=RayRole(data.role),
            submitted_by=data.submitted_by,
            target_type=data.target_type,
            target_id=data.target_id,
            feedback=data.feedback,
            expected_behavior=data.expected_behavior,
            context_scope=data.context_scope,
            contains_participant_data=data.contains_participant_data,
        )
        return {"ok": True, "candidate": candidate}
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.post("/ray-colleague/researcher/actions/{action_id}/confirm")
def confirm_ray_researcher_action(
    action_id: str,
    data: RayActionConfirmationInput,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    try:
        action = ray_colleague_service.confirm_action(
            action_id,
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id=context["account"]["account_id"],
        )
        return {"ok": True, "action": action}
    except (ValueError, PermissionError, KeyError) as exc:
        _raise_ray_colleague_http(exc)


@app.post("/ray/start")
def ray_start(data: RayStartInput):
    try:
        session = pilot_service.create_session(
            participant_id=data.participant_id,
        )

        messages = {
            "ru": (
                "Привет. Я Рэй. Давай начнём спокойно.\n\n"
                "Первый вопрос: есть ли у тебя сейчас работа, учёба "
                "или другая основная деятельность?\n\n"
                "Ответь числом: 0 — нет, 1 — да."
            ),
            "en": (
                "Hi. I’m Ray. Let’s start calmly.\n\n"
                "First question: do you currently have work, studies, "
                "or another main activity?\n\n"
                "Answer with a number: 0 — no, 1 — yes."
            ),
            "es": (
                "Hola. Soy Ray. Empecemos con calma.\n\n"
                "Primera pregunta: ¿actualmente tienes trabajo, estudios "
                "u otra actividad principal?\n\n"
                "Responde con un número: 0 — no, 1 — sí."
            ),
        }

        return {
            "ok": True,
            "session_id": session.session_id,
            "lang": data.lang,
            "ray": {
                "status": "question",
                "message": messages.get(data.lang, messages["ru"]),
                "awaiting_variable_code": "d0",
                "expected_response_target": "answers.d0",
            },
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/ray/chat/{session_id}")
def ray_global_chat(
    session_id: str,
    data: RayChatInput,
):
    try:
        session = pilot_service.get_session(session_id)
        value = parse_numeric_reply(data.message)

        if value is None:
            return {
                "ok": True,
                "session_id": session.session_id,
                "lang": data.lang,
                "ray": {
                    "status": "clarify_answer",
                    "message": (
                        "Я сейчас жду числовой ответ на текущий вопрос. "
                        "Пожалуйста, ответь числом."
                    ),
                },
            }

        if session.status.value == "CREATED":
            pilot_service.submit_answers(
                session_id=session_id,
                answers={"d0": value},
            )
            session = pilot_service.run_session(session_id)

        else:
            current_question = build_ray_next_question(
                session=session,
                lang=data.lang,
            )

            if current_question.get("status") == "question":
                variable_code = current_question.get("variable_code")

                pilot_service.submit_followup_answers(
                    session_id=session_id,
                    answers={variable_code: value},
                )

                session = pilot_service.run_session(session_id)

        return {
            "ok": True,
            "session_id": session.session_id,
            "lang": data.lang,
            "ray": build_ray_chat_response(
                session=session,
                message=data.message,
                lang=data.lang,
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/run")
def run_engine(data: RunInput):
    result = run_engine_logic(data.answers)

    return {
        "ok": True,
        "result": result,
    }

@app.post("/research/health-model/v61/run")
def run_health_model_v61(data: HealthModelV61RunInput):
    result = calculate_health_model_v61(data.answers)

    return {
        "ok": True,
        "model": result,
    }

@app.post("/pilot/sessions")
def create_pilot_session(participant_id: str):
    try:
        session = pilot_service.create_session(
            participant_id=participant_id,
        )

        return {
            "ok": True,
            "session_id": session.session_id,
            "status": session.status.value,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.get("/pilot/sessions/{session_id}")
def get_pilot_session(session_id: str):
    try:
        session = pilot_service.get_session(session_id)

        return {
            "ok": True,
            "session_id": session.session_id,
            "participant_id": session.participant_id,
            "status": session.status.value,
            "invalidated": session.invalidated,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/pilot/sessions/{session_id}/research-answers")
def get_pilot_session_research_answers(session_id: str):
    try:
        session = pilot_service.get_session(session_id)

        return {
            "ok": True,
            "session_id": session.session_id,
            "answers_count": len(session.answers or {}),
            "questionnaire_submissions_count": len(
                session.questionnaire_submissions or []
            ),
            "research_answer_records_count": len(
                session.research_answer_records or []
            ),
            "questionnaire_submissions": (
                session.questionnaire_submissions or []
            ),
            "research_answer_records": (
                session.research_answer_records or []
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/pilot/sessions/{session_id}/result")
def get_pilot_session_result(session_id: str):
    try:
        session = pilot_service.get_session(session_id)

        return {
            "ok": True,
            "session_id": session.session_id,
            "status": session.status.value,
            "result_available": bool(session.public_output),
            "public_output": session.public_output,
            "uncertainty": session.uncertainty_snapshot or {},
            "next_questions": session.next_question_snapshots or [],
            "result_is_public_safe": True,
            "raw_engine_result_included": False,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/pilot/sessions/{session_id}/participant-report")
def get_pilot_participant_report(session_id: str):
    try:
        session = pilot_service.get_session(session_id)

        record = {
            "record_id": session.session_id,
            "session_id": session.session_id,
            "study_id": session.study_id,
            "result": session.raw_engine_result or {},
        }

        level_map_record = analyze_record_level_maps(record)

        analysis = {
            "analysis_type": "health_model_current_session_participant_analysis",
            "analysis_scope": "single_session",
            "study_id": session.study_id,
            "record_count": 1,
            "level_maps": {
                "analysis_type": "resource_level_maps_single_session",
                "record_count": 1,
                "interpreted_record_count": (
                    1 if level_map_record.get("interpreted_domains") else 0
                ),
                "records": [level_map_record],
            },
        }

        report = build_participant_report(analysis)

        return {
            "ok": True,
            "session_id": session.session_id,
            "participant_report": report,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/pilot/sessions/{session_id}/participant-export")
def participant_export_pilot_session(session_id: str):
    try:
        export_data = pilot_service.generate_participant_export(
            session_id
        )

        return {
            "ok": True,
            "export": export_data,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.post("/research/objects")
def create_research_object_api(payload: ResearchObjectPayload, request: Request):
    owner = payload.owner
    authorship = None
    raw_session = request.cookies.get(SESSION_COOKIE_NAME)
    if raw_session:
        context = _researcher_session(request, require_csrf=True)
        owner = context["account"]["account_id"]
        author = researcher_account_service.authorship_snapshot(owner)
        authorship = {
            "schema_version": "research-object-authorship-1",
            "contributions": [{
                "author_identity_id": author["author_identity_id"],
                "display_name": author["display_name"],
                "roles": ["creator"],
                "recorded_at": datetime.now(UTC).isoformat(),
            }],
            "preservation_policy": "authorship_survives_account_deletion",
        }
    obj = create_research_object(
        object_type=payload.object_type,
        owner=owner,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        variables=payload.variables,
        analysis_methods=payload.analysis_methods,
        research_question=payload.research_question,
        hypothesis_basis=payload.hypothesis_basis,
        basis_notes=payload.basis_notes,
        authorship=authorship,
    )

    return {
        "ok": True,
        "object": obj,
    }


@app.get("/research/objects")
def list_research_objects_api(owner: str | None = None, object_type: str | None = None):
    return {
        "ok": True,
        "objects": list_research_objects(
            owner=owner,
            object_type=object_type,
        ),
    }


@app.get("/research/citations/contract")
def research_citation_contract():
    return {"ok": True, "contract": citation_contract()}


@app.post("/research/citations/preview")
def preview_research_citations(payload: CitationCollectionInput):
    try:
        return {"ok": True, "collection": build_citation_collection(
            title=payload.title, destination=payload.destination,
            style=payload.style, requirements_source=payload.requirements_source,
            references=payload.references,
        )}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/research/citations")
def save_research_citations(payload: CitationCollectionInput, request: Request):
    context = _researcher_session(request, require_csrf=True)
    account_id = context["account"]["account_id"]
    try:
        collection = build_citation_collection(
            title=payload.title, destination=payload.destination,
            style=payload.style, requirements_source=payload.requirements_source,
            references=payload.references,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    obj = create_research_object(
        object_type="citation_collection", owner=account_id,
        title=payload.title or "Bibliography", status="draft",
        authorship=_project_authorship(account_id),
        scientific_definition=collection,
        provenance_links=[item.get("registered_source_ref") for item in collection["references"] if item.get("registered_source_ref")],
    )
    project = None
    if payload.project_id or payload.block_id:
        if not payload.project_id or not payload.block_id:
            raise HTTPException(status_code=422, detail="PROJECT_AND_BLOCK_IDS_REQUIRED_TOGETHER")
        try:
            project = connect_project_entity(
                payload.project_id, account_id, payload.block_id,
                field_code="bibliography_versions",
                entity={"entity_type": "citation_collection", "registry_id": obj["id"],
                        "version": collection["version"], "status": obj["status"],
                        "display_name": obj["title"], "source_schema_version": collection["schema_version"],
                        "source_route": "/citation-workspace"},
            )
        except ProjectWorkspaceError as exc:
            _raise_project_workspace_http(exc)
    return {"ok": True, "object": obj, "collection": collection, "project": project}


@app.get("/research/hypotheses/contract")
def research_hypothesis_contract():
    return {"ok": True, "contract": hypothesis_contract()}


@app.get("/research/sensor-hypotheses/contract")
def research_sensor_hypothesis_contract():
    return {"ok": True, "contract": sensor_hypothesis_contract()}


@app.get("/research/qualitative-hypotheses/contract")
def research_qualitative_hypothesis_contract():
    return {"ok": True, "contract": qualitative_hypothesis_contract()}


@app.post("/research/qualitative-hypotheses/methods")
def research_qualitative_hypothesis_methods(payload: QualitativeMethodCompatibilityInput):
    try:
        methods = compatible_qualitative_methods(payload.inquiry_mode, payload.empirical_entity_types)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"ok": True, "methods": methods}


@app.post("/research/qualitative-hypotheses/validate")
def validate_research_qualitative_hypothesis(payload: QualitativeHypothesisPlanInput):
    try:
        plan = build_qualitative_hypothesis_plan(payload.plan)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"ok": True, "plan": plan}


@app.post("/research/qualitative-hypothesis-results")
def save_research_qualitative_hypothesis_result(payload: QualitativeHypothesisResultInput, request: Request):
    context = _researcher_session(request, require_csrf=True)
    owner = context["account"]["account_id"]
    try:
        result = build_qualitative_hypothesis_result(payload.result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not result["validation"]["valid"]:
        raise HTTPException(status_code=422, detail={"error": "QUALITATIVE_RESULT_INCOMPLETE", "validation": result["validation"]})
    obj = create_research_object(
        object_type="hypothesis_result", owner=owner,
        title=f"Hypothesis result: {result['hypothesis_ref']}", status="draft",
        description=result["plain_language_conclusion"],
        authorship=_project_authorship(owner), scientific_definition=result,
        provenance_links=[result["hypothesis_ref"]] + [str(x) for x in result["evidence_links"]],
    )
    project = None
    if payload.project_id:
        try:
            current_project = get_modular_research_project(payload.project_id, owner)
            result_block_id = next((item["block_id"] for item in current_project.get("blocks", [])
                                    if item.get("block_type") == "results" and item.get("lifecycle") == "connected"), None)
            if result_block_id is None:
                current_project = connect_project_block(payload.project_id, owner, "results")
                result_block_id = current_project["active_block_id"]
            project = connect_project_entity(
                payload.project_id, owner, result_block_id, field_code="result_links",
                entity={"entity_type": "hypothesis_result", "registry_id": obj["id"],
                        "version": 1, "status": obj["status"], "display_name": obj["title"],
                        "source_schema_version": result["schema_version"], "source_route": "/research-lab"},
            )
        except ProjectWorkspaceError as exc:
            _raise_project_workspace_http(exc)
    return {"ok": True, "object": obj, "result": result, "project": project}


@app.post("/research/sensor-hypotheses/methods")
def research_sensor_hypothesis_methods(payload: SensorMethodCompatibilityInput):
    try:
        methods = compatible_sensor_methods(
            validation_aim=payload.validation_aim,
            outcome_data_kind=payload.outcome_data_kind,
            repeated_measurements=payload.repeated_measurements,
            has_reference=payload.has_reference,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"ok": True, "methods": methods}


@app.post("/research/sensor-hypotheses/validate")
def validate_research_sensor_hypothesis(payload: SensorValidationPlanInput):
    try:
        plan = build_sensor_validation_plan(payload.plan)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"ok": True, "plan": plan}


@app.get("/research/hypotheses")
def list_research_hypotheses(request: Request):
    context = _researcher_session(request)
    owner = context["account"]["account_id"]
    return {"ok": True, "hypotheses": list_research_objects(owner=owner, object_type="hypothesis")}


@app.post("/research/hypotheses")
def save_research_hypothesis(payload: HypothesisDefinitionInput, request: Request):
    context = _researcher_session(request, require_csrf=True)
    owner = context["account"]["account_id"]
    try:
        definition = build_hypothesis_definition(payload.definition)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not definition["title"]:
        raise HTTPException(status_code=422, detail="HYPOTHESIS_TITLE_REQUIRED")
    if definition["status"] != "draft" and not definition["readiness"]["valid_for_status"]:
        raise HTTPException(
            status_code=422,
            detail={"error": "HYPOTHESIS_NOT_READY_FOR_STATUS", "readiness": definition["readiness"]},
        )
    obj = create_research_object(
        object_type="hypothesis", owner=owner, title=definition["title"],
        description=definition["formal_statement"], status=definition["status"],
        variables=definition["variables"], analysis_methods=definition["planned_analysis"],
        hypothesis_basis="; ".join(item["title"] for item in definition["basis_items"] if item["title"]),
        authorship=_project_authorship(owner), scientific_definition=definition,
        provenance_links=[item["registered_ref"] for item in definition["basis_items"] if item["registered_ref"]],
    )
    project = None
    project_id, block_id = payload.project_id, payload.block_id
    if block_id and not project_id:
        raise HTTPException(status_code=422, detail="PROJECT_ID_REQUIRED_WITH_BLOCK_ID")
    if project_id and not block_id:
        try:
            current_project = get_modular_research_project(project_id, owner)
            block_id = next((item["block_id"] for item in current_project.get("blocks", [])
                             if item.get("block_type") == "hypotheses" and item.get("lifecycle") == "connected"), None)
            if block_id is None:
                current_project = connect_project_block(project_id, owner, "hypotheses")
                block_id = current_project["active_block_id"]
        except ProjectWorkspaceError as exc:
            _raise_project_workspace_http(exc)
    if project_id and block_id:
        try:
            project = connect_project_entity(
                project_id, owner, block_id,
                field_code="hypothesis_versions",
                entity={"entity_type": "hypothesis", "registry_id": obj["id"],
                        "version": 1, "status": obj["status"], "display_name": obj["title"],
                        "source_schema_version": definition["schema_version"], "source_route": "/research-lab"},
            )
        except ProjectWorkspaceError as exc:
            _raise_project_workspace_http(exc)
    return {"ok": True, "object": obj, "definition": definition, "project": project}


def _raise_project_workspace_http(exc: ProjectWorkspaceError):
    raise HTTPException(status_code=exc.status_code, detail=exc.code)


def _project_authorship(account_id: str) -> dict[str, Any]:
    author = researcher_account_service.authorship_snapshot(account_id)
    return {
        "schema_version": "research-object-authorship-1",
        "contributions": [{
            "author_identity_id": author["author_identity_id"],
            "display_name": author["display_name"],
            "roles": ["creator", "scientific_author"],
            "recorded_at": datetime.now(UTC).isoformat(),
        }],
        "preservation_policy": "authorship_survives_account_deletion",
    }


@app.get("/research/projects/block-catalog")
def research_project_block_catalog(request: Request, language: str = "ru"):
    context = _researcher_session(request)
    try:
        return {
            "ok": True,
            "catalog": project_block_catalog(
                language, context["account"].get("research_profiles") or []
            ),
        }
    except ProjectWorkspaceError as exc:
        _raise_project_workspace_http(exc)


@app.get("/research/model-training/contract")
def research_model_training_contract(request: Request, language: str = "ru"):
    _researcher_session(request)
    try:
        return {"ok": True, "contract": model_training_contract(language)}
    except ModelTrainingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.code) from exc


@app.post("/research/model-training/notebook")
def create_model_training_notebook(data: ModelTrainingNotebookInput, request: Request):
    context = _researcher_session(request, require_csrf=True)
    payload = data.model_dump(exclude_none=True) if hasattr(data, "model_dump") else data.dict(exclude_none=True)
    try:
        author = researcher_account_service.authorship_snapshot(context["account"]["account_id"])
        notebook = build_colab_notebook(payload, author=author)
    except ModelTrainingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.code) from exc
    run_id = notebook["metadata"]["health_model_training"]["run_id"]
    return Response(
        content=json.dumps(notebook, ensure_ascii=False, separators=(",", ":")),
        media_type="application/x-ipynb+json",
        headers={"Content-Disposition": f'attachment; filename="health_model_training_{run_id}.ipynb"'},
    )


def _raise_fiji_http(exc: FijiIntegrationError):
    raise HTTPException(status_code=exc.status_code, detail=exc.code)


@app.get("/research/fiji/contract")
def research_fiji_contract(request: Request, language: str = "ru"):
    _researcher_session(request)
    return {"ok": True, "contract": fiji_integration_contract(language)}


@app.get("/research/fiji/installations")
def research_fiji_installations(request: Request):
    _researcher_session(request)
    return {"ok": True, "result": discover_fiji_installations()}


@app.post("/research/fiji/installations/configure")
def research_fiji_configure_installation(data: FijiInstallationInput, request: Request):
    _researcher_session(request, require_csrf=True)
    try:
        return {"ok": True, "installation": configure_fiji_installation(data.path)}
    except FijiIntegrationError as exc:
        _raise_fiji_http(exc)


@app.post("/research/fiji/launch")
def research_fiji_launch(request: Request):
    _researcher_session(request, require_csrf=True)
    try:
        return {"ok": True, "result": launch_fiji()}
    except FijiIntegrationError as exc:
        _raise_fiji_http(exc)


@app.post("/research/fiji/bridge/install")
def research_fiji_install_bridge(request: Request):
    _researcher_session(request, require_csrf=True)
    try:
        callback_base = f"{request.url.scheme}://{request.url.netloc}"
        return {"ok": True, "bridge": install_fiji_bridge(callback_base)}
    except FijiIntegrationError as exc:
        _raise_fiji_http(exc)


@app.delete("/research/fiji/bridge")
def research_fiji_remove_bridge(request: Request):
    _researcher_session(request, require_csrf=True)
    try:
        return {"ok": True, "bridge": remove_fiji_bridge()}
    except FijiIntegrationError as exc:
        _raise_fiji_http(exc)


@app.get("/research/fiji/bridge/status")
def research_fiji_bridge_status(request: Request, limit: int = 25):
    _researcher_session(request)
    return {"ok": True, "bridge": fiji_bridge_status(limit)}


@app.post("/research/fiji/bridge/events")
def research_fiji_bridge_event(payload: dict[str, Any], request: Request):
    try:
        event = record_fiji_bridge_event(request.headers.get("Authorization"), payload)
        return {"ok": True, "event_id": event["event_id"]}
    except FijiIntegrationError as exc:
        _raise_fiji_http(exc)


@app.post("/research/fiji/pipelines/validate")
def research_fiji_validate_pipeline(data: FijiPipelineInput, request: Request):
    _researcher_session(request, require_csrf=True)
    try:
        payload = data.model_dump(exclude_none=True) if hasattr(data, "model_dump") else data.dict(exclude_none=True)
        return {"ok": True, "pipeline": validate_fiji_pipeline(payload)}
    except FijiIntegrationError as exc:
        _raise_fiji_http(exc)


@app.post("/research/fiji/pipelines/execute")
def research_fiji_execute_pipeline(data: FijiPipelineInput, request: Request):
    context = _researcher_session(request, require_csrf=True)
    try:
        payload = data.model_dump(exclude_none=True) if hasattr(data, "model_dump") else data.dict(exclude_none=True)
        author = researcher_account_service.authorship_snapshot(context["account"]["account_id"])
        run = execute_fiji_pipeline(
            payload,
            actor_id=context["account"]["account_id"],
            authorship={
                **author,
                "preservation_policy": "authorship_survives_account_deletion",
            },
        )
        return {"ok": True, "run": run}
    except FijiIntegrationError as exc:
        _raise_fiji_http(exc)


@app.get("/research/fiji/runs/{run_id}")
def research_fiji_run(run_id: str, request: Request):
    _researcher_session(request)
    try:
        return {"ok": True, "run": get_fiji_run(run_id)}
    except FijiIntegrationError as exc:
        _raise_fiji_http(exc)


@app.get("/research/projects")
def research_projects(request: Request):
    context = _researcher_session(request)
    return {
        "ok": True,
        "projects": list_modular_research_projects(context["account"]["account_id"]),
    }


@app.post("/research/projects")
def create_research_project(data: ResearchProjectCreateInput, request: Request):
    context = _researcher_session(request, require_csrf=True)
    account_id = context["account"]["account_id"]
    try:
        project = create_modular_research_project(
            owner=account_id,
            authorship=_project_authorship(account_id),
            title=data.title,
            research_question=data.research_question,
            goal=data.goal,
            language=data.language,
            display_timezone=data.display_timezone,
        )
        return {"ok": True, "project": project}
    except ProjectWorkspaceError as exc:
        _raise_project_workspace_http(exc)


@app.get("/research/projects/{project_id}")
def research_project(project_id: str, request: Request):
    context = _researcher_session(request)
    try:
        return {
            "ok": True,
            "project": get_modular_research_project(
                project_id, context["account"]["account_id"]
            ),
        }
    except ProjectWorkspaceError as exc:
        _raise_project_workspace_http(exc)


@app.patch("/research/projects/{project_id}")
def update_research_project(
    project_id: str, data: ResearchProjectUpdateInput, request: Request
):
    context = _researcher_session(request, require_csrf=True)
    try:
        return {
            "ok": True,
            "project": update_modular_research_project(
                project_id, context["account"]["account_id"], data.changes
            ),
        }
    except ProjectWorkspaceError as exc:
        _raise_project_workspace_http(exc)


@app.post("/research/projects/{project_id}/blocks")
def connect_research_project_block(
    project_id: str, data: ResearchProjectBlockConnectInput, request: Request
):
    context = _researcher_session(request, require_csrf=True)
    try:
        return {
            "ok": True,
            "project": connect_project_block(
                project_id, context["account"]["account_id"], data.block_type
            ),
        }
    except ProjectWorkspaceError as exc:
        _raise_project_workspace_http(exc)


@app.patch("/research/projects/{project_id}/blocks/{block_id}")
def save_research_project_block(
    project_id: str,
    block_id: str,
    data: ResearchProjectBlockUpdateInput,
    request: Request,
):
    context = _researcher_session(request, require_csrf=True)
    try:
        return {
            "ok": True,
            "project": update_project_block(
                project_id,
                context["account"]["account_id"],
                block_id,
                data.content,
            ),
        }
    except ProjectWorkspaceError as exc:
        _raise_project_workspace_http(exc)


@app.post("/research/projects/{project_id}/blocks/{block_id}/disconnect")
def disconnect_research_project_block(
    project_id: str, block_id: str, request: Request
):
    context = _researcher_session(request, require_csrf=True)
    try:
        return {
            "ok": True,
            "project": disconnect_project_block(
                project_id, context["account"]["account_id"], block_id
            ),
        }
    except ProjectWorkspaceError as exc:
        _raise_project_workspace_http(exc)


def _localized_title(value: Any, language: str, fallback: str) -> str:
    if isinstance(value, dict):
        return str(value.get(language) or value.get("en") or value.get("ru") or value.get("es") or fallback)
    return str(value or fallback)


@app.get("/research/project-entity-catalog")
def research_project_entity_catalog(request: Request, language: str = "ru"):
    context = _researcher_session(request)
    if language not in {"ru", "en", "es"}:
        raise HTTPException(status_code=400, detail={"error": "UNSUPPORTED_CONTENT_LANGUAGE"})
    owner = context["account"]["account_id"]
    entities: list[dict[str, Any]] = []

    for bank in list_registered_question_banks():
        code = str(bank.get("bank_code") or bank.get("bank_id"))
        entities.append({
            "entity_type": "question_bank", "registry_id": code,
            "version": bank.get("definition_version", 1),
            "status": bank.get("development_status", "draft"),
            "display_name": _localized_title(bank.get("titles"), language, code),
            "source_schema_version": bank.get("schema_version"),
            "source_route": f"/question-editor?bank_id={code}",
        })
    for question in list_question_versions():
        translation = (question.get("translations") or {}).get(language) or {}
        code = str(question.get("question_code"))
        bank_id = str(question.get("bank_id"))
        entities.append({
            "entity_type": "question", "registry_id": f"{bank_id}:{code}",
            "version": question.get("question_version"),
            "status": question.get("development_status", "draft"),
            "display_name": str(translation.get("prompt") or code),
            "source_schema_version": question.get("schema_version"),
            "source_route": f"/question-editor?bank_id={bank_id}&question_code={code}",
        })
    # Include legacy registered banks/questions through the editor's normalized
    # compatibility catalog.  The project still binds an exact version and keeps
    # the original source schema; gradual migration does not make older banks unusable.
    normalized_question_catalog = list_question_editor_catalog(language)
    known_banks = {(item["registry_id"], str(item["version"])) for item in entities if item["entity_type"] == "question_bank"}
    for bank in normalized_question_catalog.get("banks", []):
        code = str(bank.get("id") or bank.get("bank_code"))
        version = bank.get("definition_version") or bank.get("version") or 1
        if (code, str(version)) in known_banks:
            continue
        entities.append({
            "entity_type": "question_bank", "registry_id": code, "version": version,
            "status": bank.get("status", "registered"), "display_name": str(bank.get("title") or code),
            "source_schema_version": bank.get("schema_version") or "legacy-question-bank-normalized-reference-1",
            "source_route": f"/question-editor?bank_id={code}",
        })
    known_questions = {(item["registry_id"], str(item["version"])) for item in entities if item["entity_type"] == "question"}
    for question in normalized_question_catalog.get("questions", []):
        bank_id, code = str(question.get("bank_id")), str(question.get("question_code"))
        registry_id = f"{bank_id}:{code}"
        version = question.get("question_version") or question.get("version") or 1
        if (registry_id, str(version)) in known_questions:
            continue
        entities.append({
            "entity_type": "question", "registry_id": registry_id, "version": version,
            "status": question.get("status", "registered"), "display_name": str(question.get("prompt") or code),
            "source_schema_version": question.get("reference_schema_version") or question.get("schema_version") or "legacy-question-normalized-reference-1",
            "source_route": f"/question-editor?bank_id={bank_id}&question_code={code}",
        })
    for parameter in list_registered_parameter_definitions(include_inactive=True, include_all_versions=True):
        enriched = enrich_model_entity(parameter)
        if enriched["entity_classification"]["entity_class"] != MODEL_PARAMETER:
            continue
        code = str(parameter.get("parameter_code"))
        entities.append({
            "entity_type": "model_parameter", "registry_id": code,
            "version": parameter.get("definition_version", 1),
            "status": parameter.get("development_status") or parameter.get("lifecycle_status") or parameter.get("status") or "draft",
            "display_name": _localized_title(parameter.get("name") or parameter.get("names") or parameter.get("title"), language, code),
            "source_schema_version": parameter.get("schema_version"),
            "source_route": f"/parameter-editor?parameter_code={code}",
        })
    for mechanism in list_registered_mechanism_definitions(include_inactive=True, include_all_versions=True):
        code = str(mechanism.get("mechanism_code"))
        entities.append({
            "entity_type": "mechanism", "registry_id": code,
            "version": mechanism.get("definition_version", 1),
            "status": mechanism.get("development_status") or mechanism.get("lifecycle_status") or mechanism.get("status") or "draft",
            "display_name": _localized_title(mechanism.get("name") or mechanism.get("names") or mechanism.get("title"), language, code),
            "source_schema_version": mechanism.get("schema_version"),
            "source_route": f"/mechanism-editor?mechanism_code={code}",
        })
    for method in list_probabilistic_methods(language).get("methods", []):
        method_id = str(method["method_id"])
        entities.append({
            "entity_type": "probabilistic_method", "registry_id": method_id,
            "version": 1, "status": method.get("execution_status", "registered"),
            "display_name": str(method.get("title") or method_id),
            "source_schema_version": "probabilistic-method-registry-1",
            "source_route": f"/probabilistic-methods?method_id={method_id}",
        })
    for method in METHODS:
        method_id = str(method["method_id"])
        entities.append({
            "entity_type": "analysis_method", "registry_id": method_id,
            "version": 1, "status": method.get("execution_status", "registered_without_runner"),
            "display_name": str(method.get("title") or method_id),
            "source_schema_version": "analysis-method-registry-1",
            "source_route": f"/analysis-builder?method_id={method_id}",
        })
    for instrument in list_connected_instruments():
        instrument_id = str(instrument.get("instrument_id"))
        connector = instrument.get("connector") or {}
        entities.append({
            "entity_type": "measurement_instrument", "registry_id": instrument_id,
            "version": instrument.get("revision", 1), "status": instrument.get("status", "connected"),
            "display_name": str(connector.get("title") or instrument_id),
            "source_schema_version": instrument.get("schema_version"),
            "source_route": "/measurement-setup",
            "time_contract": instrument.get("time_contract") or {"contract_version": "measurement-time-contract-1", "binding_status": "configured_at_measurement_session"},
        })
    for record in list_research_objects(owner=owner):
        object_type = str(record.get("object_type") or "")
        mapped = {
            "dataset": "measurement_dataset", "measurement_dataset": "measurement_dataset",
            "questionnaire_result": "questionnaire_result", "parameter_result": "parameter_result",
            "result": "analysis_result", "analysis_result": "analysis_result", "hypothesis_result": "hypothesis_result",
            "observable_marker": "observable_marker",
            "citation_collection": "citation_collection",
            "evidence_review": "evidence_review",
        }.get(object_type)
        if not mapped:
            continue
        entities.append({
            "entity_type": mapped, "registry_id": str(record.get("id")),
            "version": record.get("version", 1), "status": record.get("status", "draft"),
            "display_name": str(record.get("title") or record.get("id")),
            "source_schema_version": record.get("schema_version"),
            "source_route": (
                "/evidence-review" if mapped == "evidence_review"
                else "/citation-workspace" if mapped == "citation_collection"
                else "/data-preparation" if "result" not in mapped
                else "/scientific-results"
            ),
        })
    return {"ok": True, "schema_version": "research-project-entity-catalog-1", "language": language, "entities": entities}


def _evidence_review_catalog(request: Request, language: str) -> dict[str, Any]:
    if language not in {"ru", "en", "es"}:
        raise HTTPException(status_code=400, detail="UNSUPPORTED_CONTENT_LANGUAGE")
    entities = research_project_entity_catalog(request, language)["entities"]
    category_by_type = {
        "question_bank": "questionnaires", "question": "questions",
        "model_parameter": "model_parameters", "mechanism": "model_mechanisms",
        "measurement_instrument": "connected_instruments",
        "measurement_dataset": "registered_data", "questionnaire_result": "registered_data",
        "parameter_result": "registered_data", "analysis_result": "registered_results",
        "hypothesis_result": "registered_results", "observable_marker": "observable_markers",
        "analysis_method": "statistical_methods", "probabilistic_method": "probabilistic_methods",
        "citation_collection": "scientific_sources", "evidence_review": "previous_reviews",
    }
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(*, category: str, registry_id: str, title: str, version: Any = 1,
            status: str = "registered", source_route: str = "", details: dict[str, Any] | None = None) -> None:
        catalog_id = f"{category}:{registry_id}:v{version}"
        if catalog_id in seen:
            return
        seen.add(catalog_id)
        items.append({
            "catalog_id": catalog_id, "category": category,
            "registry_id": registry_id, "version": version, "title": title,
            "status": status, "source_route": source_route, "details": details or {},
        })

    for entity in entities:
        entity_type = str(entity.get("entity_type") or "")
        category = category_by_type.get(entity_type, "registered_objects")
        add(
            category=category, registry_id=str(entity.get("registry_id")),
            version=entity.get("version", 1), title=str(entity.get("display_name") or entity.get("registry_id")),
            status=str(entity.get("status") or "registered"), source_route=str(entity.get("source_route") or ""),
            details={"entity_type": entity_type, "schema_version": entity.get("source_schema_version")},
        )

    for method in qualitative_hypothesis_contract().get("analytic_approaches", []):
        add(
            category="qualitative_methods", registry_id=str(method["method_id"]),
            title=str(method.get("title") or method["method_id"]),
            status="registered_planning_method_requires_bound_material", source_route="/research-lab",
            details={"materials": method.get("materials", []), "modes": method.get("modes", [])},
        )
    for method in sensor_hypothesis_contract().get("methods", []):
        add(
            category="sensor_validation_methods", registry_id=str(method["method_id"]),
            title=str(method.get("title") or method["method_id"]),
            status=str(method.get("execution_status") or "registered_without_validated_runner"),
            source_route="/technical-hypothesis-lab",
            details={"aims": method.get("aims", []), "data_kinds": method.get("data_kinds", [])},
        )

    browser_sources = [
        ("camera", "Camera / video", "MediaDevices"),
        ("microphone", "Microphone / audio", "MediaDevices"),
        ("web_serial", "Web Serial sensor or device", "WebSerial"),
        ("web_usb", "WebUSB device", "WebUSB"),
        ("web_bluetooth", "Bluetooth device", "WebBluetooth"),
        ("geolocation", "Geolocation", "Geolocation"),
        ("measurement_file", "Measurement file", "FileAPI"),
        ("manual_measurement", "Manual registered measurement description", "manual_form"),
    ]
    for registry_id, title, capability in browser_sources:
        add(
            category="available_acquisition_methods", registry_id=registry_id,
            title=title, status="requires_explicit_researcher_selection_and_permission",
            source_route="/measurement-setup", details={"connection_method": capability},
        )
    return {
        "schema_version": "evidence-acquisition-catalog-1", "language": language,
        "selection_policy": "registered_choice_does_not_assert_scientific_compatibility_or_execution_readiness",
        "items": sorted(items, key=lambda item: (item["category"], item["title"].casefold(), item["catalog_id"])),
    }


@app.get("/research/evidence-review/contract")
def research_evidence_review_contract(request: Request, language: str = "ru"):
    _researcher_session(request)
    return {"ok": True, "contract": evidence_review_contract(), "catalog": _evidence_review_catalog(request, language)}


@app.get("/research/evidence-reviews")
def research_evidence_reviews(request: Request, review_id: str | None = None):
    context = _researcher_session(request)
    return {"ok": True, "reviews": list_evidence_reviews(context["account"]["account_id"], review_id=review_id)}


@app.post("/research/evidence-review/validate")
def validate_research_evidence_review(data: EvidenceReviewInput, request: Request):
    _researcher_session(request, require_csrf=True)
    catalog = _evidence_review_catalog(request, data.language)
    catalog_items_by_id = {item["catalog_id"]: item for item in catalog["items"]}
    try:
        plan = build_evidence_review_plan(
            data.plan, status=data.status,
            valid_catalog_ids=set(catalog_items_by_id),
            catalog_items_by_id=catalog_items_by_id,
        )
    except EvidenceReviewError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.code) from exc
    return {"ok": True, "plan": plan}


@app.post("/research/evidence-reviews")
def save_research_evidence_review_api(data: EvidenceReviewInput, request: Request):
    context = _researcher_session(request, require_csrf=True)
    owner = context["account"]["account_id"]
    catalog = _evidence_review_catalog(request, data.language)
    catalog_items_by_id = {item["catalog_id"]: item for item in catalog["items"]}
    try:
        plan = build_evidence_review_plan(
            data.plan, status=data.status,
            valid_catalog_ids=set(catalog_items_by_id),
            catalog_items_by_id=catalog_items_by_id,
        )
        record = save_evidence_review(
            owner=owner, authorship=_project_authorship(owner), status=data.status,
            language=data.language, plan=plan, project_id=data.project_id,
            block_id=data.block_id, review_id=data.review_id,
        )
        project = None
        if data.project_id and data.block_id:
            current = get_modular_research_project(data.project_id, owner)
            block = next((item for item in current.get("blocks", []) if item.get("block_id") == data.block_id), None)
            field_code = {"introduction": "source_notes", "scientific_context": "evidence_links"}.get((block or {}).get("block_type"))
            if field_code:
                project = connect_project_entity(
                    data.project_id, owner, data.block_id, field_code=field_code,
                    entity={
                        "entity_type": "evidence_review", "registry_id": record["review_id"],
                        "version": record["version"], "status": record["status"],
                        "display_name": record["title"], "source_schema_version": record["schema_version"],
                        "source_route": f"/evidence-review?review_id={record['review_id']}",
                    },
                )
    except (EvidenceReviewError, ProjectWorkspaceError) as exc:
        status_code = getattr(exc, "status_code", 422)
        code = getattr(exc, "code", str(exc))
        raise HTTPException(status_code=status_code, detail=code) from exc
    return {"ok": True, "review": record, "plan": plan, "project": project}


@app.post("/research/projects/{project_id}/blocks/{block_id}/entities")
def connect_research_project_entity(project_id: str, block_id: str, data: ResearchProjectEntityConnectInput, request: Request):
    context = _researcher_session(request, require_csrf=True)
    try:
        requested_type = str(data.entity.get("entity_type") or "")
        requested_id = str(data.entity.get("registry_id") or "")
        requested_version = data.entity.get("version")
        catalog = research_project_entity_catalog(
            request, context["account"].get("preferred_language") or "ru"
        )["entities"]
        canonical = next((item for item in catalog if item["entity_type"] == requested_type and item["registry_id"] == requested_id and str(item["version"]) == str(requested_version)), None)
        if canonical is None:
            raise ProjectWorkspaceError("PROJECT_ENTITY_NOT_FOUND_IN_REGISTERED_CATALOG", 404)
        return {"ok": True, "project": connect_project_entity(project_id, context["account"]["account_id"], block_id, field_code=data.field_code, entity=canonical)}
    except ProjectWorkspaceError as exc:
        _raise_project_workspace_http(exc)


@app.delete("/research/projects/{project_id}/blocks/{block_id}/entities/{link_id}")
def disconnect_research_project_entity(project_id: str, block_id: str, link_id: str, request: Request):
    context = _researcher_session(request, require_csrf=True)
    try:
        return {"ok": True, "project": disconnect_project_entity(project_id, context["account"]["account_id"], block_id, link_id)}
    except ProjectWorkspaceError as exc:
        _raise_project_workspace_http(exc)


@app.get("/research/probabilistic-methods")
def probabilistic_method_catalog(request: Request, language: str = "ru"):
    _researcher_session(request)
    try:
        return {"ok": True, "catalog": list_probabilistic_methods(language)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post("/research/probabilistic-methods/run")
def execute_probabilistic_method(data: ProbabilisticAnalysisRunInput, request: Request):
    context = _researcher_session(request, require_csrf=True)
    try:
        result = run_probabilistic_method(
            method_id=data.method_id,
            payload=data.payload,
            actor_account_id=context["account"]["account_id"],
            project_id=data.project_id,
            block_id=data.block_id,
        )
        return {"ok": True, "analysis": result}
    except ProbabilisticMethodError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.code)

@app.get("/pilot/sessions/{session_id}/research-export")
def research_export_pilot_session(session_id: str):
    try:
        export_data = pilot_service.generate_research_export(
            session_id
        )

        return {
            "ok": True,
            "export": export_data,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/research/analysis/run")
def run_research_analysis(study_id: str | None = None):
    result = run_health_model_research_analysis(
        study_id=study_id,
    )

    return {
        "ok": True,
        "analysis": result,
    }

def serialize_pilot_session_for_research(session):
    return {
        "record_id": session.session_id,
        "record_source": "pilot_session",
        "record_type": "pilot_session",
        "status": session.status.value,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "closed_at": (
            session.closed_at.isoformat()
            if session.closed_at is not None
            else None
        ),
        "session_id": session.session_id,
        "account_id": None,
        "participant_id": session.participant_id,
        "subject_link_id": session.subject_link_id,
        "study_id": session.study_id or "health_model",
        "language": None,
        "answers_count": len(session.answers or {}),
        "has_raw_engine_result": bool(session.raw_engine_result),
        "has_public_output": bool(session.public_output),
    }

@app.get("/research/answers/summary")
def summarize_research_answers(
    request: Request,
    question_code: str,
    study_id: str | None = None,
):
    _researcher_session(request)
    values = []

    for research_record in list_research_records(study_id=study_id):
        for answer_record in research_record.get("research_answer_records", []):
            if answer_record.get("question_code") != question_code:
                continue

            value = answer_record.get("answer_value")
            if isinstance(value, (int, float)):
                values.append(value)

    for session in store.list_all():
        if study_id is not None and session.study_id != study_id:
            continue

        for answer_record in session.research_answer_records or []:
            if answer_record.get("question_code") != question_code:
                continue

            value = answer_record.get("answer_value")
            if isinstance(value, (int, float)):
                values.append(value)

    return {
        "ok": True,
        "question_code": question_code,
        "study_id": study_id,
        "count": len(values),
        "values": values,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
        "mean": sum(values) / len(values) if values else None,
    }

@app.get("/research/answers")
def list_research_answers(
    request: Request,
    question_code: str | None = None,
    study_id: str | None = None,
):
    _researcher_session(request)
    records = []

    for research_record in list_research_records(study_id=study_id):
        for answer_record in research_record.get("research_answer_records", []):
            if question_code is not None and answer_record.get("question_code") != question_code:
                continue

            records.append({
                **answer_record,
                "record_source": "research_record",
                "parent_record_id": research_record.get("record_id"),
            })

    for session in store.list_all():
        if study_id is not None and session.study_id != study_id:
            continue

        for answer_record in session.research_answer_records or []:
            if question_code is not None and answer_record.get("question_code") != question_code:
                continue

            records.append({
                **answer_record,
                "record_source": "pilot_session",
                "parent_record_id": session.session_id,
            })

    return {
        "ok": True,
        "question_code": question_code,
        "study_id": study_id,
        "records_count": len(records),
        "records": records,
    }

@app.get("/research/participant-data/records")
def list_participant_data_records(request: Request, study_id: str | None = None):
    _researcher_session(request)
    research_records = list_research_records(study_id=study_id)

    research_items = [
        {
            "record_id": record.get("record_id"),
            "record_source": "research_record",
            "record_type": record.get("record_type"),
            "status": record.get("status"),
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
            "session_id": record.get("session_id"),
            "account_id": record.get("account_id"),
            "participant_id": None,
            "subject_link_id": None,
            "study_id": record.get("study_id"),
            "language": record.get("language"),
            "answers_count": len(record.get("answers", {}) or {}),
            "has_raw_engine_result": bool(record.get("result")),
            "has_public_output": bool(
                (record.get("result") or {}).get("summary")
            ),
        }
        for record in research_records
    ]

    pilot_sessions = store.list_all()

    pilot_items = [
        serialize_pilot_session_for_research(session)
        for session in pilot_sessions
    ]

    transformation_items = []
    for run in list_transformation_runs(study_id=study_id):
        result = run.get("result") or {}
        transformation_items.append({
            "record_id": run.get("run_id"),
            "record_source": "data_transformation_run",
            "record_type": result.get("source_type"),
            "status": "RUN_COMPLETED",
            "created_at": run.get("applied_at"),
            "updated_at": run.get("applied_at"),
            "session_id": None,
            "account_id": None,
            "participant_id": None,
            "subject_link_id": None,
            "study_id": run.get("study_id"),
            "study_ids": run.get("study_ids", []),
            "study_scope_status": run.get("study_scope_status"),
            "language": None,
            "answers_count": result.get("usable_count", 0),
            "has_raw_engine_result": False,
            "has_public_output": False,
        })

    all_items = research_items + pilot_items + transformation_items

    if study_id:
        all_items = [
            item for item in all_items
            if (
                item.get("study_id") == study_id
                or study_id in (item.get("study_ids") or [])
            )
        ]

    all_items = sorted(
        all_items,
        key=lambda item: item.get("created_at") or "",
        reverse=True,
    )

    return {
        "ok": True,
        "records": all_items,
    }


@app.get("/research/participant-data/records/{record_id}")
def get_participant_data_record(record_id: str, request: Request):
    _researcher_session(request)
    records = list_research_records()

    for record in records:
        if record.get("record_id") == record_id:
            return {
                "ok": True,
                "record_source": "research_record",
                "record": record,
            }

    session = pilot_service.get_session(record_id)

    if session is not None:
        raw_payload = {
            "payload_type": "questionnaire_answers",
            "study_id": session.study_id or "health_model",
            "answers": session.answers,
        }

        analysis_output = session.raw_engine_result or {}

        prepared_domain_output = build_prepared_domain_output(
            domain_data_identity=session.domain_data_identity or {},
            raw_payload=raw_payload,
            analysis_output=analysis_output,
        )

        return {
            "ok": True,
            "record_source": "pilot_session",
            "record": {
                **serialize_pilot_session_for_research(session),
                "domain_data_identity": session.domain_data_identity,
                "raw_payload": raw_payload,
                "prepared_domain_output": prepared_domain_output,
                "analysis_output": analysis_output,
                "answers": session.answers,
                "raw_engine_result": session.raw_engine_result,
                "public_output": session.public_output,
                "uncertainty_snapshot": session.uncertainty_snapshot,
                "next_question_snapshots": session.next_question_snapshots,
                "run_history": session.run_history,
            },
        }

    transformation_run = get_transformation_run(record_id)
    if transformation_run is not None:
        result = transformation_run.get("result") or {}
        return {
            "ok": True,
            "record_source": "data_transformation_run",
            "record": {
                "record_id": transformation_run.get("run_id"),
                "record_source": "data_transformation_run",
                "record_type": result.get("source_type"),
                "status": "RUN_COMPLETED",
                "created_at": transformation_run.get("applied_at"),
                "updated_at": transformation_run.get("applied_at"),
                "study_id": transformation_run.get("study_id"),
                "study_ids": transformation_run.get("study_ids", []),
                "study_scope_status": transformation_run.get("study_scope_status"),
                "answers_count": result.get("usable_count", 0),
                "prepared_observations": result.get("records", []),
                "transformation_run": transformation_run,
            },
        }

    raise HTTPException(status_code=404, detail="Record not found")


@app.get("/research/prepared-data/{run_id}/dataset")
def get_prepared_transformation_dataset(
    run_id: str,
    request: Request,
    analysis_scope: str,
    repeated_measure_policy: str = "reject_repeated",
    participant_reference: str | None = None,
    study_id: str | None = None,
):
    _researcher_session(request)
    return build_transformation_run_dataset(
        run_id=run_id,
        analysis_scope=analysis_scope,
        repeated_measure_policy=repeated_measure_policy,
        participant_reference=participant_reference,
        study_id=study_id,
    )


def _scientific_raw_result(record: dict) -> dict:
    snapshot = record.get("research_snapshot") or {}
    health_summary = (
        snapshot.get("health_model_research_model_summary") or {}
    )
    value = (
        record.get("raw_engine_result")
        or record.get("analysis_output")
        or record.get("result")
        or health_summary
        or {}
    )
    return value if isinstance(value, dict) else {}


def _scientific_health_summary(record: dict) -> dict:
    snapshot = record.get("research_snapshot") or {}
    raw = _scientific_raw_result(record)
    return (
        snapshot.get("health_model_research_model_summary")
        or raw.get("health_model_research_model_summary")
        or {}
    )


def _scientific_participant_reference(record: dict) -> str:
    snapshot = record.get("research_snapshot") or {}
    reference = snapshot.get("participant_reference") or {}
    source_session = snapshot.get("source_session") or {}
    identity = record.get("domain_data_identity") or {}
    if not isinstance(reference, dict):
        reference = {"participant_reference": reference}
    if not isinstance(source_session, dict):
        source_session = {}
    if not isinstance(identity, dict):
        identity = {}
    answer_records = record.get("research_answer_records") or []
    first_answer = answer_records[0] if answer_records else {}
    return str(
        record.get("participant_id")
        or identity.get("participant_id")
        or source_session.get("participant_id")
        or first_answer.get("participant_id")
        or record.get("account_id")
        or reference.get("participant_id")
        or reference.get("participant_reference")
        or reference.get("export_scoped_participant_reference")
        or ""
    )


def _scientific_parameter_records(record: dict) -> list[dict]:
    raw = _scientific_raw_result(record)
    summary = _scientific_health_summary(record)
    values = (
        summary.get("research_calculated_parameter_records")
        or raw.get("research_calculated_parameter_records")
        or record.get("research_calculated_parameter_records")
        or []
    )
    return [item for item in values if isinstance(item, dict)]


def _scientific_mapping_records(record: dict) -> list[dict]:
    raw = _scientific_raw_result(record)
    summary = _scientific_health_summary(record)
    values = (
        summary.get("question_parameter_mapping_records")
        or raw.get("question_parameter_mapping_records")
        or []
    )
    return [item for item in values if isinstance(item, dict)]


def _scientific_coverage(record: dict) -> dict:
    raw = _scientific_raw_result(record)
    summary = _scientific_health_summary(record)
    coverage = summary.get("coverage") or raw.get("coverage") or {}
    return coverage if isinstance(coverage, dict) else {}


def _scientific_full_records() -> list[dict]:
    records = [
        deepcopy(record)
        for record in list_research_records()
    ]
    for session in store.list_all():
        serialized = serialize_pilot_session_for_research(session)
        records.append({
            **serialized,
            "record_source": "pilot_session",
            "domain_data_identity": session.domain_data_identity,
            "analysis_output": session.raw_engine_result or {},
            "raw_engine_result": session.raw_engine_result,
            "public_output": session.public_output,
            "answers": session.answers,
            "research_answer_records": (
                session.research_answer_records or []
            ),
        })
    return records


def _scientific_parameter_view(
    parameter: dict,
    *,
    record: dict,
    participant_reference: str,
) -> dict:
    observation_time = (
        parameter.get("observation_time")
        or parameter.get("measured_at")
        or parameter.get("calculated_at")
        or record.get("updated_at")
        or record.get("created_at")
    )
    return {
        "parameter_code": parameter.get("parameter_code"),
        "title": (
            parameter.get("title")
            or parameter.get("parameter_title")
        ),
        "value": parameter.get(
            "parameter_value",
            parameter.get("value"),
        ),
        "value_type": (
            parameter.get("parameter_value_type")
            or parameter.get("value_type")
        ),
        "scale_type": parameter.get("scale_type"),
        "unit": parameter.get("unit"),
        "model_id": parameter.get("model_id"),
        "model_version": parameter.get("model_version"),
        "calculation_version": parameter.get("calculation_version"),
        "source_mode": parameter.get("source_mode"),
        "quality_status": (
            parameter.get("quality_status")
            or parameter.get("status")
        ),
        "uncertainty": parameter.get("uncertainty"),
        "observation_time": observation_time,
        "global_time_reference": (
            parameter.get("global_time_reference") or "UTC"
        ),
        "participant_reference": participant_reference,
        "record_id": record.get("record_id") or record.get("session_id"),
        "session_id": record.get("session_id"),
        "study_id": record.get("study_id"),
        "raw": parameter,
    }


def _scientific_record_view(record: dict) -> dict:
    raw = _scientific_raw_result(record)
    snapshot = record.get("research_snapshot") or {}
    source_session = snapshot.get("source_session") or {}
    participant_reference = _scientific_participant_reference(record)
    parameter_records = [
        _scientific_parameter_view(
            item,
            record=record,
            participant_reference=participant_reference,
        )
        for item in _scientific_parameter_records(record)
    ]
    coverage = _scientific_coverage(record)
    missing_critical = coverage.get("missing_critical_data") or []
    missing_required = coverage.get("missing_required_data") or []
    provided_inputs = coverage.get("provided_inputs") or []
    model_ids = sorted({
        str(item.get("model_id"))
        for item in parameter_records
        if item.get("model_id")
    })
    model_versions = sorted({
        str(item.get("model_version"))
        for item in parameter_records
        if item.get("model_version")
    })
    record_id = record.get("record_id") or record.get("session_id")
    observation_time = (
        record.get("updated_at")
        or source_session.get("updated_at")
        or record.get("created_at")
    )
    readiness = raw.get("readiness") or {}
    if not isinstance(readiness, dict):
        readiness = {"status": readiness}
    forecast = raw.get("forecast") or {}
    if not isinstance(forecast, dict):
        forecast = {}
    readiness_status = (
        raw.get("readiness_status")
        or readiness.get("status")
        or raw.get("state")
        or ""
    )
    forecast_allowed = raw.get("forecast_allowed")
    if forecast_allowed is None:
        forecast_allowed = forecast.get(
            "forecast_allowed"
        )
    if forecast_allowed is None:
        forecast_allowed = (
            snapshot.get("forecast_summary") or {}
        ).get("allowed")
    return {
        "record_id": record_id,
        "record_source": (
            record.get("record_source")
            or record.get("record_type")
        ),
        "study_id": (
            record.get("study_id")
            or source_session.get("study_id")
            or raw.get("study_id")
        ),
        "participant_reference": participant_reference,
        "session_id": (
            record.get("session_id")
            or source_session.get("session_id")
        ),
        "status": (
            record.get("status")
            or source_session.get("source_session_status")
        ),
        "readiness_status": readiness_status,
        "forecast_allowed": forecast_allowed,
        "observation_time": observation_time,
        "global_time_reference": "UTC",
        "language": record.get("language"),
        "model_ids": model_ids,
        "model_versions": model_versions,
        "parameter_count": len(parameter_records),
        "unique_parameter_count": len({
            item.get("parameter_code")
            for item in parameter_records
            if item.get("parameter_code")
        }),
        "parameters": parameter_records,
        "coverage": {
            "coverage_ratio": coverage.get("coverage_ratio"),
            "provided_count": coverage.get("provided_count"),
            "core_required_count": coverage.get("core_required_count"),
            "provided_inputs": provided_inputs,
            "missing_critical_data": missing_critical,
            "missing_required_data": missing_required,
        },
        "quality": {
            "missing_critical_count": len(missing_critical),
            "missing_required_count": len(missing_required),
            "has_critical_missingness": bool(missing_critical),
        },
        "mapping_count": len(_scientific_mapping_records(record)),
    }


def _scientific_record_matches(
    view: dict,
    *,
    study_id: str | None,
    participant_reference: str | None,
    model_id: str | None,
    status: str | None,
    search: str | None,
    time_from: str | None,
    time_to: str | None,
) -> bool:
    if study_id and view.get("study_id") != study_id:
        return False
    if (
        participant_reference
        and view.get("participant_reference") != participant_reference
    ):
        return False
    if model_id and model_id not in view.get("model_ids", []):
        return False
    if status and view.get("status") != status:
        return False
    observation_time = str(view.get("observation_time") or "")
    if time_from and observation_time and observation_time < time_from:
        return False
    if time_to and observation_time and observation_time > time_to:
        return False
    if search:
        needle = search.strip().lower()
        haystack = " ".join(str(value or "") for value in [
            view.get("record_id"),
            view.get("study_id"),
            view.get("participant_reference"),
            view.get("session_id"),
            view.get("status"),
            view.get("readiness_status"),
            *view.get("model_ids", []),
            *[
                item.get("parameter_code")
                for item in view.get("parameters", [])
            ],
        ]).lower()
        if needle not in haystack:
            return False
    return True


@app.get("/research/scientific-results/catalog")
def scientific_results_catalog(
    request: Request,
    study_id: str | None = None,
    participant_reference: str | None = None,
    model_id: str | None = None,
    status: str | None = None,
    search: str | None = None,
    time_from: str | None = None,
    time_to: str | None = None,
    offset: int = 0,
    limit: int = 500,
):
    _researcher_session(request)
    safe_offset = max(0, offset)
    safe_limit = min(max(1, limit), 2000)
    views = [
        _scientific_record_view(record)
        for record in _scientific_full_records()
    ]
    filtered = [
        view
        for view in views
        if _scientific_record_matches(
            view,
            study_id=study_id,
            participant_reference=participant_reference,
            model_id=model_id,
            status=status,
            search=search,
            time_from=time_from,
            time_to=time_to,
        )
    ]
    filtered.sort(
        key=lambda item: str(item.get("observation_time") or ""),
        reverse=True,
    )
    page = filtered[safe_offset:safe_offset + safe_limit]
    return {
        "ok": True,
        "schema_version": "scientific-results-catalog-2",
        "global_time_reference": "UTC",
        "total_count": len(filtered),
        "offset": safe_offset,
        "limit": safe_limit,
        "truncated": safe_offset + len(page) < len(filtered),
        "records": page,
        "facets": {
            "studies": sorted({
                item.get("study_id") for item in views
                if item.get("study_id")
            }),
            "models": sorted({
                model for item in views
                for model in item.get("model_ids", [])
            }),
            "statuses": sorted({
                item.get("status") for item in views
                if item.get("status")
            }),
        },
    }


@app.get("/research/scientific-results/participant")
def scientific_results_participant(
    participant_reference: str,
    study_id: str | None = None,
    record_id: str | None = None,
):
    full_records = _scientific_full_records()
    views = []
    selected_raw = None
    for record in full_records:
        view = _scientific_record_view(record)
        if view.get("participant_reference") != participant_reference:
            continue
        if study_id and view.get("study_id") != study_id:
            continue
        views.append(view)
        if record_id and view.get("record_id") == record_id:
            selected_raw = record
    views.sort(
        key=lambda item: str(item.get("observation_time") or ""),
        reverse=True,
    )
    selected_id = (
        record_id
        if record_id and any(
            item.get("record_id") == record_id for item in views
        )
        else (views[0].get("record_id") if views else None)
    )
    if selected_raw is None and selected_id:
        for record in full_records:
            view = _scientific_record_view(record)
            if view.get("record_id") == selected_id:
                selected_raw = record
                break
    return {
        "ok": True,
        "schema_version": "scientific-participant-timeline-2",
        "participant_reference": participant_reference,
        "study_id": study_id,
        "selected_record_id": selected_id,
        "records": views,
        "selected_record": next(
            (
                item for item in views
                if item.get("record_id") == selected_id
            ),
            None,
        ),
        "selected_record_mapping": (
            _scientific_mapping_records(selected_raw)
            if selected_raw else []
        ),
        "selected_record_raw": selected_raw,
        "global_time_reference": "UTC",
    }

@app.post("/research/participant-data/records/{record_id}/analyze")
def analyze_participant_data_record(record_id: str):
    records = list_research_records()

    for record in records:
        if record.get("record_id") == record_id:
            analysis = run_health_model_research_analysis(
                study_id=record.get("study_id"),
            )

            return {
                "ok": True,
                "record_id": record_id,
                "record_source": "research_record",
                "analysis": analysis,
            }

    session = pilot_service.get_session(record_id)

    if session is not None:
        record = {
            "record_id": session.session_id,
            "session_id": session.session_id,
            "study_id": session.study_id or "health_model",
            "result": session.raw_engine_result or {},
        }

        level_map_record = analyze_record_level_maps(record)

        analysis = {
            "analysis_type": "health_model_single_pilot_session_analysis",
            "analysis_scope": "single_pilot_session",
            "study_id": session.study_id or "health_model",
            "record_count": 1,
            "level_maps": {
                "analysis_type": "resource_level_maps_single_session",
                "record_count": 1,
                "interpreted_record_count": (
                    1 if level_map_record.get("interpreted_domains") else 0
                ),
                "records": [level_map_record],
            },
        }

        return {
            "ok": True,
            "record_id": record_id,
            "record_source": "pilot_session",
            "analysis": analysis,
        }

@app.get("/research/analysis/results")
def list_research_analysis_results():
    return {
        "ok": True,
        "results": load_analysis_results(),
    }

@app.get("/data-check", response_class=HTMLResponse)
def data_check_page():
    return Path(
        "static/data_check.html"
    ).read_text(
        encoding="utf-8"
    )

@app.get("/research-lab")
def research_lab_page():
    return FileResponse("static/qualitative_hypothesis_lab.html")


@app.get("/technical-hypothesis-lab")
def technical_hypothesis_lab_page():
    return FileResponse("static/research_lab.html")

@app.get("/citation-workspace")
def citation_workspace_page():
    return FileResponse("static/citation_workspace.html")

@app.get("/evidence-review", response_class=HTMLResponse)
def evidence_review_page():
    return FileResponse("static/scientific_evidence_review.html")

@app.get("/research-workspace", response_class=HTMLResponse)
def research_workspace_page():
    return Path(
        "static/research_workspace.html"
    ).read_text(
        encoding="utf-8"
    )


@app.get("/researcher-account", response_class=HTMLResponse)
def researcher_account_page():
    return Path("static/researcher_account.html").read_text(encoding="utf-8")


@app.get("/research-project/new", response_class=HTMLResponse)
def new_research_project_page():
    return Path("static/research_project.html").read_text(encoding="utf-8")


@app.get("/research-project/{project_id}", response_class=HTMLResponse)
def existing_research_project_page(project_id: str):
    return Path("static/research_project.html").read_text(encoding="utf-8")


@app.get("/probabilistic-methods", response_class=HTMLResponse)
def probabilistic_methods_page():
    return Path("static/probabilistic_methods.html").read_text(encoding="utf-8")


@app.get("/ray-settings", response_class=HTMLResponse)
def ray_settings_page():
    return Path("static/ray_settings.html").read_text(encoding="utf-8")


@app.get("/question-editor", response_class=HTMLResponse)
def question_editor_page():
    return Path("static/question_editor.html").read_text(encoding="utf-8")


@app.get("/parameter-editor", response_class=HTMLResponse)
def parameter_editor_page():
    return Path("static/parameter_editor.html").read_text(encoding="utf-8")


@app.get("/model-logic-editor", response_class=HTMLResponse)
def model_logic_editor_page():
    return Path("static/model_logic_editor.html").read_text(encoding="utf-8")


@app.get("/mechanism-editor", response_class=HTMLResponse)
def mechanism_editor_page():
    return Path("static/mechanism_editor.html").read_text(encoding="utf-8")


@app.get("/data-editor", response_class=HTMLResponse)
def data_editor_page():
    return Path("static/data_editor.html").read_text(encoding="utf-8")


@app.get("/model-training", response_class=HTMLResponse)
def model_training_page():
    return Path("static/model_training.html").read_text(encoding="utf-8")


@app.get("/fiji-integration", response_class=HTMLResponse)
def fiji_integration_page():
    return Path("static/fiji_integration.html").read_text(encoding="utf-8")


@app.get(
    "/model-parameter-constructor",
    response_class=HTMLResponse,
)
def model_parameter_constructor_page():
    return Path(
        "static/model_parameter_constructor.html"
    ).read_text(
        encoding="utf-8"
    )

@app.get("/research-participant", response_class=HTMLResponse)
def research_participant_page():
    return Path(
        "static/research_participant.html"
    ).read_text(
        encoding="utf-8"
    )

@app.get("/data-preparation", response_class=HTMLResponse)
def data_preparation_page():
    return Path(
        "static/data_preparation.html"
    ).read_text(
        encoding="utf-8"
    )

def _question_bank_file_info(bank_id: str, lang: str):
    allowed_langs = {"ru", "en", "es"}

    if lang not in allowed_langs:
        raise HTTPException(status_code=400, detail="Unsupported language")

    variable_name = f"QUESTION_BANK_{lang.upper()}"

    if bank_id == "health_model":
        filename = {
            "ru": "QUESTION_BANK_RU.py",
            "en": "QUESTION_BANK_EN.py",
            "es": "QUESTION_BANK_ES.py",
        }[lang]

        return Path("question_banks") / filename, variable_name

    if bank_id == "decision_under_uncertainty":
        filename = {
            "ru": "decision_under_uncertainty_questions_ru.py",
            "en": "decision_under_uncertainty_questions_en.py",
            "es": "decision_under_uncertainty_questions_es.py",
        }[lang]

        return (
            Path("assessment/studies/decision_under_uncertainty") / filename,
            variable_name,
        )

    filename = {
        "ru": "QUESTION_BANK_RU.py",
        "en": "QUESTION_BANK_EN.py",
        "es": "QUESTION_BANK_ES.py",
    }[lang]

    return Path("question_banks") / bank_id / filename, variable_name


def _load_question_bank_from_file(path: Path, variable_name: str):
    if not path.exists():
        raise HTTPException(status_code=404, detail="Question bank file not found")

    module_name = "dynamic_question_bank_" + path.stem + "_" + str(abs(hash(str(path))))

    spec = importlib.util.spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        raise HTTPException(status_code=500, detail="Question bank import failed")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    bank = getattr(module, variable_name, None)

    if bank is None:
        raise HTTPException(status_code=500, detail="Question bank variable not found")

    return bank

PILOT_BANKS_CONFIG_PATH = Path("data/pilot_questionnaire_banks.json")

def load_pilot_questionnaire_banks(project_id: str) -> list[str]:
    if not PILOT_BANKS_CONFIG_PATH.exists():
        return []

    data = json.loads(
        PILOT_BANKS_CONFIG_PATH.read_text(encoding="utf-8")
    )

    return data.get(project_id, [])


def save_pilot_questionnaire_banks(
    project_id: str,
    enabled_bank_ids: list[str],
):
    PILOT_BANKS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if PILOT_BANKS_CONFIG_PATH.exists():
        data = json.loads(
            PILOT_BANKS_CONFIG_PATH.read_text(encoding="utf-8")
        )
    else:
        data = {}

    data[project_id] = enabled_bank_ids

    PILOT_BANKS_CONFIG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

@app.get("/pilot/questionnaire-banks")
def get_pilot_questionnaire_banks(
    project_id: str = "health_model_pilot",
):
    langs = ["ru", "en", "es"]
    banks_by_id = {}

    # 1. Assessment-опросники: intro/resource/decision
    for assessment in list_assessments():
        bank_id = assessment["id"]
        title = assessment.get("title", {})

        banks_by_id[bank_id] = {
            "id": bank_id,
            "status": assessment.get("status", "active"),
            "title_by_lang": {
                "ru": title.get("ru", bank_id) if isinstance(title, dict) else str(title),
                "en": title.get("en", bank_id) if isinstance(title, dict) else str(title),
                "es": title.get("es", bank_id) if isinstance(title, dict) else str(title),
            },
        }

    # 2. Реальные question banks: health_model, DU, созданные банки
    for bank in list_question_banks()["banks"]:
        bank_id = bank["id"]

        if bank_id not in banks_by_id:
            banks_by_id[bank_id] = {
                "id": bank_id,
                "status": bank.get("status", "active"),
                "title_by_lang": {
                    "ru": bank.get("title", bank_id),
                    "en": bank.get("title", bank_id),
                    "es": bank.get("title", bank_id),
                },
            }

    enabled = set(load_pilot_questionnaire_banks(project_id))

    return {
        "ok": True,
        "project_id": project_id,
        "enabled_bank_ids": list(enabled),
        "banks": [
            {
                **bank,
                "enabled": bank["id"] in enabled,
            }
            for bank in banks_by_id.values()
        ],
    }

@app.post("/pilot/questionnaire-banks")
def update_pilot_questionnaire_banks(
    payload: PilotQuestionnaireBanksPayload,
    project_id: str = "health_model_pilot",
):
    save_pilot_questionnaire_banks(
        project_id=project_id,
        enabled_bank_ids=payload.enabled_bank_ids,
    )

    return {
        "ok": True,
        "project_id": project_id,
        "enabled_bank_ids": payload.enabled_bank_ids,
    }

@app.get("/question-banks")
def list_question_banks():
    banks = [
        {
            "id": "health_model",
            "title": "Health Model",
            "status": "active",
        },
        {
            "id": "decision_under_uncertainty",
            "title": "Decision Under Uncertainty",
            "status": "active",
        },
    ]

    custom_root = Path("question_banks")

    if custom_root.exists():
        for bank_dir in custom_root.iterdir():
            if not bank_dir.is_dir():
                continue

            if not (bank_dir / "__init__.py").exists():
                continue

            bank_id = bank_dir.name

            if any(bank["id"] == bank_id for bank in banks):
                continue

            banks.append({
                "id": bank_id,
                "title": bank_id.replace("_", " ").title(),
                "status": "draft",
            })

    registered_by_code = {
        bank["bank_code"]: bank
        for bank in list_registered_question_banks()
    }
    for bank in banks:
        registered = registered_by_code.pop(bank["id"], None)
        if registered is None:
            continue
        bank.update({
            "bank_uuid": registered["bank_id"],
            "title_translations": registered["titles"],
            "status": registered["development_status"],
            "definition_version": registered["definition_version"],
            "registry_schema_version": registered["registry_schema_version"],
        })
    for code, registered in registered_by_code.items():
        banks.append({
            "id": code,
            "bank_uuid": registered["bank_id"],
            "title": next((registered["titles"].get(lang) for lang in ("ru", "en", "es") if registered["titles"].get(lang)), code),
            "title_translations": registered["titles"],
            "status": registered["development_status"],
            "definition_version": registered["definition_version"],
            "registry_schema_version": registered["registry_schema_version"],
        })

    return {
        "ok": True,
        "banks": banks,
    }

@app.get("/questionnaire-components")
def get_questionnaire_components():
    return {
        "ok": True,
        "components": {
            "question_types": list_question_types(),
            "response_types": list_response_types(),
            "scale_types": list_scale_types(),
            "presentation_types": list_presentation_types(),
            "transition_types": list_transition_types(),
        },
    }


@app.post("/questionnaire-components/validate")
def validate_questionnaire_components(payload: dict):
    return {
        "ok": True,
        "validation": validate_question_measurement_contract(
            payload.get("question_type"),
            payload.get("response_type"),
            payload.get("scale_type"),
            payload.get("presentation_type"),
        ),
    }


@app.get("/research/measurement-scales")
def get_measurement_scale_registry(
    source_type: str | None = None,
    question_constructor: bool | None = None,
    parameter_constructor: bool | None = None,
    include_non_active: bool = False,
):
    definitions = list_scale_definitions(
        source_type=source_type,
        question_constructor_enabled=(
            question_constructor
        ),
        parameter_constructor_enabled=(
            parameter_constructor
        ),
        include_non_active=include_non_active,
    )
    return {
        "ok": True,
        "registry": get_scale_registry_contract(),
        "definition_count": len(definitions),
        "definitions": definitions,
    }


@app.get("/research/measurement-scales/{scale_code}")
def get_measurement_scale_definition(
    scale_code: str,
):
    definition = get_scale_definition(scale_code)
    if definition is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "MEASUREMENT_SCALE_NOT_FOUND",
                "scale_code": scale_code,
            },
        )
    return {"ok": True, "definition": definition}

@app.get("/question-banks/{bank_id}")
def read_question_bank(bank_id: str, lang: str = "ru"):
    if bank_id in {"intro", "resource", "decision"}:
        assessment = get_assessment(
            assessment_id=bank_id,
            question_bank=get_question_bank(lang),
        )

        if assessment is None:
            raise HTTPException(status_code=404, detail="Assessment not found")

        if assessment.get("ok") is False:
            raise HTTPException(status_code=404, detail=assessment)

        questions = assessment.get("questions", [])
        overlays = active_question_overlays(bank_id, lang)
        questions = [
            {**question, **overlays.get(question.get("code") or question.get("question_code"), {})}
            for question in questions
        ]
        present_codes = {
            question.get("code") or question.get("question_code")
            for question in questions
        }
        questions.extend(
            overlay for code, overlay in overlays.items() if code not in present_codes
        )
        return {
            "ok": True,
            "bank_id": bank_id,
            "language": lang,
            "source_file": None,
            "variable_name": None,
            "questions": questions,
        }

    path, variable_name = _question_bank_file_info(bank_id, lang)
    bank = _load_question_bank_from_file(path, variable_name)

    questions = list(bank.values())
    overlays = active_question_overlays(bank_id, lang)
    questions = [
        {**question, **overlays.get(question.get("code") or question.get("question_code"), {})}
        for question in questions
    ]
    present_codes = {
        question.get("code") or question.get("question_code")
        for question in questions
    }
    questions.extend(
        overlay for code, overlay in overlays.items() if code not in present_codes
    )
    return {
        "ok": True,
        "bank_id": bank_id,
        "language": lang,
        "source_file": str(path),
        "variable_name": variable_name,
        "questions": questions,
    }

@app.post("/question-banks")
def create_question_bank(payload: CreateQuestionBankPayload):
    bank_id = payload.bank_id.strip().lower()

    if not bank_id:
        raise HTTPException(status_code=400, detail="Bank id missing")

    if not bank_id.replace("_", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail="Bank id may contain only letters, numbers and underscore",
        )

    base_path = Path("question_banks") / bank_id

    if base_path.exists():
        raise HTTPException(status_code=400, detail="Question bank already exists")

    base_path.mkdir(parents=True)

    files = {
        "ru": ("QUESTION_BANK_RU.py", "QUESTION_BANK_RU"),
        "en": ("QUESTION_BANK_EN.py", "QUESTION_BANK_EN"),
        "es": ("QUESTION_BANK_ES.py", "QUESTION_BANK_ES"),
    }

    for filename, variable_name in files.values():
        (base_path / filename).write_text(
            f"{variable_name} = {{}}\n",
            encoding="utf-8",
        )

    (base_path / "__init__.py").write_text(
        "from .QUESTION_BANK_RU import QUESTION_BANK_RU\n"
        "from .QUESTION_BANK_EN import QUESTION_BANK_EN\n"
        "from .QUESTION_BANK_ES import QUESTION_BANK_ES\n\n"
        "QUESTION_BANKS = {\n"
        '    "ru": QUESTION_BANK_RU,\n'
        '    "en": QUESTION_BANK_EN,\n'
        '    "es": QUESTION_BANK_ES,\n'
        "}\n\n"
        "def get_question_bank(lang: str):\n"
        '    return QUESTION_BANKS.get(lang, QUESTION_BANK_RU)\n',
        encoding="utf-8",
    )

    return {
        "ok": True,
        "bank": {
            "id": bank_id,
            "title": payload.title,
            "status": "draft",
            "path": str(base_path),
        },
    }

@app.delete("/question-banks/{bank_id}")
def delete_question_bank(bank_id: str):
    protected_bank_ids = {
        "health_model",
        "decision_under_uncertainty",
        "intro",
        "resource",
        "decision",
    }

    normalized_bank_id = bank_id.strip().lower()

    if not normalized_bank_id:
        raise HTTPException(
            status_code=400,
            detail="Bank id missing",
        )

    if normalized_bank_id in protected_bank_ids:
        raise HTTPException(
            status_code=400,
            detail="System question bank cannot be deleted",
        )

    if not normalized_bank_id.replace("_", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail=(
                "Bank id may contain only letters, "
                "numbers and underscore"
            ),
        )

    bank_path = Path("question_banks") / normalized_bank_id

    if not bank_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Question bank not found",
        )

    if not bank_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="Question bank path is not a directory",
        )

    connected_projects = []

    if PILOT_BANKS_CONFIG_PATH.exists():
        pilot_config = json.loads(
            PILOT_BANKS_CONFIG_PATH.read_text(
                encoding="utf-8",
            )
        )

        for project_id, enabled_bank_ids in pilot_config.items():
            if normalized_bank_id in (
                enabled_bank_ids or []
            ):
                connected_projects.append(project_id)

    if connected_projects:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "QUESTION_BANK_IS_CONNECTED",
                "message": (
                    "Disconnect the question bank "
                    "from the pilot before deleting it"
                ),
                "connected_projects": connected_projects,
            },
        )

    shutil.rmtree(bank_path)

    return {
        "ok": True,
        "deleted_bank_id": normalized_bank_id,
        "deleted_path": str(bank_path),
    }

@app.post("/question-banks/{bank_id}/questions")
def save_question_bank_questions(bank_id: str, payload: QuestionBankSavePayload):
    if not payload.source_file:
        raise HTTPException(status_code=400, detail="Source file missing")

    if not payload.variable_name:
        raise HTTPException(status_code=400, detail="Variable name missing")

    path = Path(payload.source_file)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Source file not found")

    question_bank = {}

    for question in payload.questions:
        code = question.get("code")

        if not code:
            raise HTTPException(status_code=400, detail="Question code missing")

        question_bank[code] = question

    content = (
        f"{payload.variable_name} = "
        f"{pformat(question_bank, width=120, sort_dicts=False)}\n"
    )

    path.write_text(content, encoding="utf-8")

    return {
        "ok": True,
        "bank_id": bank_id,
        "language": payload.language,
        "saved_questions": len(question_bank),
        "file": str(path),
    }

@app.get("/assessments/{assessment_id}")
def read_assessment(assessment_id: str, lang: str = "ru"):
    assessment = get_assessment(
        assessment_id=assessment_id,
        question_bank=get_question_bank(lang),
    )

    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if assessment.get("ok") is False:
        raise HTTPException(status_code=500, detail=assessment)

    return assessment

@app.post("/assessments/{assessment_id}/questions")
def save_assessment_questions(assessment_id: str, payload: QuestionBankSavePayload):
    allowed_langs = {"ru", "en", "es"}
    if payload.language not in allowed_langs:
        raise HTTPException(status_code=400, detail="Unsupported language")

    file_maps = {
        "health_model": {
            "ru": (Path("question_banks/QUESTION_BANK_RU.py"), "QUESTION_BANK_RU"),
            "en": (Path("question_banks/QUESTION_BANK_EN.py"), "QUESTION_BANK_EN"),
            "es": (Path("question_banks/QUESTION_BANK_ES.py"), "QUESTION_BANK_ES"),
        },
        "decision_under_uncertainty": {
            "ru": (
                Path("assessment/studies/decision_under_uncertainty/decision_under_uncertainty_questions_ru.py"),
                "QUESTION_BANK_RU",
            ),
            "en": (
                Path("assessment/studies/decision_under_uncertainty/decision_under_uncertainty_questions_en.py"),
                "QUESTION_BANK_EN",
            ),
            "es": (
                Path("assessment/studies/decision_under_uncertainty/decision_under_uncertainty_questions_es.py"),
                "QUESTION_BANK_ES",
            ),
        },
    }

    if assessment_id not in file_maps:
        raise HTTPException(status_code=400, detail="Unsupported assessment")

    path, variable_name = file_maps[assessment_id][payload.language]

    question_bank = {}

    for question in payload.questions:
        code = question.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Question code missing")
        question_bank[code] = question

    content = f"{variable_name} = {pformat(question_bank, width=120, sort_dicts=False)}\n"
    path.write_text(content, encoding="utf-8")

    return {
        "ok": True,
        "assessment_id": assessment_id,
        "language": payload.language,
        "saved_questions": len(question_bank),
        "file": str(path),
    }

@app.get("/research/entities")
def list_research_entities_api(
    request: Request,
    entity_type: str | None = None,
    language: str = "ru",
):
    context = _researcher_session(request)
    return {
        "ok": True,
        "entities": list_entities(
            entity_type=entity_type,
            language=language,
            owner=context["account"]["account_id"],
        ),
    }


@app.get("/research/hypothesis-entities")
def list_hypothesis_entities_api(request: Request, project_id: str | None = None,
                                 mode: str = "humanities_qualitative", language: str = "ru"):
    context = _researcher_session(request)
    return {
        "ok": True,
        "schema_version": "hypothesis-eligible-entity-catalog-1",
        "entities": list_hypothesis_entities(
            owner=context["account"]["account_id"], project_id=project_id,
            language=language, mode=mode,
        ),
    }

@app.get("/questionnaire-du")
def questionnaire_du_page():
    return FileResponse("static/questionnaire_du.html")

class DUAnswerPayload(BaseModel):
    session_id: str
    question_code: str
    value: int
    language: str = "ru"


@app.get("/du/first-question")
def du_first_question(language: str = "ru"):
    bank = QUESTION_BANK.get(language, QUESTION_BANK["ru"])
    return {
        "ok": True,
        "question": bank.get("DU1"),
    }


@app.post("/du/answer")
def du_answer(payload: DUAnswerPayload):
    bank = QUESTION_BANK.get(payload.language, QUESTION_BANK["ru"])
    question = bank.get(payload.question_code)

    if question is None:
        return {
            "ok": False,
            "error": "UNKNOWN_QUESTION",
        }

    next_code = get_next_question_code(payload.question_code, payload.value)

    if not next_code or next_code.endswith("_RESERVED"):
        return {
            "ok": True,
            "done": True,
            "next_code": next_code,
            "question": None,
        }

    return {
        "ok": True,
        "done": False,
        "next_code": next_code,
        "question": bank.get(next_code),
    }

@app.post("/pilot/sessions/{session_id}/answers")
def submit_pilot_answers(
    session_id: str,
    data: SubmitAnswersInput,
):
    try:
        session = pilot_service.submit_answers(
            session_id=session_id,
            answers=data.answers,
            domain_data_identity=data.domain_data_identity,
        )

        return {
            "ok": True,
            "status": session.status.value,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/pilot/sessions/{session_id}/followup-answers")
def submit_pilot_followup_answers(
    session_id: str,
    data: SubmitAnswersInput,
):
    try:
        session = pilot_service.submit_followup_answers(
            session_id=session_id,
            answers=data.answers,
        )

        return {
            "ok": True,
            "status": session.status.value,
            "answers_count": len(session.answers),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/pilot/sessions/{session_id}/run")
def run_pilot_session(session_id: str):
    try:
        session = pilot_service.run_session(session_id)

        health_model_v61 = calculate_health_model_v61(
            session.answers or {},
        )

        return {
            "ok": True,
            "status": session.status.value,
            "health_model_v61": health_model_v61,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/pilot/sessions/{session_id}/ray-next-question")
def get_ray_next_question(
    session_id: str,
    lang: str = "ru",
):
    try:
        session = pilot_service.get_session(session_id)

        return {
            "ok": True,
            "ray": build_ray_next_question(
                session=session,
                lang=lang,
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.post("/pilot/sessions/{session_id}/ray-answer")
def submit_ray_answer(
    session_id: str,
    data: RayAnswerInput,
):
    try:
        pilot_service.submit_followup_answers(
            session_id=session_id,
            answers={
                data.variable_code: data.value,
            },
        )

        session = pilot_service.run_session(session_id)

        return {
            "ok": True,
            "status": session.status.value,
            "ray": build_ray_next_question(
                session=session,
                lang="ru",
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.post("/pilot/sessions/{session_id}/ray-chat")
def ray_chat(
    session_id: str,
    data: RayChatInput,
):
    try:
        session = pilot_service.get_session(session_id)

        current_question = build_ray_next_question(
            session=session,
            lang=data.lang,
        )

        if current_question.get("status") == "question":
            value = parse_numeric_reply(data.message)

            if value is not None:
                variable_code = current_question.get("variable_code")

                pilot_service.submit_followup_answers(
                    session_id=session_id,
                    answers={
                        variable_code: value,
                    },
                )

                session = pilot_service.run_session(session_id)

                return {
                    "ok": True,
                    "ray": build_ray_chat_response(
                        session=session,
                        message=data.message,
                        lang=data.lang,
                    ),
                }

        return {
            "ok": True,
            "ray": build_ray_chat_response(
                session=session,
                message=data.message,
                lang=data.lang,
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.get("/pilot/sessions/{session_id}/export")
def export_pilot_session(session_id: str):
    try:
        export_data = pilot_service.generate_export(
            session_id
        )

        return {
            "ok": True,
            "export": export_data,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.post("/pilot/sessions/{session_id}/close")
def close_pilot_session(session_id: str):
    try:
        session = pilot_service.close_session(
            session_id
        )

        return {
            "ok": True,
            "status": session.status.value,
            "closed_at": (
                session.closed_at.isoformat()
                if session.closed_at is not None
                else None
            ),
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )


@app.post("/pilot/sessions/{session_id}/invalidate")
def invalidate_pilot_session(
    session_id: str,
    data: InvalidateSessionInput,
):
    try:
        session = pilot_service.invalidate_session(
            session_id=session_id,
            reason=data.reason,
        )

        return {
            "ok": True,
            "status": session.status.value,
            "invalidated": session.invalidated,
            "reason": session.invalidation_reason,
        }

    except PilotSessionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()["error"],
        )

@app.get("/assessment", response_class=HTMLResponse)
def assessment_page():
    return Path(
        "static/assessment.html"
    ).read_text(
        encoding="utf-8"
    )

@app.get("/consent/{version}/{lang}", response_class=HTMLResponse)
def consent_page(version: str, lang: str):
    allowed_versions = {"pilot_v1"}
    allowed_langs = {"ru", "en", "es"}

    if version not in allowed_versions:
        raise HTTPException(status_code=404, detail="Consent version not found")

    if lang not in allowed_langs:
        raise HTTPException(status_code=404, detail="Consent language not found")

    path = Path("static/consent") / version / f"{lang}.html"

    if not path.exists():
        raise HTTPException(status_code=404, detail="Consent file not found")

    return path.read_text(encoding="utf-8")

@app.get("/analysis-check", response_class=HTMLResponse)
def analysis_check_page():
    return Path(
        "static/analysis_check.html"
    ).read_text(
        encoding="utf-8"
    )
@app.get("/pilot-result", response_class=HTMLResponse)
def pilot_result_page():
    return Path("static/pilot_result.html").read_text(encoding="utf-8")
   
@app.get("/scientific-results", response_class=HTMLResponse)
def scientific_results_page():
    return Path("static/scientific_results.html").read_text(
        encoding="utf-8"
    )
 
@app.post("/du/complete")
def du_complete(payload: DUCompletePayload):
    service = DecisionUnderUncertaintyService()
    result = service.process_completed_block(payload.answers)

    saved_result = result_service.save(
        account_id=payload.account_id,
        session_id=payload.session_id,
        study_id="decision_under_uncertainty",
        result=result,
    )
    save_du_research_record(
        session_id=payload.session_id,
        account_id=payload.account_id,
        answers=payload.answers,
        result=result,
        language=payload.language,
        domain_data_identity=payload.domain_data_identity,
    )
    return {
        "ok": True,
        "session_id": payload.session_id,
        "result_id": saved_result.get("created_at"),
        "summary": result["summary"],
    }

@app.get("/pilot/accounts/{account_id}/results")
def get_account_results(account_id: str):
    return {
        "ok": True,
        "account_id": account_id,
        "results": result_service.list(account_id),
    }

@app.get("/measurement-setup", response_class=HTMLResponse)
def measurement_setup_page():
    return Path(
        "static/measurement_setup.html"
    ).read_text(
        encoding="utf-8"
    )


@app.get("/measurement/connectors")
def list_measurement_connectors_api():
    return {
        "ok": True,
        "connectors": discover_measurement_connectors(),
    }


def require_measurement_time_binding(graph: dict) -> dict:
    normalized_graph = deepcopy(graph)
    normalized_graph["time_reference"] = (
        normalize_measurement_time_reference(
            normalized_graph.get("time_reference")
        )
    )
    validation = validate_measurement_time_reference(
        normalized_graph["time_reference"]
    )
    normalized_graph.setdefault("metadata", {})[
        "time_validation"
    ] = validation
    normalized_graph.setdefault("quality", {})[
        "time_binding_status"
    ] = validation["status"]
    if validation["valid"] is not True:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "MEASUREMENT_TIME_BINDING_INVALID",
                "validation": validation,
            },
        )
    return normalized_graph

@app.post("/measurement/graphs")
def save_measurement_graph_api(payload: MeasurementGraphPayload):
    graph = require_measurement_time_binding(payload.graph)
    saved = save_measurement_graph(graph)

    return {
        "ok": True,
        "saved": saved,
    }

@app.post("/measurement/create")
def create_measurement_api(data: CreateMeasurementInput):
    measurement_session = create_measurement_session(
        measurement_type=data.measurement_type,
        connector=data.connector,
        study_id=data.study_id,
        participant_id=data.participant_id,
        session_id=data.session_id,
        series_id=data.series_id,
        series_position=data.series_position,
    )

    return {
        "ok": True,
        "measurement_session": measurement_session,
    }

@app.post("/measurement/finish")
def finish_measurement_api(data: FinishMeasurementInput):
    measurement_session = mark_finished(
        data.measurement_session,
        raw_file_path=data.raw_file_path,
        original_file_name=data.original_file_name,
        file_type=data.file_type,
        checksum=data.checksum,
    )

    graph = build_measurement_graph_from_session(
        measurement_session,
        context=data.context or {},
    )

    return {
        "ok": True,
        "measurement_session": measurement_session,
        "measurement_graph": graph,
    }

@app.post("/measurement/save")
def save_measurement_api(data: SaveMeasurementInput):
    graph = require_measurement_time_binding(
        data.measurement_graph
    )
    saved = save_measurement_graph(graph)

    return {
        "ok": True,
        "saved": saved,
    }

@app.post("/measurement/instruments/connect")
def connect_measurement_instrument_api(data: ConnectInstrumentInput):
    instrument = connect_instrument(
        instrument_id=data.instrument_id,
        connector=data.connector,
        measurement_type=data.measurement_type,
        study_id=data.study_id,
        participant_id=data.participant_id,
        session_id=data.session_id,
        context=data.context or {},
    )

    return {
        "ok": True,
        "instrument": instrument,
    }


@app.get("/measurement/instruments")
def list_measurement_instruments_api():
    return {
        "ok": True,
        "instruments": list_connected_instruments(),
    }


@app.post("/measurement/instruments/{instrument_id}/disconnect")
def disconnect_measurement_instrument_api(instrument_id: str):
    instrument = disconnect_instrument(instrument_id)

    return {
        "ok": True,
        "instrument": instrument,
    }

@app.get("/research/dependencies/available")
def get_available_research_dependencies(
    study_id: str,
):
    answer_records = []

    for research_record in list_research_records(study_id=study_id):
        answer_records.extend(
            research_record.get("research_answer_records", [])
        )

    for session in store.list_all():
        if session.study_id != study_id:
            continue

        answer_records.extend(
            session.research_answer_records or []
        )

    return build_available_dependencies(
        study_id=study_id,
        answer_records=answer_records,
    )

def build_answer_records_from_answers(
    *,
    study_id: str,
    record_id: str,
    session_id: str | None,
    answers: dict,
) -> list[dict]:
    return [
        {
            "answer_record_id": f"{record_id}:{question_code}",
            "record_type": "questionnaire_answer",
            "study_id": study_id,
            "session_id": session_id,
            "question_code": question_code,
            "answer_value": answer_value,
            "answer_value_type": type(answer_value).__name__,
            "source_mode": "answers_fallback",
        }
        for question_code, answer_value in (answers or {}).items()
    ]

def collect_answer_records_for_study(
    study_id: str,
) -> list[dict]:
    answer_records: list[dict] = []

    for research_record in list_research_records(
        study_id=study_id,
    ):
        records = (
            research_record.get(
                "research_answer_records",
                [],
            )
            or []
        )

        if records:
            answer_records.extend(records)
            continue

        answers = research_record.get("answers", {}) or {}

        if answers:
            answer_records.extend(
                build_answer_records_from_answers(
                    study_id=(
                        research_record.get("study_id")
                        or study_id
                    ),
                    record_id=(
                        research_record.get("record_id")
                        or "research_record"
                    ),
                    session_id=research_record.get(
                        "session_id"
                    ),
                    answers=answers,
                )
            )

    for session in store.list_all():
        if session.study_id != study_id:
            continue

        records = (
            session.research_answer_records
            or []
        )

        if records:
            answer_records.extend(records)
            continue

        # Явный legacy fallback только для старых сессий,
        # где research_answer_records ещё не существовали.
        answer_records.extend(
            build_answer_records_from_answers(
                study_id=(
                    session.study_id
                    or study_id
                ),
                record_id=session.session_id,
                session_id=session.session_id,
                answers=session.answers or {},
            )
        )

    return answer_records

RESEARCH_USABLE_SESSION_STATUSES = {
    "RUN_COMPLETED",
    "EXPORT_READY",
    "CLOSED",
}


def _parse_research_datetime(
    value: Any,
) -> datetime | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        normalized = value.strip()

        if not normalized:
            return None

        if normalized.endswith("Z"):
            normalized = (
                normalized[:-1] + "+00:00"
            )

        try:
            parsed = datetime.fromisoformat(
                normalized
            )
        except ValueError:
            return None
    else:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)

    return parsed.astimezone(UTC)


def _questionnaire_id_from_answer_record(
    answer_record: dict,
    session_study_id: str | None,
) -> str | None:
    identity = (
        answer_record.get(
            "domain_data_identity",
            {},
        )
        or {}
    )

    return (
        identity.get("data_source_path")
        or answer_record.get("questionnaire_id")
        or session_study_id
        or answer_record.get("study_id")
    )


def _participant_reference_from_answer_record(
    answer_record: dict,
) -> tuple[str | None, str | None]:
    subject_link_id = answer_record.get(
        "subject_link_id"
    )

    if subject_link_id:
        return (
            str(subject_link_id),
            "subject_link_id",
        )

    participant_id = answer_record.get(
        "participant_id"
    )

    if participant_id:
        return (
            str(participant_id),
            "participant_id_fallback",
        )

    return None, None


def _answer_observation_time(
    *,
    answer_record: dict,
    session,
) -> tuple[datetime | None, str | None]:
    identity = (
        answer_record.get(
            "domain_data_identity",
            {},
        )
        or {}
    )

    candidates = [
        (
            identity.get(
                "collection_finished_at"
            ),
            "collection_finished_at",
        ),
        (
            answer_record.get("created_at"),
            "answer_record_created_at",
        ),
        (
            getattr(
                session,
                "updated_at",
                None,
            ),
            "session_updated_at",
        ),
        (
            getattr(
                session,
                "created_at",
                None,
            ),
            "session_created_at",
        ),
    ]

    for raw_value, source in candidates:
        parsed = _parse_research_datetime(
            raw_value
        )

        if parsed is not None:
            return parsed, source

    return None, None


def _question_group_metadata(
    answer_record: dict,
) -> dict:
    return {
        "question_uuid": (
            answer_record.get("question_uuid")
            or answer_record.get("question_id")
        ),
        "question_id": answer_record.get(
            "question_id"
        ),
        "question_code": answer_record.get(
            "question_code"
        ),
        "question_bank_id": answer_record.get(
            "question_bank_id"
        ),
        "question_bank_code": answer_record.get(
            "question_bank_code"
        ),
        "question_block": answer_record.get(
            "question_block"
        ),
        "question_family": answer_record.get(
            "question_family"
        ),
        "question_domain": answer_record.get(
            "question_domain"
        ),
        "question_version": answer_record.get(
            "question_version"
        ),
        "scale_type": answer_record.get(
            "scale_type"
        ),
        "score_direction": answer_record.get(
            "score_direction"
        ),
        "answer_value_type": answer_record.get(
            "answer_value_type"
        ),
    }


def build_questionnaire_measurement_catalog(
    *,
    project_id: str,
    study_id: str | None = None,
    questionnaire_id: str | None = None,
    include_all_measurements: bool = False,
) -> dict:
    connected_questionnaire_ids = (
        load_pilot_questionnaire_banks(
            project_id
        )
    )

    connected_set = set(
        connected_questionnaire_ids
    )

    available_study_ids = sorted({
        str(session.study_id)
        for session in store.list_all()
        if session.study_id
        and session.status.value in RESEARCH_USABLE_SESSION_STATUSES
        and not session.invalidated
    })
    study_scope_required = study_id is None and len(available_study_ids) > 1
    if study_id is None and len(available_study_ids) == 1:
        study_id = available_study_ids[0]

    groups: dict[
        tuple[str, str],
        dict,
    ] = {}

    excluded_records: list[dict] = []
    configuration_issues: list[dict] = []
    if study_scope_required:
        configuration_issues.append({
            "issue_code": "STUDY_SCOPE_REQUIRED",
            "available_study_ids": available_study_ids,
            "reason": "Questionnaire results from different studies must not be pooled implicitly.",
        })

    seen_unconnected_questionnaires: set[
        str
    ] = set()

    for session in store.list_all():
        if study_scope_required:
            continue
        if study_id is not None and session.study_id != study_id:
            continue
        session_status = session.status.value

        records = (
            session.research_answer_records
            or []
        )

        if (
            session_status
            not in RESEARCH_USABLE_SESSION_STATUSES
        ):
            for answer_record in records:
                excluded_records.append({
                    "reason_code": (
                        "SESSION_STATUS_NOT_USABLE"
                    ),
                    "session_id": (
                        session.session_id
                    ),
                    "session_status": (
                        session_status
                    ),
                    "question_code": (
                        answer_record.get(
                            "question_code"
                        )
                    ),
                    "question_uuid": (
                        answer_record.get(
                            "question_uuid"
                        )
                        or answer_record.get(
                            "question_id"
                        )
                    ),
                })

            continue

        if session.invalidated:
            for answer_record in records:
                excluded_records.append({
                    "reason_code": (
                        "SESSION_INVALIDATED"
                    ),
                    "session_id": (
                        session.session_id
                    ),
                    "session_status": (
                        session_status
                    ),
                    "question_code": (
                        answer_record.get(
                            "question_code"
                        )
                    ),
                    "question_uuid": (
                        answer_record.get(
                            "question_uuid"
                        )
                        or answer_record.get(
                            "question_id"
                        )
                    ),
                })

            continue

        if not records:
            excluded_records.append({
                "reason_code": (
                    "RESEARCH_ANSWER_RECORDS_MISSING"
                ),
                "session_id": session.session_id,
                "session_status": session_status,
                "study_id": session.study_id,
                "answers_count": len(
                    session.answers or {}
                ),
            })
            continue

        for answer_record in records:
            current_questionnaire_id = (
                _questionnaire_id_from_answer_record(
                    answer_record,
                    session.study_id,
                )
            )

            if not current_questionnaire_id:
                excluded_records.append({
                    "reason_code": (
                        "QUESTIONNAIRE_ID_MISSING"
                    ),
                    "session_id": (
                        session.session_id
                    ),
                    "question_code": (
                        answer_record.get(
                            "question_code"
                        )
                    ),
                    "answer_record_id": (
                        answer_record.get(
                            "answer_record_id"
                        )
                    ),
                })
                continue

            if (
                current_questionnaire_id
                not in connected_set
            ):
                if (
                    current_questionnaire_id
                    not in
                    seen_unconnected_questionnaires
                ):
                    configuration_issues.append({
                        "issue_code": (
                            "DATA_EXISTS_FOR_UNCONNECTED_QUESTIONNAIRE"
                        ),
                        "questionnaire_id": (
                            current_questionnaire_id
                        ),
                        "project_id": project_id,
                    })

                    seen_unconnected_questionnaires.add(
                        current_questionnaire_id
                    )

            if (
                questionnaire_id is not None
                and
                current_questionnaire_id
                != questionnaire_id
            ):
                continue

            question_uuid = (
                answer_record.get(
                    "question_uuid"
                )
                or answer_record.get(
                    "question_id"
                )
            )

            if not question_uuid:
                excluded_records.append({
                    "reason_code": (
                        "QUESTION_UUID_MISSING"
                    ),
                    "questionnaire_id": (
                        current_questionnaire_id
                    ),
                    "session_id": (
                        session.session_id
                    ),
                    "question_code": (
                        answer_record.get(
                            "question_code"
                        )
                    ),
                    "answer_record_id": (
                        answer_record.get(
                            "answer_record_id"
                        )
                    ),
                })
                continue

            (
                participant_reference,
                participant_reference_source,
            ) = (
                _participant_reference_from_answer_record(
                    answer_record
                )
            )

            if not participant_reference:
                excluded_records.append({
                    "reason_code": (
                        "PARTICIPANT_REFERENCE_MISSING"
                    ),
                    "questionnaire_id": (
                        current_questionnaire_id
                    ),
                    "question_uuid": (
                        question_uuid
                    ),
                    "session_id": (
                        session.session_id
                    ),
                    "answer_record_id": (
                        answer_record.get(
                            "answer_record_id"
                        )
                    ),
                })
                continue

            (
                observation_time,
                observation_time_source,
            ) = _answer_observation_time(
                answer_record=answer_record,
                session=session,
            )

            if observation_time is None:
                excluded_records.append({
                    "reason_code": (
                        "OBSERVATION_TIME_MISSING_OR_INVALID"
                    ),
                    "questionnaire_id": (
                        current_questionnaire_id
                    ),
                    "question_uuid": (
                        question_uuid
                    ),
                    "participant_reference": (
                        participant_reference
                    ),
                    "session_id": (
                        session.session_id
                    ),
                    "answer_record_id": (
                        answer_record.get(
                            "answer_record_id"
                        )
                    ),
                })
                continue

            if "answer_value" not in answer_record:
                excluded_records.append({
                    "reason_code": (
                        "ANSWER_VALUE_MISSING"
                    ),
                    "questionnaire_id": (
                        current_questionnaire_id
                    ),
                    "question_uuid": (
                        question_uuid
                    ),
                    "participant_reference": (
                        participant_reference
                    ),
                    "session_id": (
                        session.session_id
                    ),
                    "answer_record_id": (
                        answer_record.get(
                            "answer_record_id"
                        )
                    ),
                })
                continue

            group_key = (
                current_questionnaire_id,
                str(question_uuid),
            )

            if group_key not in groups:
                groups[group_key] = {
                    "questionnaire_id": (
                        current_questionnaire_id
                    ),
                    **_question_group_metadata(
                        answer_record
                    ),
                    "_latest_by_participant": {},
                    "_all_measurements": [],
                    "_all_valid_count": 0,
                    "_not_selected_latest_count": 0,
                }

            group = groups[group_key]
            group["_all_valid_count"] += 1

            candidate = {
                "answer_record_id": (
                    answer_record.get(
                        "answer_record_id"
                    )
                ),
                "submission_id": (
                    answer_record.get(
                        "submission_id"
                    )
                ),
                "questionnaire_id": (
                    current_questionnaire_id
                ),
                "question_uuid": str(
                    question_uuid
                ),
                "question_code": (
                    answer_record.get(
                        "question_code"
                    )
                ),
                "participant_reference": (
                    participant_reference
                ),
                "participant_reference_source": (
                    participant_reference_source
                ),
                "session_id": (
                    session.session_id
                ),
                "session_status": (
                    session_status
                ),
                "study_id": (
                    answer_record.get("study_id")
                    or session.study_id
                ),
                "answer_value": (
                    answer_record.get(
                        "answer_value"
                    )
                ),
                "answer_value_type": (
                    answer_record.get(
                        "answer_value_type"
                    )
                ),
                "answer_revision": (
                    answer_record.get(
                        "answer_revision"
                    )
                    or 0
                ),
                "observation_time": (
                    observation_time.isoformat()
                ),
                "observation_time_source": (
                    observation_time_source
                ),
                "global_time_reference": "UTC",
                "global_time_scale_reference": (
                    build_scale_reference("datetime")
                ),
                "timezone": "UTC",
                "clock_source": (
                    "application_server_timestamp"
                ),
                "synchronization_reference": None,
                "time_binding_status": (
                    "bound_with_unverified_clock"
                ),
                "_observation_time": (
                    observation_time
                ),
            }

            # Keep the complete valid time series. The latest-per-participant
            # index below remains a separate cross-participant projection and
            # must never delete earlier observations needed for longitudinal
            # analysis of one participant.
            group["_all_measurements"].append(candidate)

            previous = group[
                "_latest_by_participant"
            ].get(participant_reference)

            if previous is None:
                group[
                    "_latest_by_participant"
                ][participant_reference] = (
                    candidate
                )
                continue

            previous_sort_key = (
                previous["_observation_time"],
                int(
                    previous.get(
                        "answer_revision",
                        0,
                    )
                ),
                str(
                    previous.get(
                        "answer_record_id"
                    )
                    or ""
                ),
            )

            candidate_sort_key = (
                candidate["_observation_time"],
                int(
                    candidate.get(
                        "answer_revision",
                        0,
                    )
                ),
                str(
                    candidate.get(
                        "answer_record_id"
                    )
                    or ""
                ),
            )

            if (
                candidate_sort_key
                > previous_sort_key
            ):
                group[
                    "_not_selected_latest_count"
                ] += 1

                group[
                    "_latest_by_participant"
                ][participant_reference] = (
                    candidate
                )
            else:
                group[
                    "_not_selected_latest_count"
                ] += 1

    questionnaire_groups: dict[
        str,
        list[dict],
    ] = defaultdict(list)

    for group in groups.values():
        measurements = list(
            group[
                "_latest_by_participant"
            ].values()
        )

        measurements.sort(
            key=lambda item: (
                item["_observation_time"],
                item["participant_reference"],
            ),
            reverse=True,
        )

        public_measurements = [
            {
                key: value
                for key, value in item.items()
                if not key.startswith("_")
            }
            for item in measurements
        ]

        all_measurements = sorted(
            group["_all_measurements"],
            key=lambda item: (
                item["_observation_time"],
                item["participant_reference"],
                str(item.get("answer_record_id") or ""),
            ),
        )

        public_all_measurements = [
            {
                key: value
                for key, value in item.items()
                if not key.startswith("_")
            }
            for item in all_measurements
        ]

        participant_references = sorted({
            item["participant_reference"]
            for item in public_all_measurements
        })

        first_observation_time = (
            public_all_measurements[0]["observation_time"]
            if public_all_measurements
            else None
        )
        last_observation_time = (
            public_all_measurements[-1]["observation_time"]
            if public_all_measurements
            else None
        )

        questionnaire_groups[
            group["questionnaire_id"]
        ].append({
            key: value
            for key, value in group.items()
            if not key.startswith("_")
        } | {
            "unique_participant_count": (
                len(public_measurements)
            ),
            "observation_count": len(
                public_all_measurements
            ),
            "participant_references": (
                participant_references
            ),
            "first_observation_time": (
                first_observation_time
            ),
            "last_observation_time": (
                last_observation_time
            ),
            "valid_measurement_count_before_latest_rule": (
                group["_all_valid_count"]
            ),
            "superseded_measurement_count": 0,
            "not_selected_for_latest_projection_count": (
                group[
                    "_not_selected_latest_count"
                ]
            ),
            "measurements": public_measurements,
            **(
                {
                    "all_measurements": (
                        public_all_measurements
                    )
                }
                if include_all_measurements
                else {}
            ),
        })

    questionnaires = []

    result_questionnaire_ids = sorted(
        set(connected_questionnaire_ids)
        | set(questionnaire_groups)
    )

    for connected_id in result_questionnaire_ids:
        question_groups = questionnaire_groups.get(
            connected_id,
            [],
        )

        question_groups.sort(
            key=lambda item: (
                str(
                    item.get(
                        "question_block"
                    )
                    or ""
                ),
                str(
                    item.get(
                        "question_code"
                    )
                    or ""
                ),
                str(
                    item.get(
                        "question_uuid"
                    )
                    or ""
                ),
            )
        )

        questionnaires.append({
            "questionnaire_id": connected_id,
            "connected": (
                connected_id in connected_set
            ),
            "result_source_status": (
                "registered_and_currently_connected"
                if connected_id in connected_set
                else "stored_results_available"
            ),
            "question_count": len(
                question_groups
            ),
            "unique_measurement_count": sum(
                group[
                    "unique_participant_count"
                ]
                for group in question_groups
            ),
            "questions": question_groups,
        })

    return {
        "ok": True,
        "project_id": project_id,
        "study_id": study_id,
        "available_study_ids": available_study_ids,
        "study_scope_required": study_scope_required,
        "selected_questionnaire_id": (
            questionnaire_id
        ),
        "connected_questionnaire_ids": (
            connected_questionnaire_ids
        ),
        "questionnaires": questionnaires,
        "configuration_issues": (
            configuration_issues
        ),
        "excluded_records_count": len(
            excluded_records
        ),
        "excluded_records": excluded_records,
        "deduplication": {
            "participant_key_priority": [
                "subject_link_id",
                "participant_id",
            ],
            "question_key": "question_uuid",
            "latest_measurement_rule": [
                "collection_finished_at",
                "answer_record_created_at",
                "session_updated_at",
                "session_created_at",
                "answer_revision",
                "answer_record_id",
            ],
            "older_measurements_hidden": False,
            "older_measurements_reported_as_excluded": False,
            "projections": {
                "cross_participant": (
                    "latest_valid_measurement_per_participant"
                ),
                "within_participant": (
                    "all_valid_measurements_in_utc_order"
                ),
            },
        },
    }

@app.get("/research/questionnaire-measurements")
def get_questionnaire_measurements(
    project_id: str = "health_model_pilot",
    study_id: str | None = None,
    questionnaire_id: str | None = None,
):
    return build_questionnaire_measurement_catalog(
        project_id=project_id,
        study_id=study_id,
        questionnaire_id=questionnaire_id,
    )


@app.get("/research/questionnaire-samples")
def get_questionnaire_sample_summaries(
    request: Request,
    project_id: str = "health_model_pilot",
    study_id: str | None = None,
):
    """Lightweight catalogue for the left side of Data Explorer.

    It contains only sample/question metadata. Individual measurements are
    deliberately omitted and are loaded after the researcher selects a
    question and an analysis scope.
    """
    _researcher_session(request)
    catalog = build_questionnaire_measurement_catalog(
        project_id=project_id,
        study_id=study_id,
    )

    questionnaires = []
    bank_metadata_errors = []
    for questionnaire in catalog["questionnaires"]:
        bank_questions_by_key = {}
        try:
            bank_data = read_question_bank(
                questionnaire["questionnaire_id"],
                lang="ru",
            )
            for bank_question in bank_data.get(
                "questions",
                [],
            ):
                for key in {
                    bank_question.get("question_uuid"),
                    bank_question.get("question_id"),
                    bank_question.get("code"),
                    bank_question.get("question_code"),
                }:
                    if key:
                        bank_questions_by_key[str(key)] = (
                            bank_question
                        )
        except (
            HTTPException,
            FileNotFoundError,
            ValueError,
            KeyError,
        ) as error:
            bank_metadata_errors.append({
                "questionnaire_id": (
                    questionnaire["questionnaire_id"]
                ),
                "error": str(
                    getattr(error, "detail", error)
                ),
            })

        questions = []
        for question in questionnaire["questions"]:
            registered_question = None
            for key in (
                question.get("question_uuid"),
                question.get("question_id"),
                question.get("question_code"),
            ):
                if key and str(key) in bank_questions_by_key:
                    registered_question = (
                        bank_questions_by_key[str(key)]
                    )
                    break

            questions.append({
                key: value
                for key, value in question.items()
                if key not in {
                    "measurements",
                    "all_measurements",
                }
            } | {
                "prompt": (
                    (
                        registered_question.get("prompt")
                        or registered_question.get("text")
                        or registered_question.get("title")
                    )
                    if registered_question
                    else None
                ),
                "registered_question_found": (
                    registered_question is not None
                ),
            })

        questionnaires.append({
            "questionnaire_id": (
                questionnaire["questionnaire_id"]
            ),
            "connected": questionnaire["connected"],
            "question_count": questionnaire["question_count"],
            "unique_measurement_count": (
                questionnaire["unique_measurement_count"]
            ),
            "observation_count": sum(
                question.get("observation_count", 0)
                for question in questions
            ),
            "questions": questions,
        })

    return {
        "ok": True,
        "schema_version": (
            "questionnaire-sample-catalog-1"
        ),
        "project_id": project_id,
        "study_id": catalog.get("study_id"),
        "available_study_ids": catalog.get("available_study_ids", []),
        "study_scope_required": catalog.get("study_scope_required", False),
        "connected_questionnaire_ids": (
            catalog["connected_questionnaire_ids"]
        ),
        "questionnaires": questionnaires,
        "configuration_issues": (
            catalog["configuration_issues"]
        ),
        "excluded_records_count": (
            catalog["excluded_records_count"]
        ),
        "excluded_records": catalog["excluded_records"],
        "bank_metadata_errors": bank_metadata_errors,
        "details_loading": "on_question_selection",
    }


@app.get("/research/questionnaire-dataset")
def get_questionnaire_dataset(
    request: Request,
    questionnaire_id: str,
    question_uuid: str,
    scope: str = "cross_participant",
    project_id: str = "health_model_pilot",
    study_id: str | None = None,
    participant_reference: str | None = None,
):
    _researcher_session(request)
    normalized_scope = str(scope or "").strip().lower()
    if normalized_scope not in {
        "cross_participant",
        "within_participant",
    }:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "QUESTIONNAIRE_DATASET_SCOPE_INVALID",
                "allowed_scopes": [
                    "cross_participant",
                    "within_participant",
                ],
            },
        )

    if (
        normalized_scope == "within_participant"
        and not participant_reference
    ):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "PARTICIPANT_REFERENCE_REQUIRED",
            },
        )

    catalog = build_questionnaire_measurement_catalog(
        project_id=project_id,
        study_id=study_id,
        questionnaire_id=questionnaire_id,
        include_all_measurements=True,
    )
    questionnaire = next(
        (
            item
            for item in catalog["questionnaires"]
            if item["questionnaire_id"]
            == questionnaire_id
        ),
        None,
    )
    question = next(
        (
            item
            for item in (
                questionnaire or {}
            ).get("questions", [])
            if str(item.get("question_uuid"))
            == str(question_uuid)
        ),
        None,
    )
    if question is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "QUESTION_MEASUREMENT_SAMPLE_NOT_FOUND",
                "questionnaire_id": questionnaire_id,
                "question_uuid": question_uuid,
            },
        )

    if normalized_scope == "cross_participant":
        observations = list(
            question.get("measurements", [])
        )
        observation_unit = (
            "participant_latest_valid_answer"
        )
    else:
        observations = [
            observation
            for observation in question.get(
                "all_measurements",
                [],
            )
            if observation.get(
                "participant_reference"
            ) == participant_reference
        ]
        observations.sort(
            key=lambda item: (
                item.get("observation_time") or "",
                str(item.get("answer_record_id") or ""),
            )
        )
        observation_unit = (
            "participant_answer_at_observation_time"
        )

    public_question = {
        key: value
        for key, value in question.items()
        if key not in {
            "measurements",
            "all_measurements",
        }
    }

    return {
        "ok": True,
        "schema_version": (
            "questionnaire-analysis-dataset-1"
        ),
        "project_id": project_id,
        "study_id": catalog.get("study_id"),
        "questionnaire_id": questionnaire_id,
        "question": public_question,
        "scope": normalized_scope,
        "participant_reference": (
            participant_reference
            if normalized_scope
            == "within_participant"
            else None
        ),
        "observation_unit": observation_unit,
        "global_time_reference": "UTC",
        "selected_observation_count": len(
            observations
        ),
        "observations": observations,
        "data_loading": "selected_question_only",
    }


def _statistical_method_matches_scales(
    method: dict,
    left_scale: str | None,
    right_scale: str | None,
) -> bool:
    if not left_scale or not right_scale:
        return False
    return any(
        any(
            scale_matches_requirement(
                left_scale,
                requirement,
            )
            for requirement in pattern.get("left", [])
        )
        and any(
            scale_matches_requirement(
                right_scale,
                requirement,
            )
            for requirement in pattern.get("right", [])
        )
        for pattern in method.get("scale_patterns", [])
    )


def _build_questionnaire_multivariable_dataset(
    data: QuestionnaireMultivariableAnalysisInput,
) -> dict:
    question_uuids = list(dict.fromkeys(
        str(value).strip()
        for value in data.question_uuids
        if str(value).strip()
    ))
    if len(question_uuids) not in {2, 3}:
        return {
            "ok": False,
            "status": "two_or_three_response_variables_required",
            "selected_question_count": len(question_uuids),
        }

    scope = str(data.analysis_scope or "").strip().lower()
    if scope not in {
        "cross_participant",
        "within_participant",
        "group_comparison",
    }:
        return {
            "ok": False,
            "status": "questionnaire_analysis_scope_invalid",
        }
    if scope == "within_participant" and not data.participant_reference:
        return {
            "ok": False,
            "status": "participant_reference_required",
        }

    catalog = build_questionnaire_measurement_catalog(
        project_id=data.project_id,
        study_id=data.study_id,
        questionnaire_id=data.questionnaire_id,
        include_all_measurements=True,
    )
    questionnaire = next(
        (
            item
            for item in catalog.get("questionnaires", [])
            if item.get("questionnaire_id") == data.questionnaire_id
        ),
        None,
    )
    if questionnaire is None:
        return {
            "ok": False,
            "status": "questionnaire_results_not_found",
        }

    questions_by_uuid = {
        str(item.get("question_uuid")): item
        for item in questionnaire.get("questions", [])
        if item.get("question_uuid")
    }
    missing = [
        question_uuid
        for question_uuid in question_uuids
        if question_uuid not in questions_by_uuid
    ]
    if missing:
        return {
            "ok": False,
            "status": "selected_response_variables_not_found",
            "missing_question_uuids": missing,
        }

    selected_questions = [
        questions_by_uuid[question_uuid]
        for question_uuid in question_uuids
    ]
    variable_codes = []
    used_codes = set()
    for question in selected_questions:
        base_code = str(
            question.get("question_code")
            or question.get("question_uuid")
        )
        code = base_code
        if code in used_codes:
            code = f"{base_code}__{question['question_uuid']}"
        used_codes.add(code)
        variable_codes.append(code)

    projections = []
    for question in selected_questions:
        observations = (
            question.get("all_measurements", [])
            if scope in {"cross_participant", "group_comparison"}
            else [
                item
                for item in question.get("all_measurements", [])
                if item.get("participant_reference")
                == data.participant_reference
            ]
        )
        by_unit = {}
        for observation in observations:
            if scope in {"cross_participant", "group_comparison"}:
                participant_key = observation.get("participant_reference")
                unit_key = (
                    participant_key,
                    observation.get("session_id"),
                ) if observation.get("session_id") else (
                    participant_key,
                    observation.get("observation_time"),
                )
            else:
                unit_key = (
                    "session",
                    observation.get("session_id"),
                ) if observation.get("session_id") else (
                    "utc_time",
                    observation.get("observation_time"),
                )
            if (
                unit_key in (None, "", (None, None))
                or (
                    isinstance(unit_key, tuple)
                    and unit_key[-1] in (None, "")
                )
            ):
                continue
            by_unit[unit_key] = observation
        projections.append(by_unit)

    complete_units = set(projections[0])
    for projection in projections[1:]:
        complete_units &= set(projection)
    complete_units = sorted(
        complete_units,
        key=lambda value: str(value),
    )
    if scope in {"cross_participant", "group_comparison"}:
        latest_complete_unit_by_participant = {}
        for unit_key in complete_units:
            participant_key = unit_key[0]
            observation_times = [
                projection[unit_key].get("observation_time") or ""
                for projection in projections
            ]
            sort_key = (
                max(observation_times, default=""),
                str(unit_key[1] or ""),
            )
            previous = latest_complete_unit_by_participant.get(
                participant_key
            )
            if previous is None or sort_key > previous[0]:
                latest_complete_unit_by_participant[participant_key] = (
                    sort_key,
                    unit_key,
                )
        complete_units = [
            item[1]
            for _, item in sorted(
                latest_complete_unit_by_participant.items(),
                key=lambda pair: str(pair[0]),
            )
        ]

    answer_records = []
    rows = []
    for unit_key in complete_units:
        row_values = {}
        row_times = {}
        for index, projection in enumerate(projections):
            observation = projection[unit_key]
            variable_code = variable_codes[index]
            question = selected_questions[index]
            row_values[variable_code] = observation.get("answer_value")
            row_times[variable_code] = observation.get("observation_time")
            answer_records.append({
                "answer_record_id": observation.get("answer_record_id"),
                "record_type": "questionnaire_answer",
                "study_id": (
                    observation.get("study_id")
                    or data.study_id
                ),
                "questionnaire_id": data.questionnaire_id,
                "question_uuid": question.get("question_uuid"),
                "question_code": variable_code,
                "title": question.get("prompt") or variable_code,
                "scale_type": question.get("scale_type"),
                "answer_value": observation.get("answer_value"),
                "answer_value_type": observation.get("answer_value_type"),
                "participant_id": observation.get("participant_reference"),
                "subject_link_id": observation.get("participant_reference"),
                "session_id": observation.get("session_id"),
                "observation_time": observation.get("observation_time"),
                "global_time_reference": "UTC",
            })
        rows.append({
            "observation_unit": (
                unit_key
                if isinstance(unit_key, str)
                else list(unit_key)
            ),
            "values": row_values,
            "observation_times": row_times,
        })

    variables = [
        {
            "question_uuid": question.get("question_uuid"),
            "question_code": variable_codes[index],
            "prompt": question.get("prompt"),
            "scale_type": question.get("scale_type"),
            "scale_reference": build_scale_reference(
                question.get("scale_type")
            ) if get_scale_definition(question.get("scale_type")) else None,
        }
        for index, question in enumerate(selected_questions)
    ]

    return {
        "ok": bool(rows),
        "status": "ready" if rows else "no_complete_observation_units",
        "schema_version": "questionnaire-multivariable-dataset-1",
        "project_id": data.project_id,
        "study_id": data.study_id,
        "questionnaire_id": data.questionnaire_id,
        "analysis_scope": scope,
        "participant_reference": data.participant_reference,
        "observation_unit": (
            (
                "participant_group_at_latest_complete_questionnaire_session"
                if scope == "group_comparison"
                else "participant_at_latest_complete_questionnaire_session"
            )
            if scope in {"cross_participant", "group_comparison"}
            else "participant_questionnaire_session"
        ),
        "temporal_alignment": (
            "same_questionnaire_session_with_each_response_time_retained_in_utc"
            if scope == "cross_participant"
            else "same_questionnaire_session_with_each_response_time_retained_in_utc"
        ),
        "global_time_reference": "UTC",
        "selected_question_count": len(variables),
        "complete_observation_unit_count": len(rows),
        "variables": variables,
        "rows": rows,
        "compatible_answer_records": answer_records,
    }


def _questionnaire_pair_options(dataset: dict) -> list[dict]:
    options = []
    for left, right in combinations(dataset.get("variables", []), 2):
        pair_id = (
            f"{left['question_code']}__{right['question_code']}"
        )
        methods = []
        if dataset.get("analysis_scope") == "within_participant":
            options.append({
                "pair_id": pair_id,
                "left_variable": left,
                "right_variable": right,
                "available_methods": [],
                "status": "registered_longitudinal_method_required",
            })
            continue
        for method in METHODS:
            method_id = method.get("method_id")
            if (
                method.get("category") == "standard"
                and method_id in EXECUTABLE_METHOD_IDS
                and (
                    dataset.get("analysis_scope") != "group_comparison"
                    or str(method.get("purpose") or "").startswith("compare_")
                )
                and _statistical_method_matches_scales(
                    method,
                    left.get("scale_type"),
                    right.get("scale_type"),
                )
            ):
                methods.append({
                    "method_id": method_id,
                    "title": method.get("title"),
                    "purpose": method.get("purpose"),
                    "required_conditions": method.get(
                        "required_conditions", []
                    ),
                    "execution_status": "implemented",
                })
        options.append({
            "pair_id": pair_id,
            "left_variable": left,
            "right_variable": right,
            "available_methods": methods,
        })
    return options


def _holm_adjust(p_values: list[float]) -> list[float]:
    count = len(p_values)
    adjusted = [1.0] * count
    running_maximum = 0.0
    for rank, index in enumerate(
        sorted(range(count), key=lambda item: p_values[item])
    ):
        candidate = min(1.0, (count - rank) * p_values[index])
        running_maximum = max(running_maximum, candidate)
        adjusted[index] = running_maximum
    return adjusted


@app.post("/research/questionnaire-analysis/options")
def questionnaire_multivariable_options(
    data: QuestionnaireMultivariableAnalysisInput,
    request: Request,
):
    _researcher_session(request)
    dataset = _build_questionnaire_multivariable_dataset(data)
    return {
        "ok": dataset.get("ok", False),
        "status": dataset.get("status"),
        "dataset": {
            key: value
            for key, value in dataset.items()
            if key != "compatible_answer_records"
        },
        "pair_options": (
            _questionnaire_pair_options(dataset)
            if dataset.get("ok")
            else []
        ),
        "multiple_testing_policy": (
            "holm_family_wise_error_rate"
            if len(data.question_uuids) == 3
            else "not_required_for_single_pair"
        ),
    }


@app.post("/research/questionnaire-analysis/run")
def run_questionnaire_multivariable_analysis(
    data: QuestionnaireMultivariableAnalysisInput,
    request: Request,
):
    _researcher_session(request)
    dataset = _build_questionnaire_multivariable_dataset(data)
    if not dataset.get("ok"):
        return dataset

    pair_options = _questionnaire_pair_options(dataset)
    pair_methods = data.pair_methods or {}
    checks = []
    for pair in pair_options:
        method_id = pair_methods.get(pair["pair_id"])
        allowed_ids = {
            method["method_id"]
            for method in pair["available_methods"]
        }
        if not method_id or method_id not in allowed_ids:
            checks.append({
                "pair_id": pair["pair_id"],
                "status": "method_required_or_incompatible",
                "allowed_method_ids": sorted(allowed_ids),
            })
            continue
        result = check_pair_analysis(
            study_id=data.project_id,
            left_question_code=pair["left_variable"]["question_code"],
            right_question_code=pair["right_variable"]["question_code"],
            method_id=method_id,
            answer_records=dataset["compatible_answer_records"],
        )
        checks.append({
            "pair_id": pair["pair_id"],
            "method_id": method_id,
            **result,
        })

    blocking = [
        check
        for check in checks
        if check.get("status") != "applicable"
    ]
    if blocking:
        return {
            "ok": False,
            "status": "method_applicability_check_blocked_run",
            "checks": checks,
            "blocking_checks": blocking,
            "dataset": {
                key: value
                for key, value in dataset.items()
                if key != "compatible_answer_records"
            },
        }

    results = []
    for check in checks:
        result = run_statistical_method(
            study_id=data.project_id,
            left_question_code=check["left_question_code"],
            right_question_code=check["right_question_code"],
            method_id=check["method_id"],
            answer_records=dataset["compatible_answer_records"],
        )
        results.append({
            "pair_id": check["pair_id"],
            "method_id": check["method_id"],
            **result,
        })

    failed_results = [
        result for result in results if not result.get("ok")
    ]
    if failed_results:
        return {
            "ok": False,
            "status": "statistical_runner_failed",
            "checks": checks,
            "results": results,
        }

    raw_p_values = [float(result["p_value"]) for result in results]
    adjusted_p_values = _holm_adjust(raw_p_values)
    alpha = 0.05
    for result, adjusted_p in zip(results, adjusted_p_values):
        result["raw_p_value"] = result.get("p_value")
        result["holm_adjusted_p_value"] = adjusted_p
        result["family_wise_alpha"] = alpha
        result["family_wise_decision"] = (
            "reject_null_hypothesis"
            if adjusted_p < alpha
            else "do_not_reject_null_hypothesis"
        )

    return {
        "ok": True,
        "status": "completed",
        "analysis_type": (
            "single_pair"
            if len(results) == 1
            else "three_pair_family"
        ),
        "multiple_testing_policy": (
            "holm_family_wise_error_rate"
            if len(results) > 1
            else "not_required_for_single_pair"
        ),
        "dataset": {
            key: value
            for key, value in dataset.items()
            if key != "compatible_answer_records"
        },
        "checks": checks,
        "results": results,
    }

@app.get("/research/analysis/catalog")
def get_research_analysis_catalog(
    request: Request,
    study_id: str,
):
    _researcher_session(request)
    answer_records = []

    for research_record in list_research_records(study_id=study_id):
        records = research_record.get("research_answer_records", [])

        if records:
            answer_records.extend(records)
        else:
            answer_records.extend(
                build_answer_records_from_answers(
                    study_id=research_record.get("study_id") or study_id,
                    record_id=research_record.get("record_id") or "research_record",
                    session_id=research_record.get("session_id"),
                    answers=research_record.get("answers", {}),
                )
            )

    for session in store.list_all():
        if session.study_id != study_id:
            continue

        records = session.research_answer_records or []

        if records:
            answer_records.extend(records)
        else:
            answer_records.extend(
                build_answer_records_from_answers(
                    study_id=session.study_id or study_id,
                    record_id=session.session_id,
                    session_id=session.session_id,
                    answers=session.answers or {},
                )
            )

    return {
        "ok": True,
        **build_analysis_catalog(
            study_id=study_id,
            answer_records=answer_records,
        ),
    }

@app.get("/research/health-model/research-variables")
def list_health_model_research_variables_api():
    return {
        "ok": True,
        "variables": list_health_model_research_variables(),
    }

@app.get("/research/models")
def list_research_models_api(
    request: Request,
    include_inactive: bool = False,
):
    _researcher_session(request)
    return {
        "ok": True,
        "models": (
            list_registered_calculation_models(
                include_inactive=include_inactive,
            )
        ),
    }

@app.get(
    "/research/models/{model_id}/parameters"
)
def list_model_parameter_definitions_api(
    model_id: str,
    include_inactive: bool = False,
    include_all_versions: bool = False,
):
    if model_id != "health_model_v6_1":
        raise HTTPException(
            status_code=404,
            detail={
                "error": "MODEL_NOT_FOUND",
                "model_id": model_id,
            },
        )

    registry = build_model_parameter_registry()

    definitions = (
        registry.get("definitions", [])
    )

    if not include_inactive:
        definitions = [
            definition
            for definition in definitions
            if (
                definition.get(
                    "lifecycle_status"
                )
                or definition.get("status")
            )
            == "active"
        ]

    if not include_all_versions:
        latest_by_code = {}

        for definition in definitions:
            parameter_code = definition.get(
                "parameter_code"
            )

            if not parameter_code:
                continue

            previous = latest_by_code.get(
                parameter_code
            )

            current_version = int(
                definition.get(
                    "definition_version",
                    1,
                )
            )

            previous_version = (
                int(
                    previous.get(
                        "definition_version",
                        1,
                    )
                )
                if previous
                else None
            )

            if (
                previous is None
                or current_version
                > previous_version
            ):
                latest_by_code[
                    parameter_code
                ] = definition

        definitions = sorted(
            latest_by_code.values(),
            key=lambda definition: str(
                definition.get(
                    "parameter_code"
                )
                or ""
            ),
        )

    return {
        "ok": True,
        "model_id": model_id,
        "registry_schema_version": (
            registry.get(
                "schema_version"
            )
        ),
        "definition_schema_version": (
            registry.get(
                "definition_schema_version"
            )
        ),
        "supported_parameter_kinds": (
            registry.get(
                "supported_parameter_kinds",
                [],
            )
        ),
        "supported_value_types": (
            registry.get(
                "supported_value_types",
                [],
            )
        ),
        "supported_scale_types": (
            registry.get(
                "supported_scale_types",
                [],
            )
        ),
        "supported_calculation_statuses": (
            registry.get(
                "supported_calculation_statuses",
                [],
            )
        ),
        "supported_lifecycle_statuses": (
            registry.get(
                "supported_lifecycle_statuses",
                [],
            )
        ),
        "supported_scientific_statuses": (
            registry.get(
                "supported_scientific_statuses",
                [],
            )
        ),
        "include_inactive": include_inactive,
        "include_all_versions": (
            include_all_versions
        ),
        "definition_count": len(
            definitions
        ),
        "definitions": definitions,
    }

@app.get(
    "/research/models/{model_id}/parameters/"
    "{parameter_code}"
)
def get_model_parameter_definition_api(
    model_id: str,
    parameter_code: str,
    definition_version: int | None = None,
    include_inactive: bool = False,
):
    if model_id != "health_model_v6_1":
        raise HTTPException(
            status_code=404,
            detail={
                "error": "MODEL_NOT_FOUND",
                "model_id": model_id,
            },
        )

    definition = (
        get_model_parameter_definition(
            parameter_code,
            definition_version=(
                definition_version
            ),
            include_inactive=(
                include_inactive
            ),
        )
    )

    if definition is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": (
                    "MODEL_PARAMETER_DEFINITION_NOT_FOUND"
                ),
                "model_id": model_id,
                "parameter_code": (
                    parameter_code
                ),
                "definition_version": (
                    definition_version
                ),
            },
        )

    return {
        "ok": True,
        "model_id": model_id,
        "definition": definition,
    }


@app.get("/research/constructor/catalog")
def get_model_constructor_catalog_api(
    include_all_versions: bool = False,
):
    """One catalogue for the constructor; calculation registries stay separate."""
    return {
        "ok": True,
        "model_id": "health_model_v6_1",
        "parameters": list_registered_parameter_definitions(
            include_inactive=True,
            include_all_versions=include_all_versions,
        ),
        "mechanisms": list_registered_mechanism_definitions(
            include_inactive=True,
            include_all_versions=include_all_versions,
        ),
        "development_statuses": ["draft", "trial", "active"],
        "automatic_fields": [
            "stable_uuid",
            "definition_version",
            "schema_versions",
            "registry_registration",
            "scale_reference_when_scale_is_selected",
            "global_time_reference_requirement",
            "provenance",
        ],
        "scale_binding_policy": {
            "required": False,
            "when_selected": "registered_scale_format_is_strictly_validated",
            "when_unbound": "no_standard_statistical_method_is_assumed",
        },
    }


@app.get("/research/constructor/questions")
def get_model_constructor_question_catalog_api(
    lang: str = "ru",
):
    if lang not in {"ru", "en", "es"}:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "UNSUPPORTED_CONTENT_LANGUAGE",
                "language": lang,
            },
        )

    banks = list_question_banks().get("banks", [])
    registered_bank_ids = {
        bank.get("id")
        for bank in banks
        if bank.get("id")
    }
    for assessment in list_assessments():
        assessment_id = assessment.get("id")
        if (
            not assessment_id
            or assessment_id in registered_bank_ids
        ):
            continue
        assessment_title = assessment.get("title") or {}
        banks.append({
            "id": assessment_id,
            "title": (
                assessment_title.get(lang)
                if isinstance(assessment_title, dict)
                else str(assessment_title)
            ) or assessment_id,
            "status": assessment.get("status") or "active",
            "registry_source": "assessment_registry",
        })
        registered_bank_ids.add(assessment_id)
    question_references = []
    bank_errors = []

    for bank in banks:
        bank_id = bank.get("id")
        if not bank_id:
            continue
        try:
            bank_data = read_question_bank(bank_id, lang=lang)
        except (HTTPException, FileNotFoundError, ValueError, KeyError) as error:
            bank_errors.append({
                "bank_id": bank_id,
                "error": str(getattr(error, "detail", error)),
            })
            continue

        for question in bank_data.get("questions", []):
            question_code = question.get("code") or question.get("question_code")
            if not question_code:
                continue
            scale_type = question.get("scale_type") or (question.get("scale") or {}).get("scale_type")
            scale_definition = get_scale_definition(scale_type)
            options = question.get("answer_options") or question.get("options") or []
            allowed_range = question.get("allowed_range") or {}
            question_references.append({
                "reference_schema_version": "registered-question-reference-1",
                "bank_id": bank_id,
                "bank_title": bank.get("title") or bank_id,
                "language": lang,
                "question_id": question.get("question_id") or question_code,
                "question_code": question_code,
                "question_version": question.get("question_version") or question.get("version") or 1,
                "status": question.get("status") or bank.get("status") or "active",
                "prompt": question.get("prompt") or question.get("text") or question.get("title") or "",
                "question_type": question.get("question_type") or question.get("type"),
                "response_type": question.get("response_type") or question.get("type"),
                "value_type": question.get("value_type"),
                "allowed_values": question.get("allowed_values") or [
                    option.get("value") for option in options if isinstance(option, dict)
                ],
                "allowed_range": {
                    "minimum": allowed_range.get("minimum", allowed_range.get("min", question.get("min"))),
                    "maximum": allowed_range.get("maximum", allowed_range.get("max", question.get("max"))),
                    "step": allowed_range.get("step", question.get("step")),
                },
                "answer_options": options,
                "score_direction": question.get("score_direction") or (question.get("scale") or {}).get("direction"),
                "unit": question.get("unit") or (question.get("scale") or {}).get("unit"),
                "scale_type": scale_type,
                "scale_reference": (
                    build_scale_reference(scale_type)
                    if scale_definition is not None
                    else None
                ),
                "scale_binding_status": (
                    "registered" if scale_definition is not None else "unbound"
                ),
                "measurement_level": (
                    scale_definition.get("measurement_level")
                    if scale_definition is not None else None
                ),
                "numeric_nature": (
                    scale_definition.get("numeric_nature")
                    if scale_definition is not None else None
                ),
                "value_structure": (
                    scale_definition.get("value_structure")
                    if scale_definition is not None else None
                ),
            })

    return {
        "ok": True,
        "language": lang,
        "banks": banks,
        "question_count": len(question_references),
        "questions": question_references,
        "bank_errors": bank_errors,
    }


@app.post("/research/constructor/calculation-options")
def get_model_constructor_calculation_options_api(
    payload: dict,
):
    bindings = payload.get("question_bindings") or []
    if not isinstance(bindings, list):
        raise HTTPException(
            status_code=400,
            detail={"error": "QUESTION_BINDINGS_MUST_BE_LIST"},
        )
    return build_compatible_calculation_options(
        bindings,
        repeated_measurements=bool(payload.get("repeated_measurements")),
        ordered_measurements=bool(payload.get("ordered_measurements")),
    )


@app.get("/research/observable-markers")
def list_observable_markers_api(
    include_drafts: bool = True,
):
    return list_observable_markers(
        include_drafts=include_drafts,
    )


@app.post("/research/observable-markers/draft")
def save_observable_marker_draft_api(
    payload: dict,
):
    result = upsert_observable_marker_draft(payload)
    if result.get("ok") is not True:
        raise HTTPException(status_code=422, detail=result)
    return result


@app.post(
    "/research/observable-markers/{marker_code}/{definition_version}/transition/{target_status}"
)
def transition_observable_marker_api(
    marker_code: str,
    definition_version: int,
    target_status: str,
):
    result = transition_observable_marker(
        marker_code,
        definition_version,
        target_status,
    )
    if result.get("ok") is not True:
        raise HTTPException(status_code=422, detail=result)
    return result


@app.delete(
    "/research/observable-markers/{marker_code}/{definition_version}"
)
def delete_observable_marker_draft_api(
    marker_code: str,
    definition_version: int,
):
    result = delete_observable_marker_draft(
        marker_code,
        definition_version,
    )
    if result.get("ok") is not True:
        raise HTTPException(status_code=422, detail=result)
    return result


def _constructor_result_or_error(result: dict):
    if result.get("ok") is True:
        return result
    status = result.get("status")
    status_code = 422 if status in {
        "definition_invalid",
        "transition_validation_failed",
        "parameter_code_required",
        "mechanism_code_required",
    } else 409
    if status == "definition_not_found":
        status_code = 404
    raise HTTPException(status_code=status_code, detail=result)


@app.post("/research/constructor/{construct_type}/draft")
def upsert_constructor_draft_api(
    construct_type: str,
    definition: dict,
):
    if construct_type == "parameter":
        result = upsert_custom_model_parameter_draft(definition)
    elif construct_type == "mechanism":
        result = upsert_custom_mechanism_draft(definition)
    else:
        raise HTTPException(
            status_code=404,
            detail={"error": "CONSTRUCT_TYPE_NOT_FOUND", "construct_type": construct_type},
        )
    return _constructor_result_or_error(result)


@app.post(
    "/research/constructor/{construct_type}/{construct_code}/"
    "{definition_version}/transition/{target_status}"
)
def transition_constructor_definition_api(
    construct_type: str,
    construct_code: str,
    definition_version: int,
    target_status: str,
):
    if construct_type == "parameter":
        result = transition_custom_model_parameter_definition(
            construct_code, definition_version, target_status
        )
    elif construct_type == "mechanism":
        result = transition_custom_mechanism_definition(
            construct_code, definition_version, target_status
        )
    else:
        raise HTTPException(
            status_code=404,
            detail={"error": "CONSTRUCT_TYPE_NOT_FOUND", "construct_type": construct_type},
        )
    return _constructor_result_or_error(result)


@app.delete(
    "/research/constructor/{construct_type}/{construct_code}/"
    "{definition_version}"
)
def delete_constructor_draft_api(
    construct_type: str,
    construct_code: str,
    definition_version: int,
):
    if construct_type == "parameter":
        result = delete_custom_model_parameter_draft(
            construct_code, definition_version
        )
    elif construct_type == "mechanism":
        result = delete_custom_mechanism_draft(
            construct_code, definition_version
        )
    else:
        raise HTTPException(
            status_code=404,
            detail={"error": "CONSTRUCT_TYPE_NOT_FOUND", "construct_type": construct_type},
        )
    return _constructor_result_or_error(result)


@app.get("/research/mechanisms")
def list_mechanism_definitions_api(
    include_inactive: bool = False,
    include_all_versions: bool = False,
):
    definitions = list_registered_mechanism_definitions(
        include_inactive=include_inactive,
        include_all_versions=include_all_versions,
    )
    return {
        "ok": True,
        "definition_count": len(definitions),
        "definitions": definitions,
    }


@app.get("/research/mechanisms/{mechanism_code}")
def get_mechanism_definition_api(
    mechanism_code: str,
    definition_version: int | None = None,
    include_inactive: bool = False,
):
    definition = get_mechanism(
        mechanism_code,
        definition_version=definition_version,
        include_inactive=include_inactive,
    )
    if definition is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "MECHANISM_DEFINITION_NOT_FOUND"},
        )
    return {"ok": True, "definition": definition}


@app.post("/research/model-calculations")
def create_model_calculation_api(
    data: CreateModelCalculationInput,
):
    input_references = [
        ModelCalculationInputReference(
            source_type=(
                reference.source_type
            ),
            source_record_type=(
                reference.source_record_type
            ),
            source_record_id=(
                reference.source_record_id
            ),
            source_session_id=(
                reference.source_session_id
            ),
            source_submission_id=(
                reference.source_submission_id
            ),
            participant_id=(
                reference.participant_id
            ),
            subject_link_id=(
                reference.subject_link_id
            ),
            study_id=(
                reference.study_id
            ),
            domain_id=(
                reference.domain_id
            ),
            observation_time=(
                reference.observation_time
            ),
            global_time_reference=(
                reference.global_time_reference
            ),
            selected_variable_codes=list(
                reference
                .selected_variable_codes
            ),
            selected_record_ids=list(
                reference
                .selected_record_ids
            ),
            provenance=dict(
                reference.provenance
            ),
        )
        for reference
        in data.input_references
    ]

    try:
        run = (
            model_calculation_service
            .create_run(
                model_id=data.model_id,
                model_version=(
                    data.model_version
                ),
                calculation_version=(
                    data.calculation_version
                ),
                participant_id=(
                    data.participant_id
                ),
                subject_link_id=(
                    data.subject_link_id
                ),
                calculation_scope=(
                    data.calculation_scope
                ),
                observation_unit=(
                    data.observation_unit
                ),
                input_references=(
                    input_references
                ),
                input_snapshot=dict(
                    data.input_snapshot
                ),
                input_quality=dict(
                    data.input_quality
                ),
                provenance=dict(
                    data.provenance
                ),
            )
        )
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail={
                "error": (
                    "CALCULATION_MODEL_NOT_REGISTERED"
                ),
                "details": str(error),
            },
        )

    return {
        "ok": True,
        "run": (
            serialize_model_calculation_run(
                run
            )
        ),
    }
    
@app.post(
    "/research/model-calculations/"
    "{calculation_run_id}/run"
)
def run_model_calculation_api(
    calculation_run_id: str,
):
    try:
        run = (
            model_calculation_service
            .run_calculation(
                calculation_run_id
            )
        )

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail={
                "error": (
                    "MODEL_CALCULATION_RUN_NOT_FOUND"
                ),
                "calculation_run_id": (
                    calculation_run_id
                ),
            },
        )

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail={
                "error": (
                    "MODEL_CALCULATION_RUN_CONFLICT"
                ),
                "calculation_run_id": (
                    calculation_run_id
                ),
                "details": str(error),
            },
        )

    return {
        "ok": True,
        "run": (
            serialize_model_calculation_run(
                run
            )
        ),
    }

@app.get(
    "/research/model-calculations/"
    "{calculation_run_id}"
)
def get_model_calculation_api(
    calculation_run_id: str,
    request: Request,
):
    _researcher_session(request)
    run = model_calculation_service.get_run(
        calculation_run_id
    )

    if run is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": (
                    "MODEL_CALCULATION_RUN_NOT_FOUND"
                ),
                "calculation_run_id": (
                    calculation_run_id
                ),
            },
        )

    return {
        "ok": True,
        "run": (
            serialize_model_calculation_run(
                run
            )
        ),
    }

@app.get("/research/model-parameters/records")
def list_model_parameter_records_api(
    request: Request,
    model_id: str | None = None,
    study_id: str | None = None,
    parameter_id: str | None = None,
    parameter_code: str | None = None,
    calculation_run_id: str | None = None,
    participant_id: str | None = None,
    subject_link_id: str | None = None,
    calculation_status: str | None = None,
    include_invalidated_runs: bool = False,
):
    _researcher_session(request)
    records = (
        model_calculation_store
        .list_parameter_records(
            model_id=model_id,
            study_id=study_id,
            parameter_id=parameter_id,
            parameter_code=parameter_code,
            calculation_run_id=(
                calculation_run_id
            ),
            participant_id=participant_id,
            subject_link_id=subject_link_id,
            calculation_status=(
                calculation_status
            ),
            include_invalidated_runs=(
                include_invalidated_runs
            ),
        )
    )

    return {
        "ok": True,
        "record_source": (
            "model_calculation_store"
        ),
        "model_id": model_id,
        "study_id": study_id,
        "parameter_id": parameter_id,
        "parameter_code": parameter_code,
        "calculation_run_id": (
            calculation_run_id
        ),
        "participant_id": participant_id,
        "subject_link_id": subject_link_id,
        "calculation_status": (
            calculation_status
        ),
        "include_invalidated_runs": (
            include_invalidated_runs
        ),
        "parameter_record_count": len(
            records
        ),
        "parameter_records": records,
    }

@app.get("/research/model-parameter-measurements")
def list_model_parameter_measurements_api(
    request: Request,
    model_id: str = "health_model_v6_1",
    study_id: str | None = None,
):
    _researcher_session(request)
    parameter_records = (
        model_calculation_store
        .list_parameter_records(
            model_id=model_id,
            study_id=study_id,
            include_invalidated_runs=False,
        )
    )

    return build_model_parameter_measurement_catalog(
        parameter_records=parameter_records,
        model_id=model_id,
    )

@app.get("/research/model-parameters/available")
def list_available_model_parameters_api(
    request: Request,
    study_id: str = "health_model",
):
    _researcher_session(request)
    catalog = build_available_model_parameter_catalog(
        research_records=list_research_records(
            study_id=study_id,
        ),
        pilot_sessions=store.list_all(),
        study_id=study_id,
    )

    return {
        "ok": True,
        **catalog,
    }

@app.get("/research/model-parameters/pair-options")
def get_model_parameter_pair_options_api(
    request: Request,
    left_parameter_code: str,
    right_parameter_code: str,
    model_id: str = "health_model_v6_1",
    study_id: str | None = None,
):
    _researcher_session(request)
    parameter_records = (
        model_calculation_store
        .list_parameter_records(
            model_id=model_id,
            study_id=study_id,
            include_invalidated_runs=False,
        )
    )

    return (
        build_selected_model_parameter_pair_options(
            parameter_records=parameter_records,
            model_id=model_id,
            left_parameter_code=(
                left_parameter_code
            ),
            right_parameter_code=(
                right_parameter_code
            ),
        )
    )

@app.get("/research/model-parameters/dependencies")
def list_available_model_parameter_dependencies_api(
    request: Request,
    study_id: str = "health_model",
):
    _researcher_session(request)
    return build_available_model_parameter_dependencies(
        research_records=list_research_records(
            study_id=study_id,
        ),
        pilot_sessions=store.list_all(),
        study_id=study_id,
    )

@app.get("/research/model-parameters/pair-participants")
def list_model_parameter_pair_participants_api(
    request: Request,
    left_parameter_code: str,
    right_parameter_code: str,
    model_id: str = "health_model_v6_1",
    study_id: str | None = None,
):
    _researcher_session(request)
    parameter_records = (
        model_calculation_store
        .list_parameter_records(
            model_id=model_id,
            study_id=study_id,
            include_invalidated_runs=False,
        )
    )

    return list_model_parameter_pair_participants(
        parameter_records=parameter_records,
        model_id=model_id,
        left_parameter_code=(
            left_parameter_code
        ),
        right_parameter_code=(
            right_parameter_code
        ),
    )

@app.post("/research/analysis/check")
def check_research_analysis(
    data: AnalysisCheckInput,
    request: Request,
):
    _researcher_session(request)
    answer_records = collect_answer_records_for_study(
        data.study_id,
    )

    result = check_pair_analysis(
        study_id=data.study_id,
        left_question_code=data.left_question_code,
        right_question_code=data.right_question_code,
        method_id=data.method_id,
        answer_records=answer_records,
    )

    return result

@app.post("/research/model-parameters/dataset")
def build_model_parameter_dataset_api(
    data: ModelParameterDatasetInput,
    request: Request,
):
    _researcher_session(request)
    parameter_records = (
        model_calculation_store
        .list_parameter_records(
            model_id=data.model_id,
            study_id=data.study_id,
            include_invalidated_runs=False,
        )
    )

    return build_model_parameter_pair_dataset(
        parameter_records=parameter_records,
        model_id=data.model_id,
        left_parameter_code=(
            data.left_parameter_code
        ),
        right_parameter_code=(
            data.right_parameter_code
        ),
        analysis_scope=data.analysis_scope,
        repeated_measure_policy=(
            data.repeated_measure_policy
        ),
        participant_reference=(
            data.participant_reference
        ),
    )

@app.post("/research/model-parameters/check")
def check_model_parameter_analysis(
    data: ParameterAnalysisCheckInput,
    request: Request,
):
    _researcher_session(request)
    parameter_records = (
        model_calculation_store
        .list_parameter_records(
            model_id=data.model_id,
            study_id=data.study_id,
            include_invalidated_runs=False,
        )
    )

    dataset = build_model_parameter_pair_dataset(
        parameter_records=parameter_records,
        model_id=data.model_id,
        left_parameter_code=data.left_parameter_code,
        right_parameter_code=data.right_parameter_code,
        analysis_scope=data.analysis_scope,
        repeated_measure_policy=data.repeated_measure_policy,
        participant_reference=data.participant_reference,
    )

    if not dataset.get("ok"):
        return {
            "ok": False,
            "status": "parameter_dataset_not_ready",
            "dataset_status": dataset.get("status"),
            "dataset": dataset,
        }

    return check_model_parameter_pair_analysis(
        dataset=dataset,
        method_id=data.method_id,
    )

@app.post(
    "/research/model-parameters/statistical/run"
)
def run_model_parameter_statistical_analysis(
    data: ModelParameterStatisticalRunInput,
    request: Request,
):
    _researcher_session(request)
    parameter_records = (
        model_calculation_store
        .list_parameter_records(
            model_id=data.model_id,
            study_id=data.study_id,
            include_invalidated_runs=False,
        )
    )

    dataset = build_model_parameter_pair_dataset(
        parameter_records=parameter_records,
        model_id=data.model_id,
        left_parameter_code=(
            data.left_parameter_code
        ),
        right_parameter_code=(
            data.right_parameter_code
        ),
        analysis_scope=data.analysis_scope,
        repeated_measure_policy=(
            data.repeated_measure_policy
        ),
        participant_reference=(
            data.participant_reference
        ),
    )

    if not dataset.get("ok"):
        return {
            "ok": False,
            "status": (
                "parameter_dataset_not_ready"
            ),
            "dataset_status": dataset.get(
                "status"
            ),
            "dataset": dataset,
        }

    check_result = (
        check_model_parameter_pair_analysis(
            dataset=dataset,
            method_id=data.method_id,
        )
    )

    if (
        check_result.get("status")
        != "applicable"
    ):
        return {
            "ok": False,
            "status": "method_not_applicable",
            "check_result": check_result,
            "dataset": dataset,
        }

    answer_records = dataset.get(
        "compatible_answer_records",
        [],
    )

    result = run_statistical_method(
        study_id=data.model_id,
        left_question_code=(
            data.left_parameter_code
        ),
        right_question_code=(
            data.right_parameter_code
        ),
        method_id=data.method_id,
        answer_records=answer_records,
    )

    return {
        **result,
        "variable_source": (
            "calculated_model_parameter"
        ),
        "model_id": data.model_id,
        "analysis_scope": (
            data.analysis_scope
        ),
        "observation_unit": dataset.get(
            "observation_unit"
        ),
        "repeated_measure_policy": (
            data.repeated_measure_policy
        ),
        "participant_reference": (
            data.participant_reference
        ),
        "left_parameter_code": (
            data.left_parameter_code
        ),
        "right_parameter_code": (
            data.right_parameter_code
        ),
        "selected_observation_count": (
            dataset.get(
                "selected_observation_count"
            )
        ),
        "dataset_formation": dataset.get(
            "dataset_formation"
        ),
        "applicability_check": check_result,
    }

@app.post("/research/analysis/statistical/run")
def run_statistical_analysis(
    data: StatisticalAnalysisRunInput,
    request: Request,
):
    _researcher_session(request)
    answer_records = collect_answer_records_for_study(
        data.study_id,
    )

    check_result = check_pair_analysis(
        study_id=data.study_id,
        left_question_code=data.left_question_code,
        right_question_code=data.right_question_code,
        method_id=data.method_id,
        answer_records=answer_records,
    )

    if check_result.get("status") != "applicable":
        return {
            "ok": False,
            "status": "method_not_applicable",
            "check_result": check_result,
        }

    result = run_statistical_method(
        study_id=data.study_id,
        left_question_code=data.left_question_code,
        right_question_code=data.right_question_code,
        method_id=data.method_id,
        answer_records=answer_records,
    )

    return result

@app.get("/analysis-builder", response_class=HTMLResponse)
def analysis_builder_page():
    return Path("static/analysis_builder.html").read_text(encoding="utf-8")

@app.get("/health-model-research-entities", response_class=HTMLResponse)
def health_model_research_entities_page():
    return Path(
        "static/health_model_research_entities.html"
    ).read_text(
        encoding="utf-8"
    )

@app.get("/question-metadata", response_class=HTMLResponse)
def question_metadata_page():
    return Path(
        "static/question_metadata.html"
    ).read_text(
        encoding="utf-8"
    )


def _editor_result_or_error(result: dict):
    if result.get("ok") is True:
        return result
    status = result.get("status")
    status_code = 404 if status in {"definition_not_found", "session_not_found"} else 409
    if status in {"definition_invalid", "transition_validation_failed", "question_identity_required"}:
        status_code = 422
    raise HTTPException(status_code=status_code, detail=result)


def _find_question(bank_id: str, question_code: str, language: str) -> dict | None:
    bank = read_question_bank(bank_id, lang=language)
    for question in bank.get("questions", []):
        if str(question.get("code") or question.get("question_code") or "") == question_code:
            return question
    return None


def _create_question_bank_files(bank_code: str) -> Path:
    base_path = Path("question_banks") / bank_code
    if base_path.exists():
        raise FileExistsError(bank_code)
    base_path.mkdir(parents=True)
    files = {
        "ru": ("QUESTION_BANK_RU.py", "QUESTION_BANK_RU"),
        "en": ("QUESTION_BANK_EN.py", "QUESTION_BANK_EN"),
        "es": ("QUESTION_BANK_ES.py", "QUESTION_BANK_ES"),
    }
    for filename, variable_name in files.values():
        (base_path / filename).write_text(f"{variable_name} = {{}}\n", encoding="utf-8")
    (base_path / "__init__.py").write_text(
        "from .QUESTION_BANK_RU import QUESTION_BANK_RU\n"
        "from .QUESTION_BANK_EN import QUESTION_BANK_EN\n"
        "from .QUESTION_BANK_ES import QUESTION_BANK_ES\n\n"
        "QUESTION_BANKS = {\n"
        '    "ru": QUESTION_BANK_RU,\n'
        '    "en": QUESTION_BANK_EN,\n'
        '    "es": QUESTION_BANK_ES,\n'
        "}\n\n"
        "def get_question_bank(lang: str):\n"
        '    return QUESTION_BANKS.get(lang, QUESTION_BANK_RU)\n',
        encoding="utf-8",
    )
    return base_path


@app.post("/research/editors/question-banks")
def create_question_bank_from_editor(payload: dict):
    reserved_codes = {
        str(bank.get("id")) for bank in list_question_banks().get("banks", [])
    }
    result = register_question_bank(
        title=str(payload.get("title") or ""),
        language=str(payload.get("language") or "ru"),
        actor_id=str(payload.get("actor_id") or ""),
        reason=str(payload.get("reason") or ""),
        reserved_codes=reserved_codes,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=422, detail=result)
    bank = result["bank"]
    try:
        path = _create_question_bank_files(bank["bank_code"])
    except Exception as error:
        rollback_question_bank_registration(bank["bank_code"], bank["bank_id"])
        raise HTTPException(
            status_code=500,
            detail={"error": "QUESTION_BANK_STORAGE_CREATE_FAILED", "message": str(error)},
        ) from error
    audit = append_audit_event(
        action="question_bank_created",
        actor_id=str(payload.get("actor_id") or ""),
        object_type="question_bank",
        object_id=bank["bank_id"],
        reason=str(payload.get("reason") or ""),
        details={"bank_code": bank["bank_code"], "path": str(path)},
    )
    return {"ok": True, "bank": bank, "audit_event": audit}


def _build_question_editor_base(bank_id: str, question_code: str) -> dict:
    localized = {language: _find_question(bank_id, question_code, language) for language in ("ru", "en", "es")}
    source = localized.get("ru") or localized.get("en") or localized.get("es")
    if source is None:
        raise HTTPException(status_code=404, detail={"error": "QUESTION_NOT_FOUND", "bank_id": bank_id, "question_code": question_code})
    translations = {}
    for language, question in localized.items():
        question = question or source
        translations[language] = {
            "prompt": question.get("prompt") or question.get("text") or question.get("title") or "",
            "answer_options": question.get("answer_options") or question.get("options") or [],
        }
    raw_question_type = source.get("question_type") or source.get("type") or "single_choice"
    raw_response_type = source.get("response_type") or source.get("type") or "single_choice"
    raw_scale_type = source.get("scale_type") or (source.get("scale") or {}).get("scale_type")
    normalized_question_type = normalize_question_type_id(raw_question_type)
    normalized_response_type = normalize_response_type_id(raw_response_type)
    normalized_scale_type = normalize_scale_type_id(raw_scale_type)
    return {
        "bank_id": bank_id,
        "question_code": question_code,
        "question_id": source.get("question_id"),
        "base_version": source.get("question_version") or source.get("version") or 1,
        "translations": translations,
        "question_type": normalized_question_type,
        "response_type": normalized_response_type,
        "presentation_type": source.get("presentation_type") or source.get("presentation"),
        "scale_type": normalized_scale_type,
        "score_direction": source.get("score_direction") or (source.get("scale") or {}).get("direction"),
        "unit": source.get("unit") or (source.get("scale") or {}).get("unit"),
        "allowed_range": source.get("allowed_range") or {},
        "allowed_values": source.get("allowed_values") or [],
        "category": source.get("category") or source.get("domain") or source.get("block"),
        "routing": source.get("routing") or {},
        "calculation_role": source.get("calculation_role") or {},
        "missing_value_policy": source.get("missing_value_policy") or {},
        "marker_references": source.get("marker_references") or [],
        "authorship": source.get("authorship") or {},
        "legacy_mapping": {
            "source_question_type": raw_question_type,
            "source_response_type": raw_response_type,
            "source_scale_type": raw_scale_type,
            "question_type_normalized": raw_question_type != normalized_question_type,
            "response_type_normalized": raw_response_type != normalized_response_type,
            "scale_type_normalized": raw_scale_type != normalized_scale_type,
            "source_preserved_in_registered_bank": True,
        },
    }


@app.get("/research/editors/questions")
def list_question_editor_catalog(lang: str = "ru"):
    if lang not in {"ru", "en", "es"}:
        raise HTTPException(status_code=400, detail={"error": "UNSUPPORTED_CONTENT_LANGUAGE"})
    catalog = get_model_constructor_question_catalog_api(lang=lang)
    registered_banks = {
        bank["bank_code"]: bank for bank in list_registered_question_banks()
    }
    for bank in catalog.get("banks", []):
        registered = registered_banks.get(bank.get("id"))
        if registered is not None:
            bank["title"] = registered["titles"].get(lang) or next(
                (value for value in registered["titles"].values() if value),
                registered["bank_code"],
            )
            bank["bank_uuid"] = registered["bank_id"]
            bank["status"] = registered["development_status"]

    known = {
        (question.get("bank_id"), question.get("question_code"))
        for question in catalog.get("questions", [])
    }
    latest_editor_versions: dict[tuple[str, str], dict] = {}
    for definition in list_question_versions():
        key = (definition["bank_id"], definition["question_code"])
        current = latest_editor_versions.get(key)
        if current is None or definition["question_version"] > current["question_version"]:
            latest_editor_versions[key] = definition
    for key, definition in latest_editor_versions.items():
        if key in known:
            continue
        translation = definition.get("translations", {}).get(lang) or {}
        catalog.setdefault("questions", []).append({
            "reference_schema_version": "registered-question-reference-1",
            "bank_id": definition["bank_id"],
            "question_id": definition["question_id"],
            "question_code": definition["question_code"],
            "question_version": definition["question_version"],
            "status": definition["development_status"],
            "language": lang,
            "prompt": translation.get("prompt") or definition["question_code"],
            "question_type": definition.get("question_type"),
            "response_type": definition.get("response_type"),
            "scale_type": definition.get("scale_type"),
            "scale_reference": definition.get("scale_reference"),
            "answer_options": translation.get("answer_options") or [],
        })
    return {
        "ok": True,
        "language": lang,
        "banks": catalog.get("banks", []),
        "questions": catalog.get("questions", []),
        "versions": list_question_versions(),
        "versioning_policy": {"draft_editable": True, "trial_active_immutable": True, "active_used_by_collection": True},
    }


@app.get("/research/editors/questions/{bank_id}/{question_code}")
def get_question_editor_definition(bank_id: str, question_code: str):
    versions = list_question_versions(bank_id, question_code)
    try:
        base = _build_question_editor_base(bank_id, question_code)
    except HTTPException:
        if not versions:
            raise
        base = deepcopy(sorted(versions, key=lambda item: item["question_version"])[0])
        base["base_version"] = base["question_version"]
    return {"ok": True, "base": base, "versions": versions}


@app.post("/research/editors/questions/draft")
def save_question_editor_draft(payload: dict):
    actor_id = str(payload.pop("actor_id", "")).strip()
    if not actor_id:
        raise HTTPException(status_code=422, detail={"error": "ACTOR_ID_REQUIRED"})
    return _editor_result_or_error(upsert_question_draft(payload, actor_id=actor_id))


@app.post("/research/editors/questions/fork")
def fork_question_editor_draft(payload: dict):
    actor_id = str(payload.get("actor_id") or "").strip()
    reason = str(payload.get("reason") or "").strip()
    target_bank_id = str(payload.get("target_bank_id") or "").strip()
    source_bank_id = str(payload.get("source_bank_id") or "").strip()
    source_question_code = str(payload.get("source_question_code") or "").strip()
    definition = deepcopy(payload.get("definition") or {})
    if not all((actor_id, reason, target_bank_id, source_bank_id, source_question_code)):
        raise HTTPException(status_code=422, detail={"error": "FORK_FIELDS_REQUIRED"})
    if target_bank_id not in {
        str(bank.get("id")) for bank in list_question_banks().get("banks", [])
    }:
        raise HTTPException(status_code=404, detail={"error": "TARGET_QUESTION_BANK_NOT_FOUND"})

    existing_codes = {
        item["question_code"]
        for item in list_question_versions(bank_id=target_bank_id)
    }
    try:
        existing_codes.update(
            str(question.get("code") or question.get("question_code"))
            for question in read_question_bank(target_bank_id, lang="en").get("questions", [])
        )
    except (HTTPException, FileNotFoundError, ValueError, KeyError):
        pass
    question_code = f"q_{uuid.uuid4().hex[:12]}"
    while question_code in existing_codes:
        question_code = f"q_{uuid.uuid4().hex[:12]}"

    for field in ("question_id", "question_version", "base_version", "development_status", "status"):
        definition.pop(field, None)
    definition.update({
        "bank_id": target_bank_id,
        "question_code": question_code,
        "change_reason": reason,
    })
    definition.setdefault("provenance", {})["forked_from"] = {
        "bank_id": source_bank_id,
        "question_code": source_question_code,
        "question_id": payload.get("source_question_id"),
        "question_version": payload.get("source_question_version"),
    }
    result = _editor_result_or_error(upsert_question_draft(definition, actor_id=actor_id))
    result["forked"] = True
    result["target_bank_id"] = target_bank_id
    return result


def _resolve_routing_target(reference: dict, target_status: str) -> tuple[dict | None, dict | None]:
    bank_id = str(reference.get("bank_id") or "").strip()
    question_code = str(reference.get("question_code") or "").strip()
    if not bank_id or not question_code:
        return None, {"code": "ROUTING_TARGET_REQUIRED", "reference": reference}
    versions = list_question_versions(bank_id, question_code)
    eligible_statuses = {"active"} if target_status == "active" else {"trial", "active"}
    eligible = [
        definition for definition in versions
        if definition.get("development_status") in eligible_statuses
    ]
    if eligible:
        target = max(eligible, key=lambda item: item["question_version"])
        return {
            "bank_id": bank_id,
            "question_id": target["question_id"],
            "question_code": question_code,
            "question_version": target["question_version"],
            "version_policy": "pinned",
        }, None
    try:
        target = _find_question(bank_id, question_code, "en")
    except (HTTPException, FileNotFoundError, ValueError, KeyError):
        target = None
    if target is None:
        return None, {
            "code": "ROUTING_TARGET_NOT_FOUND_OR_NOT_READY",
            "bank_id": bank_id,
            "question_code": question_code,
            "required_status": sorted(eligible_statuses),
        }
    return {
        "bank_id": bank_id,
        "question_id": target.get("question_id") or question_code,
        "question_code": question_code,
        "question_version": target.get("question_version") or target.get("version") or 1,
        "version_policy": "pinned",
    }, None


def _validate_and_pin_question_routing(
    definition: dict,
    target_status: str,
) -> dict:
    routing = deepcopy(definition.get("routing") or {})
    errors = []
    source_key = (definition.get("bank_id"), definition.get("question_code"))
    default_action = routing.get("default_action") or "sequential"
    if default_action not in {"sequential", "specific", "terminal"}:
        errors.append({"code": "UNSUPPORTED_DEFAULT_ROUTING_ACTION"})
    if default_action == "specific":
        resolved, error = _resolve_routing_target(
            routing.get("default_target") or {}, target_status
        )
        if error:
            errors.append(error)
        elif (resolved["bank_id"], resolved["question_code"]) == source_key:
            errors.append({"code": "UNCONDITIONAL_SELF_ROUTE_FORBIDDEN"})
        else:
            routing["default_target"] = resolved
    else:
        routing.pop("default_target", None)

    supported_operators = {
        "equals", "not_equals", "greater_than", "less_than",
        "answered", "not_answered",
    }
    pinned_rules = []
    for index, rule in enumerate(routing.get("rules") or []):
        rule = deepcopy(rule)
        if rule.get("operator") not in supported_operators:
            errors.append({"code": "UNSUPPORTED_ROUTING_OPERATOR", "rule_index": index})
        resolved, error = _resolve_routing_target(rule.get("target") or {}, target_status)
        if error:
            errors.append({**error, "rule_index": index})
        elif (resolved["bank_id"], resolved["question_code"]) == source_key:
            errors.append({"code": "SELF_ROUTE_REQUIRES_EXPLICIT_LOOP_GUARD", "rule_index": index})
        else:
            rule["target"] = resolved
        pinned_rules.append(rule)
    routing["rules"] = pinned_rules
    return {"valid": not errors, "errors": errors, "routing": routing}


@app.post("/research/editors/questions/{bank_id}/{question_code}/{question_version}/transition/{target_status}")
def transition_question_editor_version(bank_id: str, question_code: str, question_version: int, target_status: str, payload: dict):
    selected = next((
        definition for definition in list_question_versions(bank_id, question_code)
        if definition["question_version"] == question_version
    ), None)
    if selected is None:
        raise HTTPException(status_code=404, detail={"error": "QUESTION_DEFINITION_NOT_FOUND"})
    routing_validation = _validate_and_pin_question_routing(selected, target_status)
    if not routing_validation["valid"]:
        raise HTTPException(
            status_code=422,
            detail={"error": "QUESTION_ROUTING_INVALID", "validation": routing_validation},
        )
    return _editor_result_or_error(transition_question_definition(
        bank_id, question_code, question_version, target_status,
        actor_id=str(payload.get("actor_id") or ""), reason=str(payload.get("reason") or ""),
        definition_patch={"routing": routing_validation["routing"]},
    ))


@app.delete("/research/editors/questions/{bank_id}/{question_code}/{question_version}")
def delete_question_editor_version(bank_id: str, question_code: str, question_version: int, actor_id: str, reason: str):
    return _editor_result_or_error(delete_question_draft(
        bank_id, question_code, question_version, actor_id=actor_id, reason=reason,
    ))


@app.get("/research/editors/parameters")
def list_parameter_editor_catalog(lang: str = "ru"):
    definitions = list_registered_parameter_definitions(include_inactive=True, include_all_versions=True)
    definitions = filter_model_entities(definitions, MODEL_PARAMETER)
    return {
        "ok": True,
        "definitions": definitions,
        "ray_explanations": {
            f"{item['parameter_code']}:{item.get('definition_version', 1)}": explain_model_definition(item, lang)
            for item in definitions
        },
        "development_statuses": ["draft", "trial", "active"],
    }


@app.get("/research/editors/parameters/{parameter_code}/{definition_version}/ray-explanation")
def explain_parameter_editor_definition(parameter_code: str, definition_version: int, lang: str = "ru"):
    definition = get_model_parameter_definition(parameter_code, definition_version=definition_version, include_inactive=True)
    if definition is None or enrich_model_entity(definition)["entity_classification"]["entity_class"] != MODEL_PARAMETER:
        raise HTTPException(status_code=404, detail={"error": "MODEL_PARAMETER_DEFINITION_NOT_FOUND"})
    return {"ok": True, "explanation": explain_model_definition(definition, lang)}


@app.post("/research/editors/parameters/{parameter_code}/{definition_version}/revision")
def create_parameter_editor_revision(parameter_code: str, definition_version: int, payload: dict):
    source = get_model_parameter_definition(parameter_code, definition_version=definition_version, include_inactive=True)
    if source is None:
        raise HTTPException(status_code=404, detail={"error": "MODEL_PARAMETER_DEFINITION_NOT_FOUND"})
    draft = deepcopy(source)
    for field in ("definition_version", "development_status", "lifecycle_status", "status"):
        draft.pop(field, None)
    draft["change_reason"] = str(payload.get("reason") or "").strip()
    draft.setdefault("provenance", {})
    draft["provenance"].update({"edited_from_version": definition_version, "edited_by": payload.get("actor_id")})
    if not draft["change_reason"] or not payload.get("actor_id"):
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    result = _constructor_result_or_error(upsert_custom_model_parameter_draft(draft))
    result["audit_event"] = append_audit_event(
        action="parameter_revision_created", actor_id=str(payload["actor_id"]),
        object_type="model_parameter_definition",
        object_id=f"{parameter_code}:{result['definition'].get('definition_version')}",
        reason=draft["change_reason"], details={"source_version": definition_version},
    )
    return result


@app.post("/research/editors/parameters/draft")
def save_parameter_editor_draft(payload: dict):
    actor_id = str(payload.pop("actor_id", "")).strip()
    reason = str(payload.get("change_reason") or "").strip()
    if not actor_id or not reason:
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    payload["entity_classification"] = {
        **enrich_model_entity(payload)["entity_classification"],
        "entity_class": MODEL_PARAMETER,
    }
    payload.setdefault("provenance", {})["edited_by"] = actor_id
    result = _constructor_result_or_error(upsert_custom_model_parameter_draft(payload))
    result["audit_event"] = append_audit_event(
        action="parameter_draft_saved", actor_id=actor_id,
        object_type="model_parameter_definition",
        object_id=f"{result['definition'].get('parameter_code')}:{result['definition'].get('definition_version')}",
        reason=reason, details={"status": result.get("status")},
    )
    return result


@app.post("/research/editors/parameters/{parameter_code}/{definition_version}/transition/{target_status}")
def transition_parameter_editor_version(parameter_code: str, definition_version: int, target_status: str, payload: dict):
    actor_id = str(payload.get("actor_id") or "").strip()
    reason = str(payload.get("reason") or "").strip()
    if not actor_id or not reason:
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    result = _constructor_result_or_error(transition_custom_model_parameter_definition(parameter_code, definition_version, target_status))
    result["audit_event"] = append_audit_event(
        action=f"parameter_transitioned_to_{target_status}", actor_id=actor_id,
        object_type="model_parameter_definition", object_id=f"{parameter_code}:{definition_version}",
        reason=reason, details={"target_status": target_status},
    )
    return result


@app.delete("/research/editors/parameters/{parameter_code}/{definition_version}")
def delete_parameter_editor_draft(parameter_code: str, definition_version: int, actor_id: str, reason: str):
    if not actor_id.strip() or not reason.strip():
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    result = _constructor_result_or_error(delete_custom_model_parameter_draft(parameter_code, definition_version))
    result["audit_event"] = append_audit_event(
        action="parameter_draft_deleted", actor_id=actor_id,
        object_type="model_parameter_definition", object_id=f"{parameter_code}:{definition_version}",
        reason=reason, details={"definition_version": definition_version},
    )
    return result


def _logic_definition_or_404(parameter_code: str, definition_version: int) -> dict:
    definition = get_model_parameter_definition(
        parameter_code, definition_version=definition_version, include_inactive=True
    )
    if definition is None or enrich_model_entity(definition)["entity_classification"]["entity_class"] != LOGIC_ENTITY:
        raise HTTPException(status_code=404, detail={"error": "MODEL_LOGIC_DEFINITION_NOT_FOUND"})
    return definition


@app.get("/research/editors/logic")
def list_model_logic_editor_catalog(lang: str = "ru"):
    definitions = filter_model_entities(
        list_registered_parameter_definitions(include_inactive=True, include_all_versions=True),
        LOGIC_ENTITY,
    )
    return {
        "ok": True,
        "definitions": definitions,
        "ray_explanations": {
            f"{item['parameter_code']}:{item.get('definition_version', 1)}": explain_model_definition(item, lang)
            for item in definitions
        },
        "development_statuses": ["draft", "trial", "active"],
    }


@app.get("/research/editors/logic/{parameter_code}/{definition_version}/ray-explanation")
def explain_model_logic_definition(parameter_code: str, definition_version: int, lang: str = "ru"):
    return {"ok": True, "explanation": explain_model_definition(
        _logic_definition_or_404(parameter_code, definition_version), lang
    )}


@app.post("/research/editors/logic/{parameter_code}/{definition_version}/revision")
def create_model_logic_revision(parameter_code: str, definition_version: int, payload: dict):
    source = _logic_definition_or_404(parameter_code, definition_version)
    actor_id = str(payload.get("actor_id") or "").strip()
    reason = str(payload.get("reason") or "").strip()
    if not actor_id or not reason:
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    draft = deepcopy(source)
    for field in ("definition_version", "development_status", "lifecycle_status", "status"):
        draft.pop(field, None)
    draft["change_reason"] = reason
    draft.setdefault("provenance", {}).update({"edited_from_version": definition_version, "edited_by": actor_id})
    result = _constructor_result_or_error(upsert_custom_model_parameter_draft(draft))
    result["audit_event"] = append_audit_event(
        action="model_logic_revision_created", actor_id=actor_id,
        object_type="model_logic_definition",
        object_id=f"{parameter_code}:{result['definition'].get('definition_version')}",
        reason=reason, details={"source_version": definition_version},
    )
    return result


@app.post("/research/editors/logic/draft")
def save_model_logic_draft(payload: dict):
    actor_id = str(payload.pop("actor_id", "")).strip()
    reason = str(payload.get("change_reason") or "").strip()
    if not actor_id or not reason:
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    classification = enrich_model_entity(payload)["entity_classification"]
    classification["entity_class"] = LOGIC_ENTITY
    payload["entity_classification"] = classification
    payload.setdefault("provenance", {})["edited_by"] = actor_id
    result = _constructor_result_or_error(upsert_custom_model_parameter_draft(payload))
    result["audit_event"] = append_audit_event(
        action="model_logic_draft_saved", actor_id=actor_id,
        object_type="model_logic_definition",
        object_id=f"{result['definition'].get('parameter_code')}:{result['definition'].get('definition_version')}",
        reason=reason, details={"status": result.get("status")},
    )
    return result


@app.post("/research/editors/logic/{parameter_code}/{definition_version}/transition/{target_status}")
def transition_model_logic_version(parameter_code: str, definition_version: int, target_status: str, payload: dict):
    _logic_definition_or_404(parameter_code, definition_version)
    actor_id = str(payload.get("actor_id") or "").strip()
    reason = str(payload.get("reason") or "").strip()
    if not actor_id or not reason:
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    result = _constructor_result_or_error(
        transition_custom_model_parameter_definition(parameter_code, definition_version, target_status)
    )
    result["audit_event"] = append_audit_event(
        action=f"model_logic_transitioned_to_{target_status}", actor_id=actor_id,
        object_type="model_logic_definition", object_id=f"{parameter_code}:{definition_version}",
        reason=reason, details={"target_status": target_status},
    )
    return result


@app.delete("/research/editors/logic/{parameter_code}/{definition_version}")
def delete_model_logic_draft(parameter_code: str, definition_version: int, actor_id: str, reason: str):
    _logic_definition_or_404(parameter_code, definition_version)
    if not actor_id.strip() or not reason.strip():
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    result = _constructor_result_or_error(delete_custom_model_parameter_draft(parameter_code, definition_version))
    result["audit_event"] = append_audit_event(
        action="model_logic_draft_deleted", actor_id=actor_id,
        object_type="model_logic_definition", object_id=f"{parameter_code}:{definition_version}",
        reason=reason, details={"definition_version": definition_version},
    )
    return result


@app.get("/research/editors/mechanisms")
def list_mechanism_editor_catalog():
    definitions = list_registered_mechanism_definitions(include_inactive=True, include_all_versions=True)
    return {"ok": True, "definitions": definitions, "development_statuses": ["draft", "trial", "active"]}


@app.post("/research/editors/mechanisms/{mechanism_code}/{definition_version}/revision")
def create_mechanism_editor_revision(mechanism_code: str, definition_version: int, payload: dict):
    source = get_mechanism(mechanism_code, definition_version=definition_version, include_inactive=True)
    if source is None:
        raise HTTPException(status_code=404, detail={"error": "MECHANISM_DEFINITION_NOT_FOUND"})
    draft = deepcopy(source)
    for field in ("definition_version", "development_status", "lifecycle_status", "status"):
        draft.pop(field, None)
    draft["change_reason"] = str(payload.get("reason") or "").strip()
    draft.setdefault("provenance", {})
    draft["provenance"].update({"edited_from_version": definition_version, "edited_by": payload.get("actor_id")})
    if not draft["change_reason"] or not payload.get("actor_id"):
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    result = _constructor_result_or_error(upsert_custom_mechanism_draft(draft))
    result["audit_event"] = append_audit_event(
        action="mechanism_revision_created", actor_id=str(payload["actor_id"]),
        object_type="mechanism_definition",
        object_id=f"{mechanism_code}:{result['definition'].get('definition_version')}",
        reason=draft["change_reason"], details={"source_version": definition_version},
    )
    return result


@app.post("/research/editors/mechanisms/draft")
def save_mechanism_editor_draft(payload: dict):
    actor_id = str(payload.pop("actor_id", "")).strip()
    reason = str(payload.get("change_reason") or "").strip()
    if not actor_id or not reason:
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    payload.setdefault("provenance", {})["edited_by"] = actor_id
    result = _constructor_result_or_error(upsert_custom_mechanism_draft(payload))
    result["audit_event"] = append_audit_event(
        action="mechanism_draft_saved", actor_id=actor_id,
        object_type="mechanism_definition",
        object_id=f"{result['definition'].get('mechanism_code')}:{result['definition'].get('definition_version')}",
        reason=reason, details={"status": result.get("status")},
    )
    return result


@app.post("/research/editors/mechanisms/{mechanism_code}/{definition_version}/transition/{target_status}")
def transition_mechanism_editor_version(mechanism_code: str, definition_version: int, target_status: str, payload: dict):
    actor_id = str(payload.get("actor_id") or "").strip()
    reason = str(payload.get("reason") or "").strip()
    if not actor_id or not reason:
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    result = _constructor_result_or_error(transition_custom_mechanism_definition(mechanism_code, definition_version, target_status))
    result["audit_event"] = append_audit_event(
        action=f"mechanism_transitioned_to_{target_status}", actor_id=actor_id,
        object_type="mechanism_definition", object_id=f"{mechanism_code}:{definition_version}",
        reason=reason, details={"target_status": target_status},
    )
    return result


@app.delete("/research/editors/mechanisms/{mechanism_code}/{definition_version}")
def delete_mechanism_editor_draft(mechanism_code: str, definition_version: int, actor_id: str, reason: str):
    if not actor_id.strip() or not reason.strip():
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    result = _constructor_result_or_error(delete_custom_mechanism_draft(mechanism_code, definition_version))
    result["audit_event"] = append_audit_event(
        action="mechanism_draft_deleted", actor_id=actor_id,
        object_type="mechanism_definition", object_id=f"{mechanism_code}:{definition_version}",
        reason=reason, details={"definition_version": definition_version},
    )
    return result


@app.get("/research/editors/data/contract")
def get_data_editor_contract():
    return transformation_contract()


@app.post("/research/editors/data/preview")
def preview_data_editor_transformation(payload: dict):
    try:
        return transform_records(
            source_type=payload.get("source_type"), records=payload.get("records") or [],
            operations=payload.get("operations") or [], context=payload.get("context") or {},
        )
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail={"error": "TRANSFORMATION_INVALID", "message": str(error)}) from error


@app.post("/research/editors/data/profile")
def profile_data_editor_input(payload: dict):
    try:
        return profile_records(
            source_type=payload.get("source_type"),
            records=payload.get("records") or [],
        )
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail={"error": "DATA_PROFILE_INVALID", "message": str(error)}) from error


@app.post("/research/editors/data/apply")
def apply_data_editor_transformation(payload: dict):
    required = [key for key in ("actor_id", "reason", "recipe_name") if not str(payload.get(key) or "").strip()]
    if required:
        raise HTTPException(status_code=422, detail={"error": "REQUIRED_FIELDS_MISSING", "fields": required})
    try:
        return apply_transformation(
            source_type=payload.get("source_type"), records=payload.get("records") or [],
            operations=payload.get("operations") or [], context=payload.get("context") or {},
            actor_id=payload["actor_id"], reason=payload["reason"], recipe_name=payload["recipe_name"],
        )
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail={"error": "TRANSFORMATION_INVALID", "message": str(error)}) from error


@app.get("/research/editors/data/recipes")
def list_data_editor_recipes(source_type: str | None = None):
    return {"ok": True, "recipes": list_recipes(source_type)}


@app.get("/research/editors/data/sessions")
def list_data_editor_sessions(
    offset: int = 0,
    limit: int = 100,
    status: str | None = None,
    purge_eligible: bool | None = None,
):
    limit = max(1, min(int(limit), 500))
    offset = max(0, int(offset))
    reference_index = build_downstream_reference_index()
    sessions = []
    ordered_sessions = sorted(
        store.list_all(), key=lambda item: item.updated_at, reverse=True
    )
    for session in ordered_sessions:
        if status and session.status.value != status:
            continue
        assessment = assess_empty_session_purge(
            session, reference_index=reference_index
        )
        if purge_eligible is not None and assessment["eligible"] is not purge_eligible:
            continue
        sessions.append({
            "session_id": session.session_id, "study_id": session.study_id,
            "participant_id": session.participant_id, "status": session.status.value,
            "created_at": session.created_at.isoformat(), "updated_at": session.updated_at.isoformat(),
            "answers_count": len(session.answers or {}),
            "research_answer_records_count": len(session.research_answer_records or []),
            "purge_assessment": assessment,
        })
    total = len(sessions)
    return {
        "ok": True,
        "offset": offset,
        "limit": limit,
        "total": total,
        "has_more": offset + limit < total,
        "sessions": sessions[offset:offset + limit],
    }


@app.get("/research/editors/data/sessions/{session_id}/purge-assessment")
def get_empty_session_purge_assessment(session_id: str):
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})
    return {"ok": True, "assessment": assess_empty_session_purge(session)}


@app.delete("/research/editors/data/sessions/{session_id}")
def purge_empty_session_api(session_id: str, payload: dict):
    return _editor_result_or_error(purge_empty_session(
        store, session_id, actor_id=str(payload.get("actor_id") or ""),
        reason=str(payload.get("reason") or ""), confirmation=str(payload.get("confirmation") or ""),
    ))


@app.post("/research/editors/data/sessions/{session_id}/invalidate")
def invalidate_session_from_data_editor(session_id: str, payload: dict):
    actor_id = str(payload.get("actor_id") or "").strip()
    reason = str(payload.get("reason") or "").strip()
    if not actor_id or not reason:
        raise HTTPException(status_code=422, detail={"error": "ACTOR_AND_REASON_REQUIRED"})
    try:
        session = pilot_service.invalidate_session(session_id=session_id, reason=reason)
    except PilotSessionError as error:
        raise HTTPException(status_code=error.status_code, detail=error.to_dict()["error"]) from error
    audit = append_audit_event(
        action="pilot_session_invalidated_from_data_editor", actor_id=actor_id,
        object_type="pilot_session", object_id=session_id, reason=reason,
        details={"status": session.status.value, "hard_deleted": False},
    )
    return {"ok": True, "status": session.status.value, "invalidated": session.invalidated, "audit_event": audit}


@app.get("/research/editors/audit")
def get_research_editor_audit(object_type: str | None = None, object_id: str | None = None, limit: int = 200):
    return {"ok": True, "events": list_audit_events(object_type=object_type, object_id=object_id, limit=limit)}
