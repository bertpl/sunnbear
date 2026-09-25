"""This package holds the machinery for sunnbear's data artifacts, with no knowledge of any specific artifact.

It depends only on `sunnbear._core.exceptions`, so every layer may use it.
"""

from .exceptions import ArtifactError
from .manifest import ArtifactFile, ArtifactManifest
