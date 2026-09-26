"""This module holds the public functions that list sunnbear's data artifacts and read their manifests.

Both functions wrap `ArtifactStore`, which reads the committed folders of the built-in artifacts;
the module also re-exports the manifest classes, so that `sunnbear.data` offers everything a user
needs to read a manifest.
"""

from .artifact_manifest import ArtifactArchiveEntry, ArtifactFileEntry, ArtifactManifest
from .artifact_store import ArtifactStore

__all__ = ["ArtifactArchiveEntry", "ArtifactFileEntry", "ArtifactManifest", "artifact_manifest", "artifact_names"]


def artifact_names() -> tuple[str, ...]:
    """Return the names of sunnbear's data artifacts, sorted."""
    return ArtifactStore.builtin_artifact_names()


def artifact_manifest(name: str) -> ArtifactManifest:
    """Return the manifest of sunnbear's data artifact with this name, without reading or downloading its data files.

    Raises:
        ArtifactError: If sunnbear has no data artifact with this name, or its manifest is missing,
            malformed, or names another artifact.
    """
    return ArtifactStore.load_builtin_manifest(name)
