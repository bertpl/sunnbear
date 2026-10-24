"""This package holds the suite pipeline: maintainer tooling that builds test functions for benchmark suites.

The pipeline is a chain of stages, each of which computes 1 output table from the outputs of the stages
before it:

- `PipelineStage` names the stages, in run order;
- `generate_candidates` builds every candidate test function of every formula;
- `validate_candidates` runs the validation checks, and records for each candidate the check that
  rejected it;
- `run_pipeline` runs the stages in order, and has a `PipelineWorkspace` write each stage's output and
  its `PipelineStageManifest` into a workspace directory.

Every run recomputes every stage. Maintainers run the pipeline from the command line, as `__main__`
describes; the pipeline's workspace directory is not part of the package.
"""

from .generation import CANDIDATES_SCHEMA, generate_candidates
from .manifest import PipelineStageManifest
from .runner import run_pipeline
from .stage import PipelineStage
from .validation import CHECKED_CANDIDATES_SCHEMA, MAX_BOUND_TO_WIDTH_RATIO, RejectionReason, validate_candidates
from .workspace import PipelineWorkspace
