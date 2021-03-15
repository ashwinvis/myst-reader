"""Compatibility layer to :module:`myst_parser.sphinx_renderer` and
:module:`myst_parser.main` which does not monkey-patch Sphinx.

"""

import tempfile
from pathlib import Path
from typing import Optional, Iterable
from contextlib import contextmanager

from bs4 import BeautifulSoup
from sphinx.application import Sphinx
from myst_parser.sphinx_renderer import sphinx_domains
from myst_parser.main import default_parser, MdParserConfig


@contextmanager
def mock_sphinx_env_compat(
    conf=None, srcdir=None, document=None, with_builder=False, raise_on_warning=False,
):
    """Set up an environment, to parse sphinx roles/directives,
    outside of a `sphinx-build`.

    :param conf: a dictionary representation of the sphinx `conf.py`
    :param srcdir: a path to a source directory
        (for example, can be used for `include` statements)

    This primarily copies the code in `sphinx.util.docutils.docutils_namespace`
    and `sphinx.util.docutils.sphinx_domains`.
    """
    with tempfile.TemporaryDirectory() as tempdir:
        # creating a builder attempts to make the doctreedir
        app = Sphinx(
            srcdir=srcdir,
            confdir=None,
            outdir=tempdir,
            doctreedir=tempdir,
            confoverrides=conf,
            buildername=with_builder,
            warningiserror=raise_on_warning,
            keep_going=True,
        )
        _sphinx_domains = sphinx_domains(app.env)
        _sphinx_domains.enable()

        if document is not None:
            document.settings.env = app.env

        try:
            yield app
        finally:
            import os

            os.listdir(tempdir)
            # revert directive/role function (ee
            # `sphinx.util.docutils.sphinx_domains`)
            _sphinx_domains.disable()


def to_sphinx(
    filename: Iterable[str],
    parser_config: Optional[MdParserConfig] = None,
    options=None,
    env=None,
    document=None,
    conf=None,
    srcdir=None,
    with_builder="singlehtml",
):
    """Render text to the docutils AST (before transforms)

    :param text: the text to render
    :param options: options to update the parser with
    :param env: The sandbox environment for the parse
        (will contain e.g. reference definitions)
    :param document: the docutils root node to use (otherwise a new one will be created)
    :param in_sphinx_env: initialise a minimal sphinx environment (useful for testing)
    :param conf: the sphinx conf.py as a dictionary
    :param srcdir: to parse to the mock sphinx env

    :returns: docutils document
    """
    from myst_parser.docutils_renderer import make_document

    md = default_parser(parser_config or MdParserConfig())
    if options:
        md.options.update(options)
    md.options["document"] = document or make_document()

    force_all = False

    with mock_sphinx_env_compat(
        conf=conf,
        srcdir=srcdir,
        document=md.options["document"],
        with_builder=with_builder,
    ) as app:
        app.build(force_all, (filename,))
        filehtml = Path(filename).with_suffix(".html").name
        output = (Path(app.outdir) / filehtml).read_text()
        return get_div_body(output)


def get_div_body(html_output):
    soup = BeautifulSoup(html_output, "html.parser")
    div = soup.findAll("div", {"class": "documentwrapper"})[0]
    return div.prettify()
