from __future__ import annotations

import html
from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceRecord:
    destination: str
    title: str | None


_ESCAPABLE = r"\`*_{}[]()#+-.!"


def _escape_destination(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _escape_title(value: str) -> str:
    return html.escape(value, quote=False).replace('"', "&quot;")


def _normalize_label(value: str) -> str:
    return " ".join(value.lower().split())


def _escape_literal_markdown(value: str) -> str:
    out: list[str] = []
    for char in value:
        if char in "![]()":
            out.append("\\")
        out.append(char)
    return "".join(out)


def _parse_title(value: str) -> str | None:
    stripped = value.strip()
    if not stripped.startswith('"') or len(stripped) < 2:
        return None
    end = stripped.rfind('"')
    if end <= 0:
        return None
    return stripped[1:end]


def _parse_definition(
    lines: list[str], index: int
) -> tuple[ReferenceRecord | None, str | None, int]:
    line = lines[index]
    if line.startswith("    "):
        return None, None, index + 1
    prefix = line[:3]
    leading = len(prefix) - len(prefix.lstrip(" "))
    if leading == 3 and len(line) > 3 and line[3] == " ":
        return None, None, index + 1
    stripped = line[leading:]
    if not stripped.startswith("["):
        return None, None, index + 1
    close = stripped.find("]:")
    if close <= 1:
        return None, None, index + 1
    label = stripped[1:close]
    rest = stripped[close + 2 :].rstrip("\n")
    consumed = index + 1
    if rest.strip() == "" and consumed < len(lines):
        candidate = lines[consumed]
        if len(candidate) - len(candidate.lstrip(" ")) <= 3:
            rest = candidate.strip()
            consumed += 1
    rest = rest.lstrip(" \t")
    if not rest:
        return None, None, index + 1
    title_text: str | None = None
    if rest.startswith("<"):
        end = rest.find(">")
        if end <= 1:
            return None, None, index + 1
        destination = rest[1:end]
        tail = rest[end + 1 :]
    else:
        parts = rest.split(None, 1)
        destination = parts[0]
        tail = parts[1] if len(parts) == 2 else ""
    if tail.strip():
        title_text = _parse_title(tail)
        if title_text is None:
            return None, None, index + 1
    elif consumed < len(lines):
        candidate = lines[consumed]
        if len(candidate) - len(candidate.lstrip(" ")) <= 3:
            maybe_title = _parse_title(candidate.strip())
            if maybe_title is not None:
                title_text = maybe_title
                consumed += 1
    record = ReferenceRecord(
        destination=_escape_destination(destination),
        title=_escape_title(title_text) if title_text is not None else None,
    )
    return record, _normalize_label(label), consumed


def strip_reference_definitions(
    text: str,
) -> tuple[str, dict[str, ReferenceRecord]]:
    lines = text.splitlines(keepends=True)
    kept: list[str] = []
    refs: dict[str, ReferenceRecord] = {}
    index = 0
    while index < len(lines):
        record, label, next_index = _parse_definition(lines, index)
        if record is None or label is None:
            kept.append(lines[index])
            index += 1
            continue
        refs[label] = record
        index = next_index
    stripped = "".join(kept)
    while stripped.endswith("\n\n\n"):
        stripped = stripped[:-1]
    return stripped, refs


def _parse_bracketed(text: str, start: int) -> tuple[str, int] | None:
    if start >= len(text) or text[start] != "[":
        return None
    depth = 1
    index = start + 1
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            index += 2
            continue
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
        index += 1
    return None


def _parse_reference_tail(
    text: str, index: int, label_text: str
) -> tuple[str | None, int, bool]:
    probe = index
    if probe < len(text) and text[probe] == " ":
        probe += 1
    if probe < len(text) and text[probe] == "\n":
        probe += 1
    if probe < len(text) and text[probe] == "[":
        parsed = _parse_bracketed(text, probe)
        if parsed is None:
            return None, index, False
        raw_label, end = parsed
        label = label_text if raw_label == "" else raw_label
        return _normalize_label(label), end, raw_label == ""
    return _normalize_label(label_text), index, False


def _render_anchor(text: str, record: ReferenceRecord) -> str:
    title = f' title="{record.title}"' if record.title is not None else ""
    return f'<a href="{record.destination}"{title}>{_escape_literal_markdown(text)}</a>'


def _render_image(
    alt_text: str, record: ReferenceRecord, *, empty_title: bool = False
) -> str:
    if record.title is not None:
        title = f' "{html.unescape(record.title)}"'
    elif empty_title:
        title = ' ""'
    else:
        title = ""
    return f"![{alt_text}]({html.unescape(record.destination)}{title})"


def _parse_inline_suffix(text: str, index: int) -> tuple[str, str | None, int] | None:
    if index >= len(text) or text[index] != "(":
        return None
    probe = index + 1
    while probe < len(text) and text[probe] in " \t":
        probe += 1
    if probe >= len(text):
        return None
    if text[probe] == "<":
        close = text.find(">", probe)
        if close == -1:
            return None
        destination = text[probe + 1 : close]
        probe = close + 1
    else:
        depth = 0
        dest_start = probe
        while probe < len(text):
            char = text[probe]
            if char == "\\" and probe + 1 < len(text):
                probe += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")" and depth > 0:
                depth -= 1
            elif char == ")" and depth == 0:
                break
            elif char in " \t" and depth == 0:
                break
            probe += 1
        destination = text[dest_start:probe]
    while probe < len(text) and text[probe] in " \t":
        probe += 1
    if probe < len(text) and text[probe] == ")":
        return destination, None, probe + 1
    title: str | None = None
    if probe < len(text) and text[probe] == '"':
        close_paren = text.find(")", probe)
        if close_paren == -1:
            return None
        close_quote = text.rfind('"', probe + 1, close_paren)
        if close_quote == -1:
            return None
        title = text[probe + 1 : close_quote]
        probe = close_quote + 1
        while probe < len(text) and text[probe] in " \t":
            probe += 1
    if probe >= len(text) or text[probe] != ")":
        return None
    return destination, title, probe + 1


def _rewrite_text(stripped: str, refs: dict[str, ReferenceRecord]) -> str:
    out: list[str] = []
    index = 0
    last_explicit_label: str | None = None
    last_explicit_text: str | None = None
    while index < len(stripped):
        line_start = index == 0 or stripped[index - 1] == "\n"
        if line_start and stripped.startswith("    ", index):
            line_end = stripped.find("\n", index)
            if line_end == -1:
                out.append(stripped[index:])
                break
            out.append(stripped[index : line_end + 1])
            index = line_end + 1
            continue
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
            label, next_index, collapsed = _parse_reference_tail(
                stripped, end, link_text
            )
            if (
                collapsed
                and label not in refs
                and last_explicit_label is not None
                and last_explicit_text == link_text
            ):
                label = last_explicit_label
            if label is not None and label in refs:
                out.append(_render_anchor(link_text, refs[label]))
                if next_index != end:
                    last_explicit_label = label
                    last_explicit_text = link_text
                index = next_index
                continue
            if next_index == end and label is not None and "[" in link_text:
                out.append("\\[" + _rewrite_text(link_text, refs) + "\\]")
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


def rewrite_task3_markdown(text: str) -> str:
    stripped, refs = strip_reference_definitions(text)
    return _rewrite_text(stripped, refs)
