import pytest

from sunnbear._core.data import ArtifactRegistry


@pytest.fixture
def isolated_artifact_registry(monkeypatch):
    """Give the test its own copy of the artifact registry, so declarations that the test defines stay out of it."""
    monkeypatch.setattr(ArtifactRegistry, "_artifacts_by_name", dict(ArtifactRegistry._artifacts_by_name))
