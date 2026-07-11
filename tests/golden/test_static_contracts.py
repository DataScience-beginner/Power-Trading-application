"""
Golden static contract tests.

These tests are intentionally fast and deterministic. They do not start the API,
connect to production, or mutate the database. They protect the minimum app
shape that future refactors and agents must preserve.
"""

from pathlib import Path
import unittest


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
        ]

        for route in required_routes:
            with self.subTest(route=route):
                self.assertIn(route, registry)

    def test_api_main_is_marked_as_refactor_target(self) -> None:
        plan = read("planning/api_refactor_plan.md")
        self.assertIn("api/main.py", plan)
        self.assertIn("2,597 lines", plan)


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


class AgentGovernanceContractTests(unittest.TestCase):
    def test_required_agents_are_registered(self) -> None:
        registry = read("agents/registry.yaml")
        self.assertIn("codebase-qc", registry)
        self.assertIn("testing-qa", registry)

    def test_root_agent_policy_references_registry(self) -> None:
        policy = read("AGENTS.md")
        self.assertIn("agents/registry.yaml", policy)


if __name__ == "__main__":
    unittest.main()
