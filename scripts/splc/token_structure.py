"""Structural validator for the explicit nested-container block grammar.

Verification-only, per
docs/superpowers/specs/2026-07-11-completability-hardening-design.md §1. It
checks lexically decoded tokens (`scripts.splc.token_decode`) against the
recursive container grammar accepted for Spike B:

    document := block*
    block    := PARA | list | blockquote
    list     := LIST_OPEN (LIST_ITEM block* ITEM_CLOSE)+ LIST_CLOSE
    blockquote := BLOCKQUOTE_OPEN block* BLOCKQUOTE_CLOSE
"""

from __future__ import annotations

from src_ir import tokens
from src_ir.tokens import StructuralRole

from .token_decode import DecodedToken


class StructuralError(ValueError):
    """Raised when a decoded token sequence violates the shipped grammar."""


def validate_stream(decoded: list[DecodedToken]) -> None:
    """Validate `decoded` against the shipped grammar, or raise `StructuralError`."""
    frames: list[tuple[str, int | bool]] = []

    def block_is_legal() -> bool:
        return not frames or frames[-1][0] in {"item", "blockquote"}

    for position, token in enumerate(decoded):
        role = tokens.ROLES.get(token.code)
        if role is None:
            raise StructuralError(
                f"position {position}: token {token.code} has no structural role"
            )

        if role is StructuralRole.LEAF_BLOCK:
            if token.code not in (tokens.PARA, tokens.HEADER, tokens.HR):
                raise StructuralError(
                    f"position {position}: leaf block {token.code} is not yet shipped"
                )
            if not block_is_legal():
                raise StructuralError(
                    f"position {position}: leaf block {token.code} appears where "
                    "a block is not legal"
                )
            if token.code == tokens.HEADER:
                level = token.payloads[0]
                if not (1 <= level <= 6):
                    raise StructuralError(
                        f"position {position}: header level {level} out of range 1-6"
                    )
        elif role is StructuralRole.CONTAINER_OPEN:
            if not block_is_legal():
                raise StructuralError(
                    f"position {position}: container {token.code} appears where "
                    "a block is not legal"
                )
            if token.code == tokens.LIST_OPEN:
                frames.append(("list", False))
            elif token.code == tokens.BLOCKQUOTE_OPEN:
                frames.append(("blockquote", False))
            else:
                raise StructuralError(
                    f"position {position}: container {token.code} is not yet shipped"
                )
        elif role is StructuralRole.ITEM:
            if not frames or frames[-1][0] != "list":
                raise StructuralError(
                    f"position {position}: item appears outside any open list"
                )
            frames[-1] = ("list", True)
            frames.append(("item", token.payloads[0]))
        elif role is StructuralRole.ITEM_CLOSE:
            if not frames or frames[-1][0] != "item":
                raise StructuralError(
                    f"position {position}: item close has no matching open item"
                )
            frames.pop()
        elif role is StructuralRole.CONTAINER_CLOSE:
            if token.code == tokens.LIST_CLOSE:
                if not frames or frames[-1][0] != "list":
                    raise StructuralError(
                        f"position {position}: list close has no matching open list"
                    )
                if not frames[-1][1]:
                    raise StructuralError(
                        f"position {position}: list closed without any item "
                        "(list := LIST_OPEN item+ LIST_CLOSE requires at least "
                        "one item)"
                    )
                frames.pop()
            elif token.code == tokens.BLOCKQUOTE_CLOSE:
                if not frames or frames[-1][0] != "blockquote":
                    raise StructuralError(
                        f"position {position}: blockquote close has no matching "
                        "open blockquote"
                    )
                frames.pop()
            else:
                raise StructuralError(
                    f"position {position}: container close {token.code} is "
                    "not yet shipped"
                )
        elif role is StructuralRole.INLINE_MARKER:
            raise StructuralError(
                f"position {position}: inline marker {token.code} is not "
                "yet legal in the block-level stream"
            )
        else:
            raise StructuralError(
                f"position {position}: unhandled structural role {role!r}"
            )

    if frames:
        raise StructuralError(
            f"stream ended with {len(frames)} structural frame(s) still open"
        )
