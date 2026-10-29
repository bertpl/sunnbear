"""`run_pipeline` runs every stage of the `stages` package, candidate generation first, on the given formulas."""

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline import stages as stages_package
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage
from sunnbear._core.benchmark.suites.pipeline.features import FeatureFidelity
from sunnbear._core.benchmark.suites.pipeline.runner import run_pipeline
from sunnbear._core.benchmark.suites.pipeline.stages import (
    CandidateGenerationStage,
    CandidateValidationStage,
    CoarseCharacterizationStage,
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
def test_the_pipeline_generates_validates_and_characterizes_the_candidates_of_the_given_formulas(tmp_path):
    """On the formulas of category 2, the pipeline writes their candidates, then the valid ones with their c-ranges,
    then every valid one with its coarse feature vector, and the scale of each feature block in every row."""
    # --- arrange ----------------------
    # The shipped formulas of category 2 form a small corpus, so the pipeline runs fast on them.
    formulas = [formula for formula in FormulaRegistry.formulas() if formula.number[0] == 2]
    core_solver_configs = [
        config for config in SolverConfigRegistry.configs() if config.role.is_used_for_problem_characterization
    ]

    # --- act --------------------------
    # pytest-xdist already runs 1 test process per CPU, so 1 worker per CPU would only make the workers wait for CPU.
    manifests = run_pipeline(
        workspace_dir=tmp_path, formulas=formulas, core_solver_configs=core_solver_configs, n_workers=2
    )

    # --- assert -----------------------
    # The output names of the stages package's stages, sorted, are its stages in run order.
    output_names_expected = sorted(
        stage_cls.output_name
        for stage_cls in _stage_classes(PipelineStage)
        if stage_cls.__module__.startswith(f"{stages_package.__name__}.")
    )
    assert [manifest.output_name for manifest in manifests] == output_names_expected
    candidates = pl.read_parquet(tmp_path / f"{CandidateGenerationStage.output_name}.parquet")
    valid_candidates = pl.read_parquet(tmp_path / f"{CandidateValidationStage.output_name}.parquet")
    coarse_features = pl.read_parquet(tmp_path / f"{CoarseCharacterizationStage.output_name}.parquet")
    assert candidates.height == sum(len(formula.build_all_candidates()) for formula in formulas)
    assert valid_candidates.select(candidates.columns).equals(candidates)
    assert ((valid_candidates["c_min"] < 0.0) & (valid_candidates["c_max"] > 0.0)).all()
    feature_column_names = FeatureFidelity.COARSE.feature_column_names(
        [config.solver_id for config in core_solver_configs]
    )
    assert coarse_features.select(valid_candidates.columns).equals(valid_candidates)
    scale_column_names = FeatureFidelity.COARSE.feature_scale_column_names()
    assert coarse_features.columns == [*valid_candidates.columns, *feature_column_names, *scale_column_names]
    assert coarse_features.select(scale_column_names).n_unique() == 1
    assert all(scale > 0.0 for scale in coarse_features.select(scale_column_names).row(0))
