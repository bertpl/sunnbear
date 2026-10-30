"""`run_pipeline` runs every stage of the `stages` package, candidate generation first, on the given formulas."""

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline import stages as stages_package
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage
from sunnbear._core.benchmark.suites.pipeline.runner import run_pipeline
from sunnbear._core.benchmark.suites.pipeline.stages import (
    DEFAULT_SPACING_MIN_DISTANCE,
    CandidateGenerationStage,
    CandidateValidationStage,
    CoarseCharacterizationStage,
    CoreSelectionStage,
    FullCharacterizationStage,
    SpacingStage,
)
from sunnbear._core.problems.core import FormulaRegistry
from sunnbear._core.solvers.core import SolverConfigRegistry


def _stage_classes(stage_cls: type[PipelineStage]) -> list[type[PipelineStage]]:
    """Return every subclass of `stage_cls`, at any depth."""
    return [
        subclass
        for direct_subclass in stage_cls.__subclasses__()
        for subclass in [direct_subclass, *_stage_classes(direct_subclass)]
    ]


@pytest.mark.only_with_numba_jit
def test_the_pipeline_runs_every_stage_on_the_candidates_of_the_given_formulas(tmp_path):
    """On formula 2.1.2, the pipeline writes 1 output per stage, in this order:

    - its candidates;
    - the valid ones with their c-ranges;
    - every valid one with its coarse feature vector, and the scale of each feature block in every row;
    - the candidates that spacing keeps at its default minimum distance;
    - each of those with its full feature vector.

    Core selection then stops the run, because 4 candidates fill no Core.
    """
    # --- arrange ----------------------
    # The shipped formula 2.1.2 has few candidates, so the pipeline runs fast on it.
    formulas = [formula for formula in FormulaRegistry.formulas() if formula.number == (2, 1, 2)]
    core_solver_configs = [
        config for config in SolverConfigRegistry.configs() if config.role.is_used_for_problem_characterization
    ]

    # --- act --------------------------
    # By default `run_pipeline` starts 1 worker per CPU, which would only make the workers wait for CPU, because
    # pytest-xdist already runs 1 test process per CPU. With 2 workers the stages still run in worker processes;
    # with 1 worker they would run in this test's process.
    result = run_pipeline(
        workspace_dir=tmp_path, formulas=formulas, core_solver_configs=core_solver_configs, n_workers=2
    )

    # --- assert -----------------------
    # The output names of the stages package's stages, sorted, are its stages in run order.
    output_names_expected = sorted(
        stage_cls.output_name
        for stage_cls in _stage_classes(PipelineStage)
        if stage_cls.__module__.startswith(f"{stages_package.__name__}.")
    )
    manifests = result.manifests
    assert [manifest.output_name for manifest in manifests] == output_names_expected[:-1]
    assert result.stop is not None
    assert result.stop.output_name == CoreSelectionStage.output_name
    assert result.stop.reason.startswith("The candidates fill no Core of 128 or more")
    candidates = pl.read_parquet(tmp_path / f"{CandidateGenerationStage.output_name}.parquet")
    valid_candidates = pl.read_parquet(tmp_path / f"{CandidateValidationStage.output_name}.parquet")
    coarse_features = pl.read_parquet(tmp_path / f"{CoarseCharacterizationStage.output_name}.parquet")
    assert candidates.height == sum(len(formula.build_all_candidates()) for formula in formulas)
    assert valid_candidates.select(candidates.columns).equals(candidates)
    assert ((valid_candidates["c_min"] < 0.0) & (valid_candidates["c_max"] > 0.0)).all()
    feature_column_names = CoarseCharacterizationStage(core_solver_configs).feature_column_names
    assert coarse_features.select(valid_candidates.columns).equals(valid_candidates)
    scale_column_names = CoarseCharacterizationStage.feature_scale_column_names()
    assert coarse_features.columns == [*valid_candidates.columns, *feature_column_names, *scale_column_names]
    assert coarse_features.select(scale_column_names).n_unique() == 1
    assert all(scale > 0.0 for scale in coarse_features.select(scale_column_names).row(0))
    spaced_candidates = pl.read_parquet(tmp_path / f"{SpacingStage.output_name}.parquet")
    assert spaced_candidates.equals(
        coarse_features.filter(pl.col("problem_id").is_in(spaced_candidates["problem_id"].to_list()))
    )
    assert manifests[3].parameters == {"min_distance": DEFAULT_SPACING_MIN_DISTANCE}
    full_features = pl.read_parquet(tmp_path / f"{FullCharacterizationStage.output_name}.parquet")
    assert full_features.select(spaced_candidates.columns).equals(spaced_candidates)
    assert full_features.columns == [
        *spaced_candidates.columns,
        *FullCharacterizationStage(core_solver_configs).feature_column_names,
        *FullCharacterizationStage.feature_scale_column_names(),
    ]
