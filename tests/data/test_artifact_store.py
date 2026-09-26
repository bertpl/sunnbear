"""`ArtifactStore` reads, writes and verifies an artifact's folder, and checks the built-in artifacts as a whole."""

import importlib
import importlib.metadata
import pkgutil
import zipfile

import pytest

import sunnbear
from sunnbear._core.data import ArtifactDeclaration, ArtifactError, ArtifactStore

from .sample_declarations import SAMPLE_LINES, SampleLinesDeclaration, define_declaration


def _define_builtin_declaration(name: str, file_path: str = "value.txt") -> type[ArtifactDeclaration]:
    """Define a 1-file declaration whose module name is inside sunnbear, so `ArtifactStore` treats it as built in.

    Defining the class registers it in `ArtifactRegistry`, so a test that calls this function must use
    the `isolated_artifact_registry` fixture.
    """
    return define_declaration(file_path, __module__="sunnbear._declared_in_a_test", name=name)


@pytest.fixture
def sample_lines_folder_in_tmp(monkeypatch, tmp_path):
    """Make `ArtifactStore` place every artifact's folder in `tmp_path`, so tests write no files in the repo.

    The fixture returns the folder of `SampleLinesDeclaration`, which does not exist until a test
    creates it or saves to it.
    """
    folder_of = classmethod(lambda cls, declaration_cls: tmp_path / declaration_cls.name)
    monkeypatch.setattr(ArtifactStore, "_folder_of", folder_of)
    return tmp_path / SampleLinesDeclaration.name


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
def test_save_writes_files_and_manifest_that_load_reads_back(sample_lines_folder_in_tmp):
    """A saved value loads back equal, and the manifest records sunnbear's version and the caller's metadata."""
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
    assert manifest.built_with == {"numpy": "2.1.0", "sunnbear": importlib.metadata.version("sunnbear")}
    assert [entry.path for entry in manifest.files] == ["lines.txt", "meta/count.txt"]


def test_save_deletes_files_that_the_new_value_does_not_produce(sample_lines_folder_in_tmp):
    """After a save, the folder holds exactly the manifest's files, so `verify` passes."""
    # --- arrange ----------------------
    sample_lines_folder_in_tmp.mkdir(parents=True)
    (sample_lines_folder_in_tmp / "old.txt").write_text("left over")

    # --- act --------------------------
    ArtifactStore.save(SampleLinesDeclaration, SAMPLE_LINES)

    # --- assert -----------------------
    assert not (sample_lines_folder_in_tmp / "old.txt").exists()
    ArtifactStore.verify(SampleLinesDeclaration)


@pytest.mark.usefixtures("sample_lines_folder_in_tmp", "isolated_artifact_registry")
def test_save_refuses_a_data_file_named_like_the_manifest():
    """A declaration that produces ``manifest.json`` as a data file cannot be saved."""
    # --- arrange ----------------------
    declaration_cls = _define_builtin_declaration("clashing", file_path="manifest.json")

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=r"data file named 'manifest\.json'"):
        ArtifactStore.save(declaration_cls, b"{}")


def test_save_refuses_a_folder_that_is_not_a_directory_on_disk(monkeypatch, tmp_path):
    """A folder inside a zip archive, as in a zipped install, cannot be written."""
    # --- arrange ----------------------
    archive = tmp_path / "package.zip"
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("artifacts/sample_lines/lines.txt", "")
    folder = zipfile.Path(archive, "artifacts/sample_lines/")
    monkeypatch.setattr(ArtifactStore, "_folder_of", classmethod(lambda cls, declaration_cls: folder))

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match="not a writable directory"):
        ArtifactStore.save(SampleLinesDeclaration, SAMPLE_LINES)


@pytest.mark.usefixtures("sample_lines_folder_in_tmp")
def test_load_without_a_manifest_fails():
    """An artifact whose folder has no manifest cannot be loaded."""
    with pytest.raises(ArtifactError, match=r"no file 'manifest\.json'"):
        ArtifactStore.load(SampleLinesDeclaration)


def test_load_manifest_refuses_a_manifest_for_another_artifact(sample_lines_folder_in_tmp):
    """A manifest whose name differs from the declaration's is refused."""
    # --- arrange ----------------------
    manifest = ArtifactStore.save(SampleLinesDeclaration, SAMPLE_LINES)
    (sample_lines_folder_in_tmp / "manifest.json").write_text(manifest.model_copy(update={"name": "other"}).to_json())

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match="is for 'other'"):
        ArtifactStore.load_manifest(SampleLinesDeclaration)


# ==================================================================================================
#  Verification
# ==================================================================================================
@pytest.mark.parametrize(
    "tamper, message",
    [
        (lambda folder: (folder / "lines.txt").unlink(), "lines.txt is missing"),
        (lambda folder: (folder / "lines.txt").write_text("edited\n"), "lines.txt differs"),
        (lambda folder: (folder / "extra.txt").write_text("x"), "extra.txt is not listed"),
    ],
)
def test_verify_reports_a_folder_that_differs_from_its_manifest(sample_lines_folder_in_tmp, tamper, message):
    """A missing, edited or unlisted file makes `verify` fail and name the file."""
    # --- arrange ----------------------
    ArtifactStore.save(SampleLinesDeclaration, SAMPLE_LINES)
    tamper(sample_lines_folder_in_tmp)

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=message):
        ArtifactStore.verify(SampleLinesDeclaration)


def test_the_builtin_artifacts_are_consistent():
    """Every built-in artifact matches its manifest, and each subfolder of the built-in artifacts folder is declared."""
    # --- arrange ----------------------
    # `ArtifactRegistry` knows a declaration only once its module is imported, so import every sunnbear module.
    for module_info in pkgutil.walk_packages(sunnbear.__path__, prefix="sunnbear."):
        importlib.import_module(module_info.name)

    # --- act / assert -----------------
    ArtifactStore.verify_builtin_artifacts()


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_verify_builtin_artifacts_reports_unverifiable_and_undeclared(monkeypatch, tmp_path):
    """A built-in declaration without files, and a folder without a declaration, are both reported."""
    # --- arrange ----------------------
    monkeypatch.setattr(ArtifactStore, "_builtin_artifacts_folder", staticmethod(lambda: tmp_path))
    (tmp_path / "orphan").mkdir()
    _define_builtin_declaration("declared_without_files")

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=r"(?s)declared_without_files.*Folder 'orphan' holds no declared artifact"):
        ArtifactStore.verify_builtin_artifacts()


@pytest.mark.usefixtures("isolated_artifact_registry")
def test_a_builtin_artifact_lives_in_the_builtin_artifacts_folder_and_a_test_fixture_beside_its_module():
    """A built-in declaration uses ``_core/data/artifacts/<name>``; any other declaration uses
    ``artifacts/<name>`` beside its own module.
    """
    # --- arrange ----------------------
    builtin_cls = _define_builtin_declaration("builtin")

    # --- act --------------------------
    builtin_folder = ArtifactStore._folder_of(builtin_cls)
    fixture_folder = ArtifactStore._folder_of(SampleLinesDeclaration)

    # --- assert -----------------------
    assert str(builtin_folder).replace("\\", "/").endswith("sunnbear/_core/data/artifacts/builtin")
    assert str(fixture_folder).replace("\\", "/").endswith("tests/data/artifacts/sample_lines")
