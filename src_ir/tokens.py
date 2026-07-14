"""Dispatch token codes, framing markers, and the arity table — one
definition, matching docs/spl/token-codes.md. The arity table is the single
home of the stream contract (design spec 2026-07-06): contract drift is
structurally impossible because Act II emission, Act III traversal, Act IV
dispatch, and the debug dump all consume this module."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

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
ITEM_CLOSE = 15

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
    HR: TokenArity(0, False),
    LIST_OPEN: TokenArity(1, False),  # kind: 1 = unordered, 2 = ordered
    LIST_ITEM: TokenArity(1, False),  # looseness: 1 = tight, 2 = loose
    LIST_CLOSE: TokenArity(0, False),
    BLOCKQUOTE_OPEN: TokenArity(0, False),
    BLOCKQUOTE_CLOSE: TokenArity(0, False),
    CODE_BLOCK: TokenArity(0, True),
    ITEM_CLOSE: TokenArity(0, False),
}


class StructuralRole(Enum):
    """Verification-only grammar role, per the recursive container grammar
    in docs/superpowers/specs/2026-07-11-completability-hardening-design.md
    §1. Never consulted by ARITY, emit_token, or any dispatch scene — a
    structural validator built on top of the lexical layer, not a change
    to it. LIST_ITEM is classified ITEM because it currently encodes
    ITEM_OPEN with implicit closure; Spike B may retire that mapping for
    explicit open/close tokens without this role name changing meaning."""

    LEAF_BLOCK = "leaf_block"
    CONTAINER_OPEN = "container_open"
    CONTAINER_CLOSE = "container_close"
    ITEM = "item"
    ITEM_CLOSE = "item_close"
    INLINE_MARKER = "inline_marker"


# Structural roles for every currently allocated token code (docs/spl/token-codes.md),
# including codes not yet emitted by any act. Extending this table never changes a
# numeric code or an ARITY entry.
ROLES: dict[int, StructuralRole] = {
    PARA: StructuralRole.LEAF_BLOCK,
    HEADER: StructuralRole.LEAF_BLOCK,
    HR: StructuralRole.LEAF_BLOCK,
    CODE_BLOCK: StructuralRole.LEAF_BLOCK,
    RAW_HTML_HASH: StructuralRole.LEAF_BLOCK,
    LIST_OPEN: StructuralRole.CONTAINER_OPEN,
    LIST_ITEM: StructuralRole.ITEM,
    LIST_CLOSE: StructuralRole.CONTAINER_CLOSE,
    BLOCKQUOTE_OPEN: StructuralRole.CONTAINER_OPEN,
    BLOCKQUOTE_CLOSE: StructuralRole.CONTAINER_CLOSE,
    ANCHOR_OPEN: StructuralRole.INLINE_MARKER,
    ANCHOR_TITLE: StructuralRole.INLINE_MARKER,
    ANCHOR_TEXT: StructuralRole.INLINE_MARKER,
    ANCHOR_CLOSE: StructuralRole.INLINE_MARKER,
    ITEM_CLOSE: StructuralRole.ITEM_CLOSE,
}
