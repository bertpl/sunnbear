"""This module re-exports the functions and manifest classes for sunnbear's data artifacts.

A data artifact is a named, frozen dataset that ships with sunnbear or is downloaded on first use.
Its manifest identifies it by a content hash and records how it was built. `artifact_names` lists
only the artifacts that sunnbear itself declares, and the first call to either function imports
every sunnbear module.
"""

from ._core.builtin_artifacts import (
    ArtifactArchiveEntry,
    ArtifactFileEntry,
    ArtifactManifest,
    artifact_manifest,
    artifact_names,
)

__all__ = ["ArtifactArchiveEntry", "ArtifactFileEntry", "ArtifactManifest", "artifact_manifest", "artifact_names"]
