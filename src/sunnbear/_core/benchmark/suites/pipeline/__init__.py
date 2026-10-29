"""This package holds the benchmark suite pipeline, the maintainer tooling that builds benchmark suites.

The pipeline is a chain of stages, each of which computes its output table from the output table of the stage before
it, adding columns and dropping rows:

- `core` holds the framework: the base class of a stage, the loop that runs the stages, and the workspace that
  stores their outputs;
- `stages` holds the stages, 1 module or subpackage per stage, whose names sort in run order;
- `snuffled_analysis` runs snuffled's analysis of a test problem, for every stage that needs one;
- `features` holds the base classes of the stages that compute the candidates' feature vectors; each such stage is a
  child class in `stages` that sets its `FeatureFidelity`;
- `run_pipeline` runs the stages in order on a set of formulas, sharing 1 pool of worker processes between them.

Every run recomputes every stage. Maintainers run the pipeline from the command line, as `__main__` describes; it
writes its outputs to the workspace directory given there, outside the package.
"""

from .core import (
    REJECTED_BY_SCHEMA,
    REJECTED_CANDIDATES_REPORT_NAME,
    REJECTIONS_PER_FORMULA_REPORT_NAME,
    PipelineStage,
    PipelineStageManifest,
    PipelineStageOutput,
    PipelineWorkspace,
    RejectionReason,
    run_stages,
)
from .features import CandidateCharacterizationStage, FeatureBlock, FeatureFidelity
from .runner import run_pipeline
from .stages import (
    C_RANGE_SCHEMA,
    CANDIDATES_SCHEMA,
    MAX_BOUND_TO_WIDTH_RATIO,
    CandidateGenerationStage,
    CandidateValidationStage,
    CoarseCharacterizationStage,
    SpacingStage,
)
