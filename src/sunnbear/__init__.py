"""`sunnbear` is a benchmarking framework for univariate root-solvers.

The top level re-exports what its two kinds of authors need:

- a **solver author** subclasses `Solver` or `BracketingSolver`, works with a
  `SolveRun` and `Interval`, and reads back a `SolveResult` with its
  `SolveStatus`; `MaxFevalsExceeded` is the interrupt a solver may see fly past;
- a **formula author** subclasses `Formula`, declares `ParamRecipe` grids, and
  gets `TestFunction` instances identified by a `FunctionId` out of the
  `FormulaRegistry`.

The reference solvers live in `sunnbear.solvers`, summary statistics in
`sunnbear.stats`.
"""

from sunnbear.errors import MaxFevalsExceeded
from sunnbear.functions import Formula, FormulaRegistry, FunctionId, ParamRecipe, TestFunction
from sunnbear.solvers import BracketingSolver, Interval, Solver, SolveResult, SolveRun, SolveStatus

__all__ = [
    "BracketingSolver",
    "Formula",
    "FormulaRegistry",
    "FunctionId",
    "Interval",
    "MaxFevalsExceeded",
    "ParamRecipe",
    "SolveResult",
    "SolveRun",
    "SolveStatus",
    "Solver",
    "TestFunction",
]
