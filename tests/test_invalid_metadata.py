"""Tests using invalid metadata for myst-reader plugin."""
import os
import unittest

from pelican.tests.support import get_settings

from pelican.plugins.myst_reader import MySTReader

DIR_PATH = os.path.dirname(__file__)
TEST_CONTENT_PATH = os.path.abspath(os.path.join(DIR_PATH, "test_content"))

# Test settings that will be set in pelicanconf.py by plugin users
MYST_EXTENSIONS = []


class TestInvalidMetadata(unittest.TestCase):
    """Invalid Metadata test cases."""

    def test_empty_file(self):
        """Check if a file is empty."""
        settings = get_settings(
            MYST_EXTENSIONS=MYST_EXTENSIONS
        )

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "empty.md")

        # If the file is empty retrieval of metadata should fail
        with self.assertRaises(Exception) as context_manager:
            myst_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find metadata. File is empty.", message)

    def test_non_empty_file_no_metadata(self):
        """Check if a file has no metadata."""
        settings = get_settings(
            MYST_EXTENSIONS=MYST_EXTENSIONS
        )

        myst_reader = MySTReader(settings)

        for source_md in (
            "no_metadata.md",
            "metadata_start_with_leading_spaces.md",
            "metadata_end_with_leading_spaces.md",
            "no_metadata_end.md",
        ):
            source_path = os.path.join(TEST_CONTENT_PATH, source_md)

            # If the file is not empty but has no metadata it should fail
            with self.assertRaises(Exception) as context_manager:
                myst_reader.read(source_path)

            message = str(context_manager.exception)
            self.assertEqual(
                "Could not find front-matter metadata or invalid formatting.",
                message
            )
