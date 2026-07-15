"""Lexical decoder: turn an integer token dump into typed tokens.

Verification-only, per
docs/superpowers/specs/2026-07-11-completability-hardening-design.md §1. It
decodes the same integer stream `./shakedown-debug` prints and that
`src_ir/tokens.py::ARITY` already defines the lexical shape of; it adds no
runtime operations and is never consulted by generated SPL.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from src_ir import tokens


class DecodeError(ValueError):
    """Raised when an integer stream cannot be lexically decoded."""


@dataclass(frozen=True)
class DecodedToken:
    """One token: its code, fixed payloads in order, and decoded text (if
    the token is text-bearing)."""

    code: int
    payloads: tuple[int, ...]
    text: str | None


def decode_stream(values: Sequence[int]) -> list[DecodedToken]:
    """Decode a full dump into typed tokens, or raise `DecodeError`.

    Rejects unknown codes, truncated fixed payloads, unterminated text runs,
    and framing markers (`STREAM_END`, `ITEM_START`, a stray `TEXT_END`) that
    appear outside their permitted phase — the only phase either marker is
    legal in this dump shape is inside a text run's own terminator.
    """
    result: list[DecodedToken] = []
    i = 0
    n = len(values)
    while i < n:
        pos = i
        code = values[i]
        i += 1
        if code == tokens.STREAM_END:
            raise DecodeError(
                f"position {pos}: STREAM_END escaped its permitted phase "
                "(it is a runtime carrier-stack sentinel, never printed by "
                "the debug dump)"
            )
        if code == tokens.ITEM_START:
            raise DecodeError(
                f"position {pos}: ITEM_START escaped its permitted phase "
                "(it is pass-internal and never crosses an act boundary, "
                "so it never appears in a dump)"
            )
        if code == tokens.RAW_HTML_START:
            raise DecodeError(
                f"position {pos}: RAW_HTML_START escaped its permitted phase "
                "(it is pass-internal and never crosses an act boundary, "
                "so it never appears in a dump)"
            )
        if code == tokens.TEXT_END:
            raise DecodeError(
                f"position {pos}: unexpected TEXT_END with no open text run"
            )
        arity = tokens.ARITY.get(code)
        if arity is None:
            raise DecodeError(f"position {pos}: unknown token code {code}")
        if i + arity.payloads > n:
            raise DecodeError(
                f"position {pos}: truncated payloads for code {code}: "
                f"needs {arity.payloads}, only {n - i} remain"
            )
        payloads = tuple(values[i : i + arity.payloads])
        i += arity.payloads
        text: str | None = None
        if arity.has_text:
            glyphs: list[int] = []
            terminated = False
            while i < n:
                value = values[i]
                i += 1
                if value == tokens.TEXT_END:
                    terminated = True
                    break
                if value in (
                    tokens.STREAM_END,
                    tokens.ITEM_START,
                    tokens.RAW_HTML_START,
                ):
                    raise DecodeError(
                        f"position {i - 1}: framing marker {value} escaped "
                        f"its permitted phase inside the text run for code "
                        f"{code}"
                    )
                if value < 1:
                    raise DecodeError(
                        f"position {i - 1}: illegal glyph value {value} "
                        f"inside the text run for code {code} (glyphs are "
                        "always >= 1)"
                    )
                glyphs.append(value)
            if not terminated:
                raise DecodeError(
                    f"position {pos}: unterminated text run for code {code} "
                    "(stream ended before TEXT_END)"
                )
            text = "".join(chr(value) for value in glyphs)
        result.append(DecodedToken(code=code, payloads=payloads, text=text))
    return result
