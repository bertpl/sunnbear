"""The release script stops when the shipped benchmark suites build details cannot be read or are stale."""

import re
from collections.abc import Callable
from types import SimpleNamespace

import pytest

from sunnbear._core.artifacts import ArtifactError, ArtifactStore


def _raise_artifact_error() -> SimpleNamespace:
    """Raise the `ArtifactError` of build details that this sunnbear cannot read."""
    raise ArtifactError("other core solver configs")


@pytest.mark.parametrize(
    "load_build_details, message",
    [
        (_raise_artifact_error, r"cannot be read \(other core solver configs\)"),
        (
            lambda: SimpleNamespace(staleness_reasons=lambda: ["1 registered candidates are missing"]),
            r"are stale \(1 registered",
        ),
    ],
)
def test_the_release_stops_on_unreadable_or_stale_build_details(
    release, monkeypatch, capsys, load_build_details: Callable[[], SimpleNamespace], message: str
):
    """Build details that cannot be read, and build details with a staleness reason, both stop the release with a hint
    to rebuild them."""
    # --- arrange ----------------------
    monkeypatch.setattr(ArtifactStore, "load", classmethod(lambda cls, declaration_cls: load_build_details()))

    # --- act --------------------------
    with pytest.raises(SystemExit):
        release.step_9_check_benchmark_suites_build_details_staleness()

    # --- assert -----------------------
    error = capsys.readouterr().err
    assert re.search(message, error)
    assert "make benchmark-suites-build-details" in error


def test_the_release_goes_on_with_build_details_that_fit(release, monkeypatch):
    """Build details without a staleness reason let the release go on."""
    # --- arrange ----------------------
    build_details = SimpleNamespace(staleness_reasons=list)
    monkeypatch.setattr(ArtifactStore, "load", classmethod(lambda cls, declaration_cls: build_details))

    # --- act / assert -----------------
    release.step_9_check_benchmark_suites_build_details_staleness()
