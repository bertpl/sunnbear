import pytest

from sunnbear._core.data import ArtifactRegistry, ArtifactStore


@pytest.fixture
def isolated_artifact_registry(monkeypatch):
    """Give the test its own copy of the artifact registry, so the test's declarations stay out of the shared one."""
    monkeypatch.setattr(ArtifactRegistry, "_declarations_by_name", dict(ArtifactRegistry._declarations_by_name))


@pytest.fixture(autouse=True)
def cache_root_in_tmp(monkeypatch, tmp_path):
    """Point the download cache into `tmp_path` through ``SUNNBEAR_DATA_DIR``, so no test touches the user's cache.

    The fixture returns the cache root, which does not exist until a file is cached.
    """
    monkeypatch.setenv("SUNNBEAR_DATA_DIR", str(tmp_path / "cache"))
    return tmp_path / "cache"


@pytest.fixture
def artifact_folders_in_tmp(monkeypatch, tmp_path):
    """Make `ArtifactStore` place every artifact's folder in `tmp_path`, so tests write no files in the repo.

    The fixture returns the parent of those folders; each folder is named after its artifact and does
    not exist until a test creates it or saves to it.
    """
    artifact_folders = tmp_path / "artifacts"
    folder_of = classmethod(lambda cls, declaration_cls: artifact_folders / declaration_cls.name)
    monkeypatch.setattr(ArtifactStore, "_folder_of", folder_of)
    return artifact_folders
