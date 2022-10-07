"""Tests using valid default files for myst-reader plugin."""
import unittest
from pathlib import Path

from pelican.plugins.myst_reader import MySTReader
from pelican.tests.support import get_settings as pelican_get_settings

DIR_PATH = Path(__file__).parent.resolve()
TEST_CONTENT_PATH = DIR_PATH / "test_content"
PATH_DIR_EXPECTED = TEST_CONTENT_PATH / "expected"
CWD = Path.cwd()


class TestValidCases(unittest.TestCase):
    """Valid test cases using default files."""

    def _test_valid(self, name, MYST_EXTENSIONS=None):

        kwargs = {}
        if MYST_EXTENSIONS:
            kwargs["MYST_EXTENSIONS"] = MYST_EXTENSIONS

        settings = pelican_get_settings(**kwargs)

        myst_reader = MySTReader(settings)

        source_path = TEST_CONTENT_PATH / (name + ".md")
        output, metadata = myst_reader.read(source_path)
        path_expected = PATH_DIR_EXPECTED / (name + ".html")
        expected = path_expected.read_text().strip()

        path_save_wrong = path_expected.with_stem(path_expected.stem + "_wrong")

        if expected != output:
            with open(path_save_wrong, "w") as file:
                file.write(output)

        self.assertEqual(
            expected,
            output,
            msg=f"Compare with meld {path_expected.relative_to(CWD)} {path_save_wrong.relative_to(CWD)}",
        )

        return output, metadata

    def test_minimal(self):
        """Check if we get the appropriate output specifying defaults."""

        output, metadata = self._test_valid("valid_content_minimal")

        self.assertEqual("Valid Content", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_mathjax(self):
        """Check if mathematics is rendered correctly with defaults."""

        output, metadata = self._test_valid(
            "valid_content_mathjax", MYST_EXTENSIONS=["dollarmath", "amsmath"]
        )

        self.assertEqual("MathJax Content", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_citations(self):
        """Check if output, citations are valid using citeproc filter."""

        output, metadata = self._test_valid("valid_content_citations")

        self.assertEqual("Valid Content With Citation", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

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

    def test_links(self):
        """Check if raw paths are left untouched in output returned."""

        output, metadata = self._test_valid("valid_content_links")

        self.assertEqual(
            "Valid Content with Fictitious Paths", str(metadata["title"])
        )
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_images(self):
        """Check with images."""

        output, metadata = self._test_valid("valid_content_images")

        self.assertEqual("Valid Content with Image", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))


if __name__ == "__main__":
    unittest.main()
