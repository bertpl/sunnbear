"""`ArtifactDataReleases` creates and reads the GitHub releases that host downloaded artifacts' archives.

A data release is a GitHub release of its own for one artifact archive, separate from package
releases: its tag is ``data-<artifact name>-<first 8 hex digits of the content hash>``, it is never
marked as the latest release, and its only file is the archive. Every call goes through the
GitHub CLI (``gh``) with the maintainer's own authentication, so publishing is internal,
maintainer-only functionality.
"""

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .exceptions import ArtifactError

# The repository that hosts the data releases, named explicitly so that publishing does not depend
# on the folder that `gh` runs in.
_GITHUB_REPOSITORY = "bertpl/sunnbear"
_GH_EXECUTABLE = "gh"
_MAINTAINER_ONLY_MESSAGE = (
    "Publishing a data release is internal, maintainer-only functionality: it needs the GitHub CLI "
    f"(gh), logged in with write access to {_GITHUB_REPOSITORY}."
)


# ==================================================================================================
#  DataRelease
# ==================================================================================================
@dataclass(frozen=True)
class DataRelease:
    """A `DataRelease` is what `ArtifactDataReleases.find` reports about an existing data release.

    Attributes:
        is_draft: Whether the release is still a draft, e.g. left behind by an interrupted publish.
        asset_urls: The download URL of each file attached to the release, keyed by file name.
    """

    is_draft: bool
    asset_urls: dict[str, str]


# ==================================================================================================
#  ArtifactDataReleases
# ==================================================================================================
class ArtifactDataReleases:
    """`ArtifactDataReleases` wraps the GitHub CLI calls that create and read data releases."""

    @staticmethod
    def tag_of(artifact_name: str, content_hash: str) -> str:
        """Return the tag of the data release of an artifact, e.g. ``data-uv_tuples-3f2a9c1e``."""
        return f"data-{artifact_name}-{content_hash[:8]}"

    @classmethod
    def check_write_access(cls) -> None:
        """Check that the GitHub CLI is installed, logged in, and allowed to write to the repository.

        Raises:
            ArtifactError: If any of these does not hold; the message says that publishing is
                maintainer-only.
        """
        try:
            can_push = (
                cls._run_gh(["api", f"repos/{_GITHUB_REPOSITORY}", "--jq", ".permissions.push"]).strip() == "true"
            )
        except ArtifactError as error:
            raise ArtifactError(f"{_MAINTAINER_ONLY_MESSAGE} {error}") from error
        if not can_push:
            raise ArtifactError(_MAINTAINER_ONLY_MESSAGE)

    @classmethod
    def find(cls, tag: str) -> DataRelease | None:
        """Return the data release with this tag, or ``None`` if the repository has no release with it."""
        try:
            output = cls._run_gh(["release", "view", tag, "--repo", _GITHUB_REPOSITORY, "--json", "isDraft,assets"])
        except ArtifactError as error:
            if "release not found" in str(error):
                return None
            raise
        release_json = json.loads(output)
        return DataRelease(
            is_draft=release_json["isDraft"],
            asset_urls={asset["name"]: asset["url"] for asset in release_json["assets"]},
        )

    @classmethod
    def create(cls, tag: str, file_name: str, content: bytes, title: str, notes: str) -> None:
        """Create and publish a data release whose only file is `content`, named `file_name`.

        The release's tag is created on the head of ``main``, and the release is not marked as the
        latest one. The GitHub CLI uploads the file while the release is still a draft and only
        then publishes it, as the repository's immutable releases require.
        """
        with tempfile.TemporaryDirectory() as folder:
            file_path = Path(folder) / file_name
            file_path.write_bytes(content)
            release_options = ["--repo", _GITHUB_REPOSITORY, "--target", "main", "--latest=false"]
            cls._run_gh(
                ["release", "create", tag, str(file_path), *release_options, "--title", title, "--notes", notes]
            )

    @staticmethod
    def _run_gh(args: list[str]) -> str:
        """Run the GitHub CLI with `args` and return its standard output.

        Raises:
            ArtifactError: If the GitHub CLI is not installed, or exits with an error; the message
                holds its error output.
        """
        try:
            # The arguments are built by this class, never by user input, and no shell is involved.
            completed = subprocess.run([_GH_EXECUTABLE, *args], capture_output=True, text=True, check=True)  # noqa: S603
        except FileNotFoundError as error:
            raise ArtifactError("The GitHub CLI (gh) is not installed.") from error
        except subprocess.CalledProcessError as error:
            raise ArtifactError(f"The GitHub CLI failed: {error.stderr.strip()}") from error
        return completed.stdout
