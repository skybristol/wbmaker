# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-07

### Major Project Modernization

This release represents a significant overhaul of the project infrastructure and development practices.

### Added
- **Development Dependencies**: pytest, pytest-cov, pytest-mock, black, ruff, mypy
- **Testing Infrastructure**: Comprehensive test suite with 21 tests and 43% coverage baseline
  - `tests/test_item.py` - Item class tests
  - Enhanced `tests/test_wb.py` - WB class tests
- **GitHub Actions CI/CD**:
  - Automated testing on Ubuntu, macOS, and Windows
  - Support for Python 3.11 and 3.12
  - Automated PyPI publishing on releases
- **Documentation**:
  - `CONTRIBUTING.md` - Contributor guidelines
  - `PROJECT_IMPROVEMENTS.md` - Detailed explanation of changes
  - `DEV_GUIDE.md` - Quick reference for developers
  - Enhanced README.md with badges, better structure, and examples
- **Development Tools**:
  - `Makefile` - Common development commands
  - Tool configurations in `pyproject.toml` (black, ruff, mypy, pytest, coverage)

### Changed
- **Code Quality**: Applied Black formatting and Ruff linting to entire codebase
- **Code Improvements**:
  - Fixed bare `except` statements with specific exception types
  - Fixed mutable default argument anti-pattern in `wb_dt()`
  - Improved type hints (proper Optional types)
  - Sorted and organized imports
- **Git Configuration**: Reorganized `.gitignore` by category, now commits `poetry.lock`
- **README.md**: Removed duplicate content, added badges, improved structure

### Fixed
- 75+ linting issues identified by Ruff
- Type checking issues (now passes mypy)
- Test structure (migrated from unittest to pytest)

### Development Status
- Updated to "Beta" quality with comprehensive testing and CI/CD
- Established baseline for future feature development
- All code passes formatting, linting, and type checking

## [0.0.12] - 2025-02-28
### Fixed
- Added wbiClass to the props structure built for a given connection to house the wikibaseintegrator.datatype for each property. This provides the objects necessary for building claims without having to interpret the type string.

## [0.0.11] - 2024-08-12
### Fixed
- Added parameters to wd_path_analysis function to make calculation of alternate paths optional and set limit on number of paths considered

## [0.0.10] - 2024-08-11
### Added
- Added the wd_path_analysis function to the WB class to identify possible options for new item classification based on path analysis in Wikidata

## [0.0.9] - 2024-08-09
### Added
- New Item class with claim handler function; handles new and updated claims, qualifiers, and references in a more compact way

## [0.0.8] - 2024-07-15
### Changed
- Added datatypes and enums from wikibaseintegrator as a convenience in building workflows

## [0.0.7] - 2024-07-10
### Changed
- Changed approach on connection details to WB instance to use explicit environment variables

## [0.0.6] - 2024-06-23
### Changed
- Increased Pandas version dependency ^2.0.0

## [0.0.5] - 2024-06-13
### Added
- Added is_bot to WB class as a parameter to handle cases where setting this flag creates a problem for provided credentials that do not have the bot flag set

## [0.0.4] - 2024-06-04
### Added
- Changed the wb.WB().property_map() function to return optional formatter URL claims
- Added wb module import to init