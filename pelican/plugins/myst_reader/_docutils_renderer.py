"""Implementation of a Docutils-based renderer for MyST documents.

See Docutils docs at: https://docutils.sourceforge.io
"""

from __future__ import annotations

from typing import Any

from docutils.core import publish_parts
from docutils.parsers.rst import Parser as RstParser
from myst_parser.config.main import MdParserConfig
from myst_parser.parsers.docutils_ import (
    Parser as MystDocutilsParser,
)
from myst_parser.parsers.docutils_ import attr_to_optparse_option


def create_myst_settings_spec(config: MdParserConfig, prefix: str = "myst_"):
    """Return a list of Docutils setting for the docutils MyST section."""
    return tuple(
        attr_to_optparse_option(at, getattr(config, at.name), prefix)
        for at in MdParserConfig.get_fields()
        if ("docutils" not in at.metadata.get("omit", []))
    )


class Parser(MystDocutilsParser):
    @classmethod
    def override_settings_spec(cls, config: MdParserConfig):
        cls.settings_spec = (
            "MyST options",
            None,
            create_myst_settings_spec(config),
            *RstParser.settings_spec,
        )


def docutils_renderer(
    content: str,
    conf: dict[str, Any],
    parser: Parser,
):
    """Use the HTML5 writer: https://docutils.sourceforge.io/docs/user/config.html#html5-writer"""
    parts = publish_parts(
        source=content,
        writer_name="html5",
        settings_overrides=conf,
        parser=parser,
    )
    output = parts["body"]
    return output.strip()
