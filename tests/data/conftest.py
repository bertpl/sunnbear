import pytest

from sunnbear._core.data import ArtifactRegistry


@pytest.fixture
def isolated_artifact_registry(monkeypatch):
    """Give the test its own copy of the artifact registry, so the test's declarations stay out of the shared one."""
    monkeypatch.setattr(ArtifactRegistry, "_declarations_by_name", dict(ArtifactRegistry._declarations_by_name))
