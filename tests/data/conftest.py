import pytest

from sunnbear._core.data import ArtifactRegistry


@pytest.fixture
def isolated_artifact_registry(monkeypatch):
    """Give the test its own copy of the registry, so test-defined Artifact subclasses don't leak past the test."""
    monkeypatch.setattr(ArtifactRegistry, "_artifacts_by_name", dict(ArtifactRegistry._artifacts_by_name))
