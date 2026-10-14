# Solver implementation principles

**These principles are a draft, a work in progress.** Not every solver follows them.

These principles decide how each of sunnbear's solvers implements its published method:

- which source it follows;
- how it is validated;
- how the iteration expressions are implemented;
- what stopping criterion is used.

The principles are general decisions that every solver follows, so that no solver gets an ad-hoc decision of its own that is inconsistent with the other solvers.

These principles cannot cover every detail and corner case. Where they leave a minor gap or a small judgment call, the solver's record makes the call case by case and marks it `JUDGMENT-CALL`, for transparency.

Each principle has an ID, such as P1 or P6, so that a docstring or a test can cite it.

## The sunnbear solver suite

sunnbear has solvers for 2 reasons:

- to characterize test functions objectively;
- to illustrate that sunnbear can reveal individual characteristics, strengths and weaknesses of solvers.

The implementations of these solvers need to be faithful enough to give a representative quantification of their properties, with the ultimate goal of illustrating the benchmark suite's capabilities, not the solvers'. This justifies, but at the same time limits, the effort spent on aligning implementation details between solvers.

## Sources

**P1. Each aspect of a solver, such as its step formula, a safeguard or its stopping rule, follows the highest source that states it completely and unambiguously.** The sources rank as follows, highest preference first; a record and a docstring name each rank by its numeral and its name, such as "III - third party":

- **I - article**: the article that published the method. Its own content ranks above any other source. Within it:
  - **Ia - article code**: a code listing printed in the article;
  - **Ib - article pseudocode**: pseudocode printed in the article;
  - **Ic - article text**: the article's prose and equations.

  Code ranks above pseudocode, because it is likely closer to the authors' experimental code.
- **II - authors' code**: the authors' own code outside the article, such as a repository, a supplement, or code sent on request;
- **III - third party**: other publicly available third-party implementations; a textbook's description and its tables count here, so the sources of a method without an original article start at this rank;
- **IV - own judgment**: sunnbear's own interpretation or choice, for an aspect that no source states, or that every source states in a form that fails its validation (P4, P5).

Where 2 sources of the same rank, such as 2 third-party implementations, state an aspect differently and both pass validation, the choice is a judgment call that favors the most widely used implementation in the Python ecosystem, such as SciPy's, because of its install base.

A source can state some aspects completely and leave others out, or state them ambiguously. So the choice is made per aspect.

**P2. A solver uses the next-ranked source for an aspect only for a reason.** The valid reasons are:

- the current source does not state the aspect completely and unambiguously;
- the solver's validation with the current source is not convincing (P5);
- there is a good reason to deviate, such as a formula whose published form fails in float64.

Without a good reason, a solver does not deviate from its article.

**P3. Each solver's module docstring declares every deviation** from the source that P1 ranks highest for that aspect.

## Validation

**P4. A solver is validated by the strongest kind of evidence that exists**, highest first; a record names each kind by its letter and its name, such as "B - third-party results":

- **A - authors' results**: numerical results in the authors' own article;
- **B - third-party results**: a third party's published numerical results for the method. They rank after A and never outweigh it, because a third party may make its own implementation decisions, which its paper does not always state;
- **C - reference implementation**: behavioral parity with a reference implementation from II - authors' code or III - third party, through a twin test, which runs the reference implementation as a `Solver` and checks that both evaluate the same x-values.

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

A solver does not restructure a formula algebraically to save flops. Where it is unclear whether a change is allowed, the solver keeps the source's form. Any other change of form needs a good reason under P2, and the module docstring states that reason: the published results reproduce better with it, or the published form fails in float64.

## Stopping

**P7. Each solver translates sunnbear's absolute tolerance `xtol` into the formulation of its own stopping rule**, such as a relative tolerance or a tolerance on the function value, and its module docstring states how.

## Variants

**P8. A solver can have variants where an implementation decision causes fundamentally different behavior**, for didactic reasons:

- at most 1 variant is core, with role `SolverRole.BUILTIN_CORE`; the other variants are secondary, with role `SolverRole.BUILTIN_SECONDARY`;
- the principles apply strictly only to the core variant. A secondary variant is provided for information and may deviate from them, but it states every deviation;
- the baseline, with role `SolverRole.BUILTIN_BASELINE`, follows the principles as strictly as a core variant.

## How the solver classes are built

These rules follow from P3 and P6: the flop counts must show the published algorithm, and a reader must be able to compare a solver with its source step by step.

- **Each solver class holds its whole algorithm**, even where 2 solvers differ in few details, as `RegulaFalsi` and `Illinois` do. A base class shared by such a family would add branches, and possibly flops, that the published algorithms do not have.
- **Variants of 1 algorithm, such as different values of 1 of its parameters, are configs of 1 class.**
- **Each solver keeps its source's variable names and symbols**, and writes 1 long method where helpers would break the step-by-step match with the source.
- **Duplication across solvers is accepted**, for solver classes, state classes, tests and twin tests alike. Code reviews that ask to merge near-duplicate solver code are answered by this section.
- **Only the framework in `core` is shared**, such as `Solver` and `SolveState`; no part of it belongs to a published algorithm.

## Each solver's record

**The module docstring of each solver's `solver.py` is that solver's record: it states how these principles apply to the solver.**

The reasons why a solver follows each of its sources are stated nowhere else, so the record keeps them next to the code, and a change of principle is checked against each record.

**A record names the source that the solver follows by default, then lists only the exceptions, each in a line or 2.** A reader skims it for what departs from that source; the code and the tests hold the details.

**A solver's record, the module docstring of its `solver.py`, uses the terms of this file without explaining them:**

- the rank labels of P1 and the kind labels of P4;
- the principle IDs;
- the 3 keywords, defined below.

Each record links back to this file in its opening lines, so a reader finds the definitions here.

Code reviews that ask a record to define these terms, or to say more about an exception than its choice, reason and effect, are answered by this section.

A record is read as plain text, since API documentation does not render the docstring of a private module, so its nested bullets follow their parent bullet without a blank line.

The record has 4 sections, each a heading of the docstring:

- **`Sources:`** lists each rank of P1 with its sources as bullets underneath, by author and year where they have them, and what each states. A rank without a source lists "none".
- **`Source per aspect:`** opens with the source that every aspect follows by default, then gives 1 bullet per exception. An exception is an aspect that follows another source, a deviation (P3), or a case marked with 1 of the keywords below. The aspects are:
  - the step formula;
  - the safeguards;
  - the constants;
  - the stopping rule;
  - the arithmetic form (P6);
  - the translation of `xtol` (P7).

  An exception states the choice, its reason and its effect, such as "the evaluation count differs by 1 in about 1 in 7,000 solves". The reason is 1 of those that P1 and P2 give:
  - the default source does not state the aspect, or states it incompletely or ambiguously;
  - the solver's validation with the default source is not convincing (P5);
  - a good reason to deviate, which the exception states (P2);
  - P1's preference among sources of the same rank, or a judgment call between them.

  A last bullet states how the solver translates `xtol` (P7).
- **`Validation:`** lists each kind of evidence in P4 with its answers as bullets underneath:
  - used, with the evidence and whether it is convincing (P5);
  - none exists;
  - not used, with the reason;
  - `TBD:`, for evidence that no test checks yet but that could validate the solver further, with what a comparison shows today, or that none was made yet.

  The docstring of the solver's test package gives the details of each published table.
- **`Variants:`** gives 1 line per config, with its role (P8), and for a secondary variant, its deviations from the principles.

**The class docstring describes what the algorithm does, and its `References:` gives the full citation of every source that the record names.** API documentation renders the docstring of the public class, not the docstring of its private module, so the full citations go in the class docstring.

A test checks that every author and year that a record's `Sources:` names appears in the class's `References:`.

**The record marks each disagreement between a solver and the principles, and each judgment call, with 1 of 3 keywords.** Each keyword starts an exception bullet, so that `grep -rnE "PRINCIPLE-(CONFLICT|GAP)|JUDGMENT-CALL" src/` lists all of them:

- **`PRINCIPLE-CONFLICT (Pn)`**: the solver breaks principle Pn. The bullet says how, and what would resolve the conflict.
- **`PRINCIPLE-GAP (Pn)`**: Pn does not decide the case, because it is silent or ambiguous. The bullet says what is undecided, and which choice the code makes.
- **`JUDGMENT-CALL`**: the principles leave a minor gap or a small judgment call, which the record makes for this solver. The bullet says which choice the code makes, why, and its effect.

A record flags a conflict and does not resolve it; resolving it is a change of its own, made under these principles.
