import importlib
from typing import Any

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from myst_parser.config.main import MdParserConfig
from myst_parser.parsers.mdit import create_md_parser


def _mdit_init_native(conf: dict[str, Any]) -> MarkdownIt:
    extensions = conf.get("myst_enable_extensions", set("front_matter"))
    md = MarkdownIt()  # .enable(rules)
    for ext in extensions:
        module = importlib.import_module(name=f".{ext}", package="mdit_py_plugins")
        plugin = getattr(module, f"{ext}_plugin")
        md = md.use(plugin)
    return md


def _mdit_init_from_myst_parser(parser_conf: MdParserConfig) -> MarkdownIt:
    # extensions = conf.get("myst_enable_extensions", set())
    # parser_conf = MdParserConfig(enable_extensions=extensions)
    return create_md_parser(parser_conf, RendererHTML)


mdit_init = _mdit_init_from_myst_parser


def mdit_renderer(
    content: str,
    parser: MarkdownIt,
):
    return parser.render(content).strip()
