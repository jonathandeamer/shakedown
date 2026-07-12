"""Structural validator for the currently shipped block grammar.

Verification-only, per
docs/superpowers/specs/2026-07-11-completability-hardening-design.md §1. It
checks lexically decoded tokens (`scripts.splc.token_decode`) against the
subset of the recursive container grammar that is actually shipped today:

    document := block*
    block    := PARA | list
    list     := LIST_OPEN item+ LIST_CLOSE
    item     := LIST_ITEM

`LIST_ITEM` may be followed directly by a nested `list` (one nesting level,
per Spike A P2) before the next sibling item or the enclosing `LIST_CLOSE`.
Loose second paragraphs and indented continuations are not separate tokens
today — they are additional glyphs folded into the same `LIST_ITEM` text
run — so a standalone `PARA` is only legal while no list is open. This is
deliberately narrower than the design's full grammar (`block*` inside an
item, blockquotes, other leaf blocks): Spike B decides the concrete
representation for those, and this validator must not accept them early.
"""

from __future__ import annotations

from src_ir import tokens
from src_ir.tokens import StructuralRole

from .token_decode import DecodedToken


class StructuralError(ValueError):
    """Raised when a decoded token sequence violates the shipped grammar."""


def validate_stream(decoded: list[DecodedToken]) -> None:
    """Validate `decoded` against the shipped grammar, or raise `StructuralError`."""
    open_lists: list[int] = []
    awaiting_item: list[bool] = []

    for position, token in enumerate(decoded):
        role = tokens.ROLES.get(token.code)
        if role is None:
            raise StructuralError(
                f"position {position}: token {token.code} has no structural role"
            )

        if role is StructuralRole.LEAF_BLOCK:
            if token.code != tokens.PARA:
                raise StructuralError(
                    f"position {position}: leaf block {token.code} is not yet shipped"
                )
            if open_lists:
                raise StructuralError(
                    f"position {position}: PARA is not yet legal inside an "
                    "open list (shipped grammar: top-level only; loose "
                    "second paragraphs are folded into the item's own text "
                    "run today)"
                )
        elif role is StructuralRole.CONTAINER_OPEN:
            if token.code != tokens.LIST_OPEN:
                raise StructuralError(
                    f"position {position}: container {token.code} is not yet shipped"
                )
            if open_lists and awaiting_item[-1]:
                raise StructuralError(
                    f"position {position}: nested list opened before its "
                    "parent list had any item (list := LIST_OPEN item+ "
                    "LIST_CLOSE requires an item first)"
                )
            open_lists.append(token.payloads[0])
            awaiting_item.append(True)
        elif role is StructuralRole.ITEM:
            if not open_lists:
                raise StructuralError(
                    f"position {position}: item appears outside any open list"
                )
            awaiting_item[-1] = False
        elif role is StructuralRole.CONTAINER_CLOSE:
            if token.code != tokens.LIST_CLOSE:
                raise StructuralError(
                    f"position {position}: container close {token.code} is "
                    "not yet shipped"
                )
            if not open_lists:
                raise StructuralError(
                    f"position {position}: list close has no matching open list"
                )
            if awaiting_item[-1]:
                raise StructuralError(
                    f"position {position}: list closed without any item "
                    "(list := LIST_OPEN item+ LIST_CLOSE requires at least "
                    "one item)"
                )
            open_lists.pop()
            awaiting_item.pop()
        elif role is StructuralRole.INLINE_MARKER:
            raise StructuralError(
                f"position {position}: inline marker {token.code} is not "
                "yet legal in the block-level stream"
            )
        else:
            raise StructuralError(
                f"position {position}: unhandled structural role {role!r}"
            )

    if open_lists:
        raise StructuralError(f"stream ended with {len(open_lists)} list(s) still open")
