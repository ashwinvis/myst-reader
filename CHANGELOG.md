# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Changed

- Upgrade to myst-parser 4.0.0.
- Bump minimal requirement to Sphinx 8.0.
- Bump minimal requirement to docutils 0.19.
- Bump minimal requirement to Python 3.10.

## [1.3.0] - 2024-05-01

It is time to move this out of beta.

### Fixed

- Clearer error messages which includes Docutils error on invalid content (by @AlxCzl in #27).

## [1.3.0b1] - 2023-07-02

### Added

- New `MYST_DOCUTILS_SETTINGS` and `MYST_SPHINX_SETTINGS` to configure each renderer and MyST parser.
- New {exception}`pelican.plugins.myst_reader.MystReaderContentError` to differentiate content related issues.
- Documents the new configuration settings.
- Adds typing to some methods.

### Changed

- Upgrade to myst-parser v2.0.0.
- Cleans up the merge of users and default settings.

### Deprecated

- Deprecates `MYST_EXTENSIONS` settings.
- Feed `MYST_EXTENSIONS` to `MYST_DOCUTILS_SETTINGS` and `MYST_SPHINX_SETTINGS` in the mean time.

### Fixed

- Forces initial header level to `<h2>` instead of `<h1>`, since Pelican will use the title field in the front-matter as the `<h1>` header of the page.

## [1.2.0b1] - 2022-10-26

### Fixed

- Detect `{cite` instead of `{cite}` to allow for all citation roles.

## [1.2.0b0] - 2022-10-26

### Changed

- Upgraded to myst-parser v0.18.0 API. Thanks [@paugier]!

## [1.1.2b0] - 2021-06-10

### Fixed

- First working release with most features in place

## [1.1.1b0] - 2021-03-15

### Changed

- Forked `pelican-pandoc-reader` and replaced Pandoc with MyST parser

## [1.1.0] - 2021-02 16

## [1.0.1] - 2021-02-05

## [1.0.0] - 2020-12-04

[Unreleased]: https://github.com/ashwinvis/myst-reader/compare/1.3.0...HEAD
[1.3.0]: https://github.com/ashwinvis/myst-reader/compare/1.3.0b1...1.3.0
[1.3.0b1]: https://github.com/ashwinvis/myst-reader/compare/1.2.0b1...1.3.0b1
[1.2.0b1]: https://github.com/ashwinvis/myst-reader/compare/1.2.0b0...1.2.0b1
[1.2.0b0]: https://github.com/ashwinvis/myst-reader/compare/1.1.2b0...1.2.0b0
[1.1.2b0]: https://github.com/ashwinvis/myst-reader/compare/1.1.1b0...1.1.2b0
[1.1.1b0]: https://github.com/ashwinvis/myst-reader/compare/1.1.0...1.1.1b0
[1.1.0]: https://github.com/ashwinvis/myst-reader/releases/tag/1.1.0
[1.0.1]: https://github.com/ashwinvis/myst-reader/releases/tag/1.0.1
[1.0.0]: https://github.com/ashwinvis/myst-reader/releases/tag/1.0.0
[@paugier]: https://github.com/paugier
