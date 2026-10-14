"""`RegulaFalsi` implements regula falsi, the bracketing algorithm based on linear interpolation.

The rest of this docstring is the record of `RegulaFalsi` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package).

Sources:
    - I - article:
      - none: regula falsi is a classical method with no article of its own.
    - II - authors' code:
      - none.
    - III - third party:
      - Oliveira and Takahashi (2020): equation 5, the chord's zero, inside their Algorithm 0, which stops once the
        interval is at most ``2 * epsilon`` wide and returns its midpoint;
      - Ford (1997), equations 2 and 3: the chord's zero in 2 forms, and which interval bound the next iteration
        keeps; no stopping rule for the method;
      - Press et al. (2007), section 9.2: prose and the routine ``rtflsp``, which stops once an evaluation moves an
        interval bound by less than its tolerance;
      - Dowell and Jarratt (1971), section 1: equation 2, the chord's zero as a correction to the newest x-value, and,
        as an example, a stopping test on the relative step;
      - Ganchovski et al. (2026): the C# false-position code of its supplementary material, which stops once 2
        successive chord zeros lie within its tolerance.
    - IV - own judgment:
      - none.

Source per aspect:
    Every aspect follows Oliveira and Takahashi (2020), the chord's zero of their equation 5 inside their Algorithm 0,
    except:
    - JUDGMENT-CALL: a function value of 0 at an initial interval bound ends the solve at that bound, as for every
      solver. Oliveira and Takahashi assume ``f(a) * f(b) < 0``, so Algorithm 0 never meets this case; ``rtflsp``
      evaluates the chord's zero first, which lies, up to rounding, at the bound where f is 0, so ``rtflsp`` takes 1
      evaluation more than `RegulaFalsi`.
    - JUDGMENT-CALL: the chord's zero is computed as the C# code of Ganchovski et al. writes it,
      ``(a * fb - b * fa) / (fb - fa)``, which negates the numerator and the denominator of equation 5. Both forms
      take the same operations and give the same x-values, so the choice has no effect.
    - JUDGMENT-CALL: the width test runs before each iteration, as in `BracketingSolver`, while Algorithm 0 runs it
      after each iteration; the 2 orders differ only on an initial interval at most ``2 * xtol`` wide, where
      Algorithm 0 evaluates 1 chord's zero more.
    - JUDGMENT-CALL: the stopping rule of Algorithm 0, which is `BracketingSolver`'s, not that of ``rtflsp`` or of the
      C# code: P1 ranks all 3 as III - third party and favors the most widely used Python implementation among them,
      but no Python implementation of the method exists; only Algorithm 0's rule guarantees an x-value within ``xtol``
      of a root. On 408 solves of the test suite's problems, at 3 values of ``xtol``, `RegulaFalsi` runs out of budget
      in 248; the rules of ``rtflsp`` and of the C# code would end 199 and 197 of these, but would return an x-value
      farther than ``xtol`` from a root in 136 and 115 of the 408 solves.
    - JUDGMENT-CALL: no safeguard keeps the chord's zero strictly inside the interval, because no source has one,
      though `BracketingSolver._next_x` must return an x-value strictly inside. Once the interval bound that each
      iteration replaces lies at the root up to rounding, the chord's zero can round onto that bound or just past it,
      and the solve then evaluates that x-value again until its budget runs out. Of the 248 solves above that run out
      of budget, 143 end this way, each at an x-value within ``xtol`` of a root.
    - Translation of ``xtol`` (P7): ``xtol`` is the tolerance epsilon of Algorithm 0.

Validation:
    - A - authors' results:
      - none exists.
    - B - third-party results:
      - PRINCIPLE-CONFLICT (P4): no test checks a published result, though the 2 tables of the TBD entries below
        would validate `RegulaFalsi`; tests of them would resolve the conflict.
      - TBD: Oliveira and Takahashi (2020), Table 1, the column "Reg.F.": 22 of its 24 counts match exactly, and 23
        when the Weierstrass function adds its terms in another order; the 24th, Trigonometric 2, is off by 1. The
        other forms of the chord's zero in the sources match at most 18 counts.
      - TBD: Ganchovski et al. (2026), Table 2, the column "fp": `RegulaFalsi` evaluates the same x-values as the
        paper's C# code on all 92 problems, and the C# code's stopping rule, applied to these x-values, gives all 92
        counts and roots.
      - not used: the regula falsi columns of other articles; the docstring of the test package
        ``tests.solvers.bracketing.regula_falsi`` lists them, with the reasons.
    - C - reference implementation:
      - none found: neither SciPy nor mpmath implements the unmodified method.

Variants:
    - `RegulaFalsiConfig`, the only config, is secondary (P8); its behavior deviates from no principle, and the
      record's only PRINCIPLE-CONFLICT concerns its validation.
"""

from sunnbear._core.solvers.core import BracketingSolver, Interval, SolveState


class RegulaFalsi(BracketingSolver):
    """`RegulaFalsi` evaluates, every iteration, the zero of the chord through ``(a, f(a))`` and ``(b, f(b))``.

    `RegulaFalsi` computes the chord's zero as ``(a * fb - b * fa) / (fb - fa)``, with ``fa`` and ``fb`` the function
    values at the interval bounds ``a`` and ``b``; each new x-value replaces the interval bound where f has the same
    sign as at the new x-value.

    `RegulaFalsi` implements the classic method, without any of the modifications that repair its known weakness.

    When the function is convex or concave on the interval, 1 interval bound is retained forever, so the interval
    never shrinks below the distance from that bound to the root, and the width test of the stopping criterion fails
    unless that distance is at most ``2 * xtol``.

    The other bound moves toward the root every iteration, and a solve whose width test keeps failing ends in 1 of 3
    ways:

    - the computed function value at an iterate is exactly 0, which ends the solve at that iterate as ``CONVERGED``;
    - the moving bound reaches the root up to rounding, so that the chord's zero rounds onto that bound or just past
      it, and the solve evaluates that x-value again every iteration until its evaluation budget is exhausted;
    - the evaluation budget is exhausted while the moving bound still approaches the root.

    A solve that exhausts its budget ends as ``MAX_FEVALS``, and its ``result.x`` is the last evaluated x-value.

    `RegulaFalsi` stops by `BracketingSolver`'s criterion, so a converged solve returns an x-value within ``xtol`` of a
    root.

    References:
        - Oliveira, I. F. D. and Takahashi, R. H. C. (2020). An enhancement of the bisection method average
          performance preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), article 5. Its
          equation 5 gives the chord's zero, and its Algorithm 0 the stopping rule of `BracketingSolver`. Its Table 1
          holds the column "Reg.F.". https://doi.org/10.1145/3423597
        - Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia
          Iranica 4(1&2), 28-34. The paper's equations 2 and 3 give the chord's zero in 2 forms; equation 3 is the
          form of `RegulaFalsi` up to the signs of its numerator and denominator.
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd edition, section 9.2.
          Cambridge University Press. The section calls the method false position and gives the routine ``rtflsp``.
        - Dowell, M. and Jarratt, P. (1971). A modified regula falsi method for computing the root of an equation.
          BIT 11(2), 168-174. Its section 1 states regula falsi as a correction to the newest x-value, and its Tables
          2 to 7 hold columns for the method. https://doi.org/10.1007/BF01934364
        - Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026). Improvements to the modified
          Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. Its supplementary material,
          https://www.mdpi.com/article/10.3390/a19050332/s1, holds C# false-position code, which computes the chord's
          zero in the form of `RegulaFalsi`; its Table 2 holds the column "fp". https://doi.org/10.3390/a19050332
    """

    name = "regula_falsi"
    version = 1

    def _next_x(self, state: SolveState, interval: Interval) -> float:
        """Return the zero of the chord through ``(a, f(a))`` and ``(b, f(b))``."""
        return (interval.a * interval.fb - interval.b * interval.fa) / (interval.fb - interval.fa)
