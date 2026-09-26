"""`artifact_names` lists only the built-in data artifacts, and `artifact_manifest` reads one's manifest."""

import pytest

from sunnbear._core.builtin_artifacts import artifact_manifest, artifact_names
from sunnbear._core.data import ArtifactError, ArtifactStore

from .sample_declarations import SampleLinesDeclaration, define_builtin_declaration


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_artifact_names_lists_built_in_declarations_only():
    """A declaration inside sunnbear is listed; a test fixture declared outside sunnbear is not."""
    # --- arrange ----------------------
    define_builtin_declaration("zz_builtin")

    # --- act --------------------------
    names = artifact_names()

    # --- assert -----------------------
    assert "zz_builtin" in names
    assert SampleLinesDeclaration.name not in names
    assert list(names) == sorted(names)


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_artifact_manifest_reads_the_manifest_of_a_built_in_artifact(monkeypatch, tmp_path):
    """`artifact_manifest` returns the manifest that `save` wrote for a built-in artifact."""
    # --- arrange ----------------------
    monkeypatch.setattr(ArtifactStore, "_builtin_artifacts_folder", staticmethod(lambda: tmp_path))
    declaration_cls = define_builtin_declaration("zz_builtin")
    saved_manifest = ArtifactStore.save(declaration_cls, b"content\n")

    # --- act / assert -----------------
    assert artifact_manifest("zz_builtin") == saved_manifest


@pytest.mark.parametrize("name", ["no_such_artifact", SampleLinesDeclaration.name])
def test_artifact_manifest_refuses_a_name_that_is_not_built_in(name):
    """An unknown name, or the name of a test fixture, is not a sunnbear data artifact."""
    with pytest.raises(ArtifactError, match=f"sunnbear has no data artifact named '{name}'"):
        artifact_manifest(name)
