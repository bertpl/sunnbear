"""`run_pipeline` runs every stage of the `stages` package, candidate generation first, on the given formulas."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.diversity_features import FeatureFidelity
from sunnbear._core.benchmark.suites.pipeline.mode import PipelineMode
from sunnbear._core.benchmark.suites.pipeline.runner import run_pipeline
from sunnbear._core.benchmark.suites.pipeline.stages import DEFAULT_SPACING_MIN_DISTANCE
from sunnbear._core.problems.core import FormulaRegistry


@pytest.mark.only_with_numba_jit
def test_the_pipeline_runs_every_stage_on_the_candidates_of_the_given_formulas(tmp_path):
    """On formula 2.1.2, the pipeline in draft mode runs the stages in run order on the formula's candidates:

    - every candidate that no stage drops reaches full characterization;
    - spacing runs at its default minimum distance;
    - full characterization runs at the coarse fidelity, as its manifest records.

    Core selection then stops the run, because 4 candidates fill no Core, so neither core selection nor distillation
    writes a manifest.
    """
    # --- arrange ----------------------
    # The shipped formula 2.1.2 has few candidates, so the pipeline runs fast on it.
    formulas = [formula for formula in FormulaRegistry.formulas() if formula.number == (2, 1, 2)]

    # --- act --------------------------
    # By default `run_pipeline` starts 1 worker per CPU, which would only make the workers wait for CPU, because
    # pytest-xdist already runs 1 test process per CPU. With 2 workers the stages still run in worker processes;
    # with 1 worker they would run in this test's process.
    result = run_pipeline(
        workspace_dir=tmp_path,
        formulas=formulas,
        n_workers=2,
        mode=PipelineMode.DRAFT,
    )

    # --- assert -----------------------
    manifests = result.manifests
    assert [manifest.stage_id for manifest in manifests] == list(PipelineStageId)[:-2]
    assert result.stop is not None
    assert result.stop.stage_id == PipelineStageId.CORE_SELECTION
    assert result.stop.reason.startswith("The candidates fill no Core of 128 or more")
    n_candidates = sum(len(formula.build_all_candidates()) for formula in formulas)
    assert manifests[0].n_candidates_out == n_candidates
    assert manifests[3].parameters == {"min_distance": DEFAULT_SPACING_MIN_DISTANCE}
    assert manifests[4].parameters == {"fidelity": FeatureFidelity.COARSE.name}
    drops = [result.state.drop_of(candidate.id) for formula in formulas for candidate in formula.build_all_candidates()]
    assert drops.count(None) == manifests[4].n_candidates_out > 0
    assert sorted(path.name for path in (tmp_path / "manifests").iterdir()) == [
        f"{stage_id}.json" for stage_id in list(PipelineStageId)[:-2]
    ]
