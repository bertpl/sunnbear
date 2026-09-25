"""This package holds the generic code for sunnbear's data artifacts, with no knowledge of any specific artifact.

The package depends only on `sunnbear._core.exceptions`, so every layer may import from it.
"""

from .exceptions import ArtifactError
from .manifest import ArtifactFileEntry, ArtifactManifest
