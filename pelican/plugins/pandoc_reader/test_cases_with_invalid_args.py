"""Tests using invalid arguments and extensions for myst-reader plugin."""
import os
import unittest

from pelican.tests.support import get_settings

from myst_reader import MySTReader

DIR_PATH = os.path.dirname(__file__)
TEST_CONTENT_PATH = os.path.abspath(os.path.join(DIR_PATH, "test_content"))

# Test settings that will be set in pelicanconf.py by plugin users
MYST_ARGS = ["--mathjax"]
MYST_EXTENSIONS = ["+smart"]


class TestInvalidCasesWithArguments(unittest.TestCase):
    """Invalid test cases using MyST arguments and extensions."""

    def test_invalid_standalone_argument(self):
        """Check that specifying --standalone raises an exception."""
        myst_arguments = ["--standalone"]
        settings = get_settings(
            MYST_EXTENSIONS=MYST_EXTENSIONS, MYST_ARGS=myst_arguments
        )

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            myst_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Argument --standalone is not supported.", message)

    def test_invalid_self_contained_argument(self):
        """Check that specifying --self-contained raises an exception."""
        myst_arguments = ["--self-contained"]
        settings = get_settings(
            MYST_EXTENSIONS=MYST_EXTENSIONS, MYST_ARGS=myst_arguments
        )

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            myst_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Argument --self-contained is not supported.", message)


if __name__ == "__main__":
    unittest.main()
