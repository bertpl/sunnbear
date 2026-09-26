"""This module re-exports the functions and manifest classes for sunnbear's data artifacts.

A data artifact is a named, frozen dataset that ships with sunnbear or is downloaded on first use.
An artifact's manifest identifies it by a content hash and records how it was built. The listing
covers only the artifacts that ship with sunnbear itself; see the docstring of the implementation
module, `sunnbear._core.data.artifact_listing`.
"""

from ._core.data.artifact_listing import (
    ArtifactArchiveEntry,
    ArtifactFileEntry,
    ArtifactManifest,
    artifact_manifest,
    artifact_names,
)

__all__ = ["ArtifactArchiveEntry", "ArtifactFileEntry", "ArtifactManifest", "artifact_manifest", "artifact_names"]
