"""`run_pipeline` runs candidate generation, then candidate validation, on the formulas that it is given."""

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.runner import run_pipeline
from sunnbear._core.benchmark.suites.pipeline.stages import CandidateGeneration, CandidateValidation
from sunnbear._core.functions.core import FormulaRegistry


def test_the_pipeline_generates_then_validates_the_candidates_of_the_given_formulas(tmp_path):
    """The pipeline writes the candidates of the given formulas, then the same candidates with their validation."""
    # --- arrange ----------------------
    # The shipped formulas of category 2 form a small corpus, so the pipeline runs fast on them.
    formulas = [formula for formula in FormulaRegistry.formulas() if formula.number[0] == 2]

    # --- act --------------------------
    manifests = run_pipeline(workspace_dir=tmp_path, formulas=formulas)

    # --- assert -----------------------
    assert [manifest.output_name for manifest in manifests] == [
        CandidateGeneration.output_name,
        CandidateValidation.output_name,
    ]
    candidates = pl.read_parquet(tmp_path / f"{CandidateGeneration.output_name}.parquet")
    checked_candidates = pl.read_parquet(tmp_path / f"{CandidateValidation.output_name}.parquet")
    assert candidates.height == sum(len(formula.build_all_candidates()) for formula in formulas)
    assert checked_candidates.drop("rejected_by").equals(candidates)
