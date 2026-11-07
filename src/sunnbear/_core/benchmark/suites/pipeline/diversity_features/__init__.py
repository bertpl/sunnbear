"""This package computes the candidates' diversity features and their empirical difficulty index (EDI).

The characterization stages compute these features, and spacing and max-div compare candidates by them; the EDI is
max-div's second distance term. The package holds:

- `DiversityFeatureFactory` computes the features: 1 candidate's raw features, and the scaled matrix of a set of
  candidates;
- `FeatureBlock` names a block of a feature vector;
- `FeatureBlockScales` holds the scale of each `FeatureBlock` over a set of candidates;
- `FeatureMatrix` holds 1 feature vector per candidate, paired with the candidate's id;
- `compute_edi` computes a candidate's empirical difficulty index (EDI) from its solves;
- `FeatureFidelity` names a fidelity, which sets how much work goes into each feature vector.
"""

from .diversity_feature_factory import DiversityFeatureFactory, FeatureBlockScales
from .edi import EDI_GPQ_LEVEL, compute_edi
from .feature_matrix import FeatureMatrix
from .feature_vector import SNUFFLED_PROPERTIES, SOLVERS_GPQ_LEVELS, FeatureBlock
from .fevals_mapping import map_fevals_to_feature
from .fidelity import FeatureFidelity
