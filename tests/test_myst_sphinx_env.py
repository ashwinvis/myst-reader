from myst_parser.mdit_to_docutils.base import make_document
from pelican.plugins.myst_reader._sphinx_renderer import mock_sphinx_env_compat


def test_myst_mock_sphinx_env_compat():
    conf = {"extensions": ["sphinxcontrib.bibtex"], "bibtex_bibfiles": ["test.bib"]}
    requested_extensions = set(conf.get("extensions"))
    with mock_sphinx_env_compat(
        conf=conf, srcdir=".", with_builder="html", document=make_document()
    ) as app:
        app_exts = sorted(app.extensions)
        assert (
            requested_extensions.intersection(app_exts) == requested_extensions
        ), f"requested {requested_extensions}, got {app_exts}"
