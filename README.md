# MyST Reader: A Plugin for Pelican

[![Build Status](https://img.shields.io/github/actions/workflow/status/ashwinvis/myst-reader/build.yaml?branch=main)](https://github.com/ashwinvis/myst-reader/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ashwinvis/myst-reader/main.svg)](https://results.pre-commit.ci/latest/github/ashwinvis/myst-reader/main)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-myst-reader)](https://pypi.org/project/pelican-myst-reader/)
![License](https://img.shields.io/pypi/l/pelican-myst-reader?color=blue)

*MyST Reader* is a [Pelican][] plugin that converts documents written in [MyST’s variant of Markdown][] into HTML.

## Requirements

This plugin requires:

- Python 3.9 or higher

## Installation

This plugin can be installed via:

```bash
python -m pip install pelican-myst-reader
```

As soon as the plugin is installed, it will automatically be used by Pelican to parse and render all Markdown files with the MyST syntax.

## Writing MyST content

MyST syntax is a superset of [CommonMark][]. So if you feed your Pelican site with
non-MyST Markdown files or other variants, most of them will probably renders as they were with this plugin.

You can then augment your plain Markdown with [MyST syntax](https://myst-parser.readthedocs.io/en/latest/syntax/typography.html) to get access to more features. You can play with the [MyST live preview](https://myst-parser.readthedocs.io/en/latest/live-preview.html) to see what is possible.

### File Metadata

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
name should be added to the [`FORMATTED_FIELDS`](https://docs.getpelican.com/en/latest/settings.html#basic-settings) list variable in
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

## Configuration

The plugin supports passing options to influence how MyST is parsed and renderered. This is done by
configuring your Pelican settings file (e.g., `pelicanconf.py`):

### Docutils Renderer

By default MyST rely on [Docutils](https://docutils.sourceforge.io/) to parse and render its syntax. That's [because MyST primarily targets Sphinx](https://myst-parser.readthedocs.io/en/latest/develop/background.html#the-relationship-between-myst-restructuredtext-and-sphinx).

To produce HTML for Pelican, *MyST Reader* uses Docutils too (and more precisely its [HTML5 Writer](https://docutils.sourceforge.io/docs/user/config.html#html5-writer)).

This plugin setup Docutils with good settings by defaults. But you can still influence it
with the `MYST_DOCUTILS_SETTINGS` setting.

Here is an example of configuration in `pelicanconf.py`:

```python
MYST_DOCUTILS_SETTINGS = {
    ### Docutils settings ###
    "strip_comments": True,

    ### MyST settings ###
    "myst_gfm_only": True,
    "myst_substitutions": {
        "key1": "I'm a **substitution**",
    },
    "myst_enable_extensions": {
        "amsmath",
        "dollarmath",
    },
}
```

See how the `MYST_DOCUTILS_SETTINGS` setting is used to pass both:
- [Docutils configuration](https://docutils.sourceforge.io/docs/user/config.html)
- [MyST parser configuration](https://myst-parser.readthedocs.io/en/latest/configuration.html#docutils-configuration), including

Also notice how:
- MyST-specific settings are prefixed with `myst_`
- the list of additional [MyST extensions](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html) to activate is set with `myst_enable_extensions`

> ⚠️ **Note:** `MYST_DOCUTILS_SETTINGS` accepts the same parameters as [Pelican’s `DOCUTILS_SETTINGS`](https://docs.getpelican.com/en/latest/settings.html#basic-settings). We could have reused them but we [decided to keep them separate](https://github.com/ashwinvis/myst-reader/pull/14#discussion_r1240757130) for clarity.

### Sphinx Renderer

*MyST Reader* also supports an alternative rendering mode using [Sphinx](https://www.sphinx-doc.org).

You can force this rendering mode for all files with:

```python
MYST_FORCE_SPHINX = True
```

> ⚠️ **Note:** Sphinx rendering is way slower (~2.5x on my machine), as it setups behind the scene a standalone Sphinx project and sequentially run a full build for each page.

If set to `False`, which is the default, an heuristic is used to determine for each file if Sphinx should be used instead of the default Docutils renderer from the section above.

This heuristic activates the Sphinx renderer if any of the following rule is met:
- a math extension from MyST
is enabled ([`dollarmath` or `amsmath`](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#math-shortcuts)) in `MYST_SPHINX_SETTINGS`
- BibTeX files are found

Now this rendering mode also has its own dedicated configuration setting: `MYST_SPHINX_SETTINGS`. It is a dictionary that will be used to build a `conf.py` file to be passed to the Sphinx builder.

Here is an example of configuration in `pelicanconf.py`:
```python
MYST_SPHINX_SETTINGS = {
    ### Sphinx settings ###
    "nitpicky": True,
    "keep_warnings": True,

    ### MyST settings ###
    "myst_gfm_only": True,
    "myst_substitutions": {
        "key1": "I'm a **substitution**",
    },
    "myst_enable_extensions": {
        "amsmath",
        "dollarmath",
    },
}
```

Like the previous renderer, it supports both settings:
- [Sphinx configuration](https://www.sphinx-doc.org/en/master/usage/configuration.html)
- [MyST parser configuration](https://myst-parser.readthedocs.io/en/latest/configuration.html#global-configuration)

And again:
- MyST-specific settings are prefixed with `myst_`
- the list of additional [MyST extensions](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html) to activate is set with `myst_enable_extensions`

### Deprecated `MYST_EXTENSIONS`

There is a dedicated `MYST_EXTENSIONS` setting to activate MyST extensions. But it is deprecated in favor of the `MYST_DOCUTILS_SETTINGS["myst_enable_extensions"]` and `MYST_SPHINX_SETTINGS["myst_enable_extensions"]` settings.

It is still loaded up by *MyST Reader* for backward compatibility but will be ignored in a future release.

If `MYST_EXTENSIONS` is set, it will be used to populate `MYST_DOCUTILS_SETTINGS["myst_enable_extensions"]` and `MYST_SPHINX_SETTINGS["myst_enable_extensions"]`.

### Reading Time

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

## Limitations

This plugin converts [MyST’s variant of Markdown][] into HTML for Pelican. MyST being a
superset of [CommonMark][CommonMark] should cover most Markdown variants. But
strictly speaking, conversion from other Markdown variants is unsupported.

Converting to output formats other than HTML is also unsupported.

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
