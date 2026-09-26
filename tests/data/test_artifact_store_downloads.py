"""`ArtifactStore` downloads the data files of an artifact with source `DOWNLOAD` into a cache, and checks them."""

from pathlib import Path

import platformdirs
import pytest

from sunnbear._core.data import ArtifactError, ArtifactManifest, ArtifactStore

from .sample_declarations import SAMPLE_LINES, SampleDownloadedLinesDeclaration, SampleLinesDeclaration

# The committed manifest of `SampleDownloadedLinesDeclaration`, read by path so that a test which
# moves artifact folders into `tmp_path` still finds it.
_COMMITTED_MANIFEST_PATH = Path(__file__).parent / "artifacts" / SampleDownloadedLinesDeclaration.name / "manifest.json"


def _load_committed_manifest() -> ArtifactManifest:
    """Return the committed manifest of `SampleDownloadedLinesDeclaration`."""
    return ArtifactManifest.from_json(_COMMITTED_MANIFEST_PATH.read_text())


def _raise_connection_error(url: str) -> bytes:
    """Stand in for a download that cannot connect."""
    raise ConnectionError(f"cannot reach {url}")


@pytest.fixture
def requested_urls(monkeypatch):
    """Replace the download with a local stand-in that serves the sample files; return the requested URLs."""
    manifest = _load_committed_manifest()
    contents = SampleLinesDeclaration.to_files(SAMPLE_LINES)
    content_by_url = {entry.url: contents[entry.path] for entry in manifest.files}
    urls = []

    def download(url: str) -> bytes:
        urls.append(url)
        return content_by_url[url]

    monkeypatch.setattr(ArtifactStore, "_download", staticmethod(download))
    return urls


@pytest.fixture
def lines_file_cache_path(cache_root_in_tmp):
    """Return the cache path of the committed downloaded artifact's ``lines.txt``."""
    manifest = _load_committed_manifest()
    return cache_root_in_tmp / manifest.name / manifest.content_hash / "lines.txt"


# ==================================================================================================
#  Loading
# ==================================================================================================
def test_load_downloads_each_file_once_and_then_reads_the_cache(requested_urls):
    """The first load downloads every file; the second load reads them all from the cache."""
    # --- act --------------------------
    first_value = ArtifactStore.load(SampleDownloadedLinesDeclaration)
    second_value = ArtifactStore.load(SampleDownloadedLinesDeclaration)

    # --- assert -----------------------
    assert first_value == second_value == SAMPLE_LINES
    assert requested_urls == [
        "https://example.invalid/sample_downloaded_lines/lines.txt",
        "https://example.invalid/sample_downloaded_lines/meta/count.txt",
    ]


def test_load_uses_files_placed_in_the_cache_by_hand(requested_urls, lines_file_cache_path):
    """A matching file already in the cache, e.g. copied there by an offline user, is not downloaded."""
    # --- arrange ----------------------
    for path, content in SampleLinesDeclaration.to_files(SAMPLE_LINES).items():
        (lines_file_cache_path.parent / path).parent.mkdir(parents=True, exist_ok=True)
        (lines_file_cache_path.parent / path).write_bytes(content)

    # --- act --------------------------
    value = ArtifactStore.load(SampleDownloadedLinesDeclaration)

    # --- assert -----------------------
    assert value == SAMPLE_LINES
    assert requested_urls == []


def test_load_downloads_again_a_cached_file_that_does_not_match_its_entry(requested_urls, lines_file_cache_path):
    """A cached file whose hash differs from its manifest entry is replaced by a fresh download."""
    # --- arrange ----------------------
    lines_file_cache_path.parent.mkdir(parents=True)
    lines_file_cache_path.write_text("corrupted\n")

    # --- act --------------------------
    value = ArtifactStore.load(SampleDownloadedLinesDeclaration)

    # --- assert -----------------------
    assert value == SAMPLE_LINES
    assert lines_file_cache_path.read_bytes() == SampleLinesDeclaration.to_files(SAMPLE_LINES)["lines.txt"]
    assert "https://example.invalid/sample_downloaded_lines/lines.txt" in requested_urls


@pytest.mark.parametrize(
    "download, message",
    [
        (_raise_connection_error, r"Downloading https://example\.invalid/\S+ to .* failed"),
        (lambda url: b"unexpected\n", r"does not match its manifest entry, so it was not stored at"),
    ],
)
def test_load_reports_a_failed_or_wrong_download_and_caches_nothing(monkeypatch, cache_root_in_tmp, download, message):
    """A download that fails, or returns other bytes than its manifest entry, is an error that names the cache path."""
    # --- arrange ----------------------
    monkeypatch.setattr(ArtifactStore, "_download", staticmethod(download))

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=message) as error_info:
        ArtifactStore.load(SampleDownloadedLinesDeclaration)
    assert str(cache_root_in_tmp) in str(error_info.value)
    assert not any(path.is_file() for path in cache_root_in_tmp.rglob("*"))


# ==================================================================================================
#  Saving and verification
# ==================================================================================================
def test_save_writes_the_data_files_to_the_cache_and_only_the_manifest_to_the_artifact_folder(
    monkeypatch, artifact_folders_in_tmp, lines_file_cache_path
):
    """A saved downloaded artifact loads back from the cache without a download, but its manifest has no URLs."""
    # --- arrange ----------------------
    monkeypatch.setattr(ArtifactStore, "_download", staticmethod(_raise_connection_error))
    folder = artifact_folders_in_tmp / SampleDownloadedLinesDeclaration.name
    folder.mkdir(parents=True)
    (folder / "lines.txt").write_text("left over\n")

    # --- act --------------------------
    ArtifactStore.save(SampleDownloadedLinesDeclaration, SAMPLE_LINES)

    # --- assert -----------------------
    assert [path.name for path in folder.iterdir()] == ["manifest.json"]
    assert (lines_file_cache_path.parent / "meta" / "count.txt").is_file()
    assert ArtifactStore.load(SampleDownloadedLinesDeclaration) == SAMPLE_LINES
    with pytest.raises(ArtifactError, match=r"lines\.txt has no download URL"):
        ArtifactStore.verify(SampleDownloadedLinesDeclaration)


@pytest.mark.usefixtures("artifact_folders_in_tmp")
def test_load_of_a_file_without_url_or_cached_copy_fails(lines_file_cache_path):
    """A saved downloaded artifact whose cached copy is gone cannot be loaded, since its manifest has no URL."""
    # --- arrange ----------------------
    ArtifactStore.save(SampleDownloadedLinesDeclaration, SAMPLE_LINES)
    lines_file_cache_path.unlink()

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=r"has no download URL for lines\.txt"):
        ArtifactStore.load(SampleDownloadedLinesDeclaration)


def test_verify_accepts_the_committed_downloaded_artifact():
    """The committed manifest is the only file in its folder and gives every file a URL, so `verify` passes."""
    assert ArtifactStore.verify(SampleDownloadedLinesDeclaration).name == SampleDownloadedLinesDeclaration.name


def test_verify_reports_a_data_file_committed_next_to_a_downloaded_artifact(artifact_folders_in_tmp):
    """A downloaded artifact's folder holds only its manifest, so a data file beside it fails `verify`."""
    # --- arrange ----------------------
    folder = artifact_folders_in_tmp / SampleDownloadedLinesDeclaration.name
    folder.mkdir(parents=True)
    (folder / "manifest.json").write_bytes(_COMMITTED_MANIFEST_PATH.read_bytes())
    (folder / "lines.txt").write_text("alpha\n")

    # --- act / assert -----------------
    with pytest.raises(
        ArtifactError, match=r"lines\.txt is next to the manifest, but the artifact's data files are downloaded"
    ):
        ArtifactStore.verify(SampleDownloadedLinesDeclaration)


# ==================================================================================================
#  Cache folder and download
# ==================================================================================================
def test_the_cache_root_is_the_user_cache_folder_unless_the_environment_variable_is_set(monkeypatch):
    """Without ``SUNNBEAR_DATA_DIR``, downloaded files are cached in the user's cache folder for sunnbear."""
    # --- arrange ----------------------
    monkeypatch.delenv("SUNNBEAR_DATA_DIR")
    manifest = _load_committed_manifest()

    # --- act --------------------------
    cache_folder = ArtifactStore._cache_folder_of(manifest)

    # --- assert -----------------------
    assert cache_folder == Path(platformdirs.user_cache_dir("sunnbear")) / manifest.name / manifest.content_hash


def test_download_returns_the_bytes_at_a_url(tmp_path):
    """The real download reads any URL that `urllib` opens; a ``file:`` URL keeps the test offline."""
    # --- arrange ----------------------
    source = tmp_path / "source.txt"
    source.write_bytes(b"alpha\n")

    # --- act / assert -----------------
    assert ArtifactStore._download(source.as_uri()) == b"alpha\n"
