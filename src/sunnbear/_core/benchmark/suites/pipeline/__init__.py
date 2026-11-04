"""This package holds the benchmark suite pipeline, the maintainer tooling that builds benchmark suites.

The pipeline is a sequence of stages that share 1 state. Every candidate stays in the state, and each stage adds its
information on the candidates that no stage before it dropped, and drops candidates of its own. The packages are:

- `core` holds the framework: what a stage is, its id, its manifest, and the workspace that stores the manifests;
- `snuffled_analysis` runs snuffled's analysis of a test problem, for every stage that needs one;
- `features` defines the candidates' feature vectors and their empirical difficulty index (EDI);
- `selection` selects the pipeline's suites, each the most diverse candidates under difficulty quotas, from the
  candidates' feature vectors;
- `state` holds the state of a run, which each stage reaches only through its own state accessor;
- `stages` holds the stages, 1 module or subpackage per stage, whose names sort in run order;
- `run_pipeline` runs the stages in order on a set of formulas, sharing 1 pool of worker processes between them, in a
  `PipelineMode` that sets how much work the stages do.

Every run recomputes every stage. Maintainers run the pipeline from the command line, as `__main__` describes; it
writes its outputs to the workspace directory given there, outside the package.
"""

from .core import (
    PipelineStage,
    PipelineStageId,
    PipelineStageManifest,
    PipelineStop,
    PipelineStopError,
    PipelineWorkspace,
)
from .diversity_features import FeatureBlock, FeatureFidelity, DiversityFeatureFactory
from .mode import PipelineMode
from .runner import PipelineRunResult, run_pipeline, run_stages
from .stages import (
    MAX_BOUND_TO_WIDTH_RATIO,
    CandidateCharacterizationStage,
    CandidateGenerationStage,
    CandidateValidationStage,
    CoarseCharacterizationStage,
    CoreSelectionStage,
    DistillationStage,
    FullCharacterizationStage,
    SpacingStage,
)
from .state import PipelineState
