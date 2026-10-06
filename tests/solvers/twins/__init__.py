"""This package holds the shared code of the twin tests, which compare a solver with a reference implementation of
its algorithm.

A twin is a test-only `Solver` that runs a reference implementation of a solver's algorithm, such as SciPy's or
mpmath's, so that the solver can be compared with it evaluation by evaluation. A twin is never registered and never
benchmarked.

Every twin test follows the same rules, so that no twin takes an undocumented approach of its own:

- it runs on `TWIN_TEST_CASES`, the test cases that all twins share;
- `assert_agrees_with_twin` compares the 2 solves evaluation by evaluation;
- each difference from exact agreement is declared once, on the twin class, with its reason in that class's
  docstring.

A twin stops where sunnbear's solver would stop, not where the reference implementation would:
`StoppingWrappedFunction` raises `TwinConvergedSignal` once the interval, split at every point evaluated so far, meets
`Interval.is_converged`. The 2 solves then evaluate the same number of points, and their different stopping
criteria never need to be declared as a deviation.
"""

from .agreement import MAX_ULPS_APART, assert_agrees_with_twin, ulps_apart
from .cases import TWIN_TEST_CASES, TwinTestCase
from .solver import StoppingWrappedFunction, TwinConvergedSignal, TwinSolver
