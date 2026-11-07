"""This package holds the contract between the benchmark suite pipeline's stages and the code that runs them.

A run is a loop over the stages, in the order of `PipelineStageId`: each stage runs on its own state accessor, and the
run records a manifest for it. This package defines what every stage shares in that loop. The loop itself is
`run_stages` in `runner`, and the information that the stages share is in `state`; both live outside this package,
because they depend on the stages, and this package imports nothing from the packages beside it.

The package holds these parts:

- `PipelineStageId` names each stage, in run order.
- `PipelineStage` is the base class of a stage. A stage runs on its state accessor, through which it reads the
  information of earlier stages and writes its own.
- `PipelineStageManifest` records how a stage ran: with which code and parameters, on how many candidates, and when;
  `PipelineWorkspace` writes the manifests into the workspace directory.
- A stage that raises `PipelineStopError` stops the run, which records the stop as a `PipelineStop`.
- `PIPELINE_ROOT_SEED` is the root seed of every random draw of the pipeline.

A stage drops a candidate with a plain string as its reason, such as ``bisection_count_not_exact``; the stage that
drops the candidate chooses the string, so no list of reasons exists.
"""

from .root_seed import PIPELINE_ROOT_SEED
from .stage import PipelineStage
from .stage_id import PipelineStageId
from .stage_manifest import PipelineStageExecutionInfo, PipelineStageManifest
from .stop_error import PipelineStop, PipelineStopError
from .workspace import PipelineWorkspace
