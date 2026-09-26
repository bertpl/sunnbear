"""This module re-exports the listing of sunnbear's built-in data artifacts, and the classes of their manifests.

A data artifact is a named, frozen dataset that ships with sunnbear or is downloaded on first use.
Its manifest identifies it by a content hash and records how it was built; see the docstring of the
implementation package, `sunnbear._core.builtin_artifacts`.
"""

from ._core.builtin_artifacts import (
    ArtifactArchiveEntry,
    ArtifactFileEntry,
    ArtifactManifest,
    artifact_manifest,
    artifact_names,
)

__all__ = ["ArtifactArchiveEntry", "ArtifactFileEntry", "ArtifactManifest", "artifact_manifest", "artifact_names"]
