"""Tests using invalid extensions for myst-reader plugin."""
import os
import unittest

from pelican.plugins.myst_reader import MySTReader
from pelican.tests.support import get_settings

DIR_PATH = os.path.dirname(__file__)
TEST_CONTENT_PATH = os.path.abspath(os.path.join(DIR_PATH, "test_content"))

# Test settings that will be set in pelicanconf.py by plugin users
MYST_EXTENSIONS = []


class TestInvalidCasesWithExts(unittest.TestCase):
    """Invalid test cases using MyST exts and extensions."""

    def test_invalid_ext(self):
        """Check that specifying --standalone raises an exception."""
        myst_exts = {"does_not_exist"}
        settings = get_settings(MYST_EXTENSIONS=myst_exts)

        with self.assertRaises(ValueError) as context_manager:
            _ = MySTReader(settings)

        message = str(context_manager.exception)
        self.assertEqual(
            f"'enable_extensions' items not recognised: {myst_exts}", message
        )


if __name__ == "__main__":
    unittest.main()
