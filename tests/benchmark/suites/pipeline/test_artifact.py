"""`BenchmarkSuitesBuildDetailsDeclaration` saves the build details as a data artifact and loads them back, and refuses
an artifact that this sunnbear cannot read."""

import pytest

from sunnbear._core.artifacts import ArtifactError, ArtifactStore
from sunnbear._core.benchmark.suites.pipeline import (
    BenchmarkSuitesBuildDetailsDeclaration,
    DiversityFeatureFactory,
    PipelineStageId,
)
from tests.benchmark.suites.pipeline.example_states import build_state_before, example_problem_ids


@pytest.fixture(autouse=True)
def _artifact_and_cache_dirs_in_tmp(monkeypatch, tmp_path):
    """Place the artifact's manifest and its download cache in `tmp_path`, so that the tests write no files in the repo
    or the user's cache."""
    monkeypatch.setattr(
        ArtifactStore, "_artifact_dir_of", classmethod(lambda cls, declaration_cls: tmp_path / declaration_cls.name)
    )
    monkeypatch.setenv("SUNNBEAR_CACHE_DIR", str(tmp_path / "cache"))


def test_the_artifact_loads_the_build_details_that_were_saved():
    """The build details loaded from the artifact give the same files as the saved ones."""
    # --- arrange ----------------------
    build_details = build_state_before(PipelineStageId.CORE_SELECTION, example_problem_ids(3)).create_build_details()
    ArtifactStore.save(BenchmarkSuitesBuildDetailsDeclaration, build_details)

    # --- act --------------------------
    loaded = ArtifactStore.load(BenchmarkSuitesBuildDetailsDeclaration)

    # --- assert -----------------------
    assert loaded.to_files() == build_details.to_files()


def test_the_artifact_refuses_build_details_of_other_core_solver_configs(monkeypatch):
    """Build details saved with the shipped core solver configs cannot be loaded once the factory names other ones."""
    # --- arrange ----------------------
    build_details = build_state_before(PipelineStageId.SPACING, example_problem_ids(3)).create_build_details()
    ArtifactStore.save(BenchmarkSuitesBuildDetailsDeclaration, build_details)
    monkeypatch.setattr(DiversityFeatureFactory, "solver_ids", property(lambda self: ("illinois",)))

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=r"cannot read the benchmark suites build details: .* not with"):
        ArtifactStore.load(BenchmarkSuitesBuildDetailsDeclaration)
