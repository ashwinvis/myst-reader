from __future__ import annotations
from docutils.core import publish_string
from myst_parser.docutils_ import Parser

from myst_parser.config.main import MdParserConfig


def via_docutils(
    source: str,
    extensions: tuple[str],
    parser: Parser,
):
    """Public API in https://myst-parser.readthedocs.io/en/v0.18.0/docutils.html"""
    output = publish_string(
        source=source,
        writer_name="html5",
        settings_overrides={
            "myst_enable_extensions": extensions,
            "embed_stylesheet": False,
        },
        parser=parser,
    )
    return output.decode("utf-8")
