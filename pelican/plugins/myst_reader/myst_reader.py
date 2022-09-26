"""Reader that processes MyST Markdown and returns HTML5."""
from __future__ import annotations

import math
import os
import re

from bs4 import BeautifulSoup, element
from docutils.core import publish_parts
from docutils.utils.code_analyzer import Lexer, LexerError, NumberLines
from markdown_it.renderer import RendererHTML
from mwc.counter import count_words_in_markdown
from myst_parser.config import main
from myst_parser.docutils_ import Parser as DocutilsParser
from myst_parser.parsers.mdit import create_md_parser
from myst_parser.sphinx_ import Parser as SphinxParser

from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open

DEFAULT_READING_SPEED = 200  # Words per minute

ENCODED_LINKS_TO_RAW_LINKS_MAP = {
    "%7Bstatic%7D": "{static}",
    "%7Battach%7D": "{attach}",
    "%7Bfilename%7D": "{filename}",
}

# Markdown variants supported in default files
# Update as MyST adds or removes support for formats
VALID_BIB_EXTENSIONS = ["bibtex", "bib"]
FILE_EXTENSIONS = [
    "md",
    "mkd",
    "mkdn",
    "mdwn",
    "mdown",
    "markdown",
    "Rmd",
    "myst",
]


def publish(
    source: str,
    extensions: tuple[str],
    parser: "Parser",
):
    """Public API in https://myst-parser.readthedocs.io/en/v0.18.0/docutils.html"""
    parts = publish_parts(
        source=source,
        writer_name="html5",
        settings_overrides={
            "myst_enable_extensions": extensions,
            "embed_stylesheet": False,
        },
        parser=parser,
    )
    output = parts["body"]
    return output.strip()



class MySTReader(BaseReader):
    """Convert files written in MyST Markdown to HTML 5."""

    enabled = True
    file_extensions = FILE_EXTENSIONS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get settings set in pelicanconf.py
        extensions = self.settings.get("MYST_EXTENSIONS", [])
        self.force_sphinx = self.settings.get("MYST_FORCE_SPHINX", False)
        if self.force_sphinx:
            self.parser = SphinxParser()
        else:
            self.parser = DocutilsParser()

        self.parser_config = main.MdParserConfig(
            # renderer="docutils",
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
        if "{cite}" in content:
            bib_files = self._find_bibs(source_path)
        else:
            bib_files = ()

        output = self._run_myst_to_html(content, source_path, bib_files)

        # Replace all occurrences of %7Bstatic%7D to {static},
        # %7Battach%7D to {attach} and %7Bfilename%7D to {filename}
        # so that static links are resolvable by pelican
        for encoded_str, raw_str in ENCODED_LINKS_TO_RAW_LINKS_MAP.items():
            output = output.replace(encoded_str, raw_str)

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
        formatted_fields = self.settings["FORMATTED_FIELDS"]

        # Cycle through the metadata and process them
        metadata = {}

        for key, value in myst_metadata.items():
            key = key.lower()
            if value and isinstance(value, str):
                value = value.strip().strip('"')

            # Process the metadata
            metadata[key] = p_value = self.process_metadata(key, value)

            if key in formatted_fields and isinstance(p_value, str):
                # Convert metadata values in markdown, if any: for example summary
                metadata[key] = self._run_myst_to_html(p_value)

        return metadata

    @staticmethod
    def _extract_contents(html_output):
        """Extracts contents inside a <main> ... </main> tag"""
        soup = BeautifulSoup(html_output, "html.parser")
        main = soup.find("main")
        # Contents inside the main tag
        return " ".join(
            str(tag)
            for tag in main.children
            if isinstance(tag, element.Tag)
        )

    def _extract_metadata(self, content):
        """Extract metadata from MyST markdown content"""
        tokens = self._run_myst_to_tokens(content)

        if not tokens:
            raise ValueError("Could not find metadata. File is empty.")

        frontmatter = tokens[0]
        if frontmatter.type != "front_matter":
            raise ValueError(
                "Could not find front-matter metadata or invalid formatting."
            )

        # Convert the metadata from string -> dict by treating it as YAML
        regex = re.compile(
            r"""(.+?)  # key, first lazy capture group, one or more character
                :\s*  # colon separator and arbitary number of whitespace
                (.*)  # value, next greedy capture group, zero or more character""",
            re.VERBOSE,
        )
        metadata_text = frontmatter.content
        # Parse markdown in frontmatter, if any
        myst_metadata = dict(regex.findall(metadata_text))

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
        # tokens = Lexer(content, "", "none")
        # return tokens
        md = create_md_parser(self.parser_config, RendererHTML)
        return md.parse(content)

    def _run_myst_to_html(self, content, source_path=None, bib_files=None) -> str:
        """Execute the MyST parser and return output."""
        if source_path and (
            self.force_sphinx
            or bib_files
            or any(
                ext in ("dollarmath", "amsmath")
                for ext in self.parser_config.enable_extensions
            )
        ):
            sphinx_conf = dict(
                extensions=[
                    "myst_parser",
                    "sphinx.ext.autosectionlabel",
                    "sphinx.ext.mathjax",
                    "sphinxcontrib.bibtex",
                ],
                bibtex_bibfiles=bib_files,
                master_doc=os.path.basename(source_path).split(".")[0],
                myst_enable_extensions=self.parser_config.enable_extensions,
            )
            # FIXME: See https://github.com/executablebooks/MyST-Parser/issues/327
            # return main.to_docutils(
            #    in_sphinx_env=True,

            return publish(
                content,
                self.parser_config.enable_extensions,
                self.parser,
                # conf=sphinx_conf,
                # srcdir=os.path.dirname(source_path),
            )
        else:
            return publish(
                content, self.parser_config.enable_extensions, self.parser
            )

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


def add_reader(readers):
    """Add the MySTReader as the reader for all MyST Markdown files."""
    for ext in MySTReader.file_extensions:
        readers.reader_classes[ext] = MySTReader


def register():
    """Register the MySTReader."""
    signals.readers_init.connect(add_reader)
