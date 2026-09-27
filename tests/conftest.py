import pytest

from sunnbear.solvers import SolverConfigRegistry


@pytest.fixture
def isolated_solver_config_registry(monkeypatch):
    """Give the test its own copy of the registry, so test-defined SolverConfig subclasses don't leak past the test."""
    monkeypatch.setattr(SolverConfigRegistry, "_configs_by_id", dict(SolverConfigRegistry._configs_by_id))
