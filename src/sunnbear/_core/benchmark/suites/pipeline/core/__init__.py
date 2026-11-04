"""This package holds the framework of the benchmark suite pipeline: what a stage is, and what a run records.

The parts of the framework work together as follows:

- `PipelineStageId` names each stage, in run order.
- `PipelineStage` is the base class of a stage. A stage runs on its state accessor, through which it reads the
  information of earlier stages and writes its own.
- `PipelineStageManifest` records how a stage ran: with which code and parameters, on how many candidates, and when;
  `PipelineWorkspace` writes the manifests into the workspace directory.
- A stage that raises `PipelineStopError` stops the run, which records the stop as a `PipelineStop`.
- `PIPELINE_ROOT_SEED` is the root seed of every random draw of the pipeline.

A stage drops a candidate with a plain string as its reason, such as ``bisection_count_not_exact``; the stage that
drops the candidate chooses the string, so no list of reasons exists.

This package imports nothing from the packages beside it.
"""

from .manifest import PipelineStageExecutionInfo, PipelineStageManifest
from .root_seed import PIPELINE_ROOT_SEED
from .stage import PipelineStage
from .stage_id import PipelineStageId
from .stop import PipelineStop, PipelineStopError
from .workspace import PipelineWorkspace
