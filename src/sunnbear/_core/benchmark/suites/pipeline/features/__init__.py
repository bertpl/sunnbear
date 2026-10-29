"""This package holds what the pipeline's stages share to compute the candidates' feature vectors at a fidelity.

A fidelity sets how much work goes into each feature vector. Each such pipeline stage is a child class, in the package
`stages`, of a base class here, and sets the fidelity:

- `FeatureFidelity` names a fidelity: the tuples of the solves and of snuffled's analyses, the budget of the analyses,
  and the names of the feature columns;
- `CandidateCharacterizationStage` is the base class of the characterization stages, which compute the feature vectors
  in `CandidateCharacterizationTask` tasks.
"""

from .characterization_stage import CandidateCharacterizationStage
from .characterization_task import CandidateCharacterizationTask
from .fidelity import ANALYTICAL_PROPERTIES, EMPIRICAL_GPQ_LEVELS, FeatureFidelity
