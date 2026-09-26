"""`ArtifactDataReleaseClient` builds the GitHub CLI calls for data releases, and reads their output."""

import json
import sys
from pathlib import Path

import pytest

import sunnbear._core.data.artifact_data_release_client as data_release_client_module
from sunnbear._core.data import ArtifactDataRelease, ArtifactDataReleaseClient, ArtifactError


def _stub_gh(monkeypatch, respond) -> list[list[str]]:
    """Replace `ArtifactDataReleaseClient._run_gh` with `respond`, which maps arguments to output.

    Return the list that records the arguments of each call.
    """
    calls = []

    def run_gh(args: list[str]) -> str:
        calls.append(args)
        return respond(args)

    monkeypatch.setattr(ArtifactDataReleaseClient, "_run_gh", staticmethod(run_gh))
    return calls


def _gh_failing_with(message: str):
    """Return a stand-in for `_run_gh` that fails as if the GitHub CLI had written `message` to its error output."""

    def respond(args: list[str]) -> str:
        raise ArtifactError(f"The GitHub CLI failed: {message}")

    return respond


# ==================================================================================================
#  Tags and access
# ==================================================================================================
def test_tag_of_names_the_artifact_and_the_shortened_content_hash():
    """A data release's tag is ``data-<name>-<first 8 hex digits of the content hash>``."""
    assert ArtifactDataReleaseClient.tag_of("uv_tuples", "3f2a9c1e" + "0" * 56) == "data-uv_tuples-3f2a9c1e"


def test_check_write_access_accepts_a_maintainer(monkeypatch):
    """The check passes when the GitHub CLI reports push permission on the repository."""
    # --- arrange ----------------------
    calls = _stub_gh(monkeypatch, lambda args: "true\n")

    # --- act --------------------------
    ArtifactDataReleaseClient.check_write_access()

    # --- assert -----------------------
    assert calls == [["api", "repos/bertpl/sunnbear", "--jq", ".permissions.push"]]


@pytest.mark.parametrize(
    "respond, message",
    [
        (lambda args: "false\n", r"maintainer-only functionality"),
        (_gh_failing_with("not logged in"), r"maintainer-only functionality.*not logged in"),
    ],
)
def test_check_write_access_refuses_anyone_else(monkeypatch, respond, message):
    """Without push permission, or without a working GitHub CLI, the error says that publishing is maintainer-only."""
    # --- arrange ----------------------
    _stub_gh(monkeypatch, respond)

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=message):
        ArtifactDataReleaseClient.check_write_access()


# ==================================================================================================
#  Finding and creating releases
# ==================================================================================================
def test_find_reads_the_draft_state_and_the_file_urls(monkeypatch):
    """`find` reports whether the release is a draft, and the download URL of each attached file."""
    # --- arrange ----------------------
    url = "https://github.com/bertpl/sunnbear/releases/download/data-x-12345678/x.tar.zst"
    output = json.dumps({"isDraft": False, "assets": [{"name": "x.tar.zst", "url": url}]})
    calls = _stub_gh(monkeypatch, lambda args: output)

    # --- act --------------------------
    release = ArtifactDataReleaseClient.find("data-x-12345678")

    # --- assert -----------------------
    assert release == ArtifactDataRelease(is_draft=False, file_urls={"x.tar.zst": url})
    assert calls == [["release", "view", "data-x-12345678", "--repo", "bertpl/sunnbear", "--json", "isDraft,assets"]]


def test_find_returns_none_for_a_missing_release(monkeypatch):
    """A release that does not exist is ``None``, not an error."""
    # --- arrange ----------------------
    _stub_gh(monkeypatch, _gh_failing_with("release not found"))

    # --- act / assert -----------------
    assert ArtifactDataReleaseClient.find("data-x-12345678") is None


def test_find_raises_for_any_other_failure(monkeypatch):
    """Any other failure of the GitHub CLI is an `ArtifactError` with its error output."""
    # --- arrange ----------------------
    _stub_gh(monkeypatch, _gh_failing_with("HTTP 502"))

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match="HTTP 502"):
        ArtifactDataReleaseClient.find("data-x-12345678")


def test_create_uploads_the_file_under_its_name_and_publishes_not_as_latest(monkeypatch):
    """`create` gives the GitHub CLI a file of the given name and content, a tag on ``main`` and ``--latest=false``."""
    # --- arrange ----------------------
    uploaded = {}

    def respond(args: list[str]) -> str:
        uploaded[Path(args[3]).name] = Path(args[3]).read_bytes()
        return ""

    calls = _stub_gh(monkeypatch, respond)

    # --- act --------------------------
    ArtifactDataReleaseClient.create("data-x-12345678", "x.tar.zst", b"archive", title="Data: x", notes="notes")

    # --- assert -----------------------
    assert uploaded == {"x.tar.zst": b"archive"}
    assert calls[0][:3] == ["release", "create", "data-x-12345678"]
    assert calls[0][4:] == [
        "--repo", "bertpl/sunnbear", "--target", "main", "--latest=false", "--title", "Data: x", "--notes", "notes"
    ]  # fmt: skip


# ==================================================================================================
#  Running the GitHub CLI
# ==================================================================================================
def test_run_gh_returns_the_standard_output(monkeypatch):
    """`_run_gh` returns what the executable writes to standard output."""
    # --- arrange ----------------------
    # Python stands in for the GitHub CLI, so the test needs neither `gh` nor the network.
    monkeypatch.setattr(data_release_client_module, "_GH_EXECUTABLE", sys.executable)

    # --- act / assert -----------------
    assert ArtifactDataReleaseClient._run_gh(["-c", "print('ok')"]) == "ok\n"


@pytest.mark.parametrize(
    "executable, args, message",
    [
        (sys.executable, ["-c", "import sys; sys.exit('boom')"], "The GitHub CLI failed: boom"),
        ("sunnbear-no-such-executable", [], r"The GitHub CLI \(gh\) is not installed"),
    ],
)
def test_run_gh_reports_a_failed_or_missing_executable(monkeypatch, executable, args, message):
    """A failing or missing executable raises `ArtifactError`, with the error output when there is one."""
    # --- arrange ----------------------
    monkeypatch.setattr(data_release_client_module, "_GH_EXECUTABLE", executable)

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=message):
        ArtifactDataReleaseClient._run_gh(args)
