"""The artifact source enum lists where an artifact's data files come from."""

import enum


class ArtifactSource(enum.Enum):
    """`ArtifactSource` says where an artifact's data files come from."""

    # The data files ship in the sunnbear package itself, next to the artifact's manifest.
    PACKAGE = "package"
