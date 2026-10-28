"""This package runs snuffled's analysis of test problems for the stages of the benchmark suite pipeline.

`SnuffledAnalysisBudget` names the budget of an analysis, and builds the analysis of a test problem at 1 tuple of
the Monte Carlo tuple set, so that every stage that runs snuffled analyzes a test problem in the same way.
"""

from .budget import SNUFFLED_ANALYSIS_ROOT_SEED, SnuffledAnalysisBudget
from .function_evaluation_error import FunctionEvaluationError
