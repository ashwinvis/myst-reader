"""Compatibility layer to :module:`myst_parser.sphinx_renderer` and
:module:`myst_parser.main` which does not monkey-patch Sphinx.

"""
from contextlib import contextmanager
import copy
from pathlib import Path
import tempfile
from typing import Iterable, Optional

from bs4 import BeautifulSoup
from docutils.parsers.rst import directives, roles
from myst_parser.config.main import MdParserConfig
from myst_parser.parsers.mdit import create_md_parser
from sphinx.application import Sphinx
from sphinx.util.docutils import additional_nodes, sphinx_domains, unregister_node


from docutils.core import publish_string
from myst_parser.sphinx_ import Parser



def via_sphinx(
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
    return output.decode('utf-8')


@contextmanager
def mock_sphinx_env_compat(
    conf=None,
    srcdir=None,
    document=None,
    with_builder=False,
    raise_on_warning=False,
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
        # store currently loaded roles/directives, so we can revert on exit
        _directives = copy.copy(directives._directives)
        _roles = copy.copy(roles._roles)

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
            # NOTE: the following cleanup is to avoid warnings while creating a Sphinx
            # Application multiple times

            # revert loaded roles/directives
            directives._directives = _directives
            roles._roles = _roles

            for node in list(additional_nodes):
                unregister_node(node)
                additional_nodes.discard(node)

            # revert directive/role function (ee
            # `sphinx.util.docutils.sphinx_domains`)
            _sphinx_domains.disable()




def get_div_body(html_output):
    soup = BeautifulSoup(html_output, "html.parser")
    div = soup.findAll("div", {"class": "documentwrapper"})[0]
    return div.prettify()
