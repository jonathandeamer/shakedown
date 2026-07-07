"""Dispatch token codes, framing markers, and the arity table — one
definition, matching docs/spl/token-codes.md. The arity table is the single
home of the stream contract (design spec 2026-07-06): contract drift is
structurally impossible because Act II emission, Act III traversal, Act IV
dispatch, and the debug dump all consume this module."""

from __future__ import annotations

from dataclasses import dataclass

PARA = 1
HEADER = 2
HR = 3
LIST_OPEN = 4
LIST_ITEM = 5
LIST_CLOSE = 6
BLOCKQUOTE_OPEN = 7
BLOCKQUOTE_CLOSE = 8
CODE_BLOCK = 9
RAW_HTML_HASH = 10
ANCHOR_OPEN = 11
ANCHOR_TITLE = 12
ANCHOR_TEXT = 13
ANCHOR_CLOSE = 14

# Framing markers — not tokens, never dispatched on by the arity table.
# TEXT_END closes a text-bearing token's glyph run (glyphs are always >= 1).
# STREAM_END is the bottom-of-stream sentinel seeded under every carrier
# stack; consumers pop until they see it. Spoken via stable_utility v0/vneg1
# per speaker, unlike Critical token-code phrases.
TEXT_END = 0
STREAM_END = -1
# ITEM_START brackets a list item's text on the intra-Act-II mixed stream
# (list-pass output): [ITEM_START, glyphs..., TEXT_END]. The paragraph pass
# replaces it with the LIST_ITEM code plus the looseness payload from the
# side channel; it never crosses an act boundary, so it never appears in a
# G2 dump. Spoken via stable_utility vneg2 per speaker.
ITEM_START = -2


@dataclass(frozen=True)
class TokenArity:
    payloads: int  # fixed integer payloads following the code
    has_text: bool  # glyph run terminated by TEXT_END follows the payloads


# Spike-scope vocabulary (2026-07-06 design). Later slices append rows here
# and in docs/spl/token-codes.md together (test_arity_table_matches_doc).
ARITY: dict[int, TokenArity] = {
    PARA: TokenArity(0, True),
    LIST_OPEN: TokenArity(1, False),  # kind: 1 = unordered, 2 = ordered
    LIST_ITEM: TokenArity(1, True),  # looseness: 1 = tight, 2 = loose
    LIST_CLOSE: TokenArity(0, False),
}
