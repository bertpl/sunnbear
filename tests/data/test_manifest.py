"""An `ArtifactManifest` identifies an artifact by its content and round-trips through deterministic JSON."""

import datetime
import json

import pytest

from sunnbear._core.data import ArtifactError, ArtifactFileEntry, ArtifactManifest


def _make_manifest(**overrides) -> ArtifactManifest:
    """Return a manifest with 2 files, overriding any field by keyword."""
    fields = {
        "name": "sample",
        "data_schema_version": 1,
        "files": (
            ArtifactFileEntry.from_content("values.csv", b"u,v\n0.25,0.75\n"),
            ArtifactFileEntry.from_content("notes/readme.txt", b"hello\n"),
        ),
        "input_artifact_hashes": {"upstream": "ab" * 32},
        "built_with": {"sunnbear": "0.1.3"},
        "build_date": datetime.date(2026, 9, 25),
        "generated_by": {"function": "sample.generate", "arguments": {"seed": 42}},
    }
    return ArtifactManifest(**(fields | overrides))


# ==================================================================================================
#  ArtifactFileEntry
# ==================================================================================================
def test_artifact_file_entry_from_content_records_hash_and_size():
    """`from_content` records the sha256 and the byte count, and `matches` accepts only that content."""
    # --- arrange / act ----------------
    entry = ArtifactFileEntry.from_content("values.csv", b"abc")

    # --- assert -----------------------
    assert entry.sha256 == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert entry.size_bytes == 3
    assert entry.matches(b"abc")
    assert not entry.matches(b"abx")


@pytest.mark.parametrize("path", ["", "/abs/values.csv", "../values.csv", "data/../../values.csv"])
def test_artifact_file_entry_rejects_a_path_outside_its_folder(path):
    """A path that is empty, absolute, or points outside the artifact's folder is refused."""
    with pytest.raises(ValueError, match="must be relative"):
        ArtifactFileEntry.from_content(path, b"abc")


# ==================================================================================================
#  Identity
# ==================================================================================================
def test_short_identity_is_the_name_and_the_shortened_content_hash():
    """`short_identity` is ``name@`` followed by the first 8 hex digits of `content_hash`."""
    # --- arrange ----------------------
    manifest = _make_manifest()

    # --- act / assert -----------------
    assert manifest.short_identity == f"sample@{manifest.content_hash[:8]}"


@pytest.mark.parametrize(
    "overrides",
    [
        {"name": "other"},
        {"data_schema_version": 2},
        {"input_artifact_hashes": {}},
        {"built_with": {"sunnbear": "9.9.9"}},
        {"build_date": datetime.date(2030, 1, 1)},
        {"generated_by": None},
    ],
)
def test_content_hash_ignores_everything_but_the_files(overrides):
    """Only the files decide the content hash; the name, schema version and build metadata do not."""
    assert _make_manifest(**overrides).content_hash == _make_manifest().content_hash


@pytest.mark.parametrize(
    "files",
    [
        (ArtifactFileEntry.from_content("values.csv", b"u,v\n0.25,0.76\n"),),  # changed content
        (ArtifactFileEntry.from_content("renamed.csv", b"u,v\n0.25,0.75\n"),),  # same content, other path
    ],
)
def test_content_hash_changes_with_file_content_or_path(files):
    """Changing a file's content or its path changes the content hash."""
    # --- arrange ----------------------
    baseline = _make_manifest(files=(ArtifactFileEntry.from_content("values.csv", b"u,v\n0.25,0.75\n"),))

    # --- act / assert -----------------
    assert _make_manifest(files=files).content_hash != baseline.content_hash


@pytest.mark.parametrize(
    "files, message",
    [
        ((), "at least 1 file"),
        (
            (ArtifactFileEntry.from_content("a.csv", b"1"), ArtifactFileEntry.from_content("a.csv", b"2")),
            "each file path once",
        ),
    ],
)
def test_manifest_rejects_missing_or_duplicate_files(files, message):
    """A manifest needs at least 1 file, and no 2 files may share a path."""
    with pytest.raises(ValueError, match=message):
        _make_manifest(files=files)


# ==================================================================================================
#  JSON
# ==================================================================================================
@pytest.mark.parametrize(
    "manifest",
    [
        _make_manifest(),
        _make_manifest(generated_by=None, input_artifact_hashes={}),
        _make_manifest(
            files=(ArtifactFileEntry.from_content("big.parquet", b"\x00\x01", url="https://example.org/big"),)
        ),
    ],
)
def test_manifest_round_trips_through_json(manifest):
    """`from_json` rebuilds an equal manifest from `to_json`'s output."""
    assert ArtifactManifest.from_json(manifest.to_json()) == manifest


def test_to_json_is_deterministic_and_records_the_content_hash():
    """`to_json` writes deterministic JSON that records `content_hash` and omits a `None` `url`."""
    # --- arrange ----------------------
    manifest = _make_manifest()

    # --- act --------------------------
    text = manifest.to_json()

    # --- assert -----------------------
    data = json.loads(text)
    assert text == json.dumps(data, sort_keys=True, indent=2) + "\n"
    assert data["content_hash"] == manifest.content_hash
    assert "url" not in data["files"][0]


def _make_edited_json(edit) -> str:
    """Return the JSON of the default manifest after `edit` changes its parsed form in place."""
    data = json.loads(_make_manifest().to_json())
    edit(data)
    return json.dumps(data)


@pytest.mark.parametrize(
    "text, message",
    [
        ("not json", "Malformed"),
        ("[]", "Malformed"),
        (_make_edited_json(lambda d: d.pop("build_date")), "Malformed"),  # missing key
        (_make_edited_json(lambda d: d.pop("content_hash")), "Malformed"),  # no recorded content hash
        (_make_edited_json(lambda d: d.update(extra=1)), "Malformed"),  # unknown key
        (_make_edited_json(lambda d: d.update(data_schema_version="1")), "Malformed"),  # wrong type
        (_make_edited_json(lambda d: d.update(data_schema_version=True)), "Malformed"),  # a bool is not an int
        (_make_edited_json(lambda d: d.update(generated_by=[1])), "Malformed"),  # generated_by is an object or null
        (_make_edited_json(lambda d: d["files"][0].update(size_bytes=-1.5)), "Malformed"),  # wrong type in a file entry
        (
            _make_edited_json(lambda d: d["files"][0].update(path="../x")),
            "Malformed",
        ),  # file path leaves the artifact's folder
        (_make_edited_json(lambda d: d.update(content_hash="0" * 64)), "hash to"),  # recorded hash is stale
        (_make_edited_json(lambda d: d["files"][0].update(sha256="0" * 64)), "hash to"),  # a file hash was edited
    ],
)
def test_from_json_rejects_a_malformed_or_inconsistent_manifest(text, message):
    """Anything but a well-formed manifest whose content hash matches its file entries raises `ArtifactError`."""
    with pytest.raises(ArtifactError, match=message):
        ArtifactManifest.from_json(text)
