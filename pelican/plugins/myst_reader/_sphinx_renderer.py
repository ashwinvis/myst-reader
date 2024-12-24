"""Implementation of a Sphinx-based renderer for MyST documents."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from shutil import copyfile
from typing import Any, Iterable

from bs4 import BeautifulSoup


def get_div_body(html_output: str) -> str:
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


def sphinx_renderer(
    content: str,
    conf: dict[str, Any],
    bib_files: Iterable[str | Path] | None = None,
    tempdir_suffix: str | None = None,
) -> str:
    """Builds a Sphinx project from a MyST ``content`` string and returns the HTML body."""
    # Do not modify the original configuration dictionary in place.
    local_conf = conf.copy()
    # Dynamiccaly add the bibtex files to the Sphinx configuration.
    if bib_files:
        bib_files = {Path(path) for path in bib_files}
        local_conf["bibtex_bibfiles"].extend(path.name for path in bib_files)
        # Only activate the bibtex extension if bib_files are provided.
        local_conf["extensions"].add("sphinxcontrib.bibtex")

    with tempfile.TemporaryDirectory(suffix=tempdir_suffix) as tempdir:
        tempdir = Path(tempdir)

        # Saves the MyST content to a temporary index.md file.
        with open(tempdir / "index.md", "w") as file:
            file.write(content)

        # Generates a Sphinx conf.py file from the configuration dictionary.
        with open(tempdir / "conf.py", "w") as file:
            for key, value in local_conf.items():
                if isinstance(value, set):
                    value = sorted(value)
                file.write(f"{key} = {repr(value)}\n")

        if bib_files:
            for path in bib_files:
                copyfile(path, tempdir / path.name)

        completed_process = subprocess.run(
            "sphinx-build . -b html _build".split(),
            cwd=tempdir,
            capture_output=True,
            text=True,
            check=False,
        )
        completed_process.check_returncode()

        with open(tempdir / "_build/index.html") as file:
            content = file.read()

    return get_div_body(content)
