"""Test-function framework: formulas, recipes, identities, registry, and the catalog.

How the pieces tie together, from authored code to a solvable function::

    Formula (subclass, auto-registered on definition)
      │ recipes() ── ParamRecipe grids ──▶ p-tuples ── is_param_tuple_valid() filter
      │
      │ candidate(p)   [framework: once-per-formula-compiled parametrized_fun,
      ▼                 bound to p in a thin closure, + bracket(p)]
    CandidateTestFunction ─── id: FunctionId(number, p) · fun: f(x, c) · bracket [a, b]
      │
      │ + calibrated c-range (external artifact; supplied to build(), never derived)
      ▼
    TestFunction ─ the benchmarkable unit: f(x, c), [a, b], [c_min, c_max]
      │
      │ bind(c)   [per Monte-Carlo run]
      ▼
    f(x) ───────── plain callable handed to a Solver

Ownership summary:

- a concrete `Formula` contributes only mathematics: `parametrized_fun`, `bracket`,
  `recipes`, optionally `is_param_tuple_valid` — one class, one module, under
  `catalog/`; defining the class registers it.
- the framework owns everything mechanical: numba compilation — once per
  formula, not per candidate (`Formula.jit`, `Formula._compiled_formula`),
  identity (`FunctionId` — the parameter tuple itself, stable and
  human-readable), `CandidateTestFunction`/`TestFunction` assembly, and discovery
  (`formulas`, `candidates`, `build`).
- `CandidateTestFunction` vs `TestFunction` differ by exactly one fact — whether a
  calibrated c-range exists — kept as two types so calibrated-ness is a
  property of the type, not a nullable field.
"""

# NOTE: import order is load-bearing. Catalog modules import framework names from this
# package, and the registry import (last) triggers the catalog auto-import — by which
# point every framework name below is already bound on this module.
from ._formula import Formula
from ._identity import FunctionId, ParamValue
from ._recipes import ParamAxis, ParamRecipe, ParamSpacing
from ._test_function import CandidateTestFunction, TestFunction
from ._types import XCFun, XFun

from ._registry import build, candidates, formulas  # isort: skip  (must come after the framework names)
