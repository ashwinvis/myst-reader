"""Tests using valid default files for myst-reader plugin."""
import os
import unittest

from pelican.plugins.myst_reader import MySTReader
from pelican.tests.support import get_settings

DIR_PATH = os.path.dirname(__file__)
TEST_CONTENT_PATH = os.path.abspath(os.path.join(DIR_PATH, "test_content"))


class TestValidCasesWithDefaults(unittest.TestCase):
    """Valid test cases using default files."""

    def test_valid_file_with_valid_defaults(self):
        """Check if we get the appropriate output specifying defaults."""
        settings = get_settings()

        myst_reader = MySTReader(settings)

        source_path = os.path.join(TEST_CONTENT_PATH, "valid_content.md")
        output, metadata = myst_reader.read(source_path)

        self.assertEqual(
            (
                "\n<p>This is some valid content that should pass."
                " If it does not pass we will know something is wrong.</p>\n"
            ),
            output,
        )

        self.assertEqual("Valid Content", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_mathjax_with_valid_defaults(self):
        """Check if mathematics is rendered correctly with defaults."""
        settings = get_settings(MYST_EXTENSIONS=["dollarmath", "amsmath"])

        myst_reader = MySTReader(settings)

        source_path = os.path.join(TEST_CONTENT_PATH, "mathjax_content.md")
        output, metadata = myst_reader.read(source_path)

        self.assertEqual(
            (
                r"""<div class="documentwrapper">
 <div class="bodywrapper">
  <div class="body" role="main">
   <div class="math notranslate nohighlight">
    \[
e^{i\theta} = \cos\theta + i \sin\theta.
\]
   </div>
  </div>
 </div>
</div>
"""
            ),
            output,
        )

        self.assertEqual("MathJax Content", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_citations(self):
        """Check if output, citations are valid using citeproc filter."""
        settings = get_settings()

        myst_reader = MySTReader(settings)

        source_path = os.path.join(TEST_CONTENT_PATH, "valid_content_with_citation.md")
        output, metadata = myst_reader.read(source_path)
        self.maxDiff = None  # pylint: disable=invalid-name

        self.assertEqual(
            (
                """\
<div class="documentwrapper">
 <div class="bodywrapper">
  <div class="body" role="main">
   <section id="string-theory">
    <h1>
     String Theory
     <a class="headerlink" href="#string-theory" title="Permalink to this headline">
      ¶
     </a>
    </h1>
    <p>
     But this foundational principle of science has now been called into question by
     <a class="reference external" href="https://www.britannica.com/science/string-theory">
      String Theory
     </a>
     , which is a
relative newcomer to theoretical physics, but one that has captured the common
imagination, judging by the popular explanations that abound on the Web
     <span id="id1">
      [
      <a class="reference internal" href="#id8">
       <span>
        Man
       </span>
      </a>
      ,
      <a class="reference internal" href="#id9">
       <span>
        Woo
       </span>
      </a>
      ,
      <a class="reference internal" href="#id10">
       <span>
        Jon
       </span>
      </a>
      ]
     </span>
     . And whether string theory is or is not
science, Popper notwithstanding, is an issue that is still up for debate
     <span id="id2">
      [
      <a class="reference internal" href="#id7">
       <span>
        Sie
       </span>
      </a>
      ,
      <a class="reference internal" href="#id4">
       <span>
        Cas
       </span>
      </a>
      ,
      <a class="reference internal" href="#id6">
       <span>
        BP
       </span>
      </a>
      ,
      <a class="reference internal" href="#id5">
       <span>
        Fra
       </span>
      </a>
      ]
     </span>
     .
    </p>
    <p id="id3">
     <dl class="citation">
      <dt class="label" id="id6">
       <span class="brackets">
        <a class="fn-backref" href="#id2">
         BP
        </a>
       </span>
      </dt>
      <dd>
       <p>
        Rafael Alves Batista and Joel Primack. Is String theory falsifiable? URL:
        <a class="reference external" href="https://metafact.io/factchecks/30-is-string-theory-falsifiable">
         https://metafact.io/factchecks/30-is-string-theory-falsifiable
        </a>
        (visited on 2020-11-12).
       </p>
      </dd>
      <dt class="label" id="id4">
       <span class="brackets">
        <a class="fn-backref" href="#id2">
         Cas
        </a>
       </span>
      </dt>
      <dd>
       <p>
        Davide Castelvecchi. Feuding physicists turn to philosophy for help. URL:
        <a class="reference external" href="https://www.nature.com/news/feuding-physicists-turn-to-philosophy-for-help-1.19076">
         https://www.nature.com/news/feuding-physicists-turn-to-philosophy-for-help-1.19076
        </a>
        (visited on 2020-11-12).
       </p>
      </dd>
      <dt class="label" id="id5">
       <span class="brackets">
        <a class="fn-backref" href="#id2">
         Fra
        </a>
       </span>
      </dt>
      <dd>
       <p>
        Matthew R Francis. Falsifiability and physics. URL:
        <a class="reference external" href="https://www.scientificamerican.com/article/is-string-theory-science/">
         https://www.scientificamerican.com/article/is-string-theory-science/
        </a>
        (visited on 2020-11-12).
       </p>
      </dd>
      <dt class="label" id="id10">
       <span class="brackets">
        <a class="fn-backref" href="#id1">
         Jon
        </a>
       </span>
      </dt>
      <dd>
       <p>
        Andrew Zimmerman Jones. The Basics of String Theory. URL:
        <a class="reference external" href="https://www.thoughtco.com/what-is-string-theory-2699363">
         https://www.thoughtco.com/what-is-string-theory-2699363
        </a>
        (visited on 2020-11-12).
       </p>
      </dd>
      <dt class="label" id="id8">
       <span class="brackets">
        <a class="fn-backref" href="#id1">
         Man
        </a>
       </span>
      </dt>
      <dd>
       <p>
        Adam Mann. What Is String Theory? URL:
        <a class="reference external" href="https://www.livescience.com/65033-what-is-string-theory.html">
         https://www.livescience.com/65033-what-is-string-theory.html
        </a>
        (visited on 2020-11-12).
       </p>
      </dd>
      <dt class="label" id="id7">
       <span class="brackets">
        <a class="fn-backref" href="#id2">
         Sie
        </a>
       </span>
      </dt>
      <dd>
       <p>
        Ethan Siegel. Why String Theory Is Not A Scientific Theory. URL:
        <a class="reference external" href="https://www.forbes.com/sites/startswithabang/2015/12/23/why-string-theory-is-not-science/">
         https://www.forbes.com/sites/startswithabang/2015/12/23/why-string-theory-is-not-science/
        </a>
        (visited on 2020-11-12).
       </p>
      </dd>
      <dt class="label" id="id9">
       <span class="brackets">
        <a class="fn-backref" href="#id1">
         Woo
        </a>
       </span>
      </dt>
      <dd>
       <p>
        Charlie Wood. What Is String Theory? URL:
        <a class="reference external" href="https://www.space.com/17594-string-theory.html">
         https://www.space.com/17594-string-theory.html
        </a>
        (visited on 2020-11-12).
       </p>
      </dd>
     </dl>
    </p>
   </section>
  </div>
 </div>
</div>
"""
            ),
            output,
        )

        self.assertEqual("Valid Content With Citation", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

        # Read twice to see if warnings are emitted by the logger
        try:
            with self.assertLogs("sphinx.sphinx.application", level="WARNING") as cm:
                output, metadata = myst_reader.read(source_path)
        except AssertionError:
            pass
        else:
            for warning_msg in cm.output:
                self.assertNotIn(
                    "is already registered, its visitors will be overridden",
                    warning_msg,
                )
                self.assertNotIn(
                    "is already registered, it will be overridden", warning_msg
                )

    def test_encoded_to_raw_conversion(self):
        """Check if raw paths are left untouched in output returned."""
        settings = get_settings()

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "valid_content_with_raw_paths.md")
        output, metadata = myst_reader.read(source_path)

        # Setting this so that assert is able to execute the difference
        self.maxDiff = None  # pylint: disable=invalid-name

        self.assertEqual(
            (
                "\n<p>This is some valid content that should pass."
                " If it does not pass we will know something is wrong.</p>\n"
                "<p>Our fictitious internal files are available"
                ' <a href="{filename}/path/to/file">at</a>:</p>\n'
                "<p>Our fictitious static files are available"
                ' <a href="{static}/path/to/file">at</a>:</p>\n'
                "<p>Our fictitious attachments are available"
                ' <a href="{attach}path/to/file">at</a>:</p>\n'
            ),
            output,
        )

        self.assertEqual(
            "Valid Content with Fictitious Raw Paths", str(metadata["title"])
        )
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_img_handling(self):
        """Check if raw paths are left untouched in output returned."""
        settings = get_settings()

        myst_reader = MySTReader(settings)
        source_path = os.path.join(TEST_CONTENT_PATH, "valid_content_with_image.md")
        output, metadata = myst_reader.read(source_path)

        # Setting this so that assert is able to execute the difference
        self.maxDiff = None  # pylint: disable=invalid-name

        self.assertEqual(
            """
<p>This is file contains a image.</p>
<p><img src="/path/to/title.png" alt="Image alt title" /></p>
<p><a href="https://example.com/link.png"><img src="/path/to/link.png" alt="Image with link" /></a></p>
""",
            output,
        )

        self.assertEqual("Valid Content with Image", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))


if __name__ == "__main__":
    unittest.main()
