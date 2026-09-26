"""This module re-exports the functions and manifest classes for sunnbear's data artifacts.

A data artifact is a named, frozen dataset that ships with sunnbear or is downloaded on first use.
An artifact's manifest identifies it by a content hash and records how it was built.

`artifact_names` lists only the artifacts defined in sunnbear's own code; artifacts that tests or
other packages define are not listed. The first call to `artifact_names` or `artifact_manifest`
imports every module of `sunnbear._core`.
"""

from ._core.builtin_artifact_listing import (
    ArtifactArchiveEntry,
    ArtifactFileEntry,
    ArtifactManifest,
    artifact_manifest,
    artifact_names,
)

__all__ = ["ArtifactArchiveEntry", "ArtifactFileEntry", "ArtifactManifest", "artifact_manifest", "artifact_names"]
