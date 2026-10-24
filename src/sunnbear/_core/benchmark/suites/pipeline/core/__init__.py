"""This package holds the framework of the benchmark suite pipeline: what a stage is, and how the stages run.

How the pieces tie together:

- `PipelineStage` is the base class of a stage. A stage names its output, declares the stages whose outputs it
  reads, and computes its output from theirs.
- `run_stages` runs a list of stages in order. It hands each stage the outputs of its input stages, times the
  stage, and has the `PipelineWorkspace` write the stage's output.
- `PipelineWorkspace` writes each stage's output into the workspace directory, together with a
  `PipelineStageManifest`.
- `PipelineStageManifest` records how a stage built its output: the sha256 of the output and of the stage's inputs,
  the sunnbear version, the row and rejection counts, and the timing.

A stage that rejects candidates marks each candidate in a ``rejected_by`` column, which names the reason or holds
``""`` for a candidate that the stage keeps; the manifest counts the rejections per reason.

This package imports nothing from the stages, which the package `stages` beside it implements.
"""

from .manifest import PipelineStageManifest
from .stage import PipelineStage
from .stage_runner import run_stages
from .workspace import PipelineWorkspace
