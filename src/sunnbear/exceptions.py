"""This module collects every exception sunnbear raises, in one import location.

All derive from `SunnbearError`; each is defined in the layer that raises it and re-exported here.
"""

from sunnbear._core.exceptions import SunnbearError
from sunnbear._core.functions.exceptions import InvalidParamsError, UnknownFormulaError

__all__ = ["InvalidParamsError", "SunnbearError", "UnknownFormulaError"]
