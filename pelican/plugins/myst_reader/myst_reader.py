"""Reader that processes MyST Markdown and returns HTML5."""
import json
import math
import os
import re

import bs4
from mwc.counter import count_words_in_markdown
from yaml import safe_load

from myst_parser import main

from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open

DIR_PATH = os.path.dirname(__file__)
TEMPLATES_PATH = os.path.abspath(os.path.join(DIR_PATH, "templates"))
MYST_READER_HTML_TEMPLATE = "myst-reader-default.html"
DEFAULT_READING_SPEED = 200  # Words per minute

ENCODED_LINKS_TO_RAW_LINKS_MAP = {
    "%7Bstatic%7D": "{static}",
    "%7Battach%7D": "{attach}",
    "%7Bfilename%7D": "{filename}",
}

# Markdown variants supported in default files
# Update as MyST adds or removes support for formats
VALID_INPUT_FORMATS = (
    "commonmark",
    "markdown",
)
VALID_OUTPUT_FORMATS = ("html", "html5")
VALID_BIB_EXTENSIONS = ["json", "yaml", "bibtex", "bib"]
FILE_EXTENSIONS = ["md", "mkd", "mkdn", "mdwn", "mdown", "markdown", "Rmd", "myst"]
DEFAULT_MYST_EXECUTABLE = None
MYST_SUPPORTED_MAJOR_VERSION = 0
MYST_SUPPORTED_MINOR_VERSION = 13


class MySTReader(BaseReader):
    """Convert files written in MyST Markdown to HTML 5."""

    enabled = True
    file_extensions = FILE_EXTENSIONS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get settings set in pelicanconf.py
        extensions = self.settings.get("MYST_EXTENSIONS", [])
        self.parser_config = main.MdParserConfig(
            renderer="html",
            enable_extensions=extensions
        )

    def read(self, source_path):
        """Parse MyST Markdown and return HTML5 markup and metadata."""
        # Get the user-defined path to the MyST executable or fall back to default
        # Open Markdown file and read content
        content = ""
        with pelican_open(source_path) as file_content:
            content = file_content

        # Retrieve HTML content and metadata
        metadata = self._extract_metadata(content)
        output = self._create_html(source_path, content)

        return output, metadata

    def _create_html(self, source_path, content):
        """Create HTML5 content."""

        # Find and add bibliography if citations are specified
        if "{cite}" in content and "{bibliography}" not in content:
            for bib_file in self._find_bibs(source_path):
                content += f"""

```{{bibliography}} {bib_file}
```

"""
        # Create HTML content using myst-reader-default.html template
        output = self._run_myst_to_html(content)

        return output

    def _calculate_reading_time(self, content):
        """Calculate time taken to read content."""
        reading_speed = self.settings.get("READING_SPEED", DEFAULT_READING_SPEED)
        wordcount = count_words_in_markdown(content)

        time_unit = "minutes"
        try:
            reading_time = math.ceil(float(wordcount) / float(reading_speed))
            if reading_time == 1:
                time_unit = "minute"
            reading_time = "{} {}".format(str(reading_time), time_unit)
        except ValueError as words_per_minute_nan:
            raise ValueError(
                "READING_SPEED setting must be a number."
            ) from words_per_minute_nan

        return reading_time

    def _process_metadata(self, myst_metadata):
        """Process MyST metadata and add it to Pelican."""
        # Cycle through the metadata and process them
        metadata = {}
        for key, value in myst_metadata.items():
            key = key.lower()
            if value and isinstance(value, str):
                value = value.strip().strip('"')

            # Process the metadata
            p_value = self.process_metadata(key, value)
            # Convert metadata values in markdown, if any: for example summary
            metadata[key] = (
                self._run_myst_to_html(p_value).strip().strip("<p>").strip("</p>")
                if isinstance(p_value, str) else p_value
            )
        return metadata

    def _extract_metadata(self, content):
        tokens = self._run_myst_to_tokens(content)

        frontmatter = tokens[0]
        if frontmatter.type != "front_matter":
            raise ValueError("Could not find front-matter metadata")

        # Convert the metadata from string -> dict by treating it as YAML
        regex = re.compile(
            r"""(.+?)  # key, first lazy capture group, one or more character
                :\s*  # colon separator and arbitary number of whitespace
                (.*)  # value, next greedy capture group, zero or more character""",
            re.VERBOSE
        )
        metadata_text = frontmatter.content
        # Parse markdown in frontmatter, if any
        myst_metadata = dict(regex.findall(metadata_text))

        # Replace all occurrences of %7Bstatic%7D to {static},
        # %7Battach%7D to {attach} and %7Bfilename%7D to {filename}
        # so that static links are resolvable by pelican
        # FIXME: remove?
        #  for encoded_str, raw_str in ENCODED_LINKS_TO_RAW_LINKS_MAP.items():
        #      output = output.replace(encoded_str, raw_str)

        # Parse MyST metadata and add it to Pelican
        metadata = self._process_metadata(myst_metadata)

        # FIXME:
        #  if table_of_contents:
        #      # Create table of contents and add to metadata
        #      metadata["toc"] = self.process_metadata("toc", toc)
        #
        if self.settings.get("CALCULATE_READING_TIME", []):
            # Calculate reading time and add to metadata
            metadata["reading_time"] = self.process_metadata(
                "reading_time", self._calculate_reading_time(content)
            )
        return metadata

    def _run_myst_to_tokens(self, content):
        """Execute the MyST parser and generate the syntax tree / tokens"""
        return main.to_tokens(content, config=self.parser_config)

    def _run_myst_to_html(self, content):
        """Execute the MyST parser and return output."""
        return main.to_html(content, config=self.parser_config)

    @staticmethod
    def _find_bibs(source_path):
        """Find bibliographies recursively in the sourcepath given."""
        bib_files = []
        filename = os.path.splitext(os.path.basename(source_path))[0]
        directory_path = os.path.dirname(os.path.abspath(source_path))
        for root, _, files in os.walk(directory_path):
            for extension in VALID_BIB_EXTENSIONS:
                bib_name = ".".join([filename, extension])
                if bib_name in files:
                    bib_files.append(os.path.join(root, bib_name))
        return bib_files

    @staticmethod
    def _check_input_format(defaults):
        """Check if the input format given is a Markdown variant."""
        reader = ""
        reader_input = defaults.get("reader", "")
        from_input = defaults.get("from", "")

        # Case where no input format is specified
        if not reader_input and not from_input:
            raise ValueError("No input format specified.")

        # Case where both reader and from are specified which is not supported
        if reader_input and from_input:
            raise ValueError(
                (
                    "Specifying both from and reader is not supported."
                    " Please specify just one."
                )
            )

        if reader_input or from_input:
            if reader_input:
                reader = reader_input
            elif from_input:
                reader = from_input

            reader_prefix = reader.replace("+", "-").split("-")[0]

            # Check to see if the reader_prefix matches a valid input format
            if reader_prefix not in VALID_INPUT_FORMATS:
                raise ValueError("Input type has to be a Markdown variant.")
        return reader

    @staticmethod
    def _check_output_format(defaults):
        """Check if the output format is HTML or HTML5."""
        writer_output = defaults.get("writer", "")
        to_output = defaults.get("to", "")

        # Case where both writer and to are specified which is not supported
        if writer_output and to_output:
            raise ValueError(
                (
                    "Specifying both to and writer is not supported."
                    " Please specify just one."
                )
            )

        # Case where neither writer nor to value is set to html
        if (
            writer_output not in VALID_OUTPUT_FORMATS
            and to_output not in VALID_OUTPUT_FORMATS
        ):
            output_formats = " or ".join(VALID_OUTPUT_FORMATS)
            raise ValueError(
                "Output format type must be either {}.".format(output_formats)
            )


def add_reader(readers):
    """Add the MySTReader as the reader for all MyST Markdown files."""
    for ext in MySTReader.file_extensions:
        readers.reader_classes[ext] = MySTReader


def register():
    """Register the MySTReader."""
    signals.readers_init.connect(add_reader)
