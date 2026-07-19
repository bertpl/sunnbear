# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- `sunnbear.stats`: geometric pseudo-quantiles (`gpq`/`owg`) and exact mean pairwise L1 distance
- Test-function framework: formulas with parameter recipes, stable function identities, and a file-drop formula catalog

### Changed

### Deprecated

### Removed

### Fixed

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
