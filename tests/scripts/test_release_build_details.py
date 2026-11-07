"""The release script stops when the shipped benchmark suites build details cannot be read or are stale."""

import re
from collections.abc import Callable

import pytest

from sunnbear._core.artifacts import ArtifactError, ArtifactStore


class _BuildDetailsWithStalenessReasons:
    """`_BuildDetailsWithStalenessReasons` stands in for build details whose `staleness_reasons` gives fixed reasons."""

    def __init__(self, reasons: list[str]) -> None:
        """Create build details that report `reasons`."""
        self.reasons = reasons

    def staleness_reasons(self) -> list[str]:
        """Return the reasons that the constructor received."""
        return self.reasons


def _raise_artifact_error() -> _BuildDetailsWithStalenessReasons:
    """Raise the `ArtifactError` of build details that this sunnbear cannot read."""
    raise ArtifactError("other core solver configs")


@pytest.mark.parametrize(
    "load_build_details, message",
    [
        (_raise_artifact_error, r"cannot be read \(other core solver configs\)"),
        (
            lambda: _BuildDetailsWithStalenessReasons(["1 registered candidates are missing"]),
            r"are stale \(1 registered",
        ),
    ],
)
def test_the_release_stops_on_unreadable_or_stale_build_details(
    release, monkeypatch, capsys, load_build_details: Callable[[], _BuildDetailsWithStalenessReasons], message: str
):
    """Build details that cannot be read, and build details with a staleness reason, both stop the release with a hint
    to rebuild them."""
    # --- arrange ----------------------
    monkeypatch.setattr(ArtifactStore, "load", classmethod(lambda cls, declaration_cls: load_build_details()))

    # --- act --------------------------
    with pytest.raises(SystemExit):
        release.step_9_check_build_details_fit()

    # --- assert -----------------------
    error = capsys.readouterr().err
    assert re.search(message, error)
    assert "make benchmark-suites-build-details" in error


def test_the_release_goes_on_with_build_details_that_fit(release, monkeypatch):
    """Build details without a staleness reason let the release go on."""
    # --- arrange ----------------------
    build_details = _BuildDetailsWithStalenessReasons([])
    monkeypatch.setattr(ArtifactStore, "load", classmethod(lambda cls, declaration_cls: build_details))

    # --- act / assert -----------------
    release.step_9_check_build_details_fit()
