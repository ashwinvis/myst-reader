"""Tests using invalid metadata for myst-reader plugin."""

import os
import unittest

from pelican.plugins.myst_reader import MySTReader
from pelican.plugins.myst_reader.exceptions import MystReaderContentError
from pelican.tests.support import get_settings

DIR_PATH = os.path.dirname(__file__)
TEST_CONTENT_PATH = os.path.abspath(os.path.join(DIR_PATH, "test_content"))

# Test settings that will be set in pelicanconf.py by plugin users
MYST_EXTENSIONS = []


class TestInvalidMetadata(unittest.TestCase):
    """Invalid Metadata test cases."""

    def test_empty_file(self):
        """Check if a file is empty."""
        settings = get_settings(MYST_EXTENSIONS=MYST_EXTENSIONS)

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "empty.md")

        # If the file is empty retrieval of metadata should fail
        with self.assertRaises(Exception) as context_manager:
            myst_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find metadata. File is empty.", message)

    def test_non_empty_file_no_metadata(self):
        """Check if a file has no metadata."""
        settings = get_settings(MYST_EXTENSIONS=MYST_EXTENSIONS)

        myst_reader = MySTReader(settings)

        msg1 = "Could not find front-matter metadata or invalid formatting."
        msg2 = "Malformed content or front-matter metadata"

        for source_md, expected_msg in (
            ("no_metadata.md", msg1),
            ("metadata_start_with_leading_spaces.md", msg1),
            ("metadata_end_with_leading_spaces.md", msg2),
            ("no_metadata_end.md", msg2),
        ):
            source_path = os.path.join(TEST_CONTENT_PATH, source_md)

            # If the file is not empty but has no metadata it should fail
            with self.assertRaises(MystReaderContentError) as context_manager:
                myst_reader.read(source_path)

            message = str(context_manager.exception)
            self.assertEqual(expected_msg, message)
