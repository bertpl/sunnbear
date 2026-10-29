"""This package runs snuffled's analysis of test problems for the stages of the benchmark suite pipeline.

Every stage that runs snuffled analyzes a test problem in the same way, through 2 parts of this package:

- `SnuffledAnalysisBudget` names the budget of an analysis, and its `extract_properties_or_rejection_reason` builds
  the analysis of a test problem at 1 tuple of the Monte Carlo tuple set and reads the analysis's properties;
- `extract_properties_or_rejection_reason` holds the rules by which snuffled's diagnostics reject the test problem.
"""

from .budget import SnuffledAnalysisBudget
from .diagnostic_rules import FLAG_REJECTION_REASONS, MAX_ZERO_WIDTH_IN_XTOL, extract_properties_or_rejection_reason
from .function_evaluation_error import FunctionEvaluationError
