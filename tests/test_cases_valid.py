"""Tests using valid default files for myst-reader plugin."""

from pathlib import Path
import sys

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


def _test_valid(name, MYST_EXTENSIONS=None):
    kwargs = {}
    if MYST_EXTENSIONS:
        kwargs["MYST_EXTENSIONS"] = MYST_EXTENSIONS

    settings = pelican_get_settings(**kwargs)

    myst_reader = MySTReader(settings)

    source_path = TEST_CONTENT_PATH / (name + ".md")
    output, metadata = myst_reader.read(source_path)
    path_expected = PATH_DIR_EXPECTED / (name + ".html")
    expected = path_expected.read_text().strip()

    path_failed = PATH_DIR_FAILED / path_expected.name
    if expected != output:
        path_failed.write_text(output)

    assert expected == output, (
        f"Compare with meld {path_expected.relative_to(CWD)} "
        f"{path_failed.relative_to(CWD)}"
    )

    return output, metadata


def test_minimal():
    """Check if we get the appropriate output specifying defaults."""

    output, metadata = _test_valid("valid_content_minimal")

    assert "Valid Content" == str(metadata["title"])
    assert "My Author" == str(metadata["author"])
    assert "2020-10-16 00:00:00" == str(metadata["date"])


def test_mathjax():
    """Check if mathematics is rendered correctly with defaults."""

    output, metadata = _test_valid(
        "valid_content_mathjax", MYST_EXTENSIONS=["dollarmath", "amsmath"]
    )

    assert "MathJax Content" == str(metadata["title"])
    assert "My Author" == str(metadata["author"])
    assert "2020-10-16 00:00:00" == str(metadata["date"])


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


def test_links():
    """Check if raw paths are left untouched in output returned."""

    output, metadata = _test_valid("valid_content_links")

    assert "Valid Content with Fictitious Paths" == str(metadata["title"])

    assert "My Author" == str(metadata["author"])
    assert "2020-10-16 00:00:00" == str(metadata["date"])


def test_images():
    """Check with images."""

    output, metadata = _test_valid("valid_content_images")

    assert "Valid Content with Image" == str(metadata["title"])
    assert "My Author" == str(metadata["author"])
    assert "2020-10-16 00:00:00" == str(metadata["date"])
