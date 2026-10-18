# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

### Changed

- Require max-div ≥ 0.21.8
- Measure every statistic of `MCTuplesStats` cyclically, with each axis as a circle on which 0 and 1 meet, which changes their values
- Improve the cyclic spread statistics of the tuple sets that `generate_mc_tuples` builds; each size no longer spans the full range of u and of v

### Deprecated

### Removed

### Fixed

### Security

## 0.2.9 (2026-10-18)

### Changed

- Declare solver configs in 1 `SolverConfigsDeclaration` subclass per solver class, which lists the configs as `SolverConfig` values
- Rename the `"bracketing_solver"` variant of `Ridders` to `"standard_stopping_criterion"`
- Stop `Brent`, `Chandrupatla`, `TOMS748`, `AndersonBjorck`, `SteffenBrent`, `ModAB` and `CARF` once the interval is at most `2*xtol` wide and return its midpoint, as `Bisection` does, which changes their benchmark results
- Make the `"standard_stopping_criterion"` variant the core config of `Ridders`, which changes the benchmark results of `Ridders`

### Fixed

- Fix `CARF` ending a solve as `SOLVER_ERROR` on functions with tiny values near the root, such as `x^19`, which also changes some benchmark results of `CARF`
- Fix trivially inefficient floating-point operations in `Secant`, `SteffenBrent` and `ModAB`, with results staying bit-identical

## 0.2.8 (2026-10-14)

### Changed

- Require counted-float ≥ 2.8.0
- Rebuild the shipped Monte Carlo tuple set with improved spread statistics; benchmark results on it differ from those on the previous set

## 0.2.7 (2026-10-13)

### Changed

- Raise a `ValueError` in `compute_xtol_range` when the interval lies too far from 0 for its width
- Make the flop counts of `ITP` consistent with its published algorithm
- Change the midpoint that `SteffenBrent` evaluates to the one that reproduces the iterates published by Steffen et al., which changes the benchmark results of `SteffenBrent`

## 0.2.6 (2026-10-13)

### Added

- Add `MCTuples.bit_stats()`, which reports how many bits of information the u values and the v values of a tuple set hold

### Changed

- Make every u value and v value of the tuple sets that `generate_mc_tuples` builds hold at least 50 bits of information, as `MCTuples.bit_stats()` measures them
- Make each size of the tuple sets that `generate_mc_tuples` builds span the full range of u and of v, to within 1/1024 at each end
- Improve the spread statistics of the tuple sets that `generate_mc_tuples` builds
- Rebuild the shipped Monte Carlo tuple set with improved spread statistics; benchmark results on it differ from those on the previous set

## 0.2.5 (2026-10-12)

### Added

- Add the `n_refinement_random_candidates_per_cell` argument to `generate_mc_tuples`

### Changed

- Compute the steps of `Illinois`, `Pegasus` and `AndersonBjorck` as their papers state them, which changes their benchmark results
- Stop `AndersonBjorck` by the stopping rule of its paper, which changes its root estimates and benchmark results
- Make `TOMS748` with `k = 2` and `ITP` with `n_slack = 0` and `variant="paper_experiments"` the core configs of their solvers, which changes how the benchmark characterizes the test functions
- Improve the spread statistics of the tuple sets that `generate_mc_tuples` builds

## 0.2.4 (2026-10-11)

### Changed

- Improve the spread statistics of the tuple sets that `generate_mc_tuples` builds
- Draw each size's `n_population` candidate tuples in `generate_mc_tuples` only in the fine lanes where that size's new tuples can go, so that every candidate can be picked
- Rebuild the shipped Monte Carlo tuple set; benchmark results on it differ from those on the previous set

### Removed

- Remove the `allocation_epsilon` and `on_size_finished` arguments of `generate_mc_tuples`

## 0.2.3 (2026-10-10)

### Added

- Add support for Python 3.15

### Changed

- Rename the parameter of `Interval.is_converged` to `xtol_doubled`

## 0.2.2 (2026-10-09)

### Added

- Add the Illinois solver, `sunnbear.solvers.Illinois`
- Add the Ridders solver, `sunnbear.solvers.Ridders`
- Add the Brent solver, `sunnbear.solvers.Brent`
- Add the Chandrupatla solver, `sunnbear.solvers.Chandrupatla`
- Add the ITP solver, `sunnbear.solvers.ITP`
- Add the TOMS 748 solver, `sunnbear.solvers.TOMS748`
- Add the Pegasus solver, `sunnbear.solvers.Pegasus`
- Add the Anderson-Björck solver, `sunnbear.solvers.AndersonBjorck`
- Add the Secant solver, `sunnbear.solvers.Secant`
- Add the Steffen-Brent solver, `sunnbear.solvers.SteffenBrent`
- Add the modified Anderson-Björck (modAB) solver, `sunnbear.solvers.ModAB`
- Add the Curvature-Adaptive Root Finder (CARF) solver, `sunnbear.solvers.CARF`
- Add gpq(0.1) spread statistics and a `score` property that combines them to `MCTuplesStats`

### Changed

- Change the signature of `generate_mc_tuples`, and give every size of the tuple sets that it builds a mean u and a mean v of exactly 0.5
- Rebuild the shipped Monte Carlo tuple set; benchmark results on it differ from those on the previous set
- Require max-div ≥ 0.21.1

### Fixed

- Fix `gpq` returning NaN at levels very close to 0 or 1, and `owg` returning NaN at a very large |p|

## 0.2.1 (2026-10-05)

### Changed

- `generate_mc_tuples` builds tuple sets with improved spread statistics; its signature changed
- the shipped Monte Carlo tuple set is rebuilt with improved spread statistics; benchmark results on it differ from those on the previous set
- requires max-div ≥ 0.21.0

## 0.2.0 (2026-10-04)

### Added

- Benchmark runs and result summaries: `sunnbear.benchmark.run_benchmark`, `load_results`, `add_derived_results` and `summarize_results`

### Changed

- The enum `MCTuplesSize` replaces `MC_TUPLES_SIZES`
- The shipped Monte Carlo tuple set is rebuilt with improved spread statistics; benchmark results on it differ from those on the previous set
- `gpq` and `owg` are now more robust and accept a wider range of inputs

### Fixed

- A data artifact's manifest names the release that ships it

## 0.1.4 (2026-09-27)

### Added

- `sunnbear.benchmark.load_mc_tuples`: the shipped set of (u, v) tuples that Monte Carlo benchmarks sample from, nested across sizes 32–1024, with its spread statistics and `generate_mc_tuples` to regenerate an equivalent set within a given time

### Removed

- Support for Python 3.11; sunnbear now requires Python 3.12 or later

## 0.1.3 (2026-09-26)

### Added

- `sunnbear.data`: list the package's data artifacts and read their manifests (content hash, versions of the libraries that built them, and the sunnbear function call that generated them)

## 0.1.2 (2026-09-24)

### Changed

- Parameter values that are the same number are equal whatever their notation, and function ids show each value in its shortest notation, e.g. `2^2.0` as `4.0`

### Removed

- `ParamValue`, `DecimalParamValue` and `ExponentialParamValue`; parameter values are plain floats

## 0.1.1 (2026-09-23)

### Changed

- Formulas are numbered by their place in a category tree, e.g. `f2.1.1`; user formulas go under category 99
- Function ids name their parameters, e.g. `f2.1.1[p1=0.2]`

## 0.1.0 (2026-09-23)

### Added

- `sunnbear.stats`: geometric pseudo-quantiles (`gpq`/`owg`) and exact mean pairwise L1 distance
- Test-function framework: formulas whose parameters are swept over grids, a stable id per test function, and a registry that rebuilds a test function from its id
- `FormulaTestCase`: declare the unit tests that check a formula next to the formula's definition
- `Solver`/`BracketingSolver`: base classes for benchmarkable root solvers; each solve has a limit on the number of function evaluations, and its flop count leaves out the flops spent inside the function being solved
- Bracketing solvers accept an interval `[a, b]` where `f` goes from negative at `a` to positive at `b`, or the reverse
- `Bisection` and `RegulaFalsi` reference solvers
- `SolverConfig`: register a solver with fixed init arguments under a stable id, with a role that decides how the benchmark treats it

### Fixed

- Miscellaneous packaging fixes

## 0.0.3 (2026-07-07)

### Added

- Package now ships type information (`py.typed`)
- Python 3.14 support and full PyPI metadata (license, classifiers, description)

### Changed

- Dependency floors raised so declared minimums genuinely support each Python version (numba, numpy, matplotlib, and SPICE-ecosystem packages)
- README badges and splash are now served from the repo / shields.io instead of GitHub Pages

### Security

- Releases now ship SLSA build provenance and a GitHub Release with the changelog excerpt
## 0.0.2 (2025-11-07)

### Changed

- Internal development-workflow changes only; no functional changes

## 0.0.1 (2025-10-12)

### Added

- Initial project setup & framework
