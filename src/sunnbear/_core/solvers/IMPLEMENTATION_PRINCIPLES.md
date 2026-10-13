# Solver implementation principles

**These principles are a draft, a work in progress.** Not every solver follows them.

These principles decide how each of sunnbear's solvers implements its published method:

- which source it follows;
- how it is validated;
- how the iteration expressions are implemented;
- what stopping criterion is used.

The principles are general decisions that every solver follows, so that no solver gets an ad-hoc decision of its own that is inconsistent with the other solvers.

Each principle has an ID, such as P1 or P6, so that a docstring or a test can cite it.

## The sunnbear solver suite

sunnbear has solvers for 2 reasons:

- to characterize test functions objectively;
- to illustrate that sunnbear can reveal individual characteristics, strengths and weaknesses of solvers.

The implementations of these solvers need to be faithful enough to give a representative quantification of their properties, with the ultimate goal of illustrating the benchmark suite's capabilities, not the solvers'. This justifies, but at the same time limits, the effort spent on aligning implementation details between solvers.

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

Where 2 sources of the same rank, such as 2 third-party implementations, state an aspect differently and both pass validation, the choice is a judgment call that favors the most widely used implementation in the Python ecosystem, such as SciPy's, because of its install base.

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
- **B** — a third party's published numerical results for the method. They rank after A and never outweigh it, because a third party may make its own implementation decisions, which its paper does not always state;
- **C** — behavioral parity with a reference implementation from source II or III, through a twin test, which runs the reference implementation as a `Solver` and checks that both evaluate the same x-values.

Where a solver's results cannot be reconciled with published results, its test package states so explicitly, with the observed deviations and an explanation where one is available.

**P5. A reproduction of published numerical results is convincing** when it:

- is exact;
- or deviates only where each deviation has a reasonable explanation:
  - a stated cause, such as a known difference in computational precision or platform;
  - an experimental difference, such as a relative tolerance in the published run, where sunnbear supports only an absolute tolerance;
  - a deviation small enough, such as 1 iteration in a limited number of cases, to come from implementation details of the published run that the authors do not state, or from differences between math libraries.

A deviation without such an explanation is not convincing. Whether a reproduction is convincing is judged case by case, for A and B alike.

The tests mark a deviation of the last kind with `UNSTATED_RUN_DETAILS` and a short observation; an unverified cause is never stated as fact.

## Detailed math implementation

Even when the math of a solver is conceptually clear, there can be different ways to implement it in code. These details matter, because they can influence:

- numerical robustness, and with it convergence and iteration counts;
- computational efficiency, which sunnbear also measures, through the counted-float package.

This section gives the principles behind these micro-decisions.

**P6. A solver computes each formula as its source for that step writes it**, because sunnbear's flop counts should show the published algorithm. Forms that are equal in exact arithmetic can round differently and count different flops.

These kinds of change leave the published algorithm intact and are allowed without a declaration:

- **an exactly equal cheaper operation**, such as `0.5 * x` for `x / 2`;
- **computing a repeated value once:** when the source computes a value several times, in the same or nearly the same form, the solver computes it once, in 1 extra assignment or by moving the formula to an earlier or later step;
- **short-circuit evaluation:** a condition that combines comparisons with Python's `and` or `or` skips the later comparisons once the earlier ones decide it, even where the source's language, such as Algol 60, evaluates them all. Skipping them changes no result, because the comparisons have no side effects.
- **sign tests that compare signs:** a test whether 2 function values differ in sign compares their signs explicitly, even where the source writes a product such as `fa * fb < 0`, because in float64 the product of 2 small values can underflow to 0. This holds as long as the product is not needed for another step.

A solver does not restructure a formula algebraically to save flops. Where it is unclear whether a change is allowed, the solver keeps the source's form. Any other change of form needs a good reason under P2, and the class docstring states that reason: the published results reproduce better with it, or the published form fails in float64.

## Stopping

**P7. Each solver translates sunnbear's absolute tolerance `xtol` into the formulation of its own stopping rule**, such as a relative tolerance or a tolerance on the function value, and its class docstring states how.

## Variants

**P8. A solver can have variants where an implementation decision causes fundamentally different behavior**, for didactic reasons:

- at most 1 variant is core, with role `SolverRole.BUILTIN_CORE`; the other variants are secondary, with role `SolverRole.BUILTIN_SECONDARY`;
- the principles apply strictly only to the core variant. A secondary variant is provided for information and may deviate from them, but it states every deviation.

## How the solver classes are built

These rules follow from P3 and P6: the flop counts must show the published algorithm, and a reader must be able to compare a solver with its source step by step.

- **Each solver class holds its whole algorithm**, even where 2 solvers differ in few details, as `RegulaFalsi` and `Illinois` do. A base class shared by such a family would add branches, and possibly flops, that the published algorithms do not have.
- **Variants of 1 algorithm, such as different values of 1 of its parameters, are configs of 1 class.**
- **Each solver keeps its source's variable names and symbols**, and writes 1 long method where helpers would break the step-by-step match with the source.
- **Duplication across solvers is accepted**, for solver classes, state classes, tests and twin tests alike. Code reviews that ask to merge near-duplicate solver code are answered by this section.
- **Only the framework in `core` is shared**, such as `Solver` and `SolveState`; no part of it belongs to a published algorithm.
