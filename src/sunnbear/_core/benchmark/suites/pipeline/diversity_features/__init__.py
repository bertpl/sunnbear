"""This package defines the candidates' feature vectors, their empirical difficulty index, and the fidelities.

The characterization stages compute these features, and the later stages compare candidates by them. The package
holds:

- `DiversityFeatureFactory` defines the feature vector: its features, and how they are computed and scaled;
- `FeatureBlock` names a block of a feature vector;
- `FeatureBlockScales` holds the scale of each `FeatureBlock` over a set of candidates;
- `FeatureMatrix` holds 1 feature vector per candidate, paired with the candidate's id;
- `compute_edi` computes a candidate's empirical difficulty index (EDI) from its solves;
- `FeatureFidelity` names a fidelity, which sets how much work goes into each feature vector.
"""

from .edi import EDI_GPQ_LEVEL, compute_edi
from .feature_matrix import FeatureMatrix
from .feature_vector import SNUFFLED_PROPERTIES, SOLVERS_GPQ_LEVELS, FeatureBlock
from .diversity_feature_factory import FeatureBlockScales, DiversityFeatureFactory
from .fevals_mapping import map_fevals_to_feature
from .fidelity import FeatureFidelity
