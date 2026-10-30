"""This package holds the framework of the benchmark suite pipeline: what a stage is, and how the stages run.

The parts of the framework work together as follows:

- `PipelineStage` is the base class of a stage. A stage names its output, and computes it from the output table of
  the stage before it: it may add columns and drop rows, never drop columns or add rows.
- `PipelineStageOutput` holds what a stage returns: its output table, and its reports, named tables that the next
  stage does not read, such as the rows that the stage dropped and why.
- `run_stages` runs a list of stages as a chain. For each stage, it:
  - hands the stage the run's `WorkerPool` and the output table of the stage before it;
  - times the stage;
  - checks the rules of the chain;
  - has the `PipelineWorkspace` write the stage's output.

  A stage that raises `PipelineStopError` stops the run, which `run_stages` returns as a `PipelineRunResult` with a
  `PipelineStop`.
- `PipelineWorkspace` writes each stage's output table and reports into the workspace directory, together with a
  `PipelineStageManifest`, and reads the reports back.
- `PipelineStageManifest` records how a stage built its output: from which input, with which code and parameters,
  and when.

The stages share 2 more things that the framework defines:

- `RejectionReason` names why a stage rejected a candidate, and `PipelineStage._build_output_with_rejection_reports`
  builds the output of a stage that rejects candidates, with 2 reports on the rejected candidates whose columns are the
  same for every such stage;
- `PIPELINE_ROOT_SEED` is the root seed of every random draw of the pipeline.

This package imports nothing from the package `stages` beside it, which implements the stages.
"""

from .manifest import PipelineStageManifest
from .rejections import (
    REJECTED_BY_SCHEMA,
    REJECTED_CANDIDATES_REPORT_NAME,
    REJECTIONS_PER_FORMULA_REPORT_NAME,
    RejectionReason,
    summarize_rejections_per_formula,
)
from .root_seed import PIPELINE_ROOT_SEED
from .stage import PipelineStage, PipelineStageOutput
from .stage_runner import PipelineRunResult, run_stages
from .stop import PipelineStop, PipelineStopError
from .workspace import PipelineWorkspace
