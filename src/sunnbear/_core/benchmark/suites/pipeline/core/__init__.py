"""This package holds the framework of the benchmark suite pipeline: what a stage is, and how the stages run.

The parts of the framework work together as follows:

- `PipelineStage` is the base class of a stage. A stage names its output, and computes it from the output table of
  the stage before it: it may add columns and drop rows, never drop columns or add rows.
- `PipelineStageOutput` holds what a stage returns: its output table, and its reports, named tables that the next
  stage does not read, such as the rows that the stage dropped and why.
- `run_stages` runs a list of stages as a chain. It hands each stage the output table of the stage before it and the
  run's `WorkerPool`, times the stage, checks the rules of the chain, and has the `PipelineWorkspace` write the stage's
  output.
- `PipelineWorkspace` writes each stage's output table and reports into the workspace directory, together with a
  `PipelineStageManifest`.
- `PipelineStageManifest` records how a stage built its output: from which input, with which code, and when.

This package imports nothing from the package `stages` beside it, which implements the stages.
"""

from .manifest import PipelineStageManifest
from .stage import PipelineStage, PipelineStageOutput
from .stage_runner import run_stages
from .workspace import PipelineWorkspace
