"""`ArtifactStore` reads, writes and verifies an artifact's directory, and checks the built-in artifacts as a whole."""

import importlib
import importlib.metadata
import pkgutil
import zipfile

import pytest

import sunnbear
from sunnbear._core.artifacts import ArtifactError, ArtifactStore

from .sample_declarations import SAMPLE_LINES, SampleLinesDeclaration, define_builtin_declaration


@pytest.fixture
def sample_lines_dir_in_tmp(artifacts_dir_in_tmp):
    """Return the directory of `SampleLinesDeclaration`, placed in `tmp_path` by `artifacts_dir_in_tmp`."""
    return artifacts_dir_in_tmp / SampleLinesDeclaration.name


# ==================================================================================================
#  The committed sample artifact
# ==================================================================================================
def test_load_reads_the_committed_sample_artifact():
    """`load` rebuilds the value from the sample artifact's files, committed next to its declaration's module."""
    assert ArtifactStore.load(SampleLinesDeclaration) == SAMPLE_LINES


def test_verify_accepts_the_committed_sample_artifact():
    """The committed sample artifact matches its manifest, so `verify` returns that manifest."""
    assert ArtifactStore.verify(SampleLinesDeclaration).name == SampleLinesDeclaration.name


# ==================================================================================================
#  Saving and loading
# ==================================================================================================
def test_save_writes_files_and_manifest_that_load_reads_back(sample_lines_dir_in_tmp):
    """A saved value loads back equal; the manifest records sunnbear's unreleased version and the caller's metadata."""
    # --- act --------------------------
    manifest = ArtifactStore.save(
        SampleLinesDeclaration,
        SAMPLE_LINES,
        built_with={"numpy": "2.1.0", "sunnbear": "0.0.0"},
        input_artifact_hashes={"upstream": "ab" * 32},
        generated_by={"function": "sample.generate"},
    )

    # --- assert -----------------------
    assert ArtifactStore.load(SampleLinesDeclaration) == SAMPLE_LINES
    assert ArtifactStore.load_manifest(SampleLinesDeclaration) == manifest
    assert manifest.built_with == {"numpy": "2.1.0", "sunnbear": importlib.metadata.version("sunnbear") + "+dev"}
    assert [entry.path for entry in manifest.files] == ["lines.txt", "meta/count.txt"]


def test_save_deletes_files_that_the_new_value_does_not_produce(sample_lines_dir_in_tmp):
    """After a save, the directory holds exactly the manifest's files, so `verify` passes."""
    # --- arrange ----------------------
    sample_lines_dir_in_tmp.mkdir(parents=True)
    (sample_lines_dir_in_tmp / "old.txt").write_text("left over")

    # --- act --------------------------
    ArtifactStore.save(SampleLinesDeclaration, SAMPLE_LINES)

    # --- assert -----------------------
    assert not (sample_lines_dir_in_tmp / "old.txt").exists()
    ArtifactStore.verify(SampleLinesDeclaration)


@pytest.mark.usefixtures("sample_lines_dir_in_tmp", "isolated_artifact_registry")
def test_save_refuses_a_data_file_named_like_the_manifest():
    """A declaration that produces ``manifest.json`` as a data file cannot be saved."""
    # --- arrange ----------------------
    declaration_cls = define_builtin_declaration("clashing", file_path="manifest.json")

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=r"data file named 'manifest\.json'"):
        ArtifactStore.save(declaration_cls, b"{}")


def test_save_refuses_an_artifact_dir_inside_a_zip_archive(monkeypatch, tmp_path):
    """A directory inside a zip archive, as in a zipped install, cannot be written."""
    # --- arrange ----------------------
    archive = tmp_path / "package.zip"
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("artifacts/sample_lines/lines.txt", "")
    artifact_dir = zipfile.Path(archive, "artifacts/sample_lines/")
    monkeypatch.setattr(ArtifactStore, "_artifact_dir_of", classmethod(lambda cls, declaration_cls: artifact_dir))

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match="is not a plain file-system directory, so it cannot be written"):
        ArtifactStore.save(SampleLinesDeclaration, SAMPLE_LINES)


@pytest.mark.usefixtures("sample_lines_dir_in_tmp")
def test_load_without_a_manifest_fails():
    """An artifact whose directory has no manifest cannot be loaded."""
    with pytest.raises(ArtifactError, match=r"no file 'manifest\.json'"):
        ArtifactStore.load(SampleLinesDeclaration)


def test_load_manifest_refuses_a_manifest_for_another_artifact(sample_lines_dir_in_tmp):
    """A manifest whose name differs from the declaration's is refused."""
    # --- arrange ----------------------
    manifest = ArtifactStore.save(SampleLinesDeclaration, SAMPLE_LINES)
    (sample_lines_dir_in_tmp / "manifest.json").write_text(manifest.model_copy(update={"name": "other"}).to_json())

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match="is for 'other'"):
        ArtifactStore.load_manifest(SampleLinesDeclaration)


# ==================================================================================================
#  Verification
# ==================================================================================================
@pytest.mark.parametrize(
    "tamper, message",
    [
        (lambda artifact_dir: (artifact_dir / "lines.txt").unlink(), "lines.txt is missing"),
        (lambda artifact_dir: (artifact_dir / "lines.txt").write_text("edited\n"), "lines.txt differs"),
        (lambda artifact_dir: (artifact_dir / "extra.txt").write_text("x"), "extra.txt is not listed"),
    ],
)
def test_verify_reports_an_artifact_dir_that_differs_from_its_manifest(sample_lines_dir_in_tmp, tamper, message):
    """A missing, edited or unlisted file makes `verify` fail and name the file."""
    # --- arrange ----------------------
    ArtifactStore.save(SampleLinesDeclaration, SAMPLE_LINES)
    tamper(sample_lines_dir_in_tmp)

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=message):
        ArtifactStore.verify(SampleLinesDeclaration)


def test_the_builtin_artifacts_are_consistent():
    """Every built-in artifact matches its manifest, and every built-in artifact directory is declared."""
    # --- arrange ----------------------
    # `verify_builtin_artifacts` checks only registered declarations, and a declaration is registered
    # only once its module is imported, so import every sunnbear module.
    for module_info in pkgutil.walk_packages(sunnbear.__path__, prefix="sunnbear."):
        importlib.import_module(module_info.name)

    # --- act / assert -----------------
    ArtifactStore.verify_builtin_artifacts()


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_verify_builtin_artifacts_reports_unverifiable_and_undeclared(monkeypatch, tmp_path):
    """A built-in declaration without files, and a directory without a declaration, are both reported."""
    # --- arrange ----------------------
    monkeypatch.setattr(ArtifactStore, "_builtin_artifacts_dir", staticmethod(lambda: tmp_path))
    (tmp_path / "orphan").mkdir()
    define_builtin_declaration("declared_without_files")

    # --- act / assert -----------------
    with pytest.raises(
        ArtifactError, match=r"(?s)declared_without_files.*Directory 'orphan' holds no declared artifact"
    ):
        ArtifactStore.verify_builtin_artifacts()


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_a_builtin_artifact_lives_in_the_builtin_artifacts_dir_and_a_test_fixture_beside_its_module():
    """A built-in declaration uses ``_core/artifacts/builtin/<name>``; any other declaration uses
    ``artifacts/<name>`` beside its own module.
    """
    # --- arrange ----------------------
    builtin_cls = define_builtin_declaration("sample_builtin")

    # --- act --------------------------
    builtin_dir = ArtifactStore._artifact_dir_of(builtin_cls)
    fixture_dir = ArtifactStore._artifact_dir_of(SampleLinesDeclaration)

    # --- assert -----------------------
    assert str(builtin_dir).replace("\\", "/").endswith("sunnbear/_core/artifacts/builtin/sample_builtin")
    assert str(fixture_dir).replace("\\", "/").endswith("tests/artifacts/artifacts/sample_lines")
