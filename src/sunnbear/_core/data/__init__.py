"""This package holds the code shared by all of sunnbear's data artifacts; no module refers to a specific artifact.

The package depends only on `sunnbear._core.exceptions`, so every other subpackage of
`sunnbear._core` may import from this package.
"""

from .artifact import ArtifactDeclaration
from .exceptions import ArtifactError
from .manifest import ArtifactFileEntry, ArtifactManifest
from .registry import ArtifactRegistry
from .residency import ArtifactResidency
