"""This package holds the base classes, the fidelities and the feature blocks of the stages that compute features.

A fidelity sets how much work goes into each feature vector. Each such pipeline stage is a child class of a base class
here, lives in the package `stages`, and sets its default fidelity. The package holds:

- `FeatureFidelity` names a fidelity;
- `FeatureBlock` names a block of a feature vector;
- `CandidateCharacterizationStage` is the base class of the characterization stages, which compute the feature vectors
  in `CandidateCharacterizationTask` tasks, then the scale of each `FeatureBlock`: its mean pairwise L1 distance
  over the kept candidates. It names the columns that it adds, and later stages read them back through it. Each
  characterization stage also reports, for each core solver config, the fraction of its solves that end without a
  correct answer.
"""

from .characterization_stage import INCORRECT_SOLVES_PER_CONFIG_REPORT_NAME, CandidateCharacterizationStage
from .characterization_task import CandidateCharacterizationResult, CandidateCharacterizationTask
from .feature_vector import SNUFFLED_PROPERTIES, SOLVERS_GPQ_LEVELS, FeatureBlock
from .fevals_mapping import map_feature_to_fevals, map_fevals_to_feature
from .fidelity import FeatureFidelity
