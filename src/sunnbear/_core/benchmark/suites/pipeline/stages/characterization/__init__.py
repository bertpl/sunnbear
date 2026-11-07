"""This package holds what the 2 characterization stages share: their base class and their worker task.

- `CandidateCharacterizationStage`, in `stage`, is the base class of `CoarseCharacterizationStage` and
  `FullCharacterizationStage`, which differ only in their stage id, their default fidelity, and the EDI that full
  characterization also stores;
- `CandidateCharacterizationTask`, in `task`, computes each candidate's `CandidateCharacterizationResult` in a worker.
"""

from .stage import CandidateCharacterizationStage
from .task import CandidateCharacterizationResult, CandidateCharacterizationTask
