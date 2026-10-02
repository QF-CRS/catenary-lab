# Changelog

All notable changes to this project will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versions follow semantic versioning while the API is still stabilising.

## [0.1.1] - 2026-10-03

Maintenance release.

- Improve numerical stability for steep, nearly straight spans by avoiding
  catastrophic cancellation in catenary elevation evaluation.
- Add a regression test for the near-linear steep-span case.
- Validate wheel builds in CI and add monthly Dependabot updates.
- Migrate package license metadata to the SPDX format.

## [0.1.0] - 2026-10-01

### Added

- analytical catenary solver for level and unequal-elevation spans;
- elevation, slope, vertical tension, tension magnitude, arc length, and sag
  calculations;
- Python API, command-line interface, JSON output, and sampling;
- unit tests, usage example, MIT license, contribution guide, and CI workflow.
