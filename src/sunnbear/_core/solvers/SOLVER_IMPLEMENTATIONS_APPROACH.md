# Solver implementations: approach

sunnbear ships solvers for 2 reasons:

- to reveal the strengths and weaknesses of root-finding methods;
- to reveal the characteristics of test functions, through how different methods behave on them.

Differences between solvers that come from small implementation choices, made by a method's authors or left open by them, serve neither goal. So this document fixes a few choices for all solvers, and a solver's other small choices need no justification. Not every solver follows the shared choices yet.

## Shared choices

These choices bind every solver's core config (role `SolverRole.BUILTIN_CORE`), and the config of every solver that has only 1. A secondary config may differ from them, and its docstring says how.

- **Stopping rule of a bracketing solver.** A solve ends once the interval is at most `2 * xtol` wide, or once the function value at an interval bound is 0, checked after every iteration. It returns that bound, or else the interval's midpoint. This is the rule of `BracketingSolver` (`Interval.is_converged` and `Interval.root`).
- **A 0 ends a solve only at an interval bound.** A function value of 0 at an initial interval bound ends the solve at once. A 0 at another x-value ends the solve only once that x-value has become an interval bound.
- **The chord's zero.** Every step that takes the zero of the chord through 2 points `(a, fa)` and `(b, fb)` computes it as `(a * fb - b * fa) / (fb - fa)`, with 1 shared function. This includes the chord steps of hybrid methods, and the open method `Secant`. A step that is not a plain chord keeps its source's form, such as a modified chord, or a chord step that its source guards against rounding.

## Step formulas

- **Each solver follows its source's step formulas.**
- **A tolerance inside a step formula stays as the source states it**, such as a minimum step that keeps the iteration from getting stuck on 1 x-value. It belongs to the method, not to its stopping rule.
- **A solver adds a correction for rounding only where a source states it.** Regula falsi, for example, computes the plain chord's zero, though in float64 that zero can round onto an interval bound.

## Validation

Published numerical results and reference implementations check that a solver implements its method's step formulas correctly:

- **A published table that depends on the paper's own stopping rule** is checked against a subclass of the solver in its test package, with that stopping rule.
- **The docstring of each solver's test package** lists the published results and reference implementations that the tests compare against, the deviations that the tests allow, and the results that the tests do not compare, each with its reason.

## Provenance

The `References:` section of each solver's class docstring cites every source used for the implementation or the validation, each with 1 line on what the solver takes from it, such as the step formula, a reference implementation's stopping rule, or a table that the tests compare against.

The class docstring states each deviation from the source in 1 bullet.

## How the solver classes are built

A reader must be able to compare a solver with its source step by step:

- **Each solver class holds its whole algorithm**, even where 2 solvers differ in few details, as `RegulaFalsi` and `Illinois` do.
- **Variants of 1 algorithm, such as different values of 1 of its parameters, are configs of 1 class.**
- **Each solver keeps its source's variable names and symbols**, and writes 1 long method where helpers would break the step-by-step match with the source.
- **Duplication across solvers is accepted**, for solver classes, state classes, tests and twin tests alike. Code reviews that ask to merge near-duplicate solver code are answered by this section.
- **Only the framework in `core` is shared**, such as `Solver`, `SolveState` and the shared choices above.
