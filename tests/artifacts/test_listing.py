"""`ArtifactStore` lists the built-in artifacts from their committed folders, and reads the manifest of one."""

import pytest

from sunnbear._core.artifacts import ArtifactError, ArtifactStore
from sunnbear._core.artifacts.listing import artifact_manifest, artifact_names

from .sample_declarations import SampleLinesDeclaration, define_builtin_declaration


@pytest.fixture
def builtin_artifacts_folder_in_tmp(monkeypatch, tmp_path):
    """Make `ArtifactStore` keep the built-in artifacts in `tmp_path`, and return that folder."""
    monkeypatch.setattr(ArtifactStore, "_builtin_artifacts_folder", staticmethod(lambda: tmp_path))
    return tmp_path


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_artifact_names_lists_one_name_per_builtin_folder(builtin_artifacts_folder_in_tmp):
    """Each subfolder of the built-in artifacts folder is listed, sorted; a file there and a test fixture are not."""
    # --- arrange ----------------------
    for name in ("zz_later", "aa_earlier"):
        ArtifactStore.save(define_builtin_declaration(name), b"content\n")
    (builtin_artifacts_folder_in_tmp / "README.txt").write_text("not an artifact\n")

    # --- act --------------------------
    names = artifact_names()

    # --- assert -----------------------
    assert names == ("aa_earlier", "zz_later")
    assert SampleLinesDeclaration.name not in names


def test_artifact_names_is_empty_without_a_builtin_artifacts_folder(builtin_artifacts_folder_in_tmp):
    """Without the folder of built-in artifacts, no artifact is listed."""
    # --- arrange ----------------------
    builtin_artifacts_folder_in_tmp.rmdir()

    # --- act / assert -----------------
    assert artifact_names() == ()


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_artifact_manifest_reads_the_manifest_of_a_builtin_artifact(builtin_artifacts_folder_in_tmp):
    """`artifact_manifest` returns the manifest that `save` wrote for a built-in artifact."""
    # --- arrange ----------------------
    saved_manifest = ArtifactStore.save(define_builtin_declaration("zz_builtin"), b"content\n")

    # --- act / assert -----------------
    assert artifact_manifest("zz_builtin") == saved_manifest


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_artifact_manifest_refuses_a_manifest_for_another_artifact(builtin_artifacts_folder_in_tmp):
    """A built-in folder whose manifest names another artifact is refused."""
    # --- arrange ----------------------
    ArtifactStore.save(define_builtin_declaration("zz_builtin"), b"content\n")
    (builtin_artifacts_folder_in_tmp / "zz_builtin").rename(builtin_artifacts_folder_in_tmp / "zz_renamed")

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match="is for 'zz_builtin', but the artifact is 'zz_renamed'"):
        artifact_manifest("zz_renamed")


@pytest.mark.usefixtures("builtin_artifacts_folder_in_tmp")
@pytest.mark.parametrize("name", ["no_such_artifact", SampleLinesDeclaration.name])
def test_artifact_manifest_refuses_a_name_that_is_not_builtin(name):
    """An unknown name, or the name of a test fixture, is not a sunnbear data artifact."""
    with pytest.raises(ArtifactError, match=f"sunnbear has no data artifact named '{name}'"):
        artifact_manifest(name)
