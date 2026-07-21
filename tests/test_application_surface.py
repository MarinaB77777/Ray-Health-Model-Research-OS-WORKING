from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
STATIC = ROOT / "static"

PROTECTED_PAGES = {
    "/research-workspace": "research_workspace.html",
    "/model-parameter-constructor": "model_parameter_constructor.html",
    "/data-preparation": "data_preparation.html",
    "/scientific-results": "scientific_results.html",
    "/research-participant": "research_participant.html",
    "/question-metadata": "question_metadata.html",
    "/ray-settings": "ray_settings.html",
    "/researcher-account": "researcher_account.html",
    "/research-project/new": "research_project.html",
    "/probabilistic-methods": "probabilistic_methods.html",
    "/model-training": "model_training.html",
    "/fiji-integration": "fiji_integration.html",
    "/research-lab": "qualitative_hypothesis_lab.html",
    "/technical-hypothesis-lab": "research_lab.html",
    "/citation-workspace": "citation_workspace.html",
}

PROTECTED_API_ROUTES = {
    ("GET", "/ray-colleague/contract"),
    ("POST", "/ray-colleague/researcher/respond"),
    ("POST", "/ray-colleague/participant/respond"),
    ("POST", "/ray-colleague/feedback"),
    ("GET", "/research/scientific-results/catalog"),
    ("GET", "/research/scientific-results/participant"),
    ("GET", "/research/questionnaire-dataset"),
    ("POST", "/research/questionnaire-analysis/options"),
    ("POST", "/research/questionnaire-analysis/run"),
    ("GET", "/research/constructor/catalog"),
    ("GET", "/research/constructor/questions"),
    ("POST", "/research/constructor/calculation-options"),
    ("POST", "/research/analysis/statistical/run"),
    ("GET", "/external-core/contract"),
    ("GET", "/external-core/settings"),
    ("GET", "/external-core/settings/effective"),
    ("POST", "/external-core/settings/drafts"),
    ("GET", "/external-core/domains"),
    ("GET", "/researcher/auth/contract"),
    ("POST", "/researcher/auth/register"),
    ("POST", "/researcher/auth/login"),
    ("GET", "/researcher/auth/session"),
    ("POST", "/researcher/auth/logout"),
    ("POST", "/researcher/auth/recover"),
    ("GET", "/researcher/account/deletion-preview"),
    ("POST", "/researcher/account/delete"),
    ("POST", "/researcher/account/preferences"),
    ("GET", "/research/projects/block-catalog"),
    ("GET", "/research/projects"),
    ("POST", "/research/projects"),
    ("GET", "/research/projects/{project_id}"),
    ("PATCH", "/research/projects/{project_id}"),
    ("POST", "/research/projects/{project_id}/blocks"),
    ("PATCH", "/research/projects/{project_id}/blocks/{block_id}"),
    ("POST", "/research/projects/{project_id}/blocks/{block_id}/disconnect"),
    ("GET", "/research/model-training/contract"),
    ("POST", "/research/model-training/notebook"),
    ("GET", "/research/fiji/contract"),
    ("GET", "/research/fiji/installations"),
    ("POST", "/research/fiji/installations/configure"),
    ("POST", "/research/fiji/launch"),
    ("POST", "/research/fiji/bridge/install"),
    ("DELETE", "/research/fiji/bridge"),
    ("GET", "/research/fiji/bridge/status"),
    ("POST", "/research/fiji/bridge/events"),
    ("POST", "/research/fiji/pipelines/validate"),
    ("POST", "/research/fiji/pipelines/execute"),
    ("GET", "/research/fiji/runs/{run_id}"),
    ("GET", "/research/probabilistic-methods"),
    ("POST", "/research/probabilistic-methods/run"),
    ("GET", "/research/editors/questions"),
    ("POST", "/research/editors/questions/draft"),
    ("POST", "/research/editors/questions/fork"),
    ("POST", "/research/editors/question-banks"),
    ("POST", "/questionnaire-components/validate"),
    ("GET", "/research/editors/parameters"),
    ("POST", "/research/editors/parameters/draft"),
    ("GET", "/research/editors/logic"),
    ("POST", "/research/editors/logic/draft"),
    ("GET", "/research/editors/mechanisms"),
    ("POST", "/research/editors/mechanisms/draft"),
    ("GET", "/research/editors/data/contract"),
    ("POST", "/research/editors/data/preview"),
    ("POST", "/research/editors/data/apply"),
    ("GET", "/research/citations/contract"),
    ("POST", "/research/citations/preview"),
    ("POST", "/research/citations"),
    ("GET", "/research/hypotheses/contract"),
    ("GET", "/research/hypotheses"),
    ("POST", "/research/hypotheses"),
    ("GET", "/research/sensor-hypotheses/contract"),
    ("POST", "/research/sensor-hypotheses/methods"),
    ("POST", "/research/sensor-hypotheses/validate"),
    ("GET", "/research/qualitative-hypotheses/contract"),
    ("POST", "/research/qualitative-hypotheses/methods"),
    ("POST", "/research/qualitative-hypotheses/validate"),
    ("POST", "/research/qualitative-hypothesis-results"),
    ("GET", "/research/hypothesis-entities"),
}

EDITOR_PAGES = {
    "/question-editor": "question_editor.html",
    "/parameter-editor": "parameter_editor.html",
    "/model-logic-editor": "model_logic_editor.html",
    "/mechanism-editor": "mechanism_editor.html",
    "/data-editor": "data_editor.html",
}


def application_routes() -> set[tuple[str, str]]:
    tree = ast.parse(MAIN.read_text(encoding="utf-8"), filename=str(MAIN))
    routes: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            function = decorator.func
            if not (
                isinstance(function, ast.Attribute)
                and isinstance(function.value, ast.Name)
                and function.value.id == "app"
                and function.attr.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE"}
                and decorator.args
                and isinstance(decorator.args[0], ast.Constant)
                and isinstance(decorator.args[0].value, str)
            ):
                continue
            routes.add((function.attr.upper(), decorator.args[0].value))
    return routes


def literal_navigation_targets(content: str) -> set[str]:
    targets: set[str] = set()
    patterns = (
        r"\bhref\s*=\s*['\"](/[^'\"#]*)['\"]",
        r"\blocation\.href\s*=\s*['\"](/[^'\"]*)['\"]",
    )
    for pattern in patterns:
        for raw in re.findall(pattern, content):
            path = urlsplit(raw).path
            if path:
                targets.add(path)
    return targets


class ApplicationSurfaceContractTests(unittest.TestCase):

    def test_public_data_results_tab_opens_the_claimed_workspaces(self):
        workspace = (STATIC / "research_workspace.html").read_text(encoding="utf-8")
        panel = workspace.split('id="dataResults"', 1)[1].split('id="componentLibrary"', 1)[0]
        self.assertIn("onclick=\"location.href='/data-preparation'\"", panel)
        self.assertIn("onclick=\"location.href='/scientific-results'\"", panel)
        self.assertNotIn("/researcher-account?next=data_results", panel)

    def test_account_data_results_navigation_preserves_project_scope(self):
        account = (STATIC / "researcher_account.html").read_text(encoding="utf-8")
        data = (STATIC / "data_preparation.html").read_text(encoding="utf-8")
        self.assertIn("openProjectData", account)
        self.assertIn("project_id=${encodeURIComponent(projectId)}", account)
        self.assertIn('dataExplorerParams.get("project_id")', data)

    @classmethod
    def setUpClass(cls) -> None:
        cls.routes = application_routes()

    def test_protected_pages_remain_registered_and_present(self) -> None:
        for route, filename in PROTECTED_PAGES.items():
            with self.subTest(route=route):
                self.assertIn(("GET", route), self.routes)
                path = STATIC / filename
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 5000)

    def test_protected_api_contracts_remain_registered(self) -> None:
        missing = sorted(PROTECTED_API_ROUTES - self.routes)
        self.assertEqual([], missing)

    def test_editors_are_separate_multilingual_pages(self) -> None:
        for route, filename in EDITOR_PAGES.items():
            with self.subTest(route=route):
                self.assertIn(("GET", route), self.routes)
                content = (STATIC / filename).read_text(encoding="utf-8")
                self.assertGreater(len(content), 5000)
                for language in ("ru", "en", "es"):
                    self.assertIn(f'value="{language}"', content)
                self.assertIn("setLang(this.value)", content)

    def test_workspace_editor_hub_links_only_to_real_pages(self) -> None:
        content = (STATIC / "research_workspace.html").read_text(encoding="utf-8")
        self.assertIn("showSection('editors')", content)
        for route in EDITOR_PAGES:
            self.assertIn(route, content)

    def test_question_editor_uses_standard_controls_not_raw_contract_json(self) -> None:
        content = (STATIC / "question_editor.html").read_text(encoding="utf-8")
        self.assertNotIn('id="advanced"', content)
        self.assertIn('id="questionType"', content)
        self.assertIn('id="responseType"', content)
        self.assertIn('id="scaleType"', content)
        self.assertIn('id="preview"', content)
        self.assertIn('id="saveBank"', content)
        self.assertIn("/research/editors/questions/fork", content)

    def test_literal_page_navigation_never_points_to_missing_get_route(self) -> None:
        get_routes = {path for method, path in self.routes if method == "GET"}
        missing: list[tuple[str, str]] = []
        for page in sorted(STATIC.glob("*.html")):
            content = page.read_text(encoding="utf-8")
            for target in literal_navigation_targets(content):
                if target not in get_routes:
                    missing.append((page.name, target))
        self.assertEqual([], missing)

    def test_working_pages_expose_one_selected_language(self) -> None:
        for filename in PROTECTED_PAGES.values():
            content = (STATIC / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertIn('value="ru"', content)
                self.assertIn('value="en"', content)
                self.assertIn('value="es"', content)
                self.assertRegex(content, r"changeLanguage\s*\(")

    def test_constructor_keeps_distinct_parameter_and_mechanism_paths(self) -> None:
        content = (STATIC / "model_parameter_constructor.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("setType('parameter')", content)
        self.assertIn("setType('mechanism')", content)
        self.assertIn('entityType==="parameter"', content)
        self.assertIn('entityType==="mechanism"', content)
        self.assertIn("/research/mechanisms", MAIN.read_text(encoding="utf-8"))

    def test_data_preparation_does_not_leave_for_nonexistent_workflow(self) -> None:
        content = (STATIC / "data_preparation.html").read_text(encoding="utf-8")
        self.assertNotIn("/data-preparation-required", content)
        self.assertIn('statusFilter.value="not_ready"', content)

    def test_workspace_opens_real_ray_settings_page(self) -> None:
        workspace = (STATIC / "research_workspace.html").read_text(encoding="utf-8")
        settings = (STATIC / "ray_settings.html").read_text(encoding="utf-8")
        self.assertIn("location.href='/ray-settings'", workspace)
        self.assertIn('onclick="saveDraft()"', settings)
        self.assertIn("/external-core/settings/effective", settings)

    def test_account_opens_the_separate_modular_project_workspace(self) -> None:
        account = (STATIC / "researcher_account.html").read_text(encoding="utf-8")
        project = (STATIC / "research_project.html").read_text(encoding="utf-8")
        self.assertIn("location.href='/research-project/new'", account)
        self.assertIn('window.location.assign("/research-project/"+encodeURIComponent(projectId))', account)
        self.assertNotIn("location.href='/research-workspace?section=projectStudio'", account)
        self.assertIn('class="card action-rail"', project)
        self.assertIn("position:sticky", project)
        self.assertIn("externalUnavailable", project)
        self.assertIn("authorship", MAIN.read_text(encoding="utf-8"))

    def test_probabilistic_workspace_is_visual_and_never_executes_unvalidated_methods(self) -> None:
        page = (STATIC / "probabilistic_methods.html").read_text(encoding="utf-8")
        registry = (ROOT / "research/probabilistic/registry.py").read_text(encoding="utf-8")
        project = (ROOT / "research/project_workspace.py").read_text(encoding="utf-8")
        self.assertIn("monte_carlo_inputs", page)
        self.assertIn("execution_status!==\"implemented\"", page)
        self.assertNotIn('id="rawJson"', page)
        self.assertIn("registered_without_validated_runner", registry)
        self.assertIn('"probabilistic_inference"', project)


if __name__ == "__main__":
    unittest.main()
