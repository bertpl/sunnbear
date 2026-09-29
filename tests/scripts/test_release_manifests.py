"""The release script finds the built-in artifact manifests built since the last release, and stamps them."""

import datetime
import importlib.util
import sys
from pathlib import Path

import pytest

from sunnbear._core.artifacts import ArtifactFileEntry, ArtifactManifest

_RELEASE_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "release.py"


# ==================================================================================================
#  Fixtures and helpers
# ==================================================================================================
@pytest.fixture(scope="module")
def release():
    """Return `scripts/release.py`, imported by path: the script is not part of the package."""
    spec = importlib.util.spec_from_file_location("release_script", _RELEASE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    # `dataclasses` looks the module up in `sys.modules` while the script's dataclass is defined.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def builtin_artifacts_dir(release, monkeypatch, tmp_path):
    """Make the release script look for the built-in artifacts in `tmp_path`, and return that directory."""
    monkeypatch.setattr(release, "BUILTIN_ARTIFACTS_DIR", tmp_path)
    return tmp_path


def _write_manifest(builtin_artifacts_dir: Path, name: str, sunnbear_version: str) -> Path:
    """Write the manifest of a 1-file artifact that records `sunnbear_version`, and return its path."""
    manifest = ArtifactManifest(
        name=name,
        files=(ArtifactFileEntry.from_content("value.txt", b"content\n"),),
        built_with={"sunnbear": sunnbear_version},
        build_date=datetime.date(2026, 9, 28),
    )
    path = builtin_artifacts_dir / name / "manifest.json"
    path.parent.mkdir(parents=True)
    path.write_text(manifest.to_json())
    return path


# ==================================================================================================
#  Finding unreleased manifests
# ==================================================================================================
def test_only_manifests_built_since_the_last_release_are_found(release, builtin_artifacts_dir):
    """A manifest that records the last release plus `+dev` is found; one that an earlier release stamped is not."""
    # --- arrange ----------------------
    fresh_path = _write_manifest(builtin_artifacts_dir, "fresh", "0.1.4+dev")
    _write_manifest(builtin_artifacts_dir, "released", "0.1.3")

    # --- act --------------------------
    paths = release.unreleased_artifact_manifest_paths("0.1.4")

    # --- assert -----------------------
    assert paths == [fresh_path]


def test_an_older_release_plus_dev_stops_the_release(release, builtin_artifacts_dir):
    """A manifest that records an older release plus `+dev` was never stamped, so the release script refuses it."""
    # --- arrange ----------------------
    _write_manifest(builtin_artifacts_dir, "stale", "0.1.3+dev")

    # --- act / assert -----------------
    with pytest.raises(ValueError, match=r"stale records sunnbear 0\.1\.3\+dev"):
        release.unreleased_artifact_manifest_paths("0.1.4")


def test_the_committed_manifests_can_be_stamped_at_the_next_release(release):
    """Every committed built-in manifest either names a release or the version in `pyproject.toml` plus `+dev`."""
    # --- act / assert -----------------
    release.unreleased_artifact_manifest_paths(release.read_pyproject_version())


# ==================================================================================================
#  Stamping
# ==================================================================================================
def test_stamping_records_the_release_version_in_unreleased_manifests_only(release, builtin_artifacts_dir):
    """The unreleased manifest records the release version with its content hash unchanged; the other is untouched."""
    # --- arrange ----------------------
    fresh_path = _write_manifest(builtin_artifacts_dir, "fresh", "0.1.4+dev")
    released_path = _write_manifest(builtin_artifacts_dir, "released", "0.1.3")
    fresh_before = ArtifactManifest.from_json(fresh_path.read_text())
    released_json_before = released_path.read_text()

    # --- act --------------------------
    paths = release.stamp_artifact_manifests(release_version="0.2.0", last_release_version="0.1.4")

    # --- assert -----------------------
    fresh_after = ArtifactManifest.from_json(fresh_path.read_text())
    assert paths == [fresh_path]
    assert fresh_after.built_with == {"sunnbear": "0.2.0"}
    assert fresh_after.content_hash == fresh_before.content_hash
    assert released_path.read_text() == released_json_before
