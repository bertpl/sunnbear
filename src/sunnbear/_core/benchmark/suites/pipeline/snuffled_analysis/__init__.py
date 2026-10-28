"""This package runs snuffled's analysis of test problems for the stages of the benchmark suite pipeline.

`SnuffledTier` names the budget of an analysis, and builds the analysis of a test problem at 1 tuple of the tuple set,
so that every stage that runs snuffled analyzes a test problem in the same way.
"""

from .tier import ROOT_SEED, SnuffledTier
