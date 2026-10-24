"""This package holds the benchmark suite pipeline, the maintainer tooling that builds benchmark suites.

The pipeline is a chain of stages, each of which computes its output table from the output table of the stage before
it, adding columns and dropping rows:

- `core` holds the framework: the base class of a stage, the loop that runs the stages, and the workspace that
  stores their outputs;
- `stages` holds the stages, 1 module per stage, whose names sort in run order;
- `run_pipeline` runs the stages in order on a set of formulas, sharing 1 pool of worker processes between them.

Every run recomputes every stage. Maintainers run the pipeline from the command line, as `__main__` describes; it
writes its outputs to the workspace directory given there, outside the package.
"""

from .core import PipelineStage, PipelineStageManifest, PipelineStageOutput, PipelineWorkspace, run_stages
from .runner import run_pipeline
from .stages import (
    CANDIDATES_SCHEMA,
    MAX_BOUND_TO_WIDTH_RATIO,
    REJECTED_CANDIDATES_SCHEMA,
    CandidateGenerationStage,
    CandidateValidationStage,
    RejectionReason,
)
