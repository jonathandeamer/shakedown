"""Act III link/image resolution (Task 3 / 3a–3e) — stream semantics.

Executes at ``ACT_III_START`` in the IR interpreter: rewrite PARA/HEADER text
payloads on Puck using the Act I Rosalind reference table so raw Markdown
links and images resolve without Python ``rewrite_task3_markdown``.

This module is the executable semantics for pure-IR contracts. A pure
op-level IR port of the same algorithms remains the end state for pure
``shakespeare`` execution; these helpers are the proven algorithm those ops
must match.

Semantics track Markdown.pl ``_DoImages`` / ``_DoAnchors`` as reflected by
local oracle witnesses in ``tests/test_act3_links_pure.py``. Deliberately
does **not** call ``rewrite_task3_markdown`` (that helper still applies
pre-Act-I strip and a few production-path divergences such as collapsed
last-explicit reuse).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.slice3_links import (
    ReferenceRecord,
    _escape_destination,
    _escape_literal_markdown,
    _escape_title,
    _parse_bracketed,
    _parse_inline_suffix,
    _parse_reference_tail,
    _render_anchor,
    _render_image,
)
from src_ir import tokens
from src_ir.cast import PUCK, ROSALIND

if TYPE_CHECKING:
    from scripts.splc.interpret import InterpreterState

RECORD_END = -6
_ROSALIND_FLOOR_LEN = 6


def _decode_rosalind_refs(stack: list[int]) -> dict[str, ReferenceRecord]:
    """Decode A1.2 records above the bootstrap floor (later store wins)."""
    if len(stack) < _ROSALIND_FLOOR_LEN:
        return {}
    pos = _ROSALIND_FLOOR_LEN
    refs: dict[str, ReferenceRecord] = {}
    while pos < len(stack):
        label_len = stack[pos]
        pos += 1
        if label_len < 0 or pos + label_len > len(stack):
            return refs
        label = "".join(chr(stack[pos + i]) for i in range(label_len))
        pos += label_len
        if pos >= len(stack):
            return refs
        dest_len = stack[pos]
        pos += 1
        if dest_len < 0 or pos + dest_len > len(stack):
            return refs
        dest = "".join(chr(stack[pos + i]) for i in range(dest_len))
        pos += dest_len
        if pos >= len(stack):
            return refs
        title_len = stack[pos]
        pos += 1
        title: str | None
        if title_len == 0:
            title = None
        else:
            if title_len < 0 or pos + title_len > len(stack):
                return refs
            title = "".join(chr(stack[pos + i]) for i in range(title_len))
            pos += title_len
        if pos >= len(stack) or stack[pos] != RECORD_END:
            return refs
        pos += 1
        refs[label] = ReferenceRecord(destination=dest, title=title)
    return refs


def _resolve_text(stripped: str, refs: dict[str, ReferenceRecord]) -> str:
    """Resolve images then anchors in one text payload (oracle-aligned).

    Unlike ``_rewrite_text``, collapsed ``[text][]`` does **not** fall back to
    the previous explicit reference id when ``text`` is missing from ``refs``
    (Markdown.pl looks up the link text only).
    """
    out: list[str] = []
    index = 0
    # Code-block opacity for four-space / tab lines (same as slice3 rewrite).
    # Act II already emits CODE_BLOCK for true code blocks; this still guards
    # lazy-continuation edge cases inside a PARA payload.
    in_code_block = False
    at_block_boundary = True
    while index < len(stripped):
        line_start = index == 0 or stripped[index - 1] == "\n"
        if line_start:
            line_end = stripped.find("\n", index)
            line_body_end = len(stripped) if line_end == -1 else line_end
            line_content = stripped[index:line_body_end]
            is_blank_line = line_content.strip() == ""
            if is_blank_line:
                in_code_block = False
                at_block_boundary = True
            elif stripped.startswith("    ", index) or stripped.startswith("\t", index):
                if at_block_boundary or in_code_block:
                    if line_end == -1:
                        out.append(stripped[index:])
                        break
                    out.append(stripped[index : line_end + 1])
                    index = line_end + 1
                    in_code_block = True
                    at_block_boundary = False
                    continue
                in_code_block = False
                at_block_boundary = False
            else:
                in_code_block = False
                at_block_boundary = False
        char = stripped[index]
        if char == "\\" and index + 1 < len(stripped):
            out.append(stripped[index : index + 2])
            index += 2
            continue
        if char == "!" and index + 1 < len(stripped) and stripped[index + 1] == "[":
            parsed = _parse_bracketed(stripped, index + 1)
            if parsed is None:
                out.append(char)
                index += 1
                continue
            alt_text, end = parsed
            inline = _parse_inline_suffix(stripped, end)
            if inline is not None:
                destination, title, next_index = inline
                # rewrite_task3 emits title-less images as `![alt](dest "")`.
                # Empty dest `![Empty]()` becomes `![Empty]( "")`, which the
                # suffix parser misreads as dest=`""`. Normalize so a second
                # resolve pass (production rewrite then Act III) is idempotent.
                if title is None and destination == '""':
                    destination = ""
                normalized = ReferenceRecord(
                    destination=_escape_destination(destination),
                    title=_escape_title(title) if title is not None else None,
                )
                out.append(_render_image(alt_text, normalized, empty_title=True))
                index = next_index
                continue
            label, next_index, _ = _parse_reference_tail(stripped, end, alt_text)
            if label is not None and label in refs:
                out.append(_render_image(alt_text, refs[label]))
                index = next_index
                continue
            if next_index != end:
                out.append(_escape_literal_markdown(stripped[index:next_index]))
                index = next_index
                continue
        if char == "[":
            parsed = _parse_bracketed(stripped, index)
            if parsed is None:
                closing = stripped.find("]", index + 1)
                newline = stripped.find("\n", index + 1)
                if closing != -1 and (newline == -1 or closing < newline):
                    literal = stripped[index : closing + 1].replace("\\]", "]")
                    out.append(_escape_literal_markdown(literal))
                    index = closing + 1
                    continue
                out.append(char)
                index += 1
                continue
            link_text, end = parsed
            inline = _parse_inline_suffix(stripped, end)
            if inline is not None:
                destination, title, next_index = inline
                record = ReferenceRecord(
                    destination=_escape_destination(destination),
                    title=_escape_title(title) if title is not None else None,
                )
                out.append(_render_anchor(link_text, record))
                index = next_index
                continue
            label, next_index, _collapsed = _parse_reference_tail(
                stripped, end, link_text
            )
            if label is not None and label in refs:
                out.append(_render_anchor(link_text, refs[label]))
                index = next_index
                continue
            if next_index == end and label is not None and "[" in link_text:
                out.append("\\[" + _resolve_text(link_text, refs) + "\\]")
                index = end
                continue
            if next_index != end or (label is not None and "[" not in link_text):
                literal_end = next_index if next_index != end else end
                out.append(_escape_literal_markdown(stripped[index:literal_end]))
                index = literal_end
                continue
        out.append(char)
        index += 1
    return "".join(out)


def _rewrite_puck_stream(
    stack: list[int], refs: dict[str, ReferenceRecord]
) -> list[int]:
    """Rewrite PARA/HEADER text payloads; leave other tokens unchanged.

    ``stack`` is bottom→top with top = next pop (first token).
    """
    if not stack:
        return stack
    # Pop order is reverse of bottom→top list.
    seq = list(reversed(stack))
    out_pop: list[int] = []
    i = 0
    while i < len(seq):
        code = seq[i]
        i += 1
        if code == tokens.STREAM_END:
            out_pop.append(code)
            out_pop.extend(seq[i:])
            break
        arity = tokens.ARITY.get(code)
        if arity is None:
            out_pop.append(code)
            continue
        out_pop.append(code)
        for _ in range(arity.payloads):
            if i >= len(seq):
                break
            out_pop.append(seq[i])
            i += 1
        if not arity.has_text:
            continue
        chars: list[int] = []
        while i < len(seq) and seq[i] != tokens.TEXT_END:
            chars.append(seq[i])
            i += 1
        if i < len(seq) and seq[i] == tokens.TEXT_END:
            i += 1
        text = "".join(chr(c) for c in chars)
        if code in (tokens.PARA, tokens.HEADER) and refs is not None:
            text = _resolve_text(text, refs)
        elif code in (tokens.PARA, tokens.HEADER):
            text = _resolve_text(text, {})
        out_pop.extend(ord(c) for c in text)
        out_pop.append(tokens.TEXT_END)
    return list(reversed(out_pop))


def apply_act3_link_resolution(state: InterpreterState) -> None:
    """Mutate Puck's token stream: resolve links/images using Rosalind refs."""
    refs = _decode_rosalind_refs(state.stacks[ROSALIND])
    state.stacks[PUCK] = _rewrite_puck_stream(state.stacks[PUCK], refs)
