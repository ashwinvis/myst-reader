from __future__ import annotations

from docutils.core import publish_parts
from myst_parser.docutils_ import Parser


def myst2html(
    source: str,
    myst_extensions: tuple[str],
    parser: Parser,
):
    """Public API in https://myst-parser.readthedocs.io/en/v0.18.0/docutils.html"""
    parts = publish_parts(
        source=source,
        writer_name="html5",
        settings_overrides={
            "myst_enable_extensions": myst_extensions,
            "embed_stylesheet": False,
        },
        parser=parser,
    )
    output = parts["body"]
    return output.strip()
