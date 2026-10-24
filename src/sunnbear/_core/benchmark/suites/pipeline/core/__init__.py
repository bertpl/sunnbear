"""This package holds the framework of the benchmark suite pipeline: what a stage is, and how the stages run.

The parts of the framework work together as follows:

- `PipelineStage` is the base class of a stage. A stage names its output, and computes it from the output of the
  stage before it, keeping all of that output's columns.
- `run_stages` runs a list of stages as a chain. It hands each stage the output of the stage before it, times the
  stage, and has the `PipelineWorkspace` write the stage's output.
- `PipelineWorkspace` writes each stage's output into the workspace directory, together with a
  `PipelineStageManifest`.
- `PipelineStageManifest` records how a stage built its output: from which input, with which code, and when.

This package imports nothing from the package `stages` beside it, which implements the stages.
"""

from .manifest import PipelineStageManifest
from .stage import PipelineStage
from .stage_runner import run_stages
from .workspace import PipelineWorkspace
