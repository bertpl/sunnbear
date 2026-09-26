"""A manifest records what a data artifact's files are, and the content hash that identifies the artifact.

A data artifact is a named, frozen dataset that sunnbear produces once and users consume, such as
a sample set for Monte Carlo runs. Its manifest records only facts that rerunning the generating
code would not reproduce; see `ArtifactManifest` for an overview of the (nested) fields of such a
manifest.

The identity of an artifact is its content hash, `ArtifactManifest.content_hash`, computed from its
file entries alone. The identity is never a hand-maintained version number, which could silently
go unchanged when the data changes.

`ArtifactManifest.short_identity` shows the content hash shortened, the way git shows commits, e.g.
``uv_tuples@3f2a9c1e``; comparisons use the full `ArtifactManifest.content_hash`.

`ArtifactManifest.to_json` writes a given manifest as the same bytes every time (keys sorted, fixed
indentation), so a changed manifest shows a readable diff. `ArtifactManifest.from_json` accepts
only a well-formed manifest whose recorded content hash matches the hash of its file entries, and
raises `ArtifactError` otherwise; it does not read the files, and `ArtifactFileEntry.matches`
checks a file's bytes against its entry.
"""

import datetime
import hashlib
import json
from pathlib import PurePosixPath
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from .exceptions import ArtifactError

_SHORT_HASH_LENGTH = 8


# ==================================================================================================
#  ArtifactManifest
# ==================================================================================================
class ArtifactManifest(BaseModel):
    """An `ArtifactManifest` describes one data artifact: its files, its content hash, and how it was built.

    Validation is strict: a value of the wrong type is refused, not converted, and unknown fields
    are refused.

    Attributes:
        files: The artifact's data files; at least 1, with unique paths. Their order is part of the
            content hash.
        input_artifact_hashes: The content hashes of the artifacts that this artifact was generated
            from, keyed by artifact name.
        built_with: The versions of sunnbear and of the libraries that affect the content, keyed by
            package name.
        build_date: The date the artifact was built.
        generated_by: The public sunnbear function call that generated the artifact, with its
            arguments, as JSON-compatible data; ``None`` when no public function generated it.
        download: The archive that holds all data files of a downloaded artifact, once it is
            published; ``None`` for an artifact shipped in the package. Not part of the content
            hash, so recording it keeps the artifact's identity.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    name: str
    files: tuple["ArtifactFileEntry", ...]
    input_artifact_hashes: dict[str, str] = Field(default_factory=dict)
    built_with: dict[str, str] = Field(default_factory=dict)
    build_date: datetime.date
    generated_by: dict[str, Any] | None = None
    download: "ArtifactArchiveEntry | None" = None

    @field_validator("files")
    @classmethod
    def _check_files_are_present_and_unique(
        cls, files: tuple["ArtifactFileEntry", ...]
    ) -> tuple["ArtifactFileEntry", ...]:
        """Refuse an empty file list, or 2 entries with the same path."""
        if not files:
            raise ValueError("An artifact has at least 1 file.")
        paths = [entry.path for entry in files]
        if len(set(paths)) != len(paths):
            raise ValueError(f"An artifact lists each file path once, got {paths}.")
        return files

    # --------------------------------------------------------------------------
    #  Identity
    # --------------------------------------------------------------------------
    @computed_field
    @property
    def content_hash(self) -> str:
        """Return the sha256, as hex, over each file's path and sha256 in `files` order."""
        digest = hashlib.sha256()
        for entry in self.files:
            digest.update(f"{entry.path}\0{entry.sha256}\n".encode())
        return digest.hexdigest()

    @property
    def short_identity(self) -> str:
        """Return the name and the shortened content hash, e.g. ``uv_tuples@3f2a9c1e``, for display only."""
        return f"{self.name}@{self.content_hash[:_SHORT_HASH_LENGTH]}"

    # --------------------------------------------------------------------------
    #  JSON
    # --------------------------------------------------------------------------
    def to_json(self) -> str:
        """Return the manifest as JSON: sorted keys, 2-space indentation, a final newline; `None` fields left out."""
        return json.dumps(self.model_dump(mode="json", exclude_none=True), sort_keys=True, indent=2) + "\n"

    @staticmethod
    def from_json(text: str) -> "ArtifactManifest":
        """Parse a manifest written by `to_json`.

        It never reads the data files; check each file's bytes with `ArtifactFileEntry.matches`.

        Raises:
            ArtifactError: If the text is not a well-formed manifest, or records a content hash
                that does not match the hash of its file entries.
        """
        try:
            manifest_json = json.loads(text)
            # `content_hash` is recorded for readers but derived from the files, so it is compared
            # after validation, not validated as an input field.
            recorded_hash = manifest_json.pop("content_hash")
            manifest = ArtifactManifest.model_validate_json(json.dumps(manifest_json))
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            raise ArtifactError(f"Malformed artifact manifest: {error}") from error
        if recorded_hash != manifest.content_hash:
            raise ArtifactError(
                f"Manifest of '{manifest.name}' records content hash {recorded_hash}, "
                f"but its file entries hash to {manifest.content_hash}."
            )
        return manifest


# ==================================================================================================
#  ArtifactContentEntry and its subclasses
# ==================================================================================================
class ArtifactContentEntry(BaseModel):
    """An `ArtifactContentEntry` records what the bytes of one file hash to; subclasses say which file it is.

    Attributes:
        sha256: The sha256 of the file's bytes, as hex.
        size_bytes: The number of bytes in the file.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    sha256: str
    size_bytes: int

    def matches(self, content: bytes) -> bool:
        """Return whether `content` has this entry's size and sha256."""
        return len(content) == self.size_bytes and hashlib.sha256(content).hexdigest() == self.sha256


class ArtifactFileEntry(ArtifactContentEntry):
    """An `ArtifactFileEntry` describes one data file of an artifact: where it lives and what its bytes hash to.

    Attributes:
        path: Where the file sits once it is available, relative to the artifact's folder for a
            file shipped in the sunnbear package, or to the artifact's cache folder for a
            downloaded one; forward slashes, never leaving that folder.
    """

    path: str

    @field_validator("path")
    @classmethod
    def _check_path_stays_inside_folder(cls, path: str) -> str:
        """Refuse a path that is empty, absolute, or contains a ``..`` part."""
        parts = PurePosixPath(path).parts
        if not parts or path.startswith("/") or ".." in parts:
            raise ValueError(f"Artifact file path '{path}' must be relative and stay inside the artifact's folder.")
        return path

    @staticmethod
    def from_content(path: str, content: bytes) -> "ArtifactFileEntry":
        """Describe a file by hashing its content."""
        return ArtifactFileEntry(path=path, sha256=hashlib.sha256(content).hexdigest(), size_bytes=len(content))


class ArtifactArchiveEntry(ArtifactContentEntry):
    """An `ArtifactArchiveEntry` describes the archive of a downloaded artifact: where to download it, and its hash.

    Attributes:
        url: Where to download the archive from.
    """

    url: str

    @staticmethod
    def from_content(url: str, content: bytes) -> "ArtifactArchiveEntry":
        """Describe an archive by hashing its content."""
        return ArtifactArchiveEntry(url=url, sha256=hashlib.sha256(content).hexdigest(), size_bytes=len(content))
