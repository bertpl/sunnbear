# Solver implementations

## I. Introduction

### I.a. Goals

The core mission of `sunnbear` is to provide a **fully transparent benchmarking system** for univariate root-finding algorithms based on an extensive, **curated suite of test problems**.  Actual solver implementations are not _directly_ part of the value proposition.

Actual solver implementations in `sunnbear` still play a critical role in achieving the following 2 goals:
1. Show that **`sunnbear` can surface differences** in fundamental characteristics, strengths and weaknesses of root-finding algorithms.
2. Provide an objective, empirical path to **establish how difficult test problems are** for a representative set of known solvers.

An explicit non-goal of `sunnbear` is to establish which existing algorithm 'is best' or 'wins'.

### I.b. Reproducibility

A **core principle of the scientific approach is reproducibility** of results.  This allows peer scientists to vet the results for correctness (peer review) and in general allows others to build further research on the results.

Some domains have inherent challenges in this area (e.g., non-exact sciences or studies that involve exceptionally expensive equipment), but numerical algorithms and especially **root-finding algorithms seem well-suited**: digitally shareable, self-contained algorithms that can run on essentially any off-the-shelf computer.

However, reproducing results can be challenging.  **Out of the 11 solvers** in section II that have a reference, the references of...
- **5** publish no code of the method, neither in the article nor as a separate download
- **3** give evaluation counts for fewer than 10 runs of the method
- **5** contain apparent typos in the algorithm description
- **2** state that their experiments ran on a machine without IEEE 754 (64-bit) floating point
- **1** publishes results that reproduce only with a detail that the article leaves out
- **4** print a test problem that does not reproduce their own published results

These counts are a lower bound: an article counts only where the evidence ties a discrepancy to 1 of the causes above, and every discrepancy whose cause we could not establish is left out.

### I.c. Implementation Approach

Due to the goals of section I.a and the challenges of section I.b, we...
- aim to implement root-finding algorithms on a best-effort basis to reproduce available results to the extent possible
- let the effort be guided by the level of detail needed to achieve the aforementioned goals
- standardize a few common elements (section IV) to ensure results are comparable and reflect each solver's fundamental characteristics without being influenced by minor implementation differences

## II. Solvers Overview

The `sunnbear` package implements **14 solver algorithms**, several provided in different flavors and settings, totaling **19 solver configurations**.

| Algorithm | Type | Configs | core config? | Year | Reference |
| --------- | ---- | ------- | ------------ | ---- | --------- |
| `Bisection` | bracketing | 1 | | – | – |
| `RegulaFalsi` | bracketing | 1 | | – | – |
| `Secant` | open | 1 | | – | – |
| `Brent` | bracketing | 1 | ✓ | 1971 | Brent (1971, 1973) |
| `Illinois` | bracketing | 1 | ✓ | 1971 | Dowell and Jarratt (1971) |
| `Pegasus` | bracketing | 1 | | 1972 | Dowell and Jarratt (1972) |
| `AndersonBjorck` | bracketing | 1 | | 1973 | Anderson and Björck (1973) |
| `Ridders` | bracketing | 3 | ✓ | 1979 | Ridders (1979) |
| `TOMS748` | bracketing | 2 | ✓ | 1995 | Alefeld, Potra and Shi (1995) |
| `Chandrupatla` | bracketing | 1 | ✓ | 1997 | Chandrupatla (1997) |
| `ITP` | bracketing | 3 | ✓ | 2020 | Oliveira and Takahashi (2020) |
| `SteffenBrent` | bracketing | 1 | | 2025 | Steffen et al. (2025) |
| `CARF` | bracketing | 1 | | 2026 | Gao (2026) |
| `ModAB` | bracketing | 1 | | 2026 | Ganchovski et al. (2026) |

The `core config?` column marks the algorithms that have a core config, which characterizes the test problems (section V).

## III. Overall Implementation Methodology

As section I.b shows, reproducing results can be challenging and not all sources are sufficiently 'complete'.

**Sources for implementation**, roughly in descending order of precedence:
1. the original article (code, pseudo-code, algorithm descriptions)
2. additional materials provided by the authors (downloads, or code shared on request)
3. 3rd party implementations, prioritizing implementations with a broad install base
4. own judgment

**Sources for validation**:
1. the original article (iteration & function evaluation counts, obtained roots, ...)
2. numerical comparison results provided by other articles or books
3. comparison against 3rd party implementations

**Notes:**
- some cases might require a combination of sources where any single source might not suffice for reproducibility
- the aforementioned order of precedence is indicative and can require judgment in cases where there are apparent problems (typos, inaccurate test problem description, etc.)
- the docstring of each solver class provides full transparency on which sources are used
- for consistency and comparability of results, certain shared implementation elements are implemented in a way that can deviate from the original formulation, as stated in section IV

## IV. Shared Implementation Choices

Inevitably, each author of a numerical algorithm makes a series of micro-decisions on how to turn the algorithm's mathematical formulas into code (order of operations, numerical tolerances, ...). The page limits of scientific articles rarely leave room for these details, so authors often fall back on the formulations in exact arithmetic.

Where an article _does_ state such details, they can still deviate from other authors' choices without constituting a fundamental difference in the algorithms' strategies.

For these reasons, the `sunnbear` implementations of the solver algorithms standardize a few recurring elements, for consistency and comparability, in line with the goals and non-goals of section I.a; section V describes the configs that deviate from these shared choices.

### IV.a. Stopping Criterion & Return Value

Some articles do not state an explicit stopping criterion (Ridders (1979): "The procedure can be terminated when a given accuracy is obtained."), others use different flavors of the same concept:
- distance between mid-point and bracket endpoint < xtol
- bracket width < 2*xtol, or < an absolute plus a relative tolerance (Brent, TOMS748, Chandrupatla, ModAB)
- step between 2 successive iterates < a tolerance (Dowell and Jarratt's ALGOL procedure for Illinois)
- |f| below a threshold (Dowell and Jarratt's tables; combined with a width test by Steffen et al. and Gao)
- variants with some numerical rounding tolerance

The returned x-value differs as well: the midpoint, the bound with the smaller |f|, or an iterate that is never evaluated.

Moreover, `sunnbear` supports only an absolute tolerance on x (`xtol`), no relative tolerances and no tolerances on f, so each solver's stopping criterion has to be expressed in terms of `xtol` alone. Therefore the stopping criterion is the primary candidate to be standardized.

#### IV.a.1. Open solvers

`Secant` is the only open solver `sunnbear` implements.  For this specific case, we follow the error test that Atkinson (1989) recommends for the secant method, which uses the step between 2 successive iterates as an estimate of the older iterate's error:
- a solve ends once the step from the newest x-value to the next secant iterate is at most `xtol`
- it then returns that next iterate, without evaluating it; near a simple root, the secant method converges superlinearly, so that iterate typically lies well within `xtol` of the root
- the test gives no guarantee: an open method keeps no interval around the root, so a step can also be small far from a root, e.g. where `f` is nearly flat

A stopping criterion that also estimates the convergence rate from the last 3 iterates (Aitken's error formula, Atkinson (1989), section 2.6) would stop about 1 evaluation earlier, but it assumes linear convergence and can stop too early after an irregular secant step.

#### IV.a.2. Bracketing algorithms

All bracketing solvers follow 3 rules, apart from the secondary configs that section V lists as not following section IV:

1. **A shared stopping criterion and return value.** At each point where a solver's source checks its own stopping criterion, a solve ends once the interval is at most `2*xtol` wide, or once the function value at an interval bound is exactly 0. It returns that bound, or else the interval's midpoint, which then lies within `xtol` of a root.
   - This is the least strict stopping criterion that still guarantees a result within `xtol` from the interval alone. A source's own stopping criterion with the same guarantee stops at the same width or a narrower one: a stopping criterion that returns an interval bound needs the interval at most `xtol` wide. So the shared stopping criterion never costs a solver an evaluation over its source's own.
   - Stopping criteria on `|f|`, or on the step between 2 iterates, can stop earlier, but they give no guarantee on the distance to a root. The benchmark scores a result farther than `xtol` from a root with a fixed high evaluation count, `max_fevals`.
   - The rule standardizes what a solve checks, not how often: each solver checks at the points where its source checks its own stopping criterion. Most sources check once per iteration; the code of Alefeld, Potra and Shi (1995), the source of `TOMS748`, checks after every step, and each `TOMS748` iteration takes several steps.
   - Ridders (1979) states no stopping criterion, so `Ridders` checks where SciPy's `ridder` does (section V.a). `Bisection` and `RegulaFalsi` have no reference, and check once per iteration.
2. **Tolerances inside the steps are kept, with their value derived from `xtol`.** Several sources keep each new x-value at least some distance away from the interval bounds or from the previous iterate (a minimum step, or a margin), so that the interval shrinks to the stopping width once the method has converged.
   - Each source sizes that distance for its own stopping criterion. The `sunnbear` solver implementations derive it from `xtol` such that it is about `xtol`, half the shared stopping width.
   - A final step past the root then leaves an interval narrower than `2*xtol`, which ends the solve with room for rounding.
   - No step can land on the far bound, because the interval stays wider than `2*xtol` while the solve continues.
3. **Machine-precision terms are dropped from the stopping criterion, but kept inside the steps; relative tolerances are 0.**
   - In a stopping criterion, a machine-precision term, such as `2*macheps*|b|` in `Brent`'s tolerance, lets a solve end even when `xtol` lies below the float spacing near the root. The benchmark never sets such an `xtol`: it keeps `xtol` above a multiple of the float spacing at the interval bounds (`compute_xtol_range`).
   - Inside a step, such a term still guards against rounding, as its source intends.
   - Each source leaves the value of a relative tolerance, such as `Chandrupatla`'s `ε_R` or `ModAB`'s `rTol`, to its caller. `sunnbear` supports only the absolute tolerance `xtol` (section IV.a), so every relative tolerance is 0, in the stopping criterion and inside the steps.

The table lists what each source states, and what the `sunnbear` solver implementations keep besides the shared stopping criterion and return value.

| Algorithm | Source's stopping criterion | Source's returned x-value | Kept inside the steps |
| --------- | --------------------------- | ------------------------- | --------------------- |
| `Brent` | half-width ≤ `tol`, or `f(b) = 0`, with `tol = 2*macheps*\|b\| + t` | `b`, the bound with the smaller `\|f\|` | minimum step `tol`, with `t = xtol` |
| `Illinois` | ALGOL: step ≤ `delta`; tables: `\|f\| < 0.5e-19` | ALGOL: the next secant's zero, not evaluated | – |
| `Pegasus` | none; experiments: `\|f\|` below a threshold | not stated | – |
| `AndersonBjorck` | `\|x1 - x0\| < δ`, or `f = 0` | the bound with the smaller `\|f\|` | step of `δ`, with `δ = xtol` |
| `Ridders` | none | not stated | – |
| `TOMS748` | width ≤ `2*tole`, with `tole = 2*macheps*\|u\| + tol` | not stated | every new x-value kept `0.7*(2*tole)` inside the interval, with `tol = xtol` |
| `Chandrupatla` | half-width < `TOL`, or `f = 0`, with `TOL = 2*ε_R*\|x\| + 0.5*ε_A` | the bound with the smaller `\|f\|` | distance `TOL` from the interval bounds, with `ε_A = 2*xtol` and `ε_R = 0` |
| `ITP` | width ≤ `2ε` | the midpoint | projection radius, which bounds how far each step may lie from the midpoint, with `ε = xtol` |
| `SteffenBrent` | width ≤ `tol1`, or `\|f(b)\|` ≤ `tol2` | `b` | – |
| `CARF` | `\|f\| < ε1`, or width < `ε2 + \|t\|*ε1` | not stated | – |
| `ModAB` | width ≤ `aTol + rTol*\|x3\|`, or `f = 0` | the next iterate, not evaluated | – (it clamps each new iterate into the interval, without a tolerance) |

`Bisection` and `RegulaFalsi` have no reference; they follow the shared stopping criterion and return value as they are.

### IV.b. Iteration Formula

Each solver computes its steps in the form of its source, the secant's zero and its own midpoints included. Forms that are equal in exact arithmetic round differently, but that rounding moves an evaluation count by about 1 near a stop, favors no solver, and is part of each source's method as published; a source's form also keeps its failures in float64, such as an overflow of `a*fb`.

A step may be rewritten only where the rewrite gives the same x-value in float64, bit for bit, and only to drop operations that an expert would not write, such as `0.5*(a + b)` for `(a + b) / 2`, or a ratio computed once that a source computes twice. For example, `SteffenBrent` and `ModAB` multiply their midpoints by 0.5, and `Secant` computes SciPy's ratio of the 2 function values once.

The midpoint that the shared stopping criterion returns (section IV.a.2) is `0.5*(a + b)` for every solver: it belongs to the stopping criterion, not to a solver's steps.

## V. Solver Configurations

Some solvers are provided in multiple configurations, which might differ in their parameters or in certain implementation details (such as the stopping criterion).

Each config has 1 of 3 roles:
- **core:** the config characterizes the test problems.
- **secondary:** the config is reported for information only.
- **baseline:** only `BisectionConfig` has this role; its evaluation count normalizes the other solvers' evaluation counts.

Only a secondary config may deviate from section IV.

| Algorithm | Config | Role | Differs in | Follows section IV |
| --------- | ------ | ---- | ---------- | ------------------ |
| `Ridders` | `RiddersStandardStoppingCriterionConfig` | core | Ridders' steps, as the article states them | yes |
| | `RiddersScipyConfig` | secondary | SciPy's step limit and stopping criterion | no: SciPy's stopping criterion |
| | `RiddersCommonsMathConfig` | secondary | Apache Commons Math's stopping criterion | no: Commons Math's stopping criterion |
| `TOMS748` | `TOMS748K2Config` | core | `k = 2`, the article's Algorithm 4.2 | yes |
| | `TOMS748K1Config` | secondary | `k = 1`, the article's Algorithm 4.1 | yes |
| `ITP` | `ITPPaperExperimentsSlack0Config` | core | the projection radius of the authors' code, `n_slack = 0` | yes |
| | `ITPPaperPseudocodeSlack0Config` | secondary | the projection radius of the article's pseudocode, `n_slack = 0` | yes |
| | `ITPPaperExperimentsSlack4Config` | secondary | the projection radius of the authors' code, `n_slack = 4` | yes |

### V.a. Ridders

Ridders (1979) states no stopping criterion, so the core config fills that gap with the shared stopping criterion of section IV.a. The 2 secondary configs show the stopping criteria of 2 widely used implementations:
- **`RiddersStandardStoppingCriterionConfig` (core):** Ridders' steps as the article states them, with the shared stopping criterion.
  - It checks that criterion where SciPy's `ridder` checks its own: right after evaluating the midpoint, it checks for a function value of 0, and after evaluating the new iterate, it checks the whole criterion.
  - Near the root, a new iterate can land between the root and the far bound, and the interval then only halves, so this config's evaluation counts can vary between near-identical functions.
- **`RiddersScipyConfig` (secondary):** SciPy's `ridder`. It limits each step so that the new iterate lies at least `xtol/2` inside the interval, which the article does not state; near the root, that limit shrinks the interval to the stopping width in fewer evaluations. It stops once the interval is narrower than `xtol`, and returns the last iterate.
- **`RiddersCommonsMathConfig` (secondary):** the stopping criterion of Apache Commons Math's `RiddersSolver`: it stops once 2 successive iterates lie at most `xtol` apart, and returns the last one. That iterate can lie more than `xtol` from a root, as on a function with a kink or with a multiple root.

### V.b. TOMS748

Alefeld, Potra and Shi (1995) publish 2 algorithms, which differ only in `k`, the number of interpolation steps in each iteration. Both configs follow section IV, so `k` is their only difference:
- **`TOMS748K2Config` (core):** `k = 2`, Algorithm 4.2. The authors' published code implements only this algorithm, and the article's Table II reports fewer evaluations for it than for Algorithm 4.1.
- **`TOMS748K1Config` (secondary):** `k = 1`, Algorithm 4.1, the default of SciPy's `toms748`.

### V.c. ITP

The 3 configs follow section IV, and differ in 2 settings: the projection radius `r`, and `n_slack`, the number of iterations that `ITP` may take beyond bisection's:
- **`ITPPaperExperimentsSlack0Config` (core):** the settings of the article's experiments and of the authors' code, with `n_slack = 0`. The authors' code lowers the article's projection radius to `max(0.99*r - xtol/2, 0)`, a margin against rounding; with it, the config reproduces 23 of the 24 evaluation counts of the article's Table 1.
- **`ITPPaperPseudocodeSlack0Config` (secondary):** the article's pseudocode as printed, without that margin, which reproduces 17 of the 24 counts. It shows what the margin buys: without it, rounding takes solves past the iteration bound of `ITP` more often.
- **`ITPPaperExperimentsSlack4Config` (secondary):** the core config with `n_slack = 4`: about 10 % slack on the 40 evaluations of bisection at `n_bisection_fevals = 40`, the largest value that the benchmark uses. No source states a value; 4 is meant as a neutral value larger than 1, to show what extra slack buys, and that rounding can still take a solve 1 iteration past its bound.

## VI. Code Organization & Validation

### VI.a. Solver Classes

A reader must be able to compare each solver with its source step by step:
- **each solver class holds its whole algorithm**, even where 2 solvers differ in few details, as `RegulaFalsi` and `Illinois` do
- **variants of 1 algorithm**, such as different values of 1 of its parameters, **are configs of 1 class** (section V)
- **each solver keeps its source's variable names and symbols**, and writes 1 long method where splitting it into helpers would make it harder to compare with its source
- **duplication across solvers is accepted**, for solver classes, state classes and tests alike; code reviews that ask to merge near-duplicate solver code are answered by this section
- **only the framework in `core` is shared**, such as `Solver`, `SolveState`, and the code that implements the shared choices of section IV

### VI.b. Validation & Provenance

The tests compare each solver with the published results and reference implementations of section III, to check that it implements its method's steps correctly:
- **a published table that depends on its article's own stopping criterion** is checked against a subclass of the solver that replaces the shared stopping criterion with the article's; that subclass lives in the solver's test package
- **the docstring of each solver's test package** lists, each with its reason: the published results and reference implementations used for comparison, the allowed deviations, and the published results not used
- **the `References:` section of each solver's class docstring** cites every source used for the implementation or the validation, with 1 line on what each source provides; the class docstring states each deviation from its sources in 1 bullet

## VII. References

- **Alefeld, G. E., Potra, F. A. and Shi, Y. (1995)**. Algorithm 748: Enclosing zeros of continuous functions. ACM Transactions on Mathematical Software 21(3), 327–344. https://doi.org/10.1145/210089.210111
- **Anderson, N. and Björck, Å. (1973)**. A new high order method of regula falsi type for computing a root of an equation. BIT 13(3), 253–264. https://doi.org/10.1007/BF01951936
- **Atkinson, K. E. (1989)**. An Introduction to Numerical Analysis, 2nd edition. John Wiley & Sons, New York. Section 2.3 (the secant method and its error test) and section 2.6 (Aitken's error formula).
- **Brent, R. P. (1971)**. An algorithm with guaranteed convergence for finding a zero of a function. The Computer Journal 14(4), 422–425. https://doi.org/10.1093/comjnl/14.4.422
- **Brent, R. P. (1973)**. Algorithms for Minimization without Derivatives. Prentice-Hall, Englewood Cliffs, New Jersey. A scan is available on the author's page: https://maths-people.anu.edu.au/~brent/pub/pub011.html
- **Chandrupatla, T. R. (1997)**. A new hybrid quadratic/bisection algorithm for finding the zero of a nonlinear function without using derivatives. Advances in Engineering Software 28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8
- **Dowell, M. and Jarratt, P. (1971)**. A modified regula falsi method for computing the root of an equation. BIT 11(2), 168–174. https://doi.org/10.1007/BF01934364
- **Dowell, M. and Jarratt, P. (1972)**. The "Pegasus" method for computing the root of an equation. BIT 12(4), 503–508. https://doi.org/10.1007/BF01932959
- **Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026)**. Improvements to the modified Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. https://doi.org/10.3390/a19050332
- **Gao, F. (2026)**. Fast and stable root-finding using clipped power interpolations. Applied Mathematics Letters 178, 109928. https://doi.org/10.1016/j.aml.2026.109928
- **Oliveira, I. F. D. and Takahashi, R. H. C. (2020)**. An enhancement of the bisection method average performance preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), Article 5. https://doi.org/10.1145/3423597
- **Ridders, C. J. F. (1979)**. A new algorithm for computing a single root of a real continuous function. IEEE Transactions on Circuits and Systems 26(11), 979–980. https://doi.org/10.1109/TCS.1979.1084580
- **Steffen, V., Della Pasqua, C. C., de Oliveira, M. S. and da Silva, E. A. (2025)**. Halving interval guaranteed for Dekker and Brent root finding methods. Examples and Counterexamples 7, 100173. https://doi.org/10.1016/j.exco.2024.100173
