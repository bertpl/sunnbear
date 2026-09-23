"""This module defines the exceptions raised by the test-function layer."""

from sunnbear._core.exceptions import SunnbearError


class UnknownFormulaError(SunnbearError):
    """Raised when a function identity references a formula number not present in the registry."""


class InvalidParamsError(SunnbearError):
    """Raised when a parameter tuple fails its formula's validity criteria."""


class FormulaTaxonomyError(SunnbearError):
    """Raised when the registered formulas and categories do not form a valid taxonomy tree."""
