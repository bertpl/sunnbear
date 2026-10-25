"""This package holds the test-problem framework: formulas, categories, recipes, identities, and the registry.

How the pieces tie together, from authored code to a solvable function::

    Formula (subclass, auto-registered on definition)
      │ build_all_candidates() ── ParamRecipe grids and tables ──▶ p-tuples,
      │                          validated against param_names,
      │                          filtered by is_param_tuple_valid(),
      │                          then near-duplicates dropped (deduplicate_param_tuples)
      │ build_candidate(p) [framework: carries the formula + identity, so the
      ▼                  callable forms are derived on demand; + interval_bounds(p)]
    CandidateTestProblem ─── id: ProblemId(number, names, p) · xc_fun: f(x, c) · interval bounds (a, b)
      │
      │ calibrated(c_min, c_max)   [c-range from an external artifact, never derived]
      ▼
    TestProblem ─ the benchmarkable unit: f(x, c), [a, b], [c_min, c_max]
      │
      │ build_x_fun(c)   [per Monte-Carlo run: one closure over the compiled body]
      ▼
    f(x) ───────── plain callable handed to a Solver

The formula taxonomy is a tree whose inner nodes are `FormulaCategory` classes and whose leaves are
formulas: a formula's number, e.g. ``(2, 1, 1)``, is its category's number, ``(2, 1)``, plus 1 element
(see `taxonomy`).

`FormulaRegistry.candidate_from_id` re-enters this chain from a stored identity,
rebuilding the `CandidateTestProblem`; `CandidateTestProblem.calibrated` then attaches a suite's c-range to it and
returns a `TestProblem`.

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
  identity (`ProblemId` — the formula number and its named parameter tuple, stable, rendered in
  one canonical spelling, and human-readable), candidate assembly and enumeration,
  and lookup (`FormulaRegistry`).
- `CandidateTestProblem` and `TestProblem` (in `test_problem`) are a candidate before and after its c-range is
  calibrated; that module explains why they are 2 types.
"""

from .category import USER_DEFINED_FORMULA_CATEGORY_NUMBER, FormulaCategory
from .formula import Formula
from .identity import ProblemId
from .param_values import (
    CANONICAL_DIGITS,
    DEDUP_DIGITS,
    ParamNotation,
    deduplicate_param_tuples,
)
from .recipes import ParamAxis, ParamGrid, ParamRecipe, ParamTable
from .registry import FormulaRegistry
from .source import FormulaSource
from .test_cases import FormulaTestCase
from .test_problem import CandidateTestProblem, TestProblem
from .types import XCFun, XFun
