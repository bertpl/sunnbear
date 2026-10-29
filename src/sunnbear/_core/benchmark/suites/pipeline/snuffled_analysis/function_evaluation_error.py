"""`FunctionEvaluationError` reports that f raised during snuffled's analysis of a test problem."""


# ==================================================================================================
#  FunctionEvaluationError
# ==================================================================================================
class FunctionEvaluationError(Exception):
    """A `FunctionEvaluationError` reports that f raised during snuffled's analysis; f's exception is its cause."""
