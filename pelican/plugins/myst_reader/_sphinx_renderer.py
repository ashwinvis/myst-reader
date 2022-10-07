"""

"""
from pathlib import Path
import tempfile
import subprocess
from textwrap import dedent

from bs4 import BeautifulSoup


def get_div_body(html_output):
    soup = BeautifulSoup(html_output, "html.parser")
    div = soup.findAll("div", {"class": "body"})[0]
    lines = div.prettify().strip().split("\n")
    return dedent("\n".join(lines[1:-1]))


def myst2html(source, sphinx_conf=None, path_bib=None):

    conf = dict(
        project="myst2html",
        author="pelican-myst-reader",
        extensions=[
            "myst_parser",
            "sphinx.ext.mathjax",
            # "sphinxcontrib.bibtex",
        ],
        # bibtex_bibfiles=["refs.bib"],
        myst_all_links_external=True,
        myst_enable_extensions=[
            "amsmath",
            "colon_fence",
            "deflist",
            "dollarmath",
        ],
    )

    with tempfile.TemporaryDirectory() as tempdir:

        tempdir = Path(tempdir)

        with open(tempdir / "index.md", "w") as file:
            file.write(source)

        with open(tempdir / "conf.py", "w") as file:
            for key, value in conf.items():
                file.write(f"{key} = {repr(value)}\n")

        with open(tempdir / "conf.py") as file:
            print(file.read())

        subprocess.run("sphinx-build . -b html _build".split(), cwd=tempdir)

        with open(tempdir / "_build/index.html") as file:
            content = file.read()

    return get_div_body(content)
