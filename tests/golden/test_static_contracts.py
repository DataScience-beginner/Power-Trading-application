"""
Golden static contract tests.

These tests are intentionally fast and deterministic. They do not start the API,
connect to production, or mutate the database. They protect the minimum app
shape that future refactors and agents must preserve.
"""

from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_api_python_sources() -> str:
    """Return all active API Python source text for route contract checks."""
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "api").rglob("*.py"))
    )


class ApiContractTests(unittest.TestCase):
    def test_core_api_endpoints_are_declared(self) -> None:
        api_sources = read_api_python_sources()
        required_routes = [
            '"/api/health"',
            '"/api/clients"',
            '"/api/analytics/summary"',
            '"/api/energy-schedule/months"',
            '"/api/energy-schedule/days"',
            '"/api/calculate/energy-schedule"',
            '"/api/reports/daily-trading/pdf"',
            '"/api/reports/daily-trading/excel"',
            '"/api/v1/ai-foundation/capabilities"',
        ]

        for route in required_routes:
            with self.subTest(route=route):
                self.assertIn(route, api_sources)

    def test_app_uses_database_dependency(self) -> None:
        api_sources = read_api_python_sources()
        app = read("api/main.py")
        self.assertIn("Depends(get_db)", api_sources)
        self.assertIn("init_db", app)

    def test_endpoint_registry_exists_and_tracks_core_routes(self) -> None:
        registry = read("api/endpoint_registry.yaml")
        required_routes = [
            "/api/health",
            "/api/clients",
            "/api/analytics/summary",
            "/api/energy-schedule/months",
            "/api/energy-schedule/days",
            "/api/calculate/energy-schedule",
            "/api/reports/daily-trading/pdf",
            "/api/reports/daily-trading/excel",
            "/api/v1/ai-foundation/capabilities",
            "/api/v1/ai-insights/quality/analyze",
            "/api/v1/ai-insights/assistant/query",
        ]

        for route in required_routes:
            with self.subTest(route=route):
                self.assertIn(route, registry)

    def test_api_main_is_marked_as_refactor_target(self) -> None:
        plan = read("planning/api_refactor_plan.md")
        self.assertIn("api/main.py", plan)
        self.assertIn("2,597 lines", plan)


class ApiRegistryRuntimeContractTests(unittest.TestCase):
    """Protect the API registry as the source of truth for agents/chatbots."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = yaml.safe_load(read("api/endpoint_registry.yaml"))

        from api.main import app

        cls.route_by_method_and_path = {}
        for route in cls.iter_fastapi_routes(app.routes):
            path = getattr(route, "path", "")
            for method in getattr(route, "methods", set()) or set():
                if method in {"HEAD", "OPTIONS"}:
                    continue
                cls.route_by_method_and_path[(method, path)] = route

    @classmethod
    def iter_fastapi_routes(cls, routes):
        """Yield concrete routes, including routers wrapped by FastAPI includes."""
        for route in routes:
            original_router = getattr(route, "original_router", None)
            if original_router is not None:
                yield from cls.iter_fastapi_routes(original_router.routes)
                continue

            yield route

    @classmethod
    def registry_endpoints(cls) -> list[dict[str, object]]:
        endpoints: list[dict[str, object]] = []
        for domain_name, domain in cls.registry["domains"].items():
            for endpoint in domain["endpoints"]:
                enriched_endpoint = dict(endpoint)
                enriched_endpoint["domain"] = domain_name
                enriched_endpoint["target_router"] = domain["target_router"]
                endpoints.append(enriched_endpoint)
        return endpoints

    def test_registered_target_router_files_exist(self) -> None:
        for domain_name, domain in self.registry["domains"].items():
            target_router = domain["target_router"]
            with self.subTest(domain=domain_name, target_router=target_router):
                self.assertTrue((ROOT / target_router).exists())

    def test_registered_endpoints_are_mounted_in_fastapi_app(self) -> None:
        for endpoint in self.registry_endpoints():
            method = endpoint["method"]
            path = endpoint["path"]
            with self.subTest(method=method, path=path):
                self.assertIn((method, path), self.route_by_method_and_path)

    def test_registered_endpoints_are_agent_readable(self) -> None:
        for endpoint in self.registry_endpoints():
            method = endpoint["method"]
            path = endpoint["path"]

            with self.subTest(method=method, path=path):
                route = self.route_by_method_and_path[(method, path)]
                self.assertTrue(getattr(route, "summary", None))
                self.assertTrue(getattr(route, "description", None))

    def test_active_api_python_files_stay_agent_maintainable(self) -> None:
        """QC rule: keep active API files small enough for humans and agents."""
        active_api_files = sorted((ROOT / "api").rglob("*.py"))

        for path in active_api_files:
            relative_path = path.relative_to(ROOT)
            line_count = len(path.read_text(encoding="utf-8").splitlines())
            with self.subTest(file=str(relative_path)):
                self.assertLessEqual(line_count, 1000)


class EnergyScheduleContractTests(unittest.TestCase):
    def test_energy_schedule_models_exist(self) -> None:
        models = read("database/models.py")
        self.assertIn("class EnergyScheduleMonth", models)
        self.assertIn("class EnergyScheduleDay", models)

    def test_energy_schedule_services_exist(self) -> None:
        required_files = [
            "database/energy_schedule_builder.py",
            "database/energy_schedule_crud.py",
            "database/energy_schedule_service.py",
            "scripts/energy_schedule/rebuild_energy_schedules.py",
        ]

        for relative_path in required_files:
            with self.subTest(file=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

    def test_frontend_energy_schedule_contract_exists(self) -> None:
        required_files = [
            "frontend-react/src/pages/EnergySchedule.tsx",
            "frontend-react/src/services/api.ts",
            "frontend-react/src/types/energySchedule.ts",
        ]

        for relative_path in required_files:
            with self.subTest(file=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

    def test_frontend_session_auto_logout_contract_exists(self) -> None:
        session = read("frontend-react/src/security/session.ts")
        hook = read("frontend-react/src/hooks/useIdleLogout.ts")
        app_shell = read("frontend-react/src/pages/AppShell.tsx")
        self.assertIn("VITE_AUTO_LOGOUT_ENABLED", session)
        self.assertIn("VITE_IDLE_TIMEOUT_MINUTES", session)
        self.assertIn("clearAuthSession", hook)
        self.assertIn("useIdleLogout", app_shell)


class AgentGovernanceContractTests(unittest.TestCase):
    def test_required_agents_are_registered(self) -> None:
        registry = read("agents/registry.yaml")
        self.assertIn("codebase-qc", registry)
        self.assertIn("testing-qa", registry)
        self.assertIn("competitive-intelligence", registry)
        self.assertIn("ai-governance", registry)
        self.assertIn("data-quality", registry)
        self.assertIn("market-insight", registry)
        self.assertIn("conversational-assistant", registry)

    def test_ai_foundation_is_agent_and_human_readable(self) -> None:
        required_files = [
            "api/schemas/ai_foundation.py",
            "api/services/ai_foundation_service.py",
            "api/routers/ai_foundation.py",
            "database/ai_foundation_models.py",
            "database/migrations/ai_foundation_v1.sql",
        ]
        for relative_path in required_files:
            with self.subTest(file=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

        schema = read("api/schemas/ai_foundation.py")
        self.assertIn("EvidenceItem", schema)
        self.assertIn("human_review_required", schema)
        self.assertIn("is_synthetic", schema)

    def test_ai_insights_contract_is_complete(self) -> None:
        required_files = [
            "api/schemas/ai_insights.py",
            "api/services/data_quality_service.py",
            "api/services/market_explanation_service.py",
            "api/services/insight_assistant_service.py",
            "api/routers/ai_insights.py",
            "database/ai_insights_models.py",
            "database/migrations/ai_insights_v1.sql",
            "frontend-react/src/pages/AIInsights.tsx",
        ]
        for relative_path in required_files:
            with self.subTest(file=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

        assistant = read("api/services/insight_assistant_service.py")
        self.assertIn('return "unsupported"', assistant)
        self.assertIn("No forecast", assistant)

    def test_authenticated_chatbot_contract_is_complete(self) -> None:
        required_files = [
            "api/security/chat_auth.py",
            "api/schemas/chatbot.py",
            "api/services/chatbot_service.py",
            "api/services/chat_model_provider.py",
            "api/routers/chat_auth.py",
            "api/routers/chatbot.py",
            "database/chatbot_models.py",
            "database/migrations/chatbot_v1.sql",
            "frontend-react/src/components/chat/ChatAssistant.tsx",
            "prompts/chatbot_system_v1.md",
        ]
        for relative_path in required_files:
            with self.subTest(file=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

        auth = read("api/security/chat_auth.py")
        self.assertIn("JWT_SECRET_KEY", auth)
        self.assertIn("authorize_scope", auth)
        provider = read("api/services/chat_model_provider.py")
        self.assertIn("GROQ_API_KEY", provider)
        self.assertIn("deterministic fallback", provider)

    def test_root_agent_policy_references_registry(self) -> None:
        policy = read("AGENTS.md")
        self.assertIn("agents/registry.yaml", policy)


if __name__ == "__main__":
    unittest.main()
