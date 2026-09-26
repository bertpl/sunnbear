"""This package holds the code shared by all of sunnbear's data artifacts; no module refers to a specific artifact.

A data artifact is a named, frozen dataset that sunnbear produces once and users consume. The
classes, by role:

- declaring an artifact:
  - `ArtifactDeclaration[T]` declares one artifact: its name, its `ArtifactSource`, and the
    conversion between a value of type ``T`` and its data files;
  - `ArtifactSource` says whether the data files ship in the package or are downloaded;
  - `ArtifactRegistry` holds every declaration, registered when its class is defined;
- describing an artifact's files:
  - `ArtifactManifest` is the ``manifest.json`` of one artifact: its file entries, its content
    hash (the artifact's identity), and how it was built;
  - `ArtifactFileEntry` describes one data file, and `ArtifactArchiveEntry` the archive of a
    downloaded artifact;
- reading and writing files:
  - `ArtifactStore` is the only code that touches artifact paths or URLs, apart from the release
    URLs that `ArtifactDataReleaseClient` reads from GitHub: it loads, saves, verifies and
    publishes an artifact through its declaration;
  - `ArtifactArchiver` packs a downloaded artifact's data files into one archive, and unpacks it;
  - `ArtifactDataReleaseClient` creates and reads the GitHub releases that host those archives,
    which `ArtifactStore.publish` uses;
- `ArtifactError` is raised when an artifact cannot be read or trusted.

The package depends only on `sunnbear._core.exceptions` and `sunnbear._core.utils`, so every other
subpackage of `sunnbear._core` may import from this package.
"""

from .artifact_archiver import ArtifactArchiver
from .artifact_data_release_client import ArtifactDataRelease, ArtifactDataReleaseClient
from .artifact_declaration import ArtifactDeclaration
from .artifact_manifest import ArtifactArchiveEntry, ArtifactFileEntry, ArtifactManifest
from .artifact_registry import ArtifactRegistry
from .artifact_source import ArtifactSource
from .artifact_store import ArtifactStore
from .exceptions import ArtifactError
