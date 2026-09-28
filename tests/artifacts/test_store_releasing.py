"""`ArtifactStore` finds the built-in artifacts built from unreleased code, and stamps them with the release version."""

import importlib.metadata

import pytest

from sunnbear._core.artifacts import ArtifactError, ArtifactStore

from .sample_declarations import define_builtin_declaration

LAST_RELEASE_VERSION = importlib.metadata.version("sunnbear")


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _save_builtin(name: str, sunnbear_version: str | None = None) -> None:
    """Save a 1-file built-in artifact; with `sunnbear_version`, rewrite its manifest to record that version."""
    ArtifactStore.save(define_builtin_declaration(name), b"content\n")
    if sunnbear_version is not None:
        folder = ArtifactStore._builtin_artifacts_folder() / name
        manifest = ArtifactStore.load_builtin_manifest(name).with_release_version(sunnbear_version)
        (folder / "manifest.json").write_text(manifest.to_json())


# ==================================================================================================
#  Finding unreleased artifacts
# ==================================================================================================
@pytest.mark.usefixtures("isolated_artifact_registry", "builtin_artifacts_folder_in_tmp")
def test_only_artifacts_built_after_the_last_release_are_unreleased():
    """A freshly saved artifact is unreleased; one that an earlier release stamped is not."""
    # --- arrange ----------------------
    _save_builtin("fresh")
    _save_builtin("released", sunnbear_version="0.0.1")

    # --- act --------------------------
    names = ArtifactStore.unreleased_builtin_artifact_names(last_release_version=LAST_RELEASE_VERSION)

    # --- assert -----------------------
    assert names == ("fresh",)


@pytest.mark.usefixtures("isolated_artifact_registry", "builtin_artifacts_folder_in_tmp")
def test_an_unreleased_artifact_after_another_release_stops_the_release():
    """An artifact that records `+dev` after a release other than the last one was never stamped, so it is refused."""
    # --- arrange ----------------------
    _save_builtin("stale", sunnbear_version="0.0.1+dev")

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=r"records sunnbear 0\.0\.1\+dev"):
        ArtifactStore.unreleased_builtin_artifact_names(last_release_version=LAST_RELEASE_VERSION)


# ==================================================================================================
#  Stamping
# ==================================================================================================
@pytest.mark.usefixtures("isolated_artifact_registry")
def test_stamping_records_the_release_version_in_unreleased_manifests_only(builtin_artifacts_folder_in_tmp):
    """The unreleased manifest records the release version with its content hash unchanged; the other is untouched."""
    # --- arrange ----------------------
    _save_builtin("fresh")
    _save_builtin("released", sunnbear_version="0.0.1")
    fresh_before = ArtifactStore.load_builtin_manifest("fresh")
    released_json_before = (builtin_artifacts_folder_in_tmp / "released" / "manifest.json").read_text()

    # --- act --------------------------
    paths = ArtifactStore.stamp_release_version(release_version="9.9.9", last_release_version=LAST_RELEASE_VERSION)

    # --- assert -----------------------
    fresh_after = ArtifactStore.load_builtin_manifest("fresh")
    assert paths == (builtin_artifacts_folder_in_tmp / "fresh" / "manifest.json",)
    assert fresh_after.built_with["sunnbear"] == "9.9.9"
    assert fresh_after.content_hash == fresh_before.content_hash
    assert (builtin_artifacts_folder_in_tmp / "released" / "manifest.json").read_text() == released_json_before


def test_stamping_refuses_a_builtin_artifacts_folder_that_is_not_on_disk(monkeypatch):
    """Inside a zipped install the built-in artifacts folder is no directory on disk, so nothing can be stamped."""
    # --- arrange ----------------------
    monkeypatch.setattr(ArtifactStore, "_builtin_artifacts_folder", staticmethod(lambda: "not a path"))

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match="not a writable directory"):
        ArtifactStore.stamp_release_version(release_version="9.9.9", last_release_version=LAST_RELEASE_VERSION)
