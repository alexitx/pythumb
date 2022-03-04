# Changelog

## [1.1.0]
### Added
- Add support for YouTube Shorts URLs

### Changed
- Update dependencies
  - requests 2.25.0 -> 2.27.1

### Fixed
- Fix AttributeError when output is stdout

## [1.0.0]
### Changes
- Add support for more thumbnail variants
- Don't raise `NotADirectoryError` from `FileExistsError` on mkdir
- Simplify exception handling and print more detailed errors in CLI
- Store image as `bytes` instead of `BytesIO`
- Disable caching of the image to allow fetching multiple sizes
- Remove unused exception arguments

### Fixes
- Reduce Windows executable file size

## [0.3.0]
### Changes
- Add docstrings and comments
- Increase default timeout to 5 seconds
- Update help for CLI argument 'timeout'

### Fixes
- Exclude python36.dll from UPX in Windows build spec

## [0.2.0]
### Changes
- Allow writing to stdout

### Fixes
- Write to stderr instead of stdout on error

## [0.1.1]
### Fixes
- Fix linux binaries archive directory
- Add missing CLI entry point

## [0.1.0]
Initial release
