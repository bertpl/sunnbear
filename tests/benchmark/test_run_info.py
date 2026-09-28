"""`BenchmarkRunInfo` records a run's inputs and versions, reads back from JSON unchanged, and allows resumes."""

import datetime

import pytest

import sunnbear.functions as functions  # Import the module, so pytest does not try to collect `TestFunction`.
from sunnbear._core.artifacts import ArtifactStore
from sunnbear._core.benchmark.exceptions import BenchmarkRunError
from sunnbear._core.benchmark.mc_tuples.artifact import MCTuplesDeclaration
from sunnbear._core.benchmark.run_info import BenchmarkRunInfo
from sunnbear._core.benchmark.run_settings import BenchmarkRunSettings
from sunnbear.solvers import SolverConfigRegistry


@pytest.fixture(scope="module")
def run_info() -> BenchmarkRunInfo:
    """Return the run info of a run of bisection on the shipped cubic."""
    return BenchmarkRunInfo.for_new_run(
        run_settings=BenchmarkRunSettings(mc_size=32, n_bisection_fevals=40, root_seed=1),
        solver_configs=[SolverConfigRegistry.config_from_id("bisection")],
        functions=[functions.FormulaRegistry.candidate_from_id("f2.1.1[p1=0.2]").calibrated(-1.0, 1.0)],
    )


def test_a_new_run_info_records_the_inputs_the_artifacts_and_the_versions(run_info):
    """A new run info records the solvers, functions, tuple set identity and package versions, and is not finished."""
    # --- assert -----------------------
    assert run_info.solver_versions == {"bisection": 1}
    assert [function.function_id for function in run_info.functions] == ["f2.1.1[p1=0.2]"]
    assert run_info.artifact_hashes == {"mc_tuples": ArtifactStore.load_manifest(MCTuplesDeclaration).content_hash}
    assert {"python", "sunnbear", "numpy", "numba", "counted-float", "polars"} <= set(run_info.package_versions)
    assert not run_info.is_finished
    assert run_info.with_finished_at_now().is_finished


@pytest.mark.parametrize("is_finished", [False, True])
def test_a_run_info_reads_back_equal_from_its_json(run_info, is_finished):
    """`from_json` reads back exactly the run info that `to_json` wrote, finished or not."""
    # --- arrange ----------------------
    original = run_info.with_finished_at_now() if is_finished else run_info

    # --- act / assert -----------------
    assert BenchmarkRunInfo.from_json(original.to_json()) == original


def test_malformed_run_info_json_is_refused():
    """`from_json` raises `BenchmarkRunError` on JSON that is not a run info."""
    # --- act / assert -----------------
    with pytest.raises(BenchmarkRunError, match="Malformed run info"):
        BenchmarkRunInfo.from_json('{"run_settings": {}}')


def test_a_run_on_another_platform_or_at_another_time_may_resume(run_info):
    """The platform and the timestamps are recorded for readers only, so they never stop a run from resuming."""
    # --- arrange ----------------------
    other = run_info.model_copy(
        update={"platform": "Other-arch", "started_at": datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC)}
    ).with_finished_at_now()

    # --- act / assert -----------------
    run_info.check_resumable_as(other)


def test_a_run_with_other_package_versions_may_not_resume(run_info):
    """A run with another package version cannot resume, because results depend on them; the error names the field."""
    # --- arrange ----------------------
    other = run_info.model_copy(update={"package_versions": run_info.package_versions | {"numpy": "0.0.0"}})

    # --- act / assert -----------------
    with pytest.raises(BenchmarkRunError, match="package_versions"):
        run_info.check_resumable_as(other)
