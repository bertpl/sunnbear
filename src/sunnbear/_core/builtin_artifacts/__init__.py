"""This package lists sunnbear's built-in data artifacts and reads their manifests, for the module `sunnbear.data`.

A built-in artifact is one whose declaration is defined inside sunnbear; test fixtures and any other
declarations are left out.

A declaration is registered only once its module is imported, so listing first imports every module
of `sunnbear._core`. That is why this package sits beside the subpackages of `sunnbear._core` that
declare artifacts, not inside `sunnbear._core.data`, which must not import those subpackages.
"""

from sunnbear._core.data import ArtifactArchiveEntry, ArtifactFileEntry, ArtifactManifest

from .listing import artifact_manifest, artifact_names
