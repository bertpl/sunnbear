# Solver implementations: approach

sunnbear ships solvers for 2 reasons:

- to reveal the strengths and weaknesses of root-finding methods;
- to reveal the characteristics of test functions, through how different methods behave on them.

A small implementation choice that makes 2 solvers behave differently serves neither goal, whether the method's authors made that choice or left it to the implementer. So this document sets a few choices for all solvers, and a solver's other small choices need no justification.

## Shared choices

These choices apply to every solver's core config (role `SolverRole.BUILTIN_CORE`), and to the config of every solver that has only 1 config. A config with another role, such as `SolverRole.BUILTIN_SECONDARY`, may differ from the shared choices, and the docstring of its config class says how.

Not all of these configs follow the shared choices: some solvers stop by their source's own stopping rule, or compute the chord's zero in their source's form.

- **Stopping rule of a bracketing solver.** After every iteration, a solve ends once the interval is at most `2 * xtol` wide, or once the function value at an interval bound is 0.
  - The solve returns the bound whose function value is 0 if there is one, and otherwise the interval's midpoint.
  - `BracketingSolver` implements this stopping rule (`Interval.is_converged` and `Interval.root`).
- **A function value of 0 ends a solve only at an interval bound.** A function value of 0 at an initial interval bound ends the solve at once. A function value of 0 at another x-value ends the solve only once that x-value has become an interval bound.
- **The chord's zero.** Every step that takes the zero of the chord through 2 points `(a, fa)` and `(b, fb)` computes it as `(a * fb - b * fa) / (fb - fa)`.
  - The chord formula applies to the chord steps of hybrid methods too, and to the open method `Secant`.
  - A step that does not compute a plain chord's zero writes its formula as its source writes it: for example, a modified chord, or a chord step whose source adds a guard against rounding.

## Step formulas

- **Each solver follows its source's step formulas**, except where the shared choices above set a formula.
- **A tolerance inside a step formula stays as the source states it**, such as a minimum step size, which keeps each new x-value at least that step size away from the earlier x-values. Such a tolerance is part of the method, not of the method's stopping rule.
- **A solver adds a correction for rounding only where a source states it.** Regula falsi, for example, computes the plain chord's zero, though in float64 that zero can round onto an interval bound.

## Validation

The tests compare each solver with published numerical results and reference implementations, to check that the solver implements its method's step formulas correctly:

- **A published table that depends on its paper's own stopping rule** is checked against a subclass of the solver that replaces the shared stopping rule with the paper's; the subclass is defined in the solver's test package.
- **The docstring of each solver's test package** lists the following, each with its reason:
  - the published results and reference implementations used for comparison;
  - the allowed deviations;
  - the published results not used for comparison.

## Provenance

The `References:` section of each solver's class docstring cites every source used for the implementation or the validation, each with 1 line on what that source provides, for example:

- the step formula;
- a reference implementation's stopping rule;
- a published table used in the tests.

The class docstring states each deviation from its sources in 1 bullet.

## How the solver classes are built

A reader must be able to compare a solver with its source step by step:

- **Each solver class holds its whole algorithm**, even where 2 solvers differ in few details, as `RegulaFalsi` and `Illinois` do.
- **Variants of one algorithm, such as different values of one of its parameters, are configs of one class.**
- **Each solver keeps its source's variable names and symbols**, and writes 1 long method where splitting it into helpers would make it harder to compare with the source step by step.
- **Duplication across solvers is accepted**, for solver classes, state classes and tests alike, including the tests that compare a solver with a reference implementation. Code reviews that ask to merge near-duplicate solver code are answered by this section.
- **Only the framework in `core` is shared**, such as `Solver`, `SolveState`, and the code that implements the shared choices above.
