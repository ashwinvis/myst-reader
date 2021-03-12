"""Test if myst executable is available."""
import os
import shutil
import unittest

from pelican.tests.support import get_settings

from myst_reader import MySTReader

DIR_PATH = os.path.dirname(__file__)
TEST_CONTENT_PATH = os.path.abspath(os.path.join(DIR_PATH, "test_content"))

# Test settings that will be set in pelicanconf.py by plugin users
PANDOC_ARGS = ["--mathjax"]
PANDOC_EXTENSIONS = ["+smart"]


class TestMySTAvailability(unittest.TestCase):
    """Test MyST availability."""

    def test_myst_availability_one(self):
        """Check if MyST executable is available."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=PANDOC_ARGS,
        )

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "empty.md")

        if not shutil.which("myst"):
            # Case where myst is not available
            with self.assertRaises(Exception) as context_manager:
                myst_reader.read(source_path)

            message = str(context_manager.exception)
            self.assertEqual("Could not find MyST. Please install.", message)
        else:
            self.assertTrue(True)

    def test_myst_availability_two(self):
        """Check if myst executable is available at the given path."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS,
            PANDOC_ARGS=PANDOC_ARGS,
            PANDOC_EXECUTABLE_PATH="0.13.5/bin/myst",
        )

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "empty.md")

        with self.assertRaises(Exception) as context_manager:
            myst_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find MyST. Please install.", message)

    def test_myst_unsupported_major_version(self):
        """Check if the installed myst has a supported major version."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS,
            PANDOC_ARGS=PANDOC_ARGS,
            PANDOC_EXECUTABLE_PATH="1.19/bin/myst",
        )

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "empty.md")

        with self.assertRaises(Exception) as context_manager:
            myst_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("MyST version must be 0.13.5 or higher.", message)

    def test_myst_unsupported_minor_version(self):
        """Check if the installed myst has a supported minor version."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS,
            PANDOC_ARGS=PANDOC_ARGS,
            PANDOC_EXECUTABLE_PATH="2.10/bin/myst",
        )

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "empty.md")

        with self.assertRaises(Exception) as context_manager:
            myst_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("MyST version must be 0.13.5 or higher.", message)


if __name__ == "__main__":
    unittest.main()
