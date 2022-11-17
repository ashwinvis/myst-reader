# MyST Reader: A Plugin for Pelican

[![Build Status](https://img.shields.io/github/workflow/status/ashwinvis/myst-reader/build)](https://github.com/ashwinvis/myst-reader/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ashwinvis/myst-reader/main.svg)](https://results.pre-commit.ci/latest/github/ashwinvis/myst-reader/main)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-myst-reader)](https://pypi.org/project/pelican-myst-reader/)
![License](https://img.shields.io/pypi/l/pelican-myst-reader?color=blue)

MyST Reader is a [Pelican][] plugin that converts documents written in [MyST’s variant of Markdown][] into HTML.

## Requirements

This plugin requires:

- Python 3.9 or higher

## Installation

This plugin can be installed via:

```bash
python -m pip install pelican-myst-reader
```

## Configuration

This plugin converts [MyST’s variant of Markdown][] into HTML. MyST being a
superset of [CommonMark][CommonMark] should cover most Markdown variants, but
strictly speaking, conversion from other Markdown variants is unsupported.
Converting to output formats other than HTML is also unsupported.

### Specifying File Metadata

The plugin expects all Markdown files to start with a YAML-formatted content header, as shown below.

```yaml
---
title: "<post-title>"
author: "<author-name>"
date: "<date>"
summary: |
  The summary (can be on more than one line)...
---
```

If the values of the metadata can include MyST syntax, in which case, the field
name should be added to the `FORMATTED_FIELDS` list variable in
`pelicanconf.py`.

> ⚠️ **Note:** The YAML-formatted header shown above is syntax specific to MyST
> for specifying content metadata. This maybe different from Pelican’s
> front-matter format. If you ever decide to stop using this plugin and switch
> to Pelican’s default Markdown handling, you may need to switch your
> front-matter metadata to [Python-Markdown’s Meta-Data
> format](https://python-markdown.github.io/extensions/meta_data/).

As a compromise and in order to support both metadata formats (although this
means deviating away from MyST standard), title case headers are acceptable.
The advantage is that files are compatible with both MyST reader and Pelican's
Markdown reader.

```yaml
---
Title: "<post-title>"
Author: "<author-name>"
Date: "<date>"
---
```

For more information on Pelican's default metadata format please visit the link below:

- [Pelican’s default metadata format](https://docs.getpelican.com/en/stable/content.html#file-metadata)

### Specifying MyST Options

The plugin supports passing options to MyST. This is done by
configuring your Pelican settings file (e.g.,
`pelicanconf.py`):

- `MYST_EXTENSIONS`

In the `MYST_EXTENSIONS` setting, you may enable/disable any number of the supported [MyST extensions](https://myst-parser.readthedocs.io/en/latest/using/syntax-optional.html):

```python
MYST_EXTENSIONS = [
    "amsmath",
    "dollarmath",
]
```

- `MYST_FORCE_SPHINX`

The Sphinx renderer is automatically used if any math extension is enabled or
BibTeX files are found. This setting would force Sphinx rendering for all cases
which is slightly slower but has more features.

```py
MYST_FORCE_SPHINX = True
```

### Calculating and Displaying Reading Time

This plugin may be used to calculate the estimated reading time of articles and pages by setting `CALCULATE_READING_TIME` to `True` in your Pelican settings file:

```python
CALCULATE_READING_TIME = True
```

You may display the estimated reading time using the `{{ article.reading_time }}` or `{{ page.reading_time }}` template variables. The unit of time will be displayed as “minute” for reading times less than or equal to one minute, or “minutes” for those greater than one minute.

The reading time is calculated by dividing the number of words by the reading speed, which is the average number words read in a minute.

The default value for reading speed is set to 200 words per minute, but may be customized by setting `READING_SPEED` to the desired words per minute value in your Pelican settings file:

```python
READING_SPEED = <words-per-minute>
```

The number of words in a document is calculated using the [Markdown Word Count](https://github.com/gandreadis/markdown-word-count) package.

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.

Special thanks to [Justin Mayer](https://justinmayer.com), [Erwin Janssen](https://github.com/ErwinJanssen), [Joseph Reagle](https://github.com/reagle) and [Deniz Turgut](https://github.com/avaris) for their improvements and feedback on this plugin.

[existing issues]: https://github.com/ashwinvis/myst-reader/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html

## License

This project is licensed under the AGPL-3.0 license.

[Pelican]: https://getpelican.com
[MyST’s variant of Markdown]: https://myst-parser.readthedocs.io/en/latest/using/syntax.html
[CommonMark]: https://commonmark.org/
