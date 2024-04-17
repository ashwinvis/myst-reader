"""Reader that processes MyST Markdown and returns HTML5."""

from __future__ import annotations

from copy import deepcopy
from enum import Enum
from io import StringIO
import math
import os
from pathlib import Path
from typing import Any, Iterable
import warnings

from bs4 import BeautifulSoup, element
import docutils
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token
from mwc.counter import count_words_in_markdown
from myst_parser.config.main import MdParserConfig
from myst_parser.docutils_ import Parser as DocutilsParser
from myst_parser.parsers.mdit import create_md_parser
import yaml

from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open

from ._docutils_renderer import docutils_renderer
from ._sphinx_renderer import sphinx_renderer
from .exceptions import MystReaderContentError

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

# Default MyST settings common to all parsers.
DEFAULT_MYST_SETTINGS = {
    # Set the default list of warnings to suppress. List available at:
    # https://myst-parser.readthedocs.io/en/latest/configuration.html#build-warnings
    "myst_suppress_warnings": [
        # Ignore the "Document headings start at H2, not H1 [myst.header]" warning,
        # since Pelican will use the title field in the front-matter as the H1 header
        # of the page.
        "myst.header",
    ],
}

# List of implemented renderers.
# TODO: refactor Renderer management with classes to make code more readable and avoid
# passing this enum as parameters everywhere. This should remove lots of duplicate code
# and make the addition of new rendered easier.
RENDERER = Enum("Renderer", ["DOCUTILS", "SPHINX"])

# Default Docutils settings.
# These are the same default as the one hard-coded in Pelican:
# https://github.com/getpelican/pelican/blob/1f6b344/pelican/readers.py#L255-L262
DEFAULT_DOCUTILS_SETTINGS = {
    "initial_header_level": "2",
    "syntax_highlight": "short",
    "input_encoding": "utf-8",
    "halt_level": 2,
    "traceback": True,
    "warning_stream": StringIO(),
    "embed_stylesheet": False,
    # Default set of MyST extensions.
    "myst_enable_extensions": set(),
} | DEFAULT_MYST_SETTINGS

# Default Sphinx settings.
# These are going to be transformed into a Sphinx conf.py file.
DEFAULT_SPHINX_SETTINGS = {
    # Dummy settings required by Sphinx. They have no influence on the produced output.
    "project": "myst2html",
    "author": "pelican-myst-reader",
    # Default set of Sphinx extensions.
    "extensions": {
        "myst_parser",
        "sphinx.ext.mathjax",
        "sphinx.ext.autosectionlabel",
    },
    "bibtex_bibfiles": [],
    # Forces all links to be external
    "myst_all_links_external": True,
    # Default set of MyST extensions.
    "myst_enable_extensions": {
        "colon_fence",
        "deflist",
    },
} | DEFAULT_MYST_SETTINGS


class MySTReader(BaseReader):
    """Convert files written in MyST Markdown to HTML 5."""

    enabled = True
    file_extensions = FILE_EXTENSIONS

    def __init__(self, *args, **kwargs):
        """Fetch settings from ``pelicanconf.py`` and initialize parsers."""
        super().__init__(*args, **kwargs)

        # Merge user-defined settings with defaults.
        self.docutils_settings = deepcopy(
            DEFAULT_DOCUTILS_SETTINGS
        ) | self.settings.get("MYST_DOCUTILS_SETTINGS", dict())
        self.sphinx_settings = deepcopy(DEFAULT_SPHINX_SETTINGS) | self.settings.get(
            "MYST_SPHINX_SETTINGS", dict()
        )

        # Add user-activated MyST extensions to the defaults.
        myst_extensions = self.settings.get("MYST_EXTENSIONS", set())
        if myst_extensions:
            warnings.warn(
                "MYST_EXTENSIONS will soon be deprecated. Use "
                "MYST_DOCUTILS_SETTINGS['myst_enable_extensions'] and "
                "MYST_SPHINX_SETTINGS['myst_enable_extensions'] instead.",
                FutureWarning,
            )
            self.docutils_settings["myst_enable_extensions"].update(myst_extensions)
            self.sphinx_settings["myst_enable_extensions"].update(myst_extensions)

        # Parse and validate MyST settings.
        docutils_myst_conf, normalized_setting = self._validate_myst_settings(
            self.docutils_settings
        )
        # Reintegrate normalized settings to the renderer settings.
        self.docutils_settings |= normalized_setting

        # Parse and validate MyST settings.
        sphinx_myst_conf, normalized_setting = self._validate_myst_settings(
            self.sphinx_settings
        )
        # Reintegrate normalized settings to the renderer settings.
        self.sphinx_settings |= normalized_setting

        # Create a MyST parser for each renderer with its own config.
        self.docutils_myst_parser = create_md_parser(docutils_myst_conf, RendererHTML)
        self.sphinx_myst_parser = create_md_parser(sphinx_myst_conf, RendererHTML)

        # Create a Docutils parser once to not have to re-create it for each file.
        self.force_sphinx = self.settings.get("MYST_FORCE_SPHINX", False)
        # Save the creation of a parser if Sphinx is forced.
        if not self.force_sphinx:
            self.docutils_parser = DocutilsParser()

    def _validate_myst_settings(
        self, settings: dict[str, Any]
    ) -> tuple(MdParserConfig, dict[str, Any]):
        """Parse, validate and normalize MyST settings.

        Returns a MyST parser configuration object and a dictionary of normalized MyST
        settings to be re-integrated to renderer settings.
        """
        # Extract MyST settings from the settings.
        myst_settings = {
            param_id.split("myst_", 1)[1]: param_value
            for param_id, param_value in settings.items()
            if param_id.startswith("myst_")
        }

        myst_config = MdParserConfig(**myst_settings)

        normalized_setting = {
            f"myst_{p_id}": p_value for p_id, p_value in myst_config.as_dict().items()
        }

        return myst_config, normalized_setting

    def read(self, source_path: str) -> tuple[str, dict[str, Any]]:
        """Parse MyST Markdown and return HTML5 markup and metadata."""
        # Get the user-defined path to the MyST executable or fall back to default
        # Open Markdown file and read content
        content = ""
        with pelican_open(source_path) as file_content:
            content = file_content

        # Retrieve HTML content and the renderer used.
        output, renderer = self._create_html(source_path, content)

        # Retrieve metadata with the same configuration as the renderer.
        metadata = self._extract_metadata(content, renderer)

        return output, metadata

    def _create_html(self, source_path: str, content: str) -> tuple[str, RENDERER]:
        """Create HTML5 content."""

        # Find and add bibliography if citations are specified
        if "{cite" in content:
            bib_files = self._find_bibs(source_path)
        else:
            bib_files = ()

        stem = Path(source_path).stem
        output, renderer = self._run_myst_to_html(
            content, bib_files=bib_files, tempdir_suffix=stem
        )

        # Replace all occurrences of %7Bstatic%7D to {static},
        # %7Battach%7D to {attach} and %7Bfilename%7D to {filename}
        # so that static links are resolvable by pelican
        for encoded_str, raw_str in ENCODED_LINKS_TO_RAW_LINKS_MAP.items():
            output = output.replace(encoded_str, raw_str)

        return output, renderer

    def _calculate_reading_time(self, content: str) -> str:
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

    def _process_metadata(self, myst_metadata: dict[str, Any]) -> dict[str, Any]:
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
                metadata[key], _ = self._run_myst_to_html(p_value)

        return metadata

    @staticmethod
    def _extract_contents(html_output: str) -> str:
        """Extracts contents inside a <main> ... </main> tag"""
        soup = BeautifulSoup(html_output, "html.parser")
        main = soup.find("main")
        # Contents inside the main tag
        return " ".join(
            str(tag) for tag in main.children if isinstance(tag, element.Tag)
        )

    def _extract_metadata(self, content: str, renderer: RENDERER) -> dict[str, Any]:
        """Extract metadata from MyST markdown content"""
        tokens = self._run_myst_to_tokens(content, renderer)

        if not tokens:
            raise MystReaderContentError("Could not find metadata. File is empty.")

        frontmatter = tokens[0]
        if frontmatter.type != "front_matter":
            raise MystReaderContentError(
                "Could not find front-matter metadata or invalid formatting."
            )

        metadata_text = frontmatter.content
        # Parse markdown in frontmatter, if any
        myst_metadata = yaml.safe_load(metadata_text)

        for key in ["date", "modified", "Date", "Modified"]:
            try:
                myst_metadata[key] = myst_metadata[key].strftime("%Y-%m-%d")
            except (AttributeError, KeyError):
                pass

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

    def _run_myst_to_tokens(self, content: str, renderer: RENDERER) -> list[Token]:
        """Execute the MyST parser and generate the syntax tree / tokens"""
        myst_parser = (
            self.sphinx_myst_parser
            if renderer == RENDERER.SPHINX
            else self.docutils_myst_parser
        )
        return myst_parser.parse(content)

    def _run_myst_to_html(
        self,
        content: str,
        bib_files: Iterable[str | Path] | None = None,
        tempdir_suffix: str | None = None,
    ) -> tuple(str, RENDERER):
        """Select the right MyST renderer for each file and return output.

        The Sphinx renderer is automatically used if:

        - any math extension is enabled, or
        - BibTeX files are found, or
        - user's settings force the use of Sphinx.
        """
        if (
            self.force_sphinx
            or bib_files
            or self.sphinx_settings["myst_enable_extensions"].intersection(
                ("dollarmath", "amsmath")
            )
            or any(
                syntax in content for syntax in ("{filename}", "{static}", "{attach}")
            )
        ):
            return (
                sphinx_renderer(
                    content,
                    conf=self.sphinx_settings,
                    bib_files=bib_files,
                    tempdir_suffix=tempdir_suffix,
                ),
                RENDERER.SPHINX,
            )
        else:
            try:
                return (
                    docutils_renderer(
                        content,
                        conf=self.docutils_settings,
                        parser=self.docutils_parser,
                    ),
                    RENDERER.DOCUTILS,
                )
            except docutils.utils.SystemMessage as err:
                raise MystReaderContentError(
                    f"Malformed content or front-matter metadata:\n{err}"
                ) from err

    @staticmethod
    def _find_bibs(source_path: str) -> list[str]:
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
