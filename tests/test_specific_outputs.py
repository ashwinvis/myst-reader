"""Tests reading time and summary output from myst-reader plugin."""
import os
import unittest

from pelican.tests.support import get_settings

from myst_reader import MySTReader

DIR_PATH = os.path.dirname(__file__)
TEST_CONTENT_PATH = os.path.abspath(os.path.join(DIR_PATH, "test_content"))

# Test settings that will be set in pelicanconf.py by plugin users
MYST_ARGS = ["--mathjax"]
MYST_EXTENSIONS = ["+smart"]
CALCULATE_READING_TIME = True
FORMATTED_FIELDS = ["summary"]


class TestReadingTimeAndSummary(unittest.TestCase):
    """Test reading time and summary formatted field."""

    def test_default_wpm_reading_time(self):
        """Check if 200 words per minute give us reading time of 1 minute."""
        settings = get_settings(
            MYST_EXTENSIONS=MYST_EXTENSIONS,
            MYST_ARGS=MYST_ARGS,
            CALCULATE_READING_TIME=CALCULATE_READING_TIME,
        )

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "reading_time_content.md")
        _, metadata = myst_reader.read(source_path)

        self.assertEqual("1 minute", str(metadata["reading_time"]))

    def test_user_defined_wpm_reading_time(self):
        """Check if 100 words per minute user defined gives us 2 minutes."""
        settings = get_settings(
            MYST_EXTENSIONS=MYST_EXTENSIONS,
            MYST_ARGS=MYST_ARGS,
            CALCULATE_READING_TIME=CALCULATE_READING_TIME,
            READING_SPEED=100,
        )

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "reading_time_content.md")
        _, metadata = myst_reader.read(source_path)

        self.assertEqual("2 minutes", str(metadata["reading_time"]))

    def test_invalid_user_defined_wpm(self):
        """Check if exception is raised if words per minute is not a number."""
        settings = get_settings(
            MYST_EXTENSIONS=MYST_EXTENSIONS,
            MYST_ARGS=MYST_ARGS,
            CALCULATE_READING_TIME=CALCULATE_READING_TIME,
            READING_SPEED="my words per minute",
        )

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "reading_time_content.md")

        with self.assertRaises(ValueError) as context_manager:
            myst_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("READING_SPEED setting must be a number.", message)

    def test_summary(self):
        """Check if summary output is valid."""
        settings = get_settings(
            MYST_EXTENSIONS=MYST_EXTENSIONS,
            MYST_ARGS=MYST_ARGS,
            FORMATTED_FIELDS=FORMATTED_FIELDS,
        )

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "valid_content_with_citation.md")
        _, metadata = myst_reader.read(source_path)

        self.assertEqual(
            (
                "But this foundational principle of science has now been"
                " called into question by"
                ' <a href="https://www.britannica.com/science/string-theory">'
                "String Theory</a>."
            ),
            str(metadata["summary"]),
        )


if __name__ == "__main__":
    unittest.main()
