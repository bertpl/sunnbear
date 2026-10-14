"""This package tests `RegulaFalsi`.

Published results:

- None: regula falsi is a classical method with no paper of its own.

Third-party published results:

- Oliveira and Takahashi (2020), Table 1, the column "Reg.F.": not checked by a test yet; the record of `RegulaFalsi`
  lists it as TBD. The table's runs stop by the rule of `BracketingSolver`, with ``xtol = 1e-10`` on ``[-1, 1]``, its
  counts leave out the 2 evaluations at the interval bounds, and "∞" marks a run that reached the cap of 10^4
  evaluations. Counted that way, the 24 counts compare with those of `RegulaFalsi` as follows:
  - 22 match, 11 of the 12 "∞" rows among them;
  - Weierstrass, printed as "∞", converges after 13 iterations, on an x-value where the test data's function is
    exactly 0. When the function adds its terms to 0.001 one at a time, as the authors' MATLAB code for the table
    does, its last bits change, and the solve reaches an x-value where the function is about -1.9e-19, onto which the
    next chord's zero rounds; the solve then evaluates that x-value until it runs out of budget, as printed;
  - Trigonometric 2 takes 10 iterations, against 11: its 10th iterate is an x-value where ``math.sin`` returns exactly
    -0.5, so the function value there is 0 and the solve ends.

  The other forms of the chord's zero in the sources match fewer counts: the forms of equation 2 of Dowell and Jarratt
  (1971) and of equation 2 of Ford (1997) match 18 each, and the form of ``rtflsp`` 17.
- Ganchovski et al. (2026), Table 2, the column "fp": not checked by a test yet; the record of `RegulaFalsi` lists it
  as TBD. The paper's C# false-position code computes the chord's zero in the form of `RegulaFalsi`, but stops once 2
  successive chord zeros lie within ``(aTol + rTol * |x|) / 2`` of each other, with ``aTol = rTol = 1e-14``, returns
  the last chord's zero without evaluating it, and gives up after 200 iterations, printed as 202 evaluations.
  `RegulaFalsi` evaluates the same x-values as that code on all 92 problems, and the C# code's stopping rule, applied
  to these x-values, gives all 92 counts of the column, and the 92 roots of the paper's supplementary results.
- Dowell and Jarratt (1971), Tables 2 to 7, the Regula Falsi columns: not reproduced. The tables stop once
  ``|f(x)| < 0.5e-19``. Near most of their roots, float64 cannot compute ``f(x)`` that accurately, so only an iterate
  with ``f(x) == 0`` meets that test, and the iteration counts cannot be compared.
- Dowell and Jarratt (1972), Problems 1 to 4, the Regula Falsi column: not reproduced. Problems 1 to 3 stop once
  ``|f(x)|`` drops below ``0.5e-17`` or ``0.5e-19``, a test that in float64 only an iterate with ``f(x) == 0``
  passes, and Problem 4 states no starting values.
- Ganchovski and Traykov (2023), Table 2, the column "fp": not compared, because the paper does not state the stopping
  rule of its false-position runs.
- Ford (1997) and Press et al. (2007), section 9.2: no numerical results for the method.

Reference implementations:

- None found: neither SciPy nor mpmath implements the unmodified method; mpmath's ``Illinois`` always scales the
  function value of a retained bound.
"""
