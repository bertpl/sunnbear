"""This package holds the benchmark suite pipeline, the maintainer tooling that builds benchmark suites.

The pipeline is a chain of stages, each of which computes 1 output table from the outputs of the stages before it:

- `core` holds the framework: the base class of a stage, the loop that runs the stages, and the workspace that
  stores their outputs;
- `stages` holds the stages, 1 module per stage, whose names sort in run order;
- `run_pipeline` runs the stages in order on a set of formulas.

Every run recomputes every stage. Maintainers run the pipeline from the command line, as `__main__` describes; it
writes its outputs to the workspace directory given there, outside the package.
"""

from .core import PipelineStage, PipelineStageManifest, PipelineWorkspace, run_stages
from .runner import run_pipeline
from .stages import (
    CANDIDATES_SCHEMA,
    CHECKED_CANDIDATES_SCHEMA,
    MAX_BOUND_TO_WIDTH_RATIO,
    CandidateGenerationStage,
    CandidateValidationStage,
    RejectionReason,
)
