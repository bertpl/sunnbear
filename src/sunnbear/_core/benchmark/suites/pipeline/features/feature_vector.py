"""`FeatureBlock` names the blocks of a candidate's feature vector, and the constants here set their contents.

A candidate's feature vector has 1 block per `FeatureBlock`:

- the solvers block, from the solves of the core solver configs: 1 geometric mean of `n_fevals_eff` per config,
  and the geometric pseudo-quantile (`gpq`) of all the candidate's solves together at each of `SOLVERS_GPQ_LEVELS`;
- the snuffled block, from snuffled's analyses: the mean of each of `SNUFFLED_PROPERTIES` over the analyses.
"""

from enum import StrEnum

from snuffled import FunctionProperty, RootProperty

SOLVERS_GPQ_LEVELS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
# `SNUFFLED_PROPERTIES` lists snuffled's root and function properties in the order in which an analysis extracts
# them: the root properties first, because the function properties reuse the samples of f that the root properties
# take.
SNUFFLED_PROPERTIES = (*RootProperty, *FunctionProperty)


# ==================================================================================================
#  FeatureBlock
# ==================================================================================================
class FeatureBlock(StrEnum):
    """A `FeatureBlock` names a block of a feature vector after its source.

    The member's value appears in the name of each of the block's columns.
    """

    SOLVERS = "solvers"
    SNUFFLED = "snuffled"
