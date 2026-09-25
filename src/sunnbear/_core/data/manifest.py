"""A manifest records what a data artifact's files are, and the content hash that identifies the artifact.

A data artifact is a named, frozen dataset that sunnbear produces once and users consume, such as
a sample set for Monte Carlo runs. Its manifest records only facts that rerunning the generating
code would not reproduce; `ArtifactManifest` and `ArtifactFileEntry` list the fields.

The identity of an artifact is its content hash, `ArtifactManifest.content_hash`, computed from its
file entries alone. The identity is never a hand-maintained version number, which could silently
go unchanged when the data changes.

`ArtifactManifest.short_identity` shows the content hash shortened, the way git shows commits, e.g.
``uv_tuples@3f2a9c1e``; comparisons use the full `ArtifactManifest.content_hash`.

`ArtifactManifest.to_json` writes deterministic JSON, so a changed manifest shows a readable diff.
`ArtifactManifest.from_json` accepts only a well-formed manifest whose recorded content hash
matches the hash of its file entries, and raises `ArtifactError` otherwise; it does not read the
files, and `ArtifactFileEntry.matches` checks a file's bytes against its entry.
"""

import datetime
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any, TypeVar, cast

from .exceptions import ArtifactError

_T = TypeVar("_T")

_SHORT_HASH_LENGTH = 8

_MANIFEST_REQUIRED_KEYS = {
    "name",
    "data_schema_version",
    "files",
    "content_hash",
    "input_artifact_hashes",
    "built_with",
    "build_date",
    "generated_by",
}
_FILE_ENTRY_REQUIRED_KEYS = {"path", "sha256", "size_bytes"}
_FILE_ENTRY_OPTIONAL_KEYS = {"url"}


# ==================================================================================================
#  ArtifactManifest
# ==================================================================================================
@dataclass(frozen=True)
class ArtifactManifest:
    """An `ArtifactManifest` describes one data artifact: its files, its content hash, and how it was built.

    Attributes:
        data_schema_version: The version of the data files' format. `from_json` does not check it;
            the code that loads the artifact compares it with the expected version.
        files: The artifact's data files; at least 1, with unique paths. Their order is part of the
            content hash.
        input_artifact_hashes: The content hashes of the artifacts that this artifact was generated
            from, keyed by artifact name.
        built_with: The versions of sunnbear and of the libraries that affect the content, keyed by
            package name.
        build_date: The date the artifact was built; defaults to the day the manifest is constructed.
        generated_by: The public sunnbear function call that generated the artifact, with its
            arguments, as JSON-compatible data; ``None`` when no public function generated it.
    """

    name: str
    data_schema_version: int
    files: tuple["ArtifactFileEntry", ...]
    # hash=False keeps these dicts out of the dataclass __hash__, since a dict is unhashable;
    # `hash=False` is unrelated to content_hash.
    input_artifact_hashes: dict[str, str] = field(default_factory=dict, hash=False)
    built_with: dict[str, str] = field(default_factory=dict, hash=False)
    build_date: datetime.date = field(default_factory=datetime.date.today)
    generated_by: dict[str, Any] | None = field(default=None, hash=False)

    def __post_init__(self) -> None:
        """Check that the manifest has files and that their paths are unique.

        Raises:
            ValueError: If `files` is empty or two files share a path.
        """
        if not self.files:
            raise ValueError(f"Artifact '{self.name}' has no files.")
        paths = [entry.path for entry in self.files]
        if len(set(paths)) != len(paths):
            raise ValueError(f"Artifact '{self.name}' lists a file path more than once: {paths}.")

    # --------------------------------------------------------------------------
    #  Identity
    # --------------------------------------------------------------------------
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
        """Return the manifest as deterministic JSON: sorted keys, 2-space indentation, a final newline."""
        manifest_json = {
            "name": self.name,
            "data_schema_version": self.data_schema_version,
            "files": [entry.to_dict() for entry in self.files],
            "content_hash": self.content_hash,
            "input_artifact_hashes": self.input_artifact_hashes,
            "built_with": self.built_with,
            "build_date": self.build_date.isoformat(),
            "generated_by": self.generated_by,
        }
        return json.dumps(manifest_json, sort_keys=True, indent=2) + "\n"

    @staticmethod
    def from_json(text: str) -> "ArtifactManifest":
        """Parse a manifest written by `to_json`.

        It never reads the data files; check each file's bytes with `ArtifactFileEntry.matches`.

        Raises:
            ArtifactError: If the text is not a well-formed manifest, or records a content hash
                that does not match the hash of its file entries.
        """
        try:
            manifest_json = _check_keys(json.loads(text), _MANIFEST_REQUIRED_KEYS, "manifest")
            generated_by = manifest_json["generated_by"]
            manifest = ArtifactManifest(
                name=_check_type(manifest_json["name"], str, "name"),
                data_schema_version=_check_type(manifest_json["data_schema_version"], int, "data_schema_version"),
                files=tuple(
                    ArtifactFileEntry.from_dict(entry_json)
                    for entry_json in _check_type(manifest_json["files"], list, "files")
                ),
                input_artifact_hashes=_check_type(
                    manifest_json["input_artifact_hashes"], dict, "input_artifact_hashes"
                ),
                built_with=_check_type(manifest_json["built_with"], dict, "built_with"),
                build_date=datetime.date.fromisoformat(_check_type(manifest_json["build_date"], str, "build_date")),
                generated_by=None if generated_by is None else _check_type(generated_by, dict, "generated_by"),
            )
        except (ValueError, TypeError) as error:
            raise ArtifactError(f"Malformed artifact manifest: {error}") from error
        if manifest_json["content_hash"] != manifest.content_hash:
            raise ArtifactError(
                f"Manifest of '{manifest.name}' records content hash {manifest_json['content_hash']}, "
                f"but its file entries hash to {manifest.content_hash}."
            )
        return manifest


# ==================================================================================================
#  ArtifactFileEntry
# ==================================================================================================
@dataclass(frozen=True)
class ArtifactFileEntry:
    """An `ArtifactFileEntry` describes one data file of an artifact: where it lives and what its bytes hash to.

    Attributes:
        path: The file's path relative to the artifact's folder, with forward slashes, never
            leaving that folder.
        sha256: The sha256 of the file's bytes, as hex.
        url: Where to download the file, for an artifact that is not shipped in the sunnbear
            package; ``None`` otherwise.
    """

    path: str
    sha256: str
    size_bytes: int
    url: str | None = None

    def __post_init__(self) -> None:
        """Check that `path` is relative and stays inside the artifact's folder.

        Raises:
            ValueError: If `path` is empty, absolute, or contains a ``..`` part.
        """
        parts = PurePosixPath(self.path).parts
        if not parts or self.path.startswith("/") or ".." in parts:
            raise ValueError(
                f"Artifact file path '{self.path}' must be relative and stay inside the artifact's folder."
            )

    @staticmethod
    def from_content(path: str, content: bytes, url: str | None = None) -> "ArtifactFileEntry":
        """Describe a file by hashing its content."""
        return ArtifactFileEntry(
            path=path, sha256=hashlib.sha256(content).hexdigest(), size_bytes=len(content), url=url
        )

    def matches(self, content: bytes) -> bool:
        """Return whether `content` has this file's size and sha256."""
        return ArtifactFileEntry.from_content(self.path, content, self.url) == self

    def to_dict(self) -> dict[str, Any]:
        """Return the file entry's JSON form; `url` is left out when it is ``None``."""
        entry_json: dict[str, Any] = {"path": self.path, "sha256": self.sha256, "size_bytes": self.size_bytes}
        if self.url is not None:
            entry_json["url"] = self.url
        return entry_json

    @staticmethod
    def from_dict(entry_json: object) -> "ArtifactFileEntry":
        """Parse the JSON form written by `to_dict`.

        Raises:
            ValueError: If keys are missing or unknown, or the path is invalid.
            TypeError: If a value has the wrong type.
        """
        entry = _check_keys(
            entry_json, _FILE_ENTRY_REQUIRED_KEYS, "file entry", optional_keys=_FILE_ENTRY_OPTIONAL_KEYS
        )
        return ArtifactFileEntry(
            path=_check_type(entry["path"], str, "path"),
            sha256=_check_type(entry["sha256"], str, "sha256"),
            size_bytes=_check_type(entry["size_bytes"], int, "size_bytes"),
            url=_check_type(entry["url"], str, "url") if "url" in entry else None,
        )


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _check_keys(
    json_value: object, required_keys: set[str], object_label: str, optional_keys: set[str] | None = None
) -> dict[str, Any]:
    """Return `json_value` unchanged if it is a JSON object with every required key and no other keys but optional ones.

    Raises:
        TypeError: If `json_value` is not a JSON object.
        ValueError: If a required key is missing or an unknown key is present.
    """
    if not isinstance(json_value, dict):
        raise TypeError(f"{object_label} must be a JSON object, got {type(json_value).__name__}.")
    missing = required_keys - json_value.keys()
    unknown = json_value.keys() - required_keys - (optional_keys or set())
    if missing or unknown:
        raise ValueError(f"{object_label} has missing keys {sorted(missing)} or unknown keys {sorted(unknown)}.")
    return cast("dict[str, Any]", json_value)


def _check_type(value: object, expected_type: type[_T], key: str) -> _T:
    """Return `value` unchanged when it has `expected_type`; a bool never counts as an int.

    Raises:
        TypeError: If `value` does not have `expected_type`.
    """
    if not isinstance(value, expected_type) or (expected_type is int and isinstance(value, bool)):
        raise TypeError(f"'{key}' must be {expected_type.__name__}, got {type(value).__name__}.")
    return value
