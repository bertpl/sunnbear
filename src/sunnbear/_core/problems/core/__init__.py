"""This package holds the test-problem framework: formulas, categories, recipes, identities, and the registry.

How the pieces tie together, from authored code to a solvable function::

    Formula (subclass, auto-registered on definition)
      │ build_all_candidates() ── ParamRecipe grids and tables ──▶ p-tuples,
      │                          validated against the names of params,
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

- a concrete `Formula` contributes its mathematics and its declared parameter
  interface: `params`, `parametrized_fun`, `interval_bounds`, `recipes`, optionally
  `is_param_tuple_valid` — one class, one module, in `catalog`; defining the
  class registers it. It also declares what a reader sees of it: its `presentation`
  (`FormulaPresentation`, in the LaTeX notation that the `presentation` package describes) and its `effect_of_c`.
  A formula from a publication declares its `location_in_publication`; the category that holds the formulas of 1
  publication declares the `Publication`, which `FormulaRegistry.publication_of` finds for each formula.
- the framework owns everything mechanical: numba compilation — once per
  formula, not per candidate (`Formula.jit`, `Formula._compiled_formula`),
  identity (`ProblemId` — the formula number and its named parameter tuple, stable, rendered in
  one canonical spelling, and human-readable), candidate assembly and enumeration,
  and lookup (`FormulaRegistry`).
- `CandidateTestProblem` and `TestProblem` (in `test_problem`) are a candidate before and after its c-range is
  calibrated; that module explains why they are 2 types.
"""

from .category import USER_DEFINED_FORMULA_CATEGORY_NUMBER, FormulaCategory
from .effect_of_c import EffectOfC
from .formula import Formula
from .identity import ProblemId
from .param import FormulaParam
from .param_values import (
    CANONICAL_DIGITS,
    DEDUP_DIGITS,
    ParamNotation,
    deduplicate_param_tuples,
)
from .presentation import PLAIN_MARKER_MACROS, FormulaPresentation, LatexTemplate
from .publication import Publication
from .recipes import ParamAxis, ParamGrid, ParamRecipe, ParamTable
from .registry import FormulaRegistry
from .test_cases import FormulaTestCase
from .test_problem import CandidateTestProblem, TestProblem
from .types import XCFun, XFun
