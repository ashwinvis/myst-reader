"""Compatibility layer to :module:`myst_parser.sphinx_renderer` which does not
monkey-patch Sphinx.

"""

import tempfile
from contextlib import contextmanager

from sphinx.application import Sphinx
from myst_parser.sphinx_renderer import sphinx_domains


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
        )
        _sphinx_domains = sphinx_domains(app.env)
        _sphinx_domains.enable()

        if document is not None:
            document.settings.env = app.env

        try:
            yield app
        finally:
            # revert directive/role function (see
            # `sphinx.util.docutils.sphinx_domains`)
            _sphinx_domains.disable()
