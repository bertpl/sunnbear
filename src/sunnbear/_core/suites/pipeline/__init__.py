"""This package holds the suite pipeline: maintainer tooling that builds test functions for benchmark suites.

The pipeline is a chain of stages, each of which computes 1 output table from the outputs of the stages
before it:

- `PipelineStage` names the stages, in run order;
- `generate_candidates` builds every candidate test function of every formula;
- `validate_candidates` runs the validation checks, and records for each candidate the check that
  rejected it;
- `run_pipeline` runs the stages in order, and has a `PipelineWorkspace` write each stage's output and
  its `PipelineStageManifest` into a workspace directory.

Every run recomputes every stage. ``python -m sunnbear._core.suites.pipeline --workspace <dir>`` runs
the pipeline over the shipped formulas; the workspace is never shipped.
"""

from .generation import CANDIDATES_SCHEMA, generate_candidates
from .manifest import PipelineStageManifest
from .runner import run_pipeline
from .stage import PipelineStage
from .validation import MAX_INTERVAL_RATIO, VALIDATION_SCHEMA, RejectionReason, count_rejections, validate_candidates
from .workspace import PipelineWorkspace
