# Changelog

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