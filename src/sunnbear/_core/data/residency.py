"""`ArtifactResidency` says where an artifact's data files live."""

import enum


class ArtifactResidency(enum.Enum):
    """`ArtifactResidency` says where an artifact's data files live."""

    # The data files ship in the sunnbear package itself, next to the artifact's manifest.
    EMBEDDED = "embedded"
