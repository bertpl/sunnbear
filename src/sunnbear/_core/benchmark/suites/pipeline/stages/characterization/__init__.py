"""This package holds what the 2 characterization stages share: their base class and their worker task.

- `CandidateCharacterizationStage`, in `stage`, is the base class of `CoarseCharacterizationStage` and
  `FineCharacterizationStage`, which differ only in their stage id and their default fidelity;
- `CandidateCharacterizationTask`, in `task`, computes each candidate's `CandidateCharacterizationResult` in a worker.
"""

from .stage import CandidateCharacterizationStage
from .task import CandidateCharacterizationResult, CandidateCharacterizationTask
