"""`run_pipeline` runs every stage of the `stages` package, candidate generation first, on the given formulas."""

import polars as pl

from sunnbear._core.benchmark.suites.pipeline import stages as stages_package
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage
from sunnbear._core.benchmark.suites.pipeline.runner import run_pipeline
from sunnbear._core.benchmark.suites.pipeline.stages import CandidateGenerationStage, CandidateValidationStage
from sunnbear._core.problems.core import FormulaRegistry


def test_the_pipeline_generates_then_validates_the_candidates_of_the_given_formulas(tmp_path):
    """The pipeline writes the candidates of the given formulas, then the valid ones with their c-ranges: all of them,
    for category 2."""
    # --- arrange ----------------------
    # The shipped formulas of category 2 form a small corpus, so the pipeline runs fast on them.
    formulas = [formula for formula in FormulaRegistry.formulas() if formula.number[0] == 2]

    # --- act --------------------------
    manifests = run_pipeline(workspace_dir=tmp_path, formulas=formulas)

    # --- assert -----------------------
    # The output names of the stages package's stages, sorted, are its stages in run order.
    output_names_expected = sorted(
        stage_cls.output_name
        for stage_cls in PipelineStage.__subclasses__()
        if stage_cls.__module__.startswith(f"{stages_package.__name__}.")
    )
    assert [manifest.output_name for manifest in manifests] == output_names_expected
    candidates = pl.read_parquet(tmp_path / f"{CandidateGenerationStage.output_name}.parquet")
    valid_candidates = pl.read_parquet(tmp_path / f"{CandidateValidationStage.output_name}.parquet")
    assert candidates.height == sum(len(formula.build_all_candidates()) for formula in formulas)
    assert valid_candidates.select(candidates.columns).equals(candidates)
    assert ((valid_candidates["c_min"] < 0.0) & (valid_candidates["c_max"] > 0.0)).all()
