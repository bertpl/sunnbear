"""`ArtifactStore` downloads the data files of an artifact with source `DOWNLOAD` into a cache, and checks them."""

from pathlib import Path

import platformdirs
import pytest

from sunnbear._core.artifacts import (
    ArtifactArchiveEntry,
    ArtifactArchiver,
    ArtifactError,
    ArtifactManifest,
    ArtifactStore,
)

from .sample_declarations import SAMPLE_LINES, SampleDownloadedLinesDeclaration, SampleLinesDeclaration

# The committed manifest of `SampleDownloadedLinesDeclaration` is read by path, so that a test that
# moves artifact folders into `tmp_path` still finds it.
_COMMITTED_MANIFEST_PATH = Path(__file__).parent / "artifacts" / SampleDownloadedLinesDeclaration.name / "manifest.json"
# The tests' stand-in for `ArtifactStore._download` serves this committed archive.
_COMMITTED_ARCHIVE_PATH = (
    Path(__file__).parent / "downloads" / ArtifactArchiver.archive_file_name(SampleDownloadedLinesDeclaration.name)
)


def _load_committed_manifest() -> ArtifactManifest:
    """Return the committed manifest of `SampleDownloadedLinesDeclaration`."""
    return ArtifactManifest.from_json(_COMMITTED_MANIFEST_PATH.read_text())


def _raise_connection_error(url: str) -> bytes:
    """Stand in for a download that cannot connect."""
    raise ConnectionError(f"cannot reach {url}")


def _stub_download(monkeypatch, content_by_url: dict[str, bytes]) -> list[str]:
    """Replace `ArtifactStore._download` with a stand-in serving `content_by_url`; return the list of requested URLs."""
    urls = []

    def download(url: str) -> bytes:
        urls.append(url)
        return content_by_url[url]

    monkeypatch.setattr(ArtifactStore, "_download", staticmethod(download))
    return urls


@pytest.fixture
def stub_download_requested_urls(monkeypatch):
    """Serve the committed archive at the committed manifest's archive URL; return the list of requested URLs."""
    archive_entry = _load_committed_manifest().archive
    return _stub_download(monkeypatch, {archive_entry.url: _COMMITTED_ARCHIVE_PATH.read_bytes()})


@pytest.fixture
def lines_file_cache_path(cache_root_in_tmp):
    """Return the cache path of ``lines.txt`` for `SampleDownloadedLinesDeclaration`."""
    manifest = _load_committed_manifest()
    return cache_root_in_tmp / manifest.name / manifest.content_hash / "lines.txt"


@pytest.fixture
def placed_archive_path(lines_file_cache_path):
    """Return the cache path where the archive of `SampleDownloadedLinesDeclaration` can be placed by hand."""
    return lines_file_cache_path.parent / ArtifactArchiver.archive_file_name(SampleDownloadedLinesDeclaration.name)


# ==================================================================================================
#  Loading
# ==================================================================================================
def test_load_downloads_the_archive_once_and_then_reads_the_cache(stub_download_requested_urls, placed_archive_path):
    """The first load downloads, unpacks and deletes the archive; the second load reads the unpacked files."""
    # --- act --------------------------
    first_value = ArtifactStore.load(SampleDownloadedLinesDeclaration)
    second_value = ArtifactStore.load(SampleDownloadedLinesDeclaration)

    # --- assert -----------------------
    assert first_value == second_value == SAMPLE_LINES
    assert stub_download_requested_urls == ["https://example.invalid/sample_downloaded_lines.tar.zst"]
    assert not placed_archive_path.exists()


def test_load_uses_files_placed_in_the_cache_by_hand(stub_download_requested_urls, lines_file_cache_path):
    """Matching files already in the cache, e.g. copied there by an offline user, need no archive."""
    # --- arrange ----------------------
    for path, content in SampleLinesDeclaration.to_files(SAMPLE_LINES).items():
        (lines_file_cache_path.parent / path).parent.mkdir(parents=True, exist_ok=True)
        (lines_file_cache_path.parent / path).write_bytes(content)

    # --- act --------------------------
    value = ArtifactStore.load(SampleDownloadedLinesDeclaration)

    # --- assert -----------------------
    assert value == SAMPLE_LINES
    assert stub_download_requested_urls == []


@pytest.mark.parametrize(
    "placed_archive_bytes, expected_urls",
    [
        (_COMMITTED_ARCHIVE_PATH.read_bytes(), []),
        (b"corrupted", ["https://example.invalid/sample_downloaded_lines.tar.zst"]),
    ],
)
def test_load_unpacks_an_archive_placed_in_the_cache_by_hand(
    stub_download_requested_urls, lines_file_cache_path, placed_archive_path, placed_archive_bytes, expected_urls
):
    """A hand-placed archive is used if it matches the archive entry, else downloaded; either way it is deleted."""
    # --- arrange ----------------------
    placed_archive_path.parent.mkdir(parents=True)
    placed_archive_path.write_bytes(placed_archive_bytes)

    # --- act --------------------------
    value = ArtifactStore.load(SampleDownloadedLinesDeclaration)

    # --- assert -----------------------
    assert value == SAMPLE_LINES
    assert stub_download_requested_urls == expected_urls
    assert lines_file_cache_path.is_file()
    assert not placed_archive_path.exists()


def test_load_downloads_again_when_a_cached_file_does_not_match_its_entry(
    stub_download_requested_urls, lines_file_cache_path
):
    """A cached file whose hash differs from its manifest entry is replaced from a fresh download of the archive."""
    # --- arrange ----------------------
    lines_file_cache_path.parent.mkdir(parents=True)
    lines_file_cache_path.write_text("corrupted\n")

    # --- act --------------------------
    value = ArtifactStore.load(SampleDownloadedLinesDeclaration)

    # --- assert -----------------------
    assert value == SAMPLE_LINES
    assert lines_file_cache_path.read_bytes() == SampleLinesDeclaration.to_files(SAMPLE_LINES)["lines.txt"]
    assert stub_download_requested_urls == ["https://example.invalid/sample_downloaded_lines.tar.zst"]


@pytest.mark.parametrize(
    "download, message",
    [
        (_raise_connection_error, r"Downloading https://example\.invalid/\S+ failed"),
        (lambda url: b"unexpected\n", r"does not match the size and sha256 in the manifest"),
    ],
)
def test_load_reports_a_failed_or_wrong_download_and_caches_nothing(
    monkeypatch, cache_root_in_tmp, placed_archive_path, download, message
):
    """A download that fails, or returns other bytes than the archive entry, is an error that names the archive path.

    The cache stays empty.
    """
    # --- arrange ----------------------
    monkeypatch.setattr(ArtifactStore, "_download", staticmethod(download))

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=message) as error_info:
        ArtifactStore.load(SampleDownloadedLinesDeclaration)
    assert str(placed_archive_path) in str(error_info.value)
    assert not any(path.is_file() for path in cache_root_in_tmp.rglob("*"))


def test_load_refuses_an_archive_whose_files_differ_from_the_manifest(monkeypatch, artifacts_folder_in_tmp):
    """An archive that matches its archive entry but holds a file that differs from its manifest entry is refused."""
    # --- arrange ----------------------
    archive_bytes = ArtifactArchiver.pack(SampleLinesDeclaration.to_files(["alpha", "beta", "delta"]))
    archive_entry = ArtifactArchiveEntry.from_content("https://example.invalid/other.tar.zst", archive_bytes)
    manifest = _load_committed_manifest().model_copy(update={"archive": archive_entry})
    folder = artifacts_folder_in_tmp / SampleDownloadedLinesDeclaration.name
    folder.mkdir(parents=True)
    (folder / "manifest.json").write_text(manifest.to_json())
    _stub_download(monkeypatch, {archive_entry.url: archive_bytes})

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=r"holds files that differ from the manifest: \['lines\.txt'\]"):
        ArtifactStore.load(SampleDownloadedLinesDeclaration)


# ==================================================================================================
#  Saving and verification
# ==================================================================================================
def test_save_writes_the_data_files_to_the_cache_and_only_the_manifest_to_the_artifact_folder(
    monkeypatch, artifacts_folder_in_tmp, lines_file_cache_path
):
    """A saved downloaded artifact has only its manifest in its folder, and loads from the data files in the cache."""
    # --- arrange ----------------------
    monkeypatch.setattr(ArtifactStore, "_download", staticmethod(_raise_connection_error))
    folder = artifacts_folder_in_tmp / SampleDownloadedLinesDeclaration.name
    folder.mkdir(parents=True)
    (folder / "lines.txt").write_text("left over\n")

    # --- act --------------------------
    ArtifactStore.save(SampleDownloadedLinesDeclaration, SAMPLE_LINES)

    # --- assert -----------------------
    assert [path.name for path in folder.iterdir()] == ["manifest.json"]
    assert (lines_file_cache_path.parent / "meta" / "count.txt").is_file()
    assert ArtifactStore.load(SampleDownloadedLinesDeclaration) == SAMPLE_LINES
    with pytest.raises(ArtifactError, match="the manifest has no archive entry"):
        ArtifactStore.verify(SampleDownloadedLinesDeclaration)


@pytest.mark.usefixtures("artifacts_folder_in_tmp")
def test_load_without_archive_entry_or_cached_copy_fails(lines_file_cache_path):
    """A saved downloaded artifact whose cached copy is gone cannot be loaded: its manifest has no archive entry."""
    # --- arrange ----------------------
    ArtifactStore.save(SampleDownloadedLinesDeclaration, SAMPLE_LINES)
    lines_file_cache_path.unlink()

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match="has no archive entry"):
        ArtifactStore.load(SampleDownloadedLinesDeclaration)


def test_verify_accepts_the_committed_downloaded_artifact():
    """The committed manifest is the only file in its folder and has an archive entry, so `verify` passes."""
    assert ArtifactStore.verify(SampleDownloadedLinesDeclaration).name == SampleDownloadedLinesDeclaration.name


def test_verify_reports_a_data_file_committed_next_to_a_downloaded_artifact(artifacts_folder_in_tmp):
    """A downloaded artifact's folder holds only its manifest, so a data file beside it fails `verify`."""
    # --- arrange ----------------------
    folder = artifacts_folder_in_tmp / SampleDownloadedLinesDeclaration.name
    folder.mkdir(parents=True)
    (folder / "manifest.json").write_bytes(_COMMITTED_MANIFEST_PATH.read_bytes())
    (folder / "lines.txt").write_text("alpha\n")

    # --- act / assert -----------------
    with pytest.raises(
        ArtifactError, match=r"lines\.txt is next to the manifest, but the artifact's data files are downloaded"
    ):
        ArtifactStore.verify(SampleDownloadedLinesDeclaration)


def test_verify_reports_an_archive_entry_for_an_artifact_shipped_in_the_package(artifacts_folder_in_tmp):
    """`verify` rejects an archive entry in the manifest of an artifact shipped in the package."""
    # --- arrange ----------------------
    manifest = ArtifactStore.save(SampleLinesDeclaration, SAMPLE_LINES)
    archive_entry = ArtifactArchiveEntry.from_content("https://example.invalid/sample_lines.tar.zst", b"")
    manifest_file = artifacts_folder_in_tmp / SampleLinesDeclaration.name / "manifest.json"
    manifest_file.write_text(manifest.model_copy(update={"archive": archive_entry}).to_json())

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match="has an archive entry, but the artifact ships in the package"):
        ArtifactStore.verify(SampleLinesDeclaration)


# ==================================================================================================
#  Cache folder and download
# ==================================================================================================
def test_the_cache_root_is_the_user_cache_folder_unless_the_environment_variable_is_set(monkeypatch):
    """Without ``SUNNBEAR_CACHE_DIR``, downloaded files are cached in the user's cache folder for sunnbear."""
    # --- arrange ----------------------
    monkeypatch.delenv("SUNNBEAR_CACHE_DIR")
    manifest = _load_committed_manifest()

    # --- act --------------------------
    cache_folder = ArtifactStore._cache_folder_of(manifest)

    # --- assert -----------------------
    assert cache_folder == Path(platformdirs.user_cache_dir("sunnbear")) / manifest.name / manifest.content_hash


def test_download_returns_the_bytes_at_a_url(tmp_path):
    """The unpatched `ArtifactStore._download` reads any URL that `urllib` opens; a ``file:`` URL keeps it offline."""
    # --- arrange ----------------------
    source = tmp_path / "source.txt"
    source.write_bytes(b"alpha\n")

    # --- act / assert -----------------
    assert ArtifactStore._download(source.as_uri()) == b"alpha\n"
