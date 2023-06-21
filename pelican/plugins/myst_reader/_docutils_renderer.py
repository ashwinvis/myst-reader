"""Implementation of a Docutils-based renderer for MyST documents.

See Docutils docs at: https://docutils.sourceforge.io
"""

from __future__ import annotations

from typing import Any

from docutils.core import publish_parts
from myst_parser.docutils_ import Parser


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
