"""`ArtifactDataReleaseClient` creates and reads the GitHub releases that host downloaded artifacts' archives.

A data release is a GitHub release that holds the archive of one artifact and is separate from the
package releases:

- its tag is the one that `ArtifactDataReleaseClient.tag_of` returns, e.g. ``data-uv_tuples-3f2a9c1e``;
- it is never marked as the latest release;
- its only file is the archive.

Every call goes through the GitHub CLI (``gh``) with the maintainer's own authentication, so
creating a data release is internal, maintainer-only functionality.
"""

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .exceptions import ArtifactError

# This repository hosts the data releases; it is named explicitly because `gh` otherwise takes the
# repository from the git checkout it runs in.
_GITHUB_REPOSITORY = "bertpl/sunnbear"
_GH_EXECUTABLE = "gh"
_MAINTAINER_ONLY_MESSAGE = (
    "Publishing a data release is internal, maintainer-only functionality: it needs the GitHub CLI "
    f"(gh), logged in with write access to {_GITHUB_REPOSITORY}."
)


# ==================================================================================================
#  ArtifactDataReleaseClient
# ==================================================================================================
class ArtifactDataReleaseClient:
    """`ArtifactDataReleaseClient` wraps the GitHub CLI calls that create and read data releases."""

    @staticmethod
    def tag_of(artifact_name: str, content_hash: str) -> str:
        """Return the tag of the data release of an artifact, e.g. ``data-uv_tuples-3f2a9c1e``."""
        return f"data-{artifact_name}-{content_hash[:8]}"

    @classmethod
    def check_write_access(cls) -> None:
        """Check that the GitHub CLI is installed, logged in, and allowed to write to the repository.

        Raises:
            ArtifactError: If the GitHub CLI is not installed, not logged in, or cannot write to the
                repository; the message says that publishing is maintainer-only.
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
    def find(cls, tag: str) -> "ArtifactDataRelease | None":
        """Return the data release with this tag, or ``None`` if the repository has no release with it.

        Raises:
            ArtifactError: If the GitHub CLI is not installed, or fails for any reason other than a
                missing release; the message holds the GitHub CLI's error output.
        """
        try:
            output = cls._run_gh(["release", "view", tag, "--repo", _GITHUB_REPOSITORY, "--json", "isDraft,assets"])
        except ArtifactError as error:
            if "release not found" in str(error):
                return None
            raise
        release_fields = json.loads(output)
        return ArtifactDataRelease(
            is_draft=release_fields["isDraft"],
            file_urls={asset["name"]: asset["url"] for asset in release_fields["assets"]},
        )

    @classmethod
    def create(cls, tag: str, file_name: str, content: bytes, title: str, notes: str) -> None:
        """Create and publish a data release whose only file is `content`, named `file_name`.

        The release's tag is created on the head of ``main``. The GitHub CLI uploads the file while
        the release is still a draft and only then publishes it, because the repository has GitHub's
        immutable releases enabled, which forbid adding files to a release after it is published. An
        interrupted call can therefore leave a draft release behind.

        Raises:
            ArtifactError: If the GitHub CLI is not installed, or fails to create the release; the
                message holds the GitHub CLI's error output.
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
                holds the GitHub CLI's error output.
        """
        try:
            # The arguments are built by this class, never by user input, and no shell is involved.
            completed = subprocess.run([_GH_EXECUTABLE, *args], capture_output=True, text=True, check=True)  # noqa: S603
        except FileNotFoundError as error:
            raise ArtifactError("The GitHub CLI (gh) is not installed.") from error
        except subprocess.CalledProcessError as error:
            raise ArtifactError(f"The GitHub CLI failed: {error.stderr.strip()}") from error
        return completed.stdout


# ==================================================================================================
#  ArtifactDataRelease, the result of ArtifactDataReleaseClient.find
# ==================================================================================================
@dataclass(frozen=True)
class ArtifactDataRelease:
    """An `ArtifactDataRelease` describes an existing data release, as `ArtifactDataReleaseClient.find` reports it.

    Attributes:
        is_draft: Whether the release is still a draft, e.g. left behind when publishing was interrupted.
        file_urls: The download URL of each file attached to the release, keyed by file name.
    """

    is_draft: bool
    file_urls: dict[str, str]
