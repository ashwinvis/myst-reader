from myst_parser.sphinx_renderer import mock_sphinx_env
from myst_parser.docutils_renderer import make_document

from pelican.plugins.myst_reader._sphinx_renderer import mock_sphinx_env_compat


def test_myst_mock_sphinx_env():
    conf = {"extensions": ["sphinxcontrib.bibtex"]}
    requested_extensions = set(conf.get("extensions"))
    with mock_sphinx_env(
        conf=conf, srcdir=".", with_builder="html", document=make_document()
    ) as app:
        app_exts = sorted(app.extensions)
        assert (
            requested_extensions.intersection(app_exts) == requested_extensions
        ), f"requested {requested_extensions}, got {app_exts}"


def test_myst_mock_sphinx_env_compat():
    conf = {"extensions": ["sphinxcontrib.bibtex"]}
    requested_extensions = set(conf.get("extensions"))
    with mock_sphinx_env_compat(
        conf=conf, srcdir=".", with_builder="html", document=make_document()
    ) as app:
        app_exts = sorted(app.extensions)
        assert (
            requested_extensions.intersection(app_exts) == requested_extensions
        ), f"requested {requested_extensions}, got {app_exts}"
