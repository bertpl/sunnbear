# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- `sunnbear.stats`: geometric pseudo-quantiles (`gpq`/`owg`) and exact mean pairwise L1 distance
- Test-function framework: formulas whose parameters are swept over grids, a stable id per test function, and a registry that rebuilds a test function from its id
- `FormulaTestCase`: declare a formula's test cases alongside its definition
- `Solver`/`BracketingSolver`: base classes for benchmarkable root solvers, with an evaluation budget and flop counting that leaves out the cost of evaluating the function being solved
- Solvers accept an interval where `f` goes from negative at `a` to positive at `b`, or the reverse
- `Bisection` and `RegulaFalsi` reference solvers
- `SolverConfig`: register a solver with fixed init arguments under a stable id, with a role that decides how the benchmark treats it

### Changed

### Deprecated

### Removed

### Fixed

- The source distribution contains the package again; the 0.0.3 source distribution installed no code

### Security

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
