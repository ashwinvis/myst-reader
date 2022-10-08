"""

"""
from pathlib import Path
from shutil import copyfile
import subprocess
import tempfile

from bs4 import BeautifulSoup


def get_div_body(html_output):
    soup = BeautifulSoup(html_output, "html.parser")
    div = soup.findAll("div", {"class": "body"})[0]
    parts = []
    for elem in div.contents:
        try:
            code = elem.prettify()
        except AttributeError:
            code = elem
        parts.append(code)
    return "\n".join(parts).strip()


def myst2html(
    source,
    sphinx_conf=None,
    sphinx_extensions=None,
    myst_extensions=None,
    bib_files=None,
    tempdir_suffix=None,
):

    conf = dict(
        project="myst2html",
        author="pelican-myst-reader",
        myst_all_links_external=True,
    )

    if sphinx_conf is not None:
        conf.update(sphinx_conf)

    if sphinx_extensions is None:
        sphinx_extensions = []

    extensions = conf.setdefault("extensions", [])
    for ext in sphinx_extensions + ["myst_parser", "sphinx.ext.mathjax"]:
        if ext not in extensions:
            extensions.append(ext)

    if bib_files is not None:
        bib_files = [Path(path) for path in bib_files]
        conf["bibtex_bibfiles"] = [path.name for path in bib_files]
        if "sphinxcontrib.bibtex" not in conf["extensions"]:
            conf["extensions"].append("sphinxcontrib.bibtex")

    myst_enable_extensions = conf.setdefault("myst_enable_extensions", [])

    if myst_extensions is None:
        myst_extensions = []
    myst_extensions.extend(["amsmath", "colon_fence", "deflist", "dollarmath"])
    if myst_extensions is not None:
        for ext in myst_extensions:
            if ext not in myst_enable_extensions:
                myst_enable_extensions.append(ext)

    with tempfile.TemporaryDirectory(suffix=tempdir_suffix) as tempdir:

        tempdir = Path(tempdir)

        with open(tempdir / "index.md", "w") as file:
            file.write(source)

        with open(tempdir / "conf.py", "w") as file:
            for key, value in conf.items():
                file.write(f"{key} = {repr(value)}\n")

        if bib_files is not None:
            for path in bib_files:
                copyfile(path, tempdir / path.name)

        completed_process = subprocess.run(
            "sphinx-build . -b html _build".split(),
            cwd=tempdir,
            capture_output=True,
            text=True,
        )
        completed_process.check_returncode()

        with open(tempdir / "_build/index.html") as file:
            content = file.read()

    return get_div_body(content)
