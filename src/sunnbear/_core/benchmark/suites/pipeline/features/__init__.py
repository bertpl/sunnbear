"""This package holds the base classes, the fidelities and the feature blocks of the stages that compute features.

A fidelity sets how much work goes into each feature vector. Each such pipeline stage is a child class, in the package
`stages`, of a base class here, and sets the fidelity. The package holds:

- `FeatureFidelity` names a fidelity;
- `FeatureBlock` names a block of a feature vector;
- `CandidateCharacterizationStage` is the base class of the characterization stages, which compute the feature vectors
  in `CandidateCharacterizationTask` tasks, then the scale of each `FeatureBlock`: its mean pairwise L1 distance
  over the kept candidates. It names the columns that it adds, and later stages read them back through it.
"""

from .characterization_stage import CandidateCharacterizationStage
from .characterization_task import CandidateCharacterizationTask
from .feature_vector import SNUFFLED_PROPERTIES, SOLVERS_GPQ_LEVELS, FeatureBlock
from .fidelity import FeatureFidelity
