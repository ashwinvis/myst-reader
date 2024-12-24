"""Tests using invalid metadata for myst-reader plugin."""

import os

import pytest

from pelican.plugins.myst_reader import MySTReader
from pelican.plugins.myst_reader.exceptions import MystReaderContentError
from pelican.tests.support import get_settings

DIR_PATH = os.path.dirname(__file__)
TEST_CONTENT_PATH = os.path.abspath(os.path.join(DIR_PATH, "test_content"))

# Test settings that will be set in pelicanconf.py by plugin users
MYST_EXTENSIONS = []


@pytest.fixture()
def myst_reader_obj():
    settings = get_settings(MYST_EXTENSIONS=MYST_EXTENSIONS)
    return MySTReader(settings)


def test_empty_file(myst_reader_obj):
    """Check if a file is empty."""
    source_path = os.path.join(TEST_CONTENT_PATH, "empty.md")

    # If the file is empty retrieval of metadata should fail
    with pytest.raises(Exception, match="Could not find metadata. File is empty."):
        myst_reader_obj.read(source_path)


msg0 = "Invalid front-matter metadata."
msg1 = "Could not find front-matter metadata or invalid formatting."
# msg2 = "Malformed content or front-matter metadata"


@pytest.mark.parametrize(
    ("source_md", "expected_msg"),
    [
        ("no_metadata.md", msg0),
        ("metadata_start_with_leading_spaces.md", msg0),
        ("metadata_end_with_leading_spaces.md", msg1),
        # FIXME: This should be caught, but the upstream implementation does nothing
        ("no_metadata_end.md", ""),
    ],
)
def test_non_empty_file_no_metadata(myst_reader_obj, source_md, expected_msg):
    """Check if a file has no metadata."""

    source_path = os.path.join(TEST_CONTENT_PATH, source_md)

    # If the file is not empty but has no metadata it should fail
    if expected_msg:
        with pytest.raises(MystReaderContentError, match=expected_msg):
            myst_reader_obj.read(source_path)
