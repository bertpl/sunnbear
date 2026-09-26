"""The artifact source enum lists where an artifact's data files come from."""

import enum


class ArtifactSource(enum.Enum):
    """`ArtifactSource` says where an artifact's data files come from."""

    # The data files ship in the sunnbear package itself, next to the artifact's manifest.
    PACKAGE = "package"
    # Only the manifest ships in the package; the data files are downloaded from the URLs in the
    # manifest, into a cache folder on the user's machine.
    DOWNLOAD = "download"
