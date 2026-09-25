"""A manifest records what a data artifact's files are, and the content hash that identifies the artifact.

A data artifact is a named, frozen dataset that sunnbear produces once and users consume, such as
the (u, v) tuple set. Its manifest records only what the code that generated it cannot: each
file's sha256 and size, the artifacts it was built from, the library versions that shaped its
content, the build date, and optionally the public call that generated it.

The identity of an artifact is its content hash: the sha256 over each file's path and sha256, in
the manifest's file order. It is never a hand-maintained version number, which could silently go
unchanged when the data changes. `ArtifactManifest.identity` shows it shortened, the way git shows
commits, e.g. ``uv_tuples@3f2a9c1e``; comparisons use the full `ArtifactManifest.content_hash`.

`ArtifactManifest.to_json` writes deterministic JSON (sorted keys, fixed indentation), so a
changed manifest shows a readable diff. `ArtifactManifest.from_json` accepts only a well-formed
manifest whose recorded content hash matches its files, and raises `ArtifactError` otherwise.
"""

import datetime
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from .exceptions import ArtifactError

# The number of hex digits of the content hash that `ArtifactManifest.identity` shows.
_SHORT_HASH_LENGTH = 8

_MANIFEST_KEYS = {"name", "schema_version", "files", "content_hash", "inputs", "built_with", "built", "generation"}
_FILE_KEYS = {"path", "sha256", "size_bytes"}
_FILE_OPTIONAL_KEYS = {"url"}


# ==================================================================================================
#  ArtifactManifest
# ==================================================================================================
@dataclass(frozen=True)
class ArtifactManifest:
    """An `ArtifactManifest` describes one data artifact: its files, its content hash, and how it was built.

    Attributes:
        name: The artifact's name, e.g. ``uv_tuples``.
        schema_version: The version of the file format; the artifact's declaration refuses a
            manifest whose schema version differs from its own.
        files: The artifact's data files; at least 1, with unique paths. Their order is part of the
            content hash.
        inputs: The content hashes of the artifacts this one was built from, by artifact name.
        built_with: The versions of sunnbear and of the libraries that shaped the content, by
            package name.
        built: The build date.
        generation: The public call that generated the artifact, with its arguments, as
            JSON-compatible data; ``None`` when there is none.
    """

    name: str
    schema_version: int
    files: tuple["ArtifactFile", ...]
    inputs: dict[str, str] = field(default_factory=dict, hash=False)
    built_with: dict[str, str] = field(default_factory=dict, hash=False)
    built: datetime.date = field(default_factory=datetime.date.today)
    generation: dict[str, Any] | None = field(default=None, hash=False)

    def __post_init__(self) -> None:
        """Check that the manifest has files and that their paths are unique.

        Raises:
            ValueError: If `files` is empty or two files share a path.
        """
        if not self.files:
            raise ValueError(f"Artifact '{self.name}' has no files.")
        paths = [file.path for file in self.files]
        if len(set(paths)) != len(paths):
            raise ValueError(f"Artifact '{self.name}' lists a file path more than once: {paths}.")

    # --------------------------------------------------------------------------
    #  Identity
    # --------------------------------------------------------------------------
    @property
    def content_hash(self) -> str:
        """Return the sha256, as hex, over each file's path and sha256 in `files` order."""
        digest = hashlib.sha256()
        for file in self.files:
            digest.update(f"{file.path}\0{file.sha256}\n".encode())
        return digest.hexdigest()

    @property
    def identity(self) -> str:
        """Return the name and the shortened content hash, e.g. ``uv_tuples@3f2a9c1e``."""
        return f"{self.name}@{self.content_hash[:_SHORT_HASH_LENGTH]}"

    # --------------------------------------------------------------------------
    #  JSON
    # --------------------------------------------------------------------------
    def to_json(self) -> str:
        """Return the manifest as deterministic JSON: sorted keys, 2-space indentation, a final newline."""
        data = {
            "name": self.name,
            "schema_version": self.schema_version,
            "files": [file.to_dict() for file in self.files],
            "content_hash": self.content_hash,
            "inputs": self.inputs,
            "built_with": self.built_with,
            "built": self.built.isoformat(),
            "generation": self.generation,
        }
        return json.dumps(data, sort_keys=True, indent=2) + "\n"

    @staticmethod
    def from_json(text: str) -> "ArtifactManifest":
        """Parse a manifest written by `to_json`.

        Raises:
            ArtifactError: If the text is not valid JSON, has missing or unknown keys or values of
                the wrong type, or records a content hash that does not match its files.
        """
        try:
            data = json.loads(text)
            _check_keys(data, _MANIFEST_KEYS, "manifest")
            manifest = ArtifactManifest(
                name=_typed(data["name"], str, "name"),
                schema_version=_typed(data["schema_version"], int, "schema_version"),
                files=tuple(ArtifactFile.from_dict(entry) for entry in _typed(data["files"], list, "files")),
                inputs=_typed(data["inputs"], dict, "inputs"),
                built_with=_typed(data["built_with"], dict, "built_with"),
                built=datetime.date.fromisoformat(_typed(data["built"], str, "built")),
                generation=None if data["generation"] is None else _typed(data["generation"], dict, "generation"),
            )
        except (ValueError, TypeError) as error:
            raise ArtifactError(f"Malformed artifact manifest: {error}") from error
        if data["content_hash"] != manifest.content_hash:
            raise ArtifactError(
                f"Manifest of '{manifest.name}' records content hash {data['content_hash']}, "
                f"but its files hash to {manifest.content_hash}."
            )
        return manifest


# ==================================================================================================
#  ArtifactFile
# ==================================================================================================
@dataclass(frozen=True)
class ArtifactFile:
    """An `ArtifactFile` describes one data file of an artifact.

    Attributes:
        path: The file's path relative to the artifact's folder, with forward slashes, never
            leaving that folder.
        sha256: The sha256 of the file's bytes, as hex.
        size_bytes: The file's size in bytes.
        url: Where to download the file, for an artifact that is not shipped in the package;
            ``None`` otherwise.
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
            raise ValueError(f"Artifact file path '{self.path}' must be relative and stay inside the artifact's folder.")

    @staticmethod
    def from_content(path: str, content: bytes, url: str | None = None) -> "ArtifactFile":
        """Describe a file by hashing its content."""
        return ArtifactFile(path=path, sha256=hashlib.sha256(content).hexdigest(), size_bytes=len(content), url=url)

    def matches(self, content: bytes) -> bool:
        """Return whether `content` has this file's size and sha256."""
        return len(content) == self.size_bytes and hashlib.sha256(content).hexdigest() == self.sha256

    def to_dict(self) -> dict[str, Any]:
        """Return the file's JSON form; `url` is left out when it is ``None``."""
        data: dict[str, Any] = {"path": self.path, "sha256": self.sha256, "size_bytes": self.size_bytes}
        if self.url is not None:
            data["url"] = self.url
        return data

    @staticmethod
    def from_dict(data: Any) -> "ArtifactFile":
        """Parse the JSON form written by `to_dict`.

        Raises:
            ValueError: If keys are missing or unknown, or the path is invalid.
            TypeError: If a value has the wrong type.
        """
        _check_keys(data, _FILE_KEYS, "file entry", optional_keys=_FILE_OPTIONAL_KEYS)
        return ArtifactFile(
            path=_typed(data["path"], str, "path"),
            sha256=_typed(data["sha256"], str, "sha256"),
            size_bytes=_typed(data["size_bytes"], int, "size_bytes"),
            url=_typed(data["url"], str, "url") if "url" in data else None,
        )


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _check_keys(data: Any, required_keys: set[str], what: str, optional_keys: set[str] | None = None) -> None:
    """Check that `data` is a JSON object with all of `required_keys` and nothing beyond `optional_keys`.

    Raises:
        TypeError: If `data` is not a JSON object.
        ValueError: If a required key is missing or an unknown key is present.
    """
    if not isinstance(data, dict):
        raise TypeError(f"{what} must be a JSON object, got {type(data).__name__}.")
    missing = required_keys - data.keys()
    unknown = data.keys() - required_keys - (optional_keys or set())
    if missing or unknown:
        raise ValueError(f"{what} has missing keys {sorted(missing)} or unknown keys {sorted(unknown)}.")


def _typed(value: Any, expected_type: type, key: str) -> Any:
    """Return `value` when it has `expected_type`; a bool never counts as an int.

    Raises:
        TypeError: If `value` does not have `expected_type`.
    """
    if not isinstance(value, expected_type) or (expected_type is int and isinstance(value, bool)):
        raise TypeError(f"'{key}' must be {expected_type.__name__}, got {type(value).__name__}.")
    return value
