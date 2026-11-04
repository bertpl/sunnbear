"""This package holds the state of a run of the benchmark suite pipeline, and the state accessor of each stage.

The state owns the information of every stage. Each stage reaches that information only through its own state accessor,
which is the contract that the stage adheres to:

- `PipelineState` holds a run's candidates and the information of each stage, and creates each stage's accessor;
- `PipelineStateStorage` holds that information: the `CandidateRegistry`, with a `CandidateDrop` for each dropped
  candidate, and 1 structure per stage;
- `PipelineStateAccessor` is the base class of the accessors, 1 per stage, such as `CandidateValidationStateAccessor`;
- `PipelineState.create_build_details` gives the outcome of a run as `BenchmarkSuitesBuildDetails`, a read-only copy
  of the run's information;
- the value objects of `stage_information`, such as `CharacterizationResults`, carry a stage's information to and from
  its accessor.

This package imports nothing from the package `stages` beside it, which imports from this package.
"""

from .accessors import (
    CandidateGenerationStateAccessor,
    CandidateValidationStateAccessor,
    CharacterizationStateAccessor,
    CoarseCharacterizationStateAccessor,
    CoreSelectionStateAccessor,
    DistillationStateAccessor,
    FullCharacterizationStateAccessor,
    PipelineStateAccessor,
    SelectionStateAccessor,
    SpacingStateAccessor,
)
from .build_details import BenchmarkSuitesBuildDetails
from .candidate_registry import CandidateDrop, CandidateRegistry
from .pipeline_state import PipelineState
from .stage_information import (
    CharacterizationResults,
    DistilledSuiteSummary,
    IntervalBounds,
    NearestKeptCandidate,
    SuiteMembership,
)
from .storage import PipelineStateStorage
