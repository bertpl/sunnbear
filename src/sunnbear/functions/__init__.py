"""Test-function framework: formulas, recipes, identities, and the registry."""

from ._formula import Formula, XCFun
from ._identity import FunctionId, format_param, parse_param
from ._recipes import ParamAxis, ParamRecipe, Spacing
from ._registry import build, candidates, formulas
from ._test_function import Candidate, TestFunction, XFun
