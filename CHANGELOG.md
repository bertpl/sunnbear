# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

### Changed

- `MC_TUPLES_SIZES` is replaced by the enum `MCTuplesSize`, whose members are the sizes of the shipped Monte Carlo tuple set
- The shipped Monte Carlo (u, v) tuple set is regenerated with an 8-hour time budget, which increases the smallest distance between its tuples at every nested size from 32 to 1024; benchmark results on the new set differ from those on the previous set

### Deprecated

### Removed

### Fixed

- Importing `sunnbear.benchmark` no longer compiles the numba functions of its max-div dependency, which could take minutes on a fresh install
- A data artifact's manifest names the sunnbear release that ships the artifact, not the release before it

### Security

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
