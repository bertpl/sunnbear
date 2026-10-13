# Solver design principles

**These principles are a draft, a work in progress.** Not every solver follows them.

These principles decide how each of sunnbear's solvers implements its published method:

- which source it follows;
- how it is validated;
- how it computes;
- when it stops.

A question about how a solver behaves is answered as a consequence of these principles, never for 1 solver at a time, so that the solvers stay consistent with each other.

Each principle has an ID, such as P1 or P5a, so that a docstring or a test can cite it.

## Why sunnbear has solvers

sunnbear has solvers for 2 reasons:

- to characterize test functions objectively;
- to show that the benchmark suite reveals the strengths and weaknesses of solvers.

The solvers give qualitative insight into the differences between methods; they do not set out to prove quantitatively which method is best. A detail of the comparison between solvers is worth investigating only as far as these 2 goals justify.

## Sources

**P1. Each aspect of a solver, such as its step formula, a safeguard or its stopping rule, follows the highest source that states it completely and unambiguously.** The sources rank as follows, highest preference first:

- **I** — the article that published the method. Its own content ranks above any other source. Within it:
  - **Ia** — a code listing printed in the article;
  - **Ib** — pseudocode printed in the article;
  - **Ic** — the article's prose and equations.

  Code ranks above pseudocode, because it is likely closer to the authors' experimental code.
- **II** — the authors' own code outside the article: a repository, a supplement, or code sent on request;
- **III** — other publicly available third-party implementations; a textbook's description and its tables count here, so a method without an original article starts at III;
- **IV** — sunnbear's own interpretation or choice, for an aspect that no source states, or that every source states in a form that fails its validation (P4, P5).

Where 2 sources of the same rank state an aspect differently and both pass validation, the choice is a judgment call that favors the most widely used implementation in the Python ecosystem, such as SciPy's, because of its install base.

A source can state some aspects completely and leave others out, or state them ambiguously. So the choice is made per aspect.

**P2. A solver uses the next-ranked source for an aspect only for a reason.** The valid reasons are:

- the current source does not state the aspect completely and unambiguously;
- the solver's validation with the current source is not convincing (P5);
- there is a good reason to deviate, such as a formula whose published form fails in float64.

Without a good reason, a solver does not deviate from its article.

**P3. Each solver's class docstring declares every deviation** from the source that P1 ranks highest for that aspect.

## Validation

**P4. A solver is validated by the strongest kind of evidence that exists**, highest first:

- **A** — numerical results in the authors' own article;
- **A′** — a third party's published numerical results for the method. They rank after A and never outweigh it, because a third party makes its own implementation decisions, which its paper does not always state;
- **B** — behavioral parity with a reference implementation from source II or III, through a twin test, which runs the reference implementation as a `Solver` and checks that both evaluate the same x-values.

For A′, only sources already cited by sunnbear count; when a method has no credible validation otherwise, sunnbear may cite 1 more source chosen for that method.

Where a paper has a table of numerical results that no test reproduces, a test is added, or the solver's test package records why the solver does not reproduce the table.

**P5. A reproduction of published numerical results is convincing** when it is exact, or when each deviation has a reasonable explanation: a stated cause, or a difference small enough to come from the authors' unstated implementation details or from a different platform, such as another language or CPU.

A deviation without such an explanation is not convincing. Whether a reproduction is convincing is judged case by case, with no fixed numbers, for A and A′ alike.

**P5a (candidate, not adopted). A published iteration count that the solver misses by 1 counts as a reasonable deviation**, even when no cause is stated for that row of the table. Any detail of a published run that the paper does not state can shift a count by 1:

- the arithmetic and its rounding;
- the math library;
- the language and its compiler;
- the many small decisions of any implementation.

The tests mark such a row with `UNSTATED_RUN_DETAILS` and a short observation; an unverified cause is never stated as fact. A deviation larger than 1 needs a cause of its own, for example a test function or solver whose properties make the iteration count sensitive to small differences in the run.

## Form

**P6. A solver computes each formula as its source for that step writes it**, because sunnbear's flop counts should show the published algorithm. Forms that are equal in exact arithmetic can round differently and count different flops.

These kinds of change leave the published algorithm intact and are allowed without a declaration:

- **an exactly equal cheaper operation**, such as `0.5 * x` for `x / 2`;
- **computing a repeated value once:** when the source computes a value several times, in the same or nearly the same form, the solver computes it once, in 1 extra assignment or by moving the formula to an earlier or later step;
- **short-circuit evaluation:** a condition that combines comparisons with Python's `and` or `or` skips the later comparisons once the earlier ones decide it, even where the source's language, such as Algol 60, evaluates them all. Skipping them changes no result, because the comparisons have no side effects.

A solver does not restructure a formula algebraically to save flops. Where it is unclear whether a change is allowed, the solver keeps the source's form. Any other change of form needs a good reason under P2, and the class docstring states that reason: the published results reproduce better with it, or the published form fails in float64.

**P7. Sign tests compare signs.** A test whether 2 function values differ in sign compares their signs explicitly, in every solver, even where its source writes a product such as `fa * fb < 0`, because in float64 the product of 2 small values can underflow to 0.

This deviation is stated here once, not per solver. The rule holds as long as the product is not needed for another step.

## Stopping

**P8. The stopping rule aims at the same accuracy for every solver:** the returned x-value lies within `xtol` of a root. That goal is reached by 2 types of rule:

- **type 1, the framework's rule, which `BracketingSolver` applies:** stop when the interval is at most `2 * xtol` wide, and return its midpoint;
- **type 2, a source's own rule:** stop when the interval is at most `xtol` wide, and return an interval bound.

A solver uses the stopping rule of the highest-ranked source whose rule guarantees `xtol`, after translating `xtol` into that rule's own tolerance. When no source has such a rule, the solver uses the framework's rule, which counts as source IV.

A type-2 rule can cost 1 evaluation more for the same guarantee; that difference is accepted, because comparing the solvers' evaluation or flop counts is not sunnbear's main goal.

Following the source comes first: reaching `xtol` never justifies changing an algorithm fundamentally. An open method cannot guarantee `xtol`, and keeps its source's rule.

## Variants

**P9. A variant exists where alternative sources for an aspect behave sufficiently differently**, such as 2 third-party implementations with different stopping rules. Adding a variant is a judgment call, and the config's docstring states its reason. Variants of 1 algorithm are configs of 1 class.

Which variant is core is not a judgment call: the core config, with role `SolverRole.BUILTIN_CORE`, is selected by P1 to P8, and every other config is `SolverRole.BUILTIN_SECONDARY`.

## How the solver classes are built

These rules follow from P3 and P6: the flop counts must show the published algorithm, and a reader must be able to compare a solver with its source step by step.

- **Each solver class holds its whole algorithm**, even where 2 solvers differ in few details, as `RegulaFalsi` and `Illinois` do. A base class shared by such a family would add branches, and possibly flops, that the published algorithms do not have.
- **Each solver keeps its source's variable names and symbols**, and writes 1 long method where helpers would break the step-by-step match with the source.
- **Duplication across solvers is accepted**, for solver classes, state classes, tests and twin tests alike. Code reviews that ask to merge near-duplicate solver code are answered by this section.
- **Only the framework in `core` is shared**, such as `Solver` and `SolveState`; no part of it belongs to a published algorithm.
