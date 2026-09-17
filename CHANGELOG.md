# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure from NOAA Fisheries AA-SI Python template

### Changed
- HB1603 UC1: `full_analysis.yaml` now fans the survey in below a pinned depth grid
  (per-file MVBS, then merge) and dedups the overlapping dive windows; the former
  `full_analysis_revised.yaml` is this file.
- HB1603 UC1: `survey_preprocess.yaml` builds the same gridded survey tier, so
  curating the shared cache and running the analysis address one set of checkpoints.
- HB1603 UC1: `sv_window_example.yaml` grids each file before fanning in, and empty
  instances pass through per-file steps.

### Deprecated
- Nothing yet

### Removed
- HB1603 UC1: `dive_profiles.yaml`, `smoke_test.yaml`, `sub_recipes/dive_windows.yaml`
  and `sub_recipes/survey_sv.yaml`, the pre-grid dive-tier shape that merged raw
  per-file Sv on `ping_time` (NaN-padded across sample-interval changes and did not
  fit in memory at cruise scale).

### Fixed
- Nothing yet

### Security
- Nothing yet

## [0.1.0] - YYYY-MM-DD

### Added
- Initial release
- NEFSC Use Case 1 pipeline notebook
- Poetry-based dependency management with AA-SI package dependencies
- Development tooling (pytest, black, pylint, pre-commit)

<!--
=============================================================================
CHANGELOG GUIDELINES
=============================================================================

When adding entries, use the following categories:
- Added: for new features
- Changed: for changes in existing functionality
- Deprecated: for soon-to-be removed features
- Removed: for now removed features
- Fixed: for any bug fixes
- Security: in case of vulnerabilities

Each release should have a version number and date in the format:
## [X.Y.Z] - YYYY-MM-DD

Link definitions should be added at the bottom (optional)
