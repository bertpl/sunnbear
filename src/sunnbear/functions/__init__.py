"""Test-function framework: formulas, recipes, identities, registry, and the catalog.

How the pieces tie together, from authored code to a solvable function::

    Formula (subclass, auto-registered on definition)
      │ build_all_candidates() ── ParamRecipe grids ──▶ p-tuples,
      │                          validated against param_names,
      │                          filtered by is_param_tuple_valid(),
      │                          deduplicated by FunctionId
      │ build_candidate(p) [framework: carries the formula + identity, so the
      ▼                  callable forms are derived on demand; + bracket(p)]
    CandidateTestFunction ─── id: FunctionId(number, p) · xc_fun: f(x, c) · bracket [a, b]
      │
      │ calibrated(c_min, c_max)   [c-range from an external artifact, never derived]
      ▼
    TestFunction ─ the benchmarkable unit: f(x, c), [a, b], [c_min, c_max]
      │
      │ build_x_fun(c)   [per Monte-Carlo run: one closure over the compiled body]
      ▼
    f(x) ───────── plain callable handed to a Solver

`FormulaRegistry.candidate_from_id` re-enters this chain from a stored identity,
rebuilding the `CandidateTestFunction` that a suite's c-range then calibrates.

Ownership summary:

- a concrete `Formula` contributes only mathematics plus its declared parameter
  interface: `param_names`, `parametrized_fun`, `bracket`, `recipes`, optionally
  `is_param_tuple_valid` — one class, one module, under `catalog/`; defining the
  class registers it.
- the framework owns everything mechanical: numba compilation — once per
  formula, not per candidate (`Formula.jit`, `Formula._compiled_formula`),
  identity (`FunctionId` — the parameter tuple itself, stable and
  human-readable), candidate assembly and enumeration, and discovery
  (`FormulaRegistry`).
- `CandidateTestFunction` vs `TestFunction` differ by exactly one fact — whether a
  calibrated c-range exists — kept as two types so calibrated-ness is a
  property of the type, not a nullable field.
"""

from ._formula import Formula
from ._identity import DecimalParamValue, ExponentialParamValue, FunctionId, ParamValue
from ._recipes import ParamAxis, ParamRecipe, ParamSpacing
from ._registry import FormulaRegistry
from ._test_function import CandidateTestFunction, TestFunction
from ._types import XCFun, XFun
