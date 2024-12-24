"""Tests using valid default files for myst-reader plugin."""

import difflib
import sys
from pathlib import Path

import bs4
import pytest

from pelican.plugins.myst_reader import MySTReader
from pelican.tests.support import get_settings as pelican_get_settings

DIR_PATH = Path(__file__).parent.resolve()
TEST_CONTENT_PATH = DIR_PATH / "test_content"
PATH_DIR_EXPECTED = TEST_CONTENT_PATH / "expected"
PATH_DIR_FAILED = TEST_CONTENT_PATH / "failed"
CWD = Path.cwd()


def _is_not_empty(path_dir):
    return path_dir.exists() and tuple(path_dir.iterdir())


def setup_module(module):
    if _is_not_empty(PATH_DIR_FAILED):
        print(
            "Directory",
            PATH_DIR_FAILED,
            "seems to contain previous failures",
            file=sys.stderr,
        )
    PATH_DIR_FAILED.mkdir(exist_ok=True)


def teardown_module(module):
    if _is_not_empty(PATH_DIR_FAILED):
        print(
            "Not removing", PATH_DIR_FAILED, "since it is not empty.", file=sys.stderr
        )
    else:
        PATH_DIR_FAILED.rmdir()


def _is_html_eq(expected: str, output: str):
    # read the html files content using Beautifulsoup
    expected_pretty = bs4.BeautifulSoup(expected, features="html.parser").prettify()
    output_pretty = bs4.BeautifulSoup(output, features="html.parser").prettify()

    diff_lines = list(
        difflib.unified_diff(expected_pretty.split("\n"), output_pretty.split("\n"))
    )

    if diff_lines:
        return False, "🫣 HTML contents differ at lines:" + "\n".join(diff_lines)
    else:
        return True, ""


def _test_valid(name, expected_name="", **pelicanconf):
    settings = pelican_get_settings(**pelicanconf)

    myst_reader = MySTReader(settings)

    source_path = TEST_CONTENT_PATH / (name + ".md")
    output, metadata = myst_reader.read(source_path)
    path_expected = PATH_DIR_EXPECTED / ((expected_name or name) + ".html")
    path_failed = PATH_DIR_FAILED / path_expected.name

    if path_expected.exists():
        expected = path_expected.read_text().strip()
    else:
        import warnings

        warnings.warn(
            f"test_cases_valid: {path_expected.relative_to(CWD)=} does not exist. "
            f"Generating {path_failed.relative_to(CWD)=} anyways."
        )
        expected = ""

    if expected != output:
        path_failed.write_text(output)

    eq, diff = _is_html_eq(expected, output)
    assert eq, diff + (
        f"🤔 Compare with meld {path_expected.relative_to(CWD)} "
        f"{path_failed.relative_to(CWD)}"
    )

    return output, metadata


def test_minimal():
    """Check if we get the appropriate output specifying defaults."""

    output, metadata = _test_valid("valid_content_minimal")

    assert "Valid Content" == str(metadata["title"])
    assert "My Author" == str(metadata["author"])
    assert "2020-10-16 00:00:00" == str(metadata["date"])


@pytest.mark.parametrize("renderer", ["DEFAULT", "SPHINX", "MDIT"])
def test_mathjax(renderer):
    """Check if mathematics is rendered correctly with defaults."""

    if renderer == "DEFAULT":
        pelicanconf = dict(MYST_EXTENSIONS=["dollarmath", "amsmath"])
    else:
        pelicanconf = {
            f"MYST_{renderer}_SETTINGS": {
                "myst_enable_extensions": ["dollarmath", "amsmath"]
            },
            f"MYST_FORCE_{renderer}": True,
        }

    output, metadata = _test_valid(
        "valid_content_mathjax", f"valid_content_mathjax_{renderer=}", **pelicanconf
    )

    assert "MathJax Content" == str(metadata["title"])
    assert "My Author" == str(metadata["author"])
    assert "2020-10-16 00:00:00" == str(metadata["date"])
    assert '<div class="math' in output


def test_citations():
    """Check if output, citations are valid using citeproc filter."""

    output, metadata = _test_valid("valid_content_citations")

    assert "Valid Content With Citation" == str(metadata["title"])
    assert "My Author" == str(metadata["author"])
    assert "2020-10-16 00:00:00" == str(metadata["date"])

    # Read twice to see if warnings are emitted by the logger
    # try:
    #     with self.assertLogs(
    #         "sphinx.sphinx.application", level="WARNING"
    #     ) as cm:
    #         output, metadata = myst_reader.read(source_path)
    # except AssertionError:
    #     pass
    # else:
    #     for warning_msg in cm.output:
    #         self.assertNotIn(
    #             "is already registered, its visitors will be overridden",
    #             warning_msg,
    #         )
    #         self.assertNotIn(
    #             "is already registered, it will be overridden", warning_msg
    #         )


@pytest.mark.parametrize("strip_comments", [True, False])
def test_comments(strip_comments):
    """Check if comments are stripped or not by docutils parser."""

    output, metadata = _test_valid(
        "valid_content_comments",
        expected_name=f"valid_content_comments_{strip_comments=}",
        MYST_DOCUTILS_SETTINGS={"strip_comments": strip_comments},
        MYST_FORCE_DOCUTILS=True,
    )

    assert "Valid Content with Comments" == str(metadata["title"])

    assert "My Author" == str(metadata["author"])
    assert "2020-10-16 00:00:00" == str(metadata["date"])

    present = not strip_comments
    assert ("standalone comment" in output) is present


def test_links():
    """Check if raw paths are left untouched in output returned."""

    output, metadata = _test_valid("valid_content_links")

    assert "Valid Content with Fictitious Paths" == str(metadata["title"])

    assert "My Author" == str(metadata["author"])
    assert "2020-10-16 00:00:00" == str(metadata["date"])


def test_images():
    """Check with images."""

    output, metadata = _test_valid(
        "valid_content_images",
        # MYST_FORCE_DOCUTILS=True,
        # MYST_DOCUTILS_SETTINGS={"myst_enable_extensions": ["colon_fence"]},
    )

    assert "Valid Content with Image" == str(metadata["title"])
    assert "My Author" == str(metadata["author"])
    assert "2020-10-16 00:00:00" == str(metadata["date"])


@pytest.mark.parametrize("renderer", ["MDIT", "SPHINX"])
def test_ext_tasklist(renderer):
    """Check if using tasklist extension generates a bullet list with checkboxes"""
    settings = {
        f"MYST_FORCE_{renderer}": True,
        f"MYST_{renderer}_SETTINGS": dict(myst_enable_extensions=["tasklist"]),
    }

    output, _ = _test_valid("ext_tasklist", f"ext_tasklist_{renderer=}", **settings)
    assert '<li class="task-list-item">' in output


@pytest.mark.parametrize("renderer", ["MDIT", "SPHINX"])
def test_ext_attrs_inline_image(renderer):
    """Check if using attrs_inline extension generates the correct
    image tag."""
    settings = {
        f"MYST_FORCE_{renderer}": True,
        "STATIC_PATHS": ["_static"],
        f"MYST_{renderer}_SETTINGS": dict(myst_enable_extensions=["attrs_inline"]),
    }

    output, _ = _test_valid(
        "ext_attrs_inline_image", f"ext_attrs_inline_image_{renderer=}", **settings
    )

    assert ('style="width: 100px;"' in output) or ('w="100px"' in output)
