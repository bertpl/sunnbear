"""This package holds the test-function framework: formulas, recipes, identities, and the registry.

How the pieces tie together, from authored code to a solvable function::

    Formula (subclass, auto-registered on definition)
      │ build_all_candidates() ── ParamRecipe grids ──▶ p-tuples,
      │                          validated against param_names,
      │                          filtered by is_param_tuple_valid(),
      │                          then near-duplicates dropped (deduplicate_param_tuples)
      │ build_candidate(p) [framework: carries the formula + identity, so the
      ▼                  callable forms are derived on demand; + interval_bounds(p)]
    CandidateTestFunction ─── id: FunctionId(number, p) · xc_fun: f(x, c) · interval bounds a, b
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

This package imports nothing from the packages beside it: the shipped formulas in
`catalog` register themselves when their modules are imported, and the parent
package imports those modules.

Ownership summary:

- a concrete `Formula` contributes only mathematics plus its declared parameter
  interface: `param_names`, `parametrized_fun`, `interval_bounds`, `recipes`, optionally
  `is_param_tuple_valid` — one class, one module, in `catalog`; defining the
  class registers it.
- the framework owns everything mechanical: numba compilation — once per
  formula, not per candidate (`Formula.jit`, `Formula._compiled_formula`),
  identity (`FunctionId` — the parameter tuple itself, stable, faithful to the
  authored notation, and human-readable), candidate assembly and enumeration,
  and lookup (`FormulaRegistry`).
- `CandidateTestFunction` vs `TestFunction` differ by exactly one fact — whether a
  calibrated c-range exists — kept as two types so calibrated-ness is a
  property of the type, not a nullable field.
"""

from .formula import Formula
from .identity import FunctionId
from .param_values import (
    CANONICAL_DIGITS,
    DEDUP_DIGITS,
    DecimalParamValue,
    ExponentialParamValue,
    ParamNotation,
    ParamValue,
    deduplicate_param_tuples,
)
from .recipes import ParamAxis, ParamRecipe
from .registry import FormulaRegistry
from .test_cases import FormulaTestCase
from .test_function import CandidateTestFunction, TestFunction
from .types import XCFun, XFun
