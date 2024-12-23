from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any, Sequence

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML, Token

if TYPE_CHECKING:
    from markdown_it.utils import EnvType, OptionsDict
from myst_parser.config.main import MdParserConfig
from myst_parser.parsers.mdit import create_md_parser


class Renderer(RendererHTML):
    def _render_img(self, token: Token) -> str:
        src = token.info.removeprefix("{image}").strip()
        # FIXME: there should be a better way of processing Docutils style
        # roles and directives! Perhaps using fieldlist plugin?
        if alt := next(
            (line for line in token.content.splitlines() if line.startswith(":alt:")),
            "",
        ):
            alt = alt.removeprefix(":alt:").strip()

        tmpToken = Token(type="", tag="", nesting=0, attrs=token.attrs.copy())
        tmpToken.attrJoin("src", src)
        tmpToken.attrJoin("alt", alt)

        return "<img" + self.renderAttrs(tmpToken) + "/>\n"

    def fence(
        self, tokens: Sequence[Token], idx: int, options: OptionsDict, env: EnvType
    ) -> str:
        token = tokens[idx]
        if token.info.startswith("{image}"):
            return self._render_img(token)
        else:
            return super().fence(tokens, idx, options, env)


def render_colon_fence_image(
    self, tokens: Sequence[Token], idx: int, options: OptionsDict, env: EnvType
) -> str:
    token = tokens[idx]
    if token.info.startswith("{image}"):
        return self._render_img(token)
    else:
        return super().colon_fence(tokens, idx, options, env)


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
    md = create_md_parser(parser_conf, Renderer)
    md.add_render_rule("colon_fence", render_colon_fence_image)
    return md


mdit_init = _mdit_init_from_myst_parser


def mdit_renderer(
    content: str,
    parser: MarkdownIt,
):
    return parser.render(content).strip()
