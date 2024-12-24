from __future__ import annotations

import importlib
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token
from mdit_py_plugins.amsmath import amsmath_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin

if TYPE_CHECKING:
    from markdown_it.utils import EnvType, OptionsDict
from myst_parser.config.main import MdParserConfig
from myst_parser.parsers.mdit import create_md_parser


class Renderer(RendererHTML):
    def _get_field(self, token: Token, field_name: str) -> str | None:
        # FIXME: there should be a better way of processing Docutils style
        # roles and directives! Perhaps using fieldlist plugin?
        if field := next(
            (
                line
                for line in token.content.splitlines()
                if line.startswith(field_name)
            ),
            "",
        ):
            return field.removeprefix(field_name).strip()

    def _render_img(self, token: Token) -> str:
        src = token.info.removeprefix("{image}").strip()
        alt = self._get_field(token, ":alt:")

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
    self: Renderer,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    token = tokens[idx]
    if token.info.startswith("{image}"):
        return self._render_img(token)
    else:
        return super().colon_fence(tokens, idx, options, env)


def math_renderer(
    content: str,
    options: dict[str, bool] | None = None,
) -> str:
    content = escapeHtml(content)
    content = content.replace("&amp;", "&")

    # NOTE:
    # display_mode is True => block
    # display_mode is False => inline
    display_mode = True if options is None else options.get("display_mode", True)
    return f"\\[ {content} \\]" if display_mode else f"\\( {content} \\)"


def _mdit_init_native(conf: dict[str, Any]) -> MarkdownIt:
    extensions = conf.get("myst_enable_extensions", set("front_matter"))
    md = MarkdownIt()  # .enable(rules)
    for ext in extensions:
        module = importlib.import_module(name=f".{ext}", package="mdit_py_plugins")
        plugin = getattr(module, f"{ext}_plugin")
        md = md.use(plugin)
    return md


def _mdit_init_from_myst_parser(config: MdParserConfig) -> MarkdownIt:
    customized_extensions: list[str] = []
    for ext in "amsmath", "dollarmath":
        if ext in config.enable_extensions:
            config.enable_extensions.remove(ext)
            customized_extensions.append(ext)

    md = create_md_parser(config, Renderer)

    if "dollarmath" in customized_extensions:
        _ = md.use(
            dollarmath_plugin,
            allow_labels=config.dmath_allow_labels,
            allow_space=config.dmath_allow_space,
            allow_digits=config.dmath_allow_digits,
            double_inline=config.dmath_double_inline,
            renderer=math_renderer,
        )
    if "amsmath" in customized_extensions:
        _ = md.use(amsmath_plugin, renderer=math_renderer)

    md.add_render_rule("colon_fence", render_colon_fence_image)

    return md


mdit_init = _mdit_init_from_myst_parser


def mdit_renderer(
    content: str,
    parser: MarkdownIt,
):
    return parser.render(content).strip()
