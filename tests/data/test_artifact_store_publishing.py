"""`ArtifactStore.publish` hosts a downloaded artifact's archive as a data release, and records it in the manifest."""

import shutil

import pytest

from sunnbear._core.data import (
    ArtifactArchiver,
    ArtifactDataReleases,
    ArtifactError,
    ArtifactStore,
    DataRelease,
)

from .sample_declarations import SAMPLE_LINES, SampleDownloadedLinesDeclaration, SampleLinesDeclaration


class _FakeGitHub:
    """`_FakeGitHub` stands in for GitHub: it holds data releases in memory, and serves their files by URL."""

    def __init__(self) -> None:
        """Start without any release."""
        self.releases: dict[str, DataRelease] = {}
        self.files_by_url: dict[str, bytes] = {}
        self.created_tags: list[str] = []

    def find(self, tag: str) -> DataRelease | None:
        """Return the release with this tag, as `ArtifactDataReleases.find` does."""
        return self.releases.get(tag)

    def create(self, tag: str, file_name: str, content: bytes, title: str, notes: str) -> None:
        """Publish a release with one file, as `ArtifactDataReleases.create` does."""
        url = f"https://example.invalid/{tag}/{file_name}"
        self.files_by_url[url] = content
        self.releases[tag] = DataRelease(is_draft=False, asset_urls={file_name: url})
        self.created_tags.append(tag)

    def download(self, url: str) -> bytes:
        """Return the file at `url`, as `ArtifactStore._download` does."""
        return self.files_by_url[url]


@pytest.fixture
def fake_github(monkeypatch, artifacts_folder_in_tmp):
    """Route every data release call and download of `ArtifactStore` to a `_FakeGitHub`, with write access."""
    github = _FakeGitHub()
    monkeypatch.setattr(ArtifactDataReleases, "check_write_access", staticmethod(lambda: None))
    monkeypatch.setattr(ArtifactDataReleases, "find", staticmethod(github.find))
    monkeypatch.setattr(ArtifactDataReleases, "create", staticmethod(github.create))
    monkeypatch.setattr(ArtifactStore, "_download", staticmethod(github.download))
    return github


def _tag_of_sample() -> str:
    """Return the data release tag of `SampleDownloadedLinesDeclaration` after it has been saved."""
    manifest = ArtifactStore.load_manifest(SampleDownloadedLinesDeclaration)
    return ArtifactDataReleases.tag_of(manifest.name, manifest.content_hash)


# ==================================================================================================
#  Publishing
# ==================================================================================================
def test_publish_creates_the_release_and_records_the_archive(fake_github, cache_root_in_tmp):
    """After `save` and `publish`, the artifact verifies, and loads from its data release with an empty cache."""
    # --- arrange ----------------------
    ArtifactStore.save(SampleDownloadedLinesDeclaration, SAMPLE_LINES)

    # --- act --------------------------
    manifest = ArtifactStore.publish(SampleDownloadedLinesDeclaration)

    # --- assert -----------------------
    assert fake_github.created_tags == [_tag_of_sample()]
    assert manifest.archive.url == f"https://example.invalid/{_tag_of_sample()}/sample_downloaded_lines.tar.zst"
    assert ArtifactStore.verify(SampleDownloadedLinesDeclaration) == manifest
    shutil.rmtree(cache_root_in_tmp)
    assert ArtifactStore.load(SampleDownloadedLinesDeclaration) == SAMPLE_LINES


def test_publish_records_an_existing_release_without_creating_another(fake_github):
    """Publishing an artifact whose data release exists checks and records that release's archive."""
    # --- arrange ----------------------
    ArtifactStore.save(SampleDownloadedLinesDeclaration, SAMPLE_LINES)
    first_manifest = ArtifactStore.publish(SampleDownloadedLinesDeclaration)

    # --- act --------------------------
    second_manifest = ArtifactStore.publish(SampleDownloadedLinesDeclaration)

    # --- assert -----------------------
    assert second_manifest == first_manifest
    assert fake_github.created_tags == [_tag_of_sample()]


def test_publish_refuses_an_existing_release_whose_files_differ(fake_github):
    """An existing data release whose archive holds other files than the manifest lists is not recorded."""
    # --- arrange ----------------------
    ArtifactStore.save(SampleDownloadedLinesDeclaration, SAMPLE_LINES)
    other_archive = ArtifactArchiver.pack(SampleLinesDeclaration.to_files(["alpha", "beta", "delta"]))
    fake_github.create(_tag_of_sample(), "sample_downloaded_lines.tar.zst", other_archive, title="", notes="")

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=r"holds files that differ from the manifest: \['lines\.txt'\]"):
        ArtifactStore.publish(SampleDownloadedLinesDeclaration)


@pytest.mark.parametrize(
    "release",
    [
        DataRelease(is_draft=True, asset_urls={"sample_downloaded_lines.tar.zst": "https://example.invalid/x"}),
        DataRelease(is_draft=False, asset_urls={}),
    ],
)
def test_publish_refuses_a_draft_or_incomplete_release(fake_github, release):
    """A data release left as a draft, or without the archive, must be deleted before publishing again."""
    # --- arrange ----------------------
    ArtifactStore.save(SampleDownloadedLinesDeclaration, SAMPLE_LINES)
    fake_github.releases[_tag_of_sample()] = release

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=r"is a draft or lacks .*gh release delete"):
        ArtifactStore.publish(SampleDownloadedLinesDeclaration)


# ==================================================================================================
#  Refusals before anything is published
# ==================================================================================================
def test_publish_needs_the_data_files_in_the_cache(fake_github, cache_root_in_tmp):
    """Without the saved data files in the cache, nothing is published."""
    # --- arrange ----------------------
    ArtifactStore.save(SampleDownloadedLinesDeclaration, SAMPLE_LINES)
    shutil.rmtree(cache_root_in_tmp)

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match="save the artifact before publishing it"):
        ArtifactStore.publish(SampleDownloadedLinesDeclaration)
    assert fake_github.created_tags == []


@pytest.mark.usefixtures("fake_github")
def test_publish_refuses_an_artifact_shipped_in_the_package():
    """An artifact shipped in the package has no data release."""
    with pytest.raises(ArtifactError, match="ships in the package"):
        ArtifactStore.publish(SampleLinesDeclaration)


def test_publish_checks_write_access_first(monkeypatch, fake_github):
    """Without write access, the error of the access check stops publishing before any release is created."""
    # --- arrange ----------------------
    ArtifactStore.save(SampleDownloadedLinesDeclaration, SAMPLE_LINES)

    def refuse() -> None:
        raise ArtifactError("maintainer-only")

    monkeypatch.setattr(ArtifactDataReleases, "check_write_access", staticmethod(refuse))

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match="maintainer-only"):
        ArtifactStore.publish(SampleDownloadedLinesDeclaration)
    assert fake_github.created_tags == []


def test_publish_reports_a_failed_download_back(monkeypatch, fake_github):
    """A release whose archive cannot be downloaded back is not recorded in the manifest."""
    # --- arrange ----------------------
    ArtifactStore.save(SampleDownloadedLinesDeclaration, SAMPLE_LINES)

    def fail(url: str) -> bytes:
        raise ConnectionError(f"cannot reach {url}")

    monkeypatch.setattr(ArtifactStore, "_download", staticmethod(fail))

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=r"Downloading https://example\.invalid/\S+ back failed"):
        ArtifactStore.publish(SampleDownloadedLinesDeclaration)
    assert ArtifactStore.load_manifest(SampleDownloadedLinesDeclaration).archive is None
