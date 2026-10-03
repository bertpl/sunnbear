"""`BenchmarkRunInfo` records a run's inputs and versions, reads back from JSON unchanged, and checks resumes."""

import datetime

import pytest

import sunnbear.functions as functions  # Import the module, so pytest does not try to collect `TestFunction`.
from sunnbear._core.artifacts import ArtifactStore
from sunnbear._core.benchmark.mc_tuples.artifact import MCTuplesDeclaration
from sunnbear._core.benchmark.runner.exceptions import BenchmarkRunError
from sunnbear._core.benchmark.runner.run_info import BenchmarkRunInfo
from sunnbear._core.benchmark.runner.run_settings import BenchmarkRunSettings
from sunnbear.solvers import SolverConfigRegistry


# ==================================================================================================
#  Fixtures
# ==================================================================================================
def _run_info_of(solver_ids: list[str], function_ids: list[str], c_max: float = 1.0) -> BenchmarkRunInfo:
    """Return the run info of a run of `solver_ids` on `function_ids`, each calibrated to c in [-1, `c_max`]."""
    return BenchmarkRunInfo.for_current_inputs(
        run_settings=BenchmarkRunSettings(mc_size=32, n_bisection_fevals=40, root_seed=1),
        solver_configs=[SolverConfigRegistry.config_from_id(solver_id) for solver_id in solver_ids],
        functions=[
            functions.FormulaRegistry.candidate_from_id(function_id).calibrated(-1.0, c_max)
            for function_id in function_ids
        ],
    )


@pytest.fixture(scope="module")
def run_info() -> BenchmarkRunInfo:
    """Return the run info of a run of bisection on the shipped cubic."""
    return _run_info_of(["bisection"], ["f2.1.1[p1=0.2]"])


# ==================================================================================================
#  Construction and JSON
# ==================================================================================================
def test_a_new_run_info_records_the_inputs_the_artifacts_and_the_versions(run_info):
    """A new run info records the solvers, functions, tuple set identity and package versions, and is not finished."""
    # --- assert -----------------------
    assert run_info.solver_versions == {"bisection": 1}
    assert [function_info.function_id for function_info in run_info.function_infos] == ["f2.1.1[p1=0.2]"]
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


# ==================================================================================================
#  Resuming
# ==================================================================================================
def test_a_run_on_another_platform_or_at_another_time_may_resume(run_info):
    """`check_resumable_as` does not compare the platform and the timestamps, so they never stop a run from resuming."""
    # --- arrange ----------------------
    other = run_info.model_copy(
        update={"platform": "Other-arch", "started_at": datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC)}
    ).with_finished_at_now()

    # --- act / assert -----------------
    run_info.check_resumable_as(other)


def test_a_run_with_other_package_versions_may_not_resume(run_info):
    """A run with another package version cannot resume, since results depend on it; the error names the field."""
    # --- arrange ----------------------
    other = run_info.model_copy(update={"package_versions": run_info.package_versions | {"numpy": "0.0.0"}})

    # --- act / assert -----------------
    with pytest.raises(BenchmarkRunError, match="package_versions"):
        run_info.check_resumable_as(other)


# ==================================================================================================
#  Combining
# ==================================================================================================
@pytest.mark.parametrize(
    "solver_ids, function_ids",
    [
        (["regula_falsi"], ["f2.1.1[p1=0.2]"]),
        (["bisection"], ["f2.1.1[p1=0.4]"]),
        (["bisection", "regula_falsi"], ["f2.1.1[p1=0.4]", "f2.1.2[p1=3.0]"]),
    ],
)
def test_runs_of_other_solvers_or_on_other_functions_are_combinable(run_info, solver_ids, function_ids):
    """Runs with the same run settings and package versions can be read as 1 table when no solver ran on the same
    test function in both."""
    # --- act / assert -----------------
    run_info.check_combinable_with(_run_info_of(solver_ids, function_ids))


@pytest.mark.parametrize(
    "other_changes, differing_field",
    [
        ({"run_settings": BenchmarkRunSettings(mc_size=64, n_bisection_fevals=40, root_seed=1)}, "run_settings"),
        ({"package_versions": {"numpy": "0.0.0"}}, "package_versions"),
        ({"solver_versions": {"bisection": 2}}, "solver_versions"),
    ],
)
def test_runs_with_other_settings_versions_or_solver_versions_are_not_combinable(
    run_info, other_changes, differing_field
):
    """Runs on different test functions are combinable only with the same run settings, package versions and solver
    versions; the error names the field that differs."""
    # --- arrange ----------------------
    other = _run_info_of(["bisection"], ["f2.1.1[p1=0.4]"])
    other = other.model_copy(update=other_changes)

    # --- act / assert -----------------
    with pytest.raises(BenchmarkRunError, match=differing_field):
        run_info.check_combinable_with(other)


def test_runs_with_another_c_range_of_a_common_function_are_not_combinable(run_info):
    """A test function in both runs must have the same c-range, even when the solvers differ."""
    # --- act / assert -----------------
    with pytest.raises(BenchmarkRunError, match="function_infos"):
        run_info.check_combinable_with(_run_info_of(["regula_falsi"], ["f2.1.1[p1=0.2]"], c_max=0.5))


def test_runs_of_a_solver_on_the_same_function_are_not_combinable(run_info):
    """`check_combinable_with` refuses 2 runs in which a solver ran on the same test function in both, since the table
    would hold those solves twice."""
    # --- act / assert -----------------
    with pytest.raises(BenchmarkRunError, match=r"ran the solvers \['bisection'\] on the test functions"):
        run_info.check_combinable_with(_run_info_of(["bisection", "regula_falsi"], ["f2.1.1[p1=0.2]"]))
