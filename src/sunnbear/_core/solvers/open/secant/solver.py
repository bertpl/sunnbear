"""`Secant` implements the secant method, which evaluates the zero of the line through the 2 latest iterates.

The rest of this docstring is the record of `Secant` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package).

Sources:
    - I - article:
      - none: the secant method is a classical method with no article of its own.
    - II - authors' code:
      - none.
    - III - third party:
      - SciPy's ``scipy.optimize.newton``, without a derivative;
      - Press et al. (2007), section 9.2: prose and the routine ``rtsec``;
      - Atkinson (1989), section 2.3: equation 2.3.1, and Table 2.3, its results on 1 problem.
    - IV - own judgment:
      - none.

Source per aspect:
    Every aspect follows SciPy, which P1 prefers among third-party sources, except:
    - Equal function values at the 2 latest x-values end the solve as ``DIVERGED``, since the secant's zero lies at
      infinity. SciPy returns their midpoint flagged as not converged, a result that the framework has no status for.
    - JUDGMENT-CALL: a function value of 0 at an initial interval bound ends the solve at that bound after the 2
      evaluations at the bounds, as for every solver. SciPy evaluates that bound a 3rd time, for the same result.
    - PRINCIPLE-GAP (P1): no rule for which interval bound starts as the newest x-value reproduces both published
      tables, and P1 prefers SciPy only among sources that pass validation. The code keeps SciPy's rule, the bound
      with the larger ``|f|``: 3 counts of Oliveira and Takahashi's Table 1 then differ by 1, and Atkinson's
      Table 2.3 needs the rule of Press et al., the bound with the smaller ``|f|``.
    - Translation of ``xtol`` (P7): ``xtol`` is SciPy's absolute tolerance ``tol``, with its relative tolerance
      ``rtol`` at 0, SciPy's default.

Validation:
    - A - authors' results:
      - none exists.
    - B - third-party results:
      - PRINCIPLE-CONFLICT (P4): not used: Oliveira and Takahashi (2020), Table 1, the column "Secant", which no test
        checks; a test of its counts would resolve the conflict.
      - not used: Atkinson (1989), Table 2.3, which needs another rule for the newest starting x-value (see above).
    - C - reference implementation:
      - used: a twin test checks that `Secant` evaluates the same x-values as SciPy's ``scipy.optimize.newton``,
        and stops and returns where SciPy does.

Variants:
    - `SecantConfig`, the only config, is secondary (P8); its deviations from the principles are the entries marked
      PRINCIPLE-CONFLICT above.
"""

from sunnbear._core.solvers.core import Solver, SolveState
from sunnbear._core.solvers.core.exceptions import DivergedError


class Secant(Solver):
    """`Secant` implements the secant method, in the form of SciPy's ``scipy.optimize.newton`` without a derivative.

    Each iteration computes the zero of the secant, the line through ``(x0, f0)`` and ``(x1, f1)``, where ``x0`` and
    ``x1`` are the 2 latest x-values, ``x1`` the newest. Near a simple root, the method converges faster than
    linearly, with order about 1.618.

    `Secant` is an open method: it keeps no interval around the root, so its iterates may leave the initial
    interval, and its result is not guaranteed to lie within ``xtol`` of a root.

    A solve runs as follows:

    - **Starting x-values:** the bounds of the initial interval. The method treats one bound as the older x-value and
      the other as the newest x-value, and the newest x-value is the bound with the larger ``|f|``, or the upper bound
      when both are equal.
    - **Step formula:** the zero of the secant, computed from the ratio of the 2 function values, with the value of
      smaller magnitude divided by the value of larger magnitude, so that the ratio's magnitude is at most 1.
    - **Stopping criterion:** the solve ends once the step from the newest x-value to the next x-value is at most
      ``xtol``, and returns that next x-value without evaluating it.
    - **Equal function values:** when the 2 latest x-values have equal function values, the secant is horizontal and
      its zero lies at infinity. `Secant` then raises `DivergedError`, which `Solver.solve` records as ``DIVERGED``.

    A small step does not show that the next x-value is close to a root: on a function that is nearly flat between 2
    x-values, a step taken far from the root can be smaller than ``xtol``.

    `Secant` keeps no interval around the root, so it writes its own loop, not `BracketingSolver`'s.

    References:
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd edition, section 9.2.
          Cambridge University Press. Its ``rtsec`` takes the bound with the smaller ``|f|`` as the newest x-value,
          where SciPy and `Secant` take the bound with the larger ``|f|``.
        - SciPy's ``scipy.optimize.newton``, without a derivative; the test suite checks `Secant` against
          ``scipy.optimize.newton``.
        - Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition, section 2.3.
          John Wiley & Sons. Its Table 2.3 starts from ``x0 = 2`` and ``x1 = 1``, so on ``[1, 2]`` it takes the bound
          with the smaller ``|f|`` as the newest x-value, as ``rtsec`` does.
        - Oliveira, I. F. D. and Takahashi, R. H. C. (2020). An enhancement of the bisection method average
          performance preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), article 5. Its
          Table 1 holds the column "Secant", for a secant method that stops once the smaller ``|f|`` of its 2 latest
          x-values is at most 1e-10. https://doi.org/10.1145/3423597
    """

    name = "secant"
    version = 1

    def _solve(self, state: SolveState) -> float:
        """Run the secant method from the interval bounds; return the first secant zero within ``xtol`` of its start.

        Each iteration computes the zero of the secant through the 2 latest x-values. If the step from the newest
        x-value to that zero is at most ``xtol``, the iteration returns the zero; otherwise it evaluates the zero and
        makes that zero the newest x-value.

        Raises:
            DivergedError: If the 2 latest x-values have equal function values, so the next x-value lies at infinity.
        """
        # --- starting x-values ------------------
        # x0 and x1 are the 2 latest x-values, x1 the newest, with function values f0 and f1.
        interval = state.interval
        x0, x1, f0, f1 = interval.a, interval.b, interval.fa, interval.fb
        # The newest x-value is the bound with the larger |f|, the upper bound when both are equal, as in SciPy.
        if abs(f1) < abs(f0):
            x0, x1, f0, f1 = x1, x0, f1, f0
        state.x_best = x1

        # --- main loop --------------------------
        while True:
            if f1 == f0:
                raise DivergedError(
                    "The 2 latest x-values have equal function values, so the next x-value is infinite."
                )
            # Divide the smaller |f| by the larger, as SciPy does, so the ratio's magnitude is at most 1.
            if abs(f1) > abs(f0):
                x = (-f0 / f1 * x1 + x0) / (1.0 - f0 / f1)
            else:
                x = (-f1 / f0 * x0 + x1) / (1.0 - f1 / f0)
            if abs(x - x1) <= state.xtol:
                return x
            x0, f0 = x1, f1
            x1, f1 = x, state.f(x)
            state.x_best = x1
