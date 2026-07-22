"""Act III — span pass over the tokenized stream (Spike A P2). Traversal
copies token codes and fixed payloads through untouched and runs the span
gamut only on text-payload glyphs (arity table in src_ir/tokens.py); the 56
span scenes are the Slice-1 port, quirks included (Romeo's write-only
destination discard pile and dead scan decrement, Rosalind's
drained-and-discarded consult pops, the hardcoded Slice 1 anchor payloads,
the `[link(` fallback that drops the current glyph).
Decoded ground truth: docs/superpowers/notes/act3-port-audit.md."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    Char,
    Expr,
    Op,
    act,
    add,
    branch,
    const,
    eq,
    goto,
    halt_act,
    let,
    pop,
    push,
    scene,
    sub,
    val,
)
from src_ir import tokens
from src_ir.act3_resolve_pure import build_resolve_scenes
from src_ir.cast import (
    HECATE,
    HORATIO,
    JULIET,
    LADY_MACBETH,
    MACBETH,
    PROSPERO,
    PUCK,
    ROMEO,
    ROSALIND,
)
from src_ir.stream import RECIPES

# Traversal routes per arity shape: (payloads, has_text). Codes with neither
# payloads nor text copy through and loop; unknown shapes fail the build.
_ARITY_ROUTE = {
    (0, True): "TRAVERSE_OPEN_TEXT",
    (1, False): "TRAVERSE_COPY_PAYLOAD_NEXT",
    (1, True): "TRAVERSE_COPY_PAYLOAD_TEXT",
}

CONT_NONE = 0
FIELD_TAG = 1
FIELD_AUTO_HREF = 2
FIELD_AUTO_TEXT = 3
FIELD_LINK_DEST = 4
FIELD_LINK_TITLE = 5
FIELD_IMAGE_DEST = 6
FIELD_IMAGE_TITLE = 7
RESUME_LINK = 8
RESUME_IMAGE = 9
RESUME_EMPH = 10
RESUME_TRIPLE_EMPH = 11
RESUME_IMAGE_TITLE = 12
RESUME_STRONG = 13
_NEWLINE = const(10)
_SPACE = const(32)


def _traverse_dispatch() -> list[Op]:
    """The token-code dispatch, generated over the arity table. Codes with
    neither payloads nor text ((0, False)) copy through and take the final
    goto back to the token loop."""
    ops: list[Op] = [
        pop(PUCK, recall="nights_next_word"),
        branch(eq(val(PUCK), const(tokens.STREAM_END)), then="LYRIC_OPEN_REVERSE"),
        push(JULIET, val(PUCK)),
    ]
    for code, arity in sorted(tokens.ARITY.items()):
        if code in (tokens.CODE_BLOCK, tokens.RAW_HTML_HASH):
            ops.append(
                branch(eq(val(PUCK), const(code)), then="TRAVERSE_COPY_CODE_TEXT")
            )
            continue
        shape = (arity.payloads, arity.has_text)
        if shape == (0, False):
            continue
        if shape not in _ARITY_ROUTE:
            raise ValueError(f"token {code}: unsupported arity {shape}")
        ops.append(branch(eq(val(PUCK), const(code)), then=_ARITY_ROUTE[shape]))
    ops.append(goto("TRAVERSE_NEXT_TOKEN"))
    return ops


def _k(n: int) -> Expr:
    """Constant, with an explicit recipe when the default decomposition
    would exceed the 4-operator compliance bound."""
    return RECIPES.get(n, const(n))


def _pop_glyph(recall_key: str) -> list[Op]:
    """Pop the next glyph into Puck and decrement Romeo's scan count."""
    return [
        pop(PUCK, recall=recall_key),
        let(ROMEO, sub(val(ROMEO), const(1))),
    ]


def _stream(*codes: int) -> list[Op]:
    """Push token codes / payload bytes onto Juliet's forward stream."""
    return [push(JULIET, _k(code)) for code in codes]


def _entity(*codes: int) -> list[Op]:
    """let+push pairs on Juliet (the entity-emission idiom)."""
    ops: list[Op] = []
    for code in codes:
        ops.append(let(JULIET, _k(code)))
        ops.append(push(JULIET, val(JULIET)))
    return ops


def _stack_text(target: Char, text: bytes) -> list[Op]:
    """Push literal bytes so later pops emit them in forward order."""
    return [
        push(target, const(tokens.STREAM_END)),
        *(push(target, _k(code)) for code in reversed(text)),
    ]


def _current() -> list[Op]:
    """Copy Puck's current glyph to Juliet and push it."""
    return [let(JULIET, val(PUCK)), push(JULIET, val(JULIET))]


ACT: Act = act(
    3,
    ROMEO,
    [
        # --- Traversal phase: walk token stream ---
        scene(
            "ACT_III_START",
            goto("RESOLVE_OPEN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        *build_resolve_scenes(),
        scene(
            "TRAVERSE_NEXT_TOKEN",
            *_traverse_dispatch(),
            anchor=JULIET,
        ),
        scene(
            "TRAVERSE_COPY_PAYLOAD_NEXT",
            pop(PUCK, recall="kept_charge"),
            push(JULIET, val(PUCK)),
            goto("TRAVERSE_NEXT_TOKEN"),
            anchor=JULIET,
        ),
        *(
            [
                scene(
                    "TRAVERSE_COPY_PAYLOAD_TEXT",
                    pop(PUCK, recall="kept_charge"),
                    push(JULIET, val(PUCK)),
                    goto("TRAVERSE_OPEN_TEXT"),
                    anchor=JULIET,
                )
            ]
            if any(
                arity.payloads == 1 and arity.has_text
                for arity in tokens.ARITY.values()
            )
            else []
        ),
        scene(
            "TRAVERSE_COPY_CODE_TEXT",
            pop(PUCK, recall="kept_charge"),
            goto("TRAVERSE_COPY_CODE_GLYPH"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "TRAVERSE_COPY_CODE_GLYPH",
            push(JULIET, val(PUCK)),
            branch(eq(val(PUCK), const(tokens.TEXT_END)), then="TRAVERSE_NEXT_TOKEN"),
            goto("TRAVERSE_COPY_CODE_TEXT"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_DEFINITION_OPEN",
            push(ROMEO, const(tokens.STREAM_END)),
            goto("LYRIC_DEFINITION_UNWIND"),
            companion=PUCK,
        ),
        scene(
            "TRAVERSE_OPEN_TEXT",
            goto("LYRIC_BUFFER_OPEN"),
            companion=PUCK,
        ),
        # --- Buffered source-region scan: drain one text run into Romeo,
        # restore source order above a temporary floor on Puck, then emit
        # ordinary glyphs one-way onto Juliet.
        scene(
            "LYRIC_BUFFER_OPEN",
            push(ROMEO, const(tokens.STREAM_END)),
            goto("LYRIC_BUFFER_DRAIN"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_BUFFER_DRAIN",
            pop(PUCK, recall="buffered_first_glyph"),
            branch(
                eq(val(PUCK), const(tokens.TEXT_END)),
                then="LYRIC_BUFFER_DRAIN_CLOSE",
                else_="LYRIC_BUFFER_KEEP",
            ),
        ),
        scene(
            "LYRIC_BUFFER_KEEP",
            push(ROMEO, val(PUCK)),
            goto("LYRIC_BUFFER_DRAIN"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_BUFFER_DRAIN_CLOSE",
            push(PUCK, const(tokens.TEXT_END)),
            goto("LYRIC_BUFFER_UNWIND"),
            companion=ROMEO,
        ),
        scene(
            "LYRIC_BUFFER_UNWIND",
            pop(ROMEO, recall="buffered_last_glyph"),
            branch(
                eq(val(ROMEO), const(tokens.STREAM_END)),
                then="LYRIC_DEFINITION_OPEN",
                else_="LYRIC_BUFFER_RETURN",
            ),
            anchor=JULIET,
        ),
        scene(
            "LYRIC_BUFFER_RETURN",
            push(PUCK, val(ROMEO)),
            goto("LYRIC_BUFFER_UNWIND"),
            companion=ROMEO,
        ),
        scene(
            "LYRIC_DEFINITION_UNWIND",
            pop(ROMEO, recall="returned_petal"),
            branch(eq(val(ROMEO), const(tokens.STREAM_END)), then="LYRIC_POP_GLYPH"),
            push(PUCK, val(ROMEO)),
            goto("LYRIC_DEFINITION_UNWIND_KEEP"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_DEFINITION_UNWIND_KEEP",
            goto("LYRIC_DEFINITION_UNWIND"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_SCAN_NEXT",
            pop(PUCK, recall="buffered_first_glyph"),
            branch(
                eq(val(PUCK), const(tokens.STREAM_END)),
                then="LYRIC_BUFFER_CLOSE",
            ),
            branch(eq(val(PUCK), _k(38)), then="LYRIC_BUFFER_ENTITY_AMP"),
            branch(eq(val(PUCK), _k(60)), then="LYRIC_BUFFER_ENTITY_ANGLE"),
            goto("LYRIC_ORDINARY_GLYPH"),
        ),
        scene(
            "LYRIC_ORDINARY_GLYPH",
            *_current(),
            goto("LYRIC_SCAN_NEXT"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_BUFFER_ENTITY_AMP",
            *_entity(*b"&amp;"),
            goto("LYRIC_SCAN_NEXT"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_BUFFER_ENTITY_ANGLE",
            *_entity(*b"&lt;"),
            goto("LYRIC_SCAN_NEXT"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_BUFFER_CLOSE",
            push(JULIET, const(tokens.TEXT_END)),
            goto("TRAVERSE_NEXT_TOKEN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        # --- Scan phase: (Puck, Romeo) ---
        scene(
            "LYRIC_POP_GLYPH",
            *_pop_glyph("mornings_first_cut"),
            branch(
                eq(val(PUCK), const(tokens.TEXT_END)),
                then="LYRIC_TEXT_END_DISPATCH",
            ),
            branch(eq(val(PUCK), _k(60)), then="LYRIC_ANGLE_TEST"),  # '<'
            branch(eq(val(PUCK), _k(33)), then="LYRIC_IMAGE_TEST"),  # '!'
            branch(eq(val(PUCK), _k(42)), then="LYRIC_EMPHASIS_OPEN"),  # '*'
            branch(eq(val(PUCK), _k(95)), then="LYRIC_EMPHASIS_OPEN"),  # '_'
            branch(eq(val(PUCK), _k(92)), then="LYRIC_ESCAPE_TEST"),  # '\'
            branch(eq(val(PUCK), _k(96)), then="LYRIC_CODE_RUN"),  # '`'
            branch(
                eq(val(PUCK), _k(91)),  # '['
                then="LYRIC_REFERENCE_POP_AFTER_OPEN",
                else_="LYRIC_TEST_AMPERSAND",
            ),
        ),
        scene(
            "LYRIC_TEXT_END_DISPATCH",
            branch(
                eq(val(LADY_MACBETH), const(RESUME_LINK)),
                then="LYRIC_RESUME_DISPATCH",
            ),
            branch(
                eq(val(LADY_MACBETH), const(RESUME_IMAGE)),
                then="LYRIC_RESUME_DISPATCH",
            ),
            branch(
                eq(val(LADY_MACBETH), const(RESUME_EMPH)),
                then="LYRIC_RESUME_DISPATCH",
            ),
            branch(
                eq(val(LADY_MACBETH), const(RESUME_TRIPLE_EMPH)),
                then="LYRIC_RESUME_DISPATCH",
            ),
            branch(
                eq(val(LADY_MACBETH), const(RESUME_IMAGE_TITLE)),
                then="LYRIC_RESUME_DISPATCH",
            ),
            branch(
                eq(val(LADY_MACBETH), const(RESUME_STRONG)),
                then="LYRIC_RESUME_DISPATCH",
            ),
            branch(
                eq(val(LADY_MACBETH), const(CONT_NONE)),
                then="TRAVERSE_COPY_TERMINATOR",
            ),
            goto("TRAVERSE_COPY_TERMINATOR"),
            anchor=LADY_MACBETH,
            companion=PUCK,
        ),
        # --- Escape machine: a backslash consumes exactly one following
        # glyph. Markdown.pl's escapable set (_EscapeSpecialChars, lines
        # 1271-1286): \ ` * _ { } [ ] ( ) > # + - . ! . A match emits the
        # glyph literally with the backslash dropped; a non-match (including
        # a trailing backslash at TEXT_END) keeps the backslash literal. The
        # backslash branch above runs before the backtick branch so an
        # escaped backtick never opens a code span.
        scene(
            "LYRIC_ESCAPE_TEST",
            *_pop_glyph("hedges_kept_glyph"),
            branch(eq(val(PUCK), const(tokens.TEXT_END)), then="LYRIC_ESCAPE_FALLBACK"),
            branch(eq(val(PUCK), _k(92)), then="LYRIC_ESCAPE_GLYPH"),  # '\'
            branch(eq(val(PUCK), _k(96)), then="LYRIC_ESCAPE_GLYPH"),  # '`'
            branch(eq(val(PUCK), _k(42)), then="LYRIC_ESCAPE_GLYPH"),  # '*'
            branch(eq(val(PUCK), _k(95)), then="LYRIC_ESCAPE_GLYPH"),  # '_'
            branch(eq(val(PUCK), _k(123)), then="LYRIC_ESCAPE_GLYPH"),  # '{'
            branch(eq(val(PUCK), _k(125)), then="LYRIC_ESCAPE_GLYPH"),  # '}'
            branch(eq(val(PUCK), _k(91)), then="LYRIC_ESCAPE_GLYPH"),  # '['
            branch(eq(val(PUCK), _k(93)), then="LYRIC_ESCAPE_GLYPH"),  # ']'
            branch(eq(val(PUCK), _k(40)), then="LYRIC_ESCAPE_GLYPH"),  # '('
            branch(eq(val(PUCK), _k(41)), then="LYRIC_ESCAPE_GLYPH"),  # ')'
            branch(eq(val(PUCK), _k(62)), then="LYRIC_ESCAPE_GLYPH"),  # '>'
            branch(eq(val(PUCK), _k(35)), then="LYRIC_ESCAPE_GLYPH"),  # '#'
            branch(eq(val(PUCK), _k(43)), then="LYRIC_ESCAPE_GLYPH"),  # '+'
            branch(eq(val(PUCK), _k(45)), then="LYRIC_ESCAPE_GLYPH"),  # '-'
            branch(eq(val(PUCK), _k(46)), then="LYRIC_ESCAPE_GLYPH"),  # '.'
            branch(eq(val(PUCK), _k(33)), then="LYRIC_ESCAPE_GLYPH"),  # '!'
            goto("LYRIC_ESCAPE_LITERAL"),
        ),
        scene(
            "LYRIC_ESCAPE_GLYPH",
            *_current(),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_ESCAPE_LITERAL",
            *_entity(*b"\\"),
            *_current(),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_ESCAPE_FALLBACK",
            *_entity(*b"\\"),
            goto("TRAVERSE_COPY_TERMINATOR"),
            anchor=JULIET,
            companion=PUCK,
        ),
        # --- Code-span machine (Amendment A1): two-character register
        # choreography. HECATE's value holds the opener run length; Romeo's
        # stack (above a private STREAM_END sentinel) holds speculative
        # source; Hecate's stack (above a private STREAM_END sentinel) holds
        # the reversed, tail-trimmed span content. Macbeth's value holds the
        # candidate closer run length.
        scene(
            "LYRIC_CODE_RUN",
            let(HECATE, const(1)),
            goto("LYRIC_CODE_COUNT"),
        ),
        scene(
            "LYRIC_CODE_COUNT",
            pop(PUCK, recall="silver_measures_leaf"),
            branch(eq(val(PUCK), _k(96)), then="LYRIC_CODE_COUNT_MORE"),
            goto("LYRIC_CODE_SEEK_OPEN"),
        ),
        scene(
            "LYRIC_CODE_COUNT_MORE",
            let(HECATE, add(val(HECATE), const(1))),
            goto("LYRIC_CODE_COUNT"),
        ),
        scene(
            "LYRIC_CODE_SEEK_OPEN",
            push(ROMEO, const(tokens.STREAM_END)),
            branch(eq(val(PUCK), const(tokens.TEXT_END)), then="LYRIC_CODE_FALLBACK"),
            goto("LYRIC_CODE_KEEP"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_CODE_KEEP",
            push(ROMEO, val(PUCK)),
            goto("LYRIC_CODE_SEEK"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_CODE_SEEK",
            pop(PUCK, recall="sought_moonlit_glyph"),
            branch(eq(val(PUCK), const(tokens.TEXT_END)), then="LYRIC_CODE_FALLBACK"),
            branch(eq(val(PUCK), _k(96)), then="LYRIC_CODE_CAND_OPEN"),
            goto("LYRIC_CODE_KEEP"),
        ),
        scene(
            "LYRIC_CODE_CAND_OPEN",
            let(MACBETH, const(1)),
            goto("LYRIC_CODE_CAND_COUNT"),
        ),
        scene(
            "LYRIC_CODE_CAND_COUNT",
            pop(PUCK, recall="answering_measures_leaf"),
            branch(eq(val(PUCK), _k(96)), then="LYRIC_CODE_CAND_MORE"),
            goto("LYRIC_CODE_COMPARE"),
        ),
        scene(
            "LYRIC_CODE_CAND_MORE",
            let(MACBETH, add(val(MACBETH), const(1))),
            goto("LYRIC_CODE_CAND_COUNT"),
        ),
        scene(
            "LYRIC_CODE_COMPARE",
            branch(
                eq(val(MACBETH), val(HECATE)),
                then="LYRIC_CODE_MATCH",
                else_="LYRIC_CODE_CAND_REPLAY",
            ),
            companion=PUCK,
        ),
        scene(
            "LYRIC_CODE_CAND_REPLAY",
            branch(eq(val(MACBETH), const(0)), then="LYRIC_CODE_CAND_DONE"),
            push(ROMEO, _k(96)),
            let(MACBETH, sub(val(MACBETH), const(1))),
            goto("LYRIC_CODE_CAND_REPLAY"),
        ),
        scene(
            "LYRIC_CODE_CAND_DONE",
            branch(eq(val(PUCK), const(tokens.TEXT_END)), then="LYRIC_CODE_FALLBACK"),
            goto("LYRIC_CODE_KEEP"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_CODE_MATCH",
            push(PUCK, val(PUCK)),  # return the lookahead glyph
            push(HECATE, const(tokens.STREAM_END)),
            goto("LYRIC_CODE_TRIM"),
            anchor=HECATE,
        ),
        scene(
            "LYRIC_CODE_TRIM",
            pop(ROMEO, recall="dew_hemmed_edge"),
            branch(eq(val(ROMEO), _k(32)), then="LYRIC_CODE_TRIM"),
            branch(eq(val(ROMEO), const(9)), then="LYRIC_CODE_TRIM"),
            branch(eq(val(ROMEO), const(tokens.STREAM_END)), then="LYRIC_CODE_BODY"),
            goto("LYRIC_CODE_REV_KEEP"),
            companion=HECATE,
        ),
        scene(
            "LYRIC_CODE_REV_KEEP",
            push(HECATE, val(ROMEO)),
            goto("LYRIC_CODE_REV"),
        ),
        scene(
            "LYRIC_CODE_REV",
            pop(ROMEO, recall="gathered_nettle"),
            branch(eq(val(ROMEO), const(tokens.STREAM_END)), then="LYRIC_CODE_BODY"),
            goto("LYRIC_CODE_REV_KEEP"),
            companion=HECATE,
        ),
        scene(
            "LYRIC_CODE_BODY",
            *_stream(*b"<code>"),
            goto("LYRIC_CODE_HEAD"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_CODE_HEAD",
            pop(HECATE, recall="sheltered_first_glyph"),
            branch(eq(val(HECATE), _k(32)), then="LYRIC_CODE_HEAD"),
            branch(eq(val(HECATE), const(9)), then="LYRIC_CODE_HEAD"),
            branch(eq(val(HECATE), const(tokens.STREAM_END)), then="LYRIC_CODE_CLOSE"),
            goto("LYRIC_CODE_GLYPH"),
            anchor=JULIET,
        ),
        scene(
            "LYRIC_CODE_GLYPH",
            branch(eq(val(HECATE), _k(38)), then="LYRIC_CODE_AMP"),
            branch(eq(val(HECATE), _k(60)), then="LYRIC_CODE_LT"),
            branch(eq(val(HECATE), _k(62)), then="LYRIC_CODE_GT"),
            goto("LYRIC_CODE_PLAIN"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_CODE_PLAIN",
            push(JULIET, val(HECATE)),
            goto("LYRIC_CODE_NEXT"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_CODE_AMP",
            *_entity(*b"&amp;"),
            goto("LYRIC_CODE_NEXT"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_CODE_LT",
            *_entity(*b"&lt;"),
            goto("LYRIC_CODE_NEXT"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_CODE_GT",
            *_entity(*b"&gt;"),
            goto("LYRIC_CODE_NEXT"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_CODE_NEXT",
            pop(HECATE, recall="sheltered_next_glyph"),
            branch(eq(val(HECATE), const(tokens.STREAM_END)), then="LYRIC_CODE_CLOSE"),
            goto("LYRIC_CODE_GLYPH"),
            anchor=JULIET,
        ),
        scene(
            "LYRIC_CODE_CLOSE",
            *_stream(*b"</code>"),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_CODE_FALLBACK",
            push(PUCK, const(tokens.TEXT_END)),
            goto("LYRIC_CODE_REPLAY"),
        ),
        scene(
            "LYRIC_CODE_REPLAY",
            pop(ROMEO, recall="returned_petal"),
            branch(eq(val(ROMEO), const(tokens.STREAM_END)), then="LYRIC_CODE_TICKS"),
            goto("LYRIC_CODE_REPLAY_KEEP"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_CODE_REPLAY_KEEP",
            push(PUCK, val(ROMEO)),
            goto("LYRIC_CODE_REPLAY"),
        ),
        scene(
            "LYRIC_CODE_TICKS",
            branch(eq(val(HECATE), const(0)), then="LYRIC_CODE_TICKS_DONE"),
            push(JULIET, _k(96)),
            let(HECATE, sub(val(HECATE), const(1))),
            goto("LYRIC_GOTO_CODE_TICKS_HEAD"),
            anchor=JULIET,
        ),
        scene(
            "LYRIC_GOTO_CODE_TICKS_HEAD",
            goto("LYRIC_GOTO_CODE_TICKS_TAIL"),
            anchor=JULIET,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_GOTO_CODE_TICKS_TAIL",
            goto("LYRIC_CODE_TICKS"),
            anchor=ROMEO,
            companion=PUCK,
        ),
        scene(
            "LYRIC_CODE_TICKS_DONE",
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=HECATE,
        ),
        # --- Task 4 protected-region scanner. This spike-scope graph keeps
        # HTML/tag fields opaque, requeues raw label/alt/emphasis bodies onto
        # Puck above private TEXT_END boundaries, and routes every private
        # boundary through the A9 resume adapter.
        scene(
            "LYRIC_ANGLE_TEST",
            pop(PUCK, recall="field_first_glyph"),
            branch(eq(val(PUCK), _k(104)), then="LYRIC_AUTOLINK_OPEN"),
            branch(eq(val(PUCK), _k(33)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(47)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(65)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(66)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(67)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(68)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(69)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(70)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(71)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(72)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(73)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(74)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(75)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(76)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(77)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(78)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(79)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(80)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(81)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(82)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(83)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(84)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(85)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(86)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(87)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(88)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(89)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(90)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(97)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(98)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(99)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(100)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(101)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(102)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(103)), then="LYRIC_HTML_OPEN"),
            branch(eq(val(PUCK), _k(115)), then="LYRIC_HTML_OPEN"),
            goto("LYRIC_OPEN_OUTPUT_LT_ENTITY_CURRENT"),
            anchor=JULIET,
        ),
        scene(
            "LYRIC_HTML_OPEN",
            *_entity(*b"<"),
            let(HECATE, const(FIELD_TAG)),
            goto("LYRIC_GOTO_HTML_REQUEUE_HEAD"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_GOTO_HTML_REQUEUE_HEAD",
            goto("LYRIC_GOTO_HTML_REQUEUE_TAIL"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_GOTO_HTML_REQUEUE_TAIL",
            goto("LYRIC_HTML_OPEN_REQUEUE"),
            anchor=PUCK,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_HTML_OPEN_REQUEUE",
            push(PUCK, val(PUCK)),
            goto("LYRIC_GOTO_FIELD_RETRY_HEAD"),
            anchor=PUCK,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_AUTOLINK_OPEN",
            *_stream(*b'<a href="'),
            let(HECATE, const(FIELD_AUTO_HREF)),
            goto("LYRIC_GOTO_AUTOLINK_DUP_HEAD"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_GOTO_AUTOLINK_DUP_HEAD",
            goto("LYRIC_GOTO_AUTOLINK_DUP_TAIL"),
            anchor=JULIET,
            companion=LADY_MACBETH,
        ),
        scene(
            "LYRIC_GOTO_AUTOLINK_DUP_TAIL",
            goto("LYRIC_AUTOLINK_OPEN_DUPLICATE"),
            anchor=LADY_MACBETH,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_AUTOLINK_OPEN_DUPLICATE",
            push(LADY_MACBETH, const(tokens.STREAM_END)),
            goto("LYRIC_AUTOLINK_OPEN_REQUEUE"),
            anchor=LADY_MACBETH,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_AUTOLINK_OPEN_REQUEUE",
            push(PUCK, val(PUCK)),
            goto("LYRIC_GOTO_FIELD_RETRY_HEAD"),
            anchor=PUCK,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_GOTO_FIELD_RETRY_HEAD",
            goto("LYRIC_GOTO_FIELD_RETRY_TAIL"),
            anchor=PUCK,
            companion=HECATE,
        ),
        scene(
            "LYRIC_GOTO_FIELD_RETRY_TAIL",
            goto("LYRIC_FIELD_RETRY"),
            anchor=HECATE,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_FIELD_RETRY",
            let(PROSPERO, val(HECATE)),
            goto("LYRIC_GOTO_FIELD_OPEN_HEAD"),
            anchor=HECATE,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_GOTO_FIELD_OPEN_HEAD",
            goto("LYRIC_GOTO_FIELD_OPEN_TAIL"),
            anchor=HECATE,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_GOTO_FIELD_OPEN_TAIL",
            goto("LYRIC_FIELD_OPEN"),
            anchor=ROMEO,
            companion=MACBETH,
        ),
        scene(
            "LYRIC_FIELD_OPEN",
            push(ROMEO, const(tokens.STREAM_END)),
            let(MACBETH, const(0)),
            goto("LYRIC_FIELD_SCAN"),
            anchor=ROMEO,
            companion=MACBETH,
        ),
        scene(
            "LYRIC_FIELD_SCAN",
            pop(PUCK, recall="field_first_glyph"),
            branch(
                eq(val(PUCK), const(tokens.TEXT_END)),
                then="LYRIC_FIELD_SOURCE_END",
            ),
            branch(eq(val(PROSPERO), const(FIELD_TAG)), then="LYRIC_HTML_FALLBACK"),
            branch(
                eq(val(PROSPERO), const(FIELD_AUTO_HREF)),
                then="LYRIC_AUTOLINK_FALLBACK",
            ),
            branch(
                eq(val(PROSPERO), const(FIELD_LINK_DEST)),
                then="LYRIC_DEST_FALLBACK",
            ),
            branch(
                eq(val(PROSPERO), const(FIELD_IMAGE_DEST)),
                then="LYRIC_DEST_FALLBACK",
            ),
            branch(
                eq(val(PROSPERO), const(FIELD_LINK_TITLE)),
                then="LYRIC_TITLE_FALLBACK",
            ),
            branch(
                eq(val(PROSPERO), const(FIELD_IMAGE_TITLE)),
                then="LYRIC_TITLE_FALLBACK",
            ),
            goto("LYRIC_FIELD_HOLD_REPLAY"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_HTML_FALLBACK",
            branch(eq(val(PUCK), _k(62)), then="LYRIC_FIELD_CLOSE_DISPATCH"),
            goto("LYRIC_FIELD_HOLD_REPLAY"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_AUTOLINK_FALLBACK",
            branch(eq(val(PUCK), _k(62)), then="LYRIC_FIELD_CLOSE_DISPATCH"),
            goto("LYRIC_FIELD_HOLD_REPLAY"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_DEST_FALLBACK",
            branch(eq(val(PUCK), _k(40)), then="LYRIC_DEST_BALANCE"),
            branch(eq(val(PUCK), _k(41)), then="LYRIC_DEST_BALANCE"),
            branch(eq(val(PUCK), _k(32)), then="LYRIC_FIELD_CLOSE_DISPATCH"),
            goto("LYRIC_FIELD_HOLD_REPLAY"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_TITLE_FALLBACK",
            branch(eq(val(PUCK), _k(34)), then="LYRIC_FIELD_CLOSE_DISPATCH"),
            goto("LYRIC_FIELD_HOLD_REPLAY"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_FIELD_HOLD_REPLAY",
            push(ROMEO, val(PUCK)),
            branch(
                eq(val(PROSPERO), const(FIELD_AUTO_HREF)),
                then="LYRIC_AUTOLINK_TEXT_KEEP",
            ),
            goto("LYRIC_FIELD_SCAN"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_AUTOLINK_TEXT_KEEP",
            push(LADY_MACBETH, val(PUCK)),
            goto("LYRIC_FIELD_SCAN"),
            companion=LADY_MACBETH,
        ),
        scene(
            "LYRIC_DEST_BALANCE",
            branch(eq(val(PUCK), _k(40)), then="LYRIC_FIELD_REV_KEEP"),
            branch(eq(val(MACBETH), const(0)), then="LYRIC_DEST_CLOSE_PAIR"),
            let(MACBETH, sub(val(MACBETH), const(1))),
            push(ROMEO, val(PUCK)),
            goto("LYRIC_FIELD_SCAN"),
            anchor=MACBETH,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_DEST_CLOSE_PAIR",
            goto("LYRIC_FIELD_CLOSE_DISPATCH"),
            anchor=ROMEO,
            companion=PUCK,
        ),
        scene(
            "LYRIC_FIELD_REV_KEEP",
            let(MACBETH, add(val(MACBETH), const(1))),
            push(ROMEO, val(PUCK)),
            goto("LYRIC_FIELD_SCAN"),
            anchor=MACBETH,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_FIELD_CLOSE_DISPATCH",
            branch(
                eq(val(PROSPERO), const(FIELD_IMAGE_TITLE)),
                then="LYRIC_FIELD_TITLE_CAPTURE",
            ),
            push(HECATE, const(tokens.STREAM_END)),
            goto("LYRIC_FIELD_REV"),
            anchor=HECATE,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_FIELD_REV",
            pop(ROMEO, recall="field_kept_mark"),
            branch(eq(val(ROMEO), const(tokens.STREAM_END)), then="LYRIC_FIELD_HEAD"),
            goto("LYRIC_FIELD_HOLD"),
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_HOLD",
            push(HECATE, val(ROMEO)),
            goto("LYRIC_FIELD_REV"),
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_HEAD",
            pop(HECATE, recall="fields_first_glyph"),
            branch(
                eq(val(HECATE), const(tokens.STREAM_END)),
                then="LYRIC_FIELD_DRAIN_CLOSE",
            ),
            goto("LYRIC_FIELD_GLYPH"),
            anchor=JULIET,
        ),
        scene(
            "LYRIC_FIELD_GLYPH",
            branch(eq(val(PROSPERO), const(FIELD_TAG)), then="LYRIC_FIELD_PLAIN"),
            branch(eq(val(HECATE), _k(38)), then="LYRIC_FIELD_AMP"),
            branch(eq(val(HECATE), _k(60)), then="LYRIC_FIELD_LT"),
            branch(eq(val(HECATE), _k(62)), then="LYRIC_FIELD_GT"),
            goto("LYRIC_FIELD_PLAIN"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_PLAIN",
            push(JULIET, val(HECATE)),
            goto("LYRIC_FIELD_NEXT"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_AMP",
            *_entity(*b"&amp;"),
            goto("LYRIC_FIELD_NEXT"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_LT",
            *_entity(*b"&lt;"),
            goto("LYRIC_FIELD_NEXT"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_GT",
            *_entity(*b"&gt;"),
            goto("LYRIC_FIELD_NEXT"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_NEXT",
            pop(HECATE, recall="fields_next_glyph"),
            branch(
                eq(val(HECATE), const(tokens.STREAM_END)),
                then="LYRIC_FIELD_DRAIN_CLOSE",
            ),
            goto("LYRIC_FIELD_GLYPH"),
            anchor=JULIET,
        ),
        scene(
            "LYRIC_FIELD_DRAIN_CLOSE",
            branch(
                eq(val(PROSPERO), const(FIELD_TAG)),
                then="LYRIC_FIELD_TITLE_RESTORE",
            ),
            branch(
                eq(val(PROSPERO), const(FIELD_AUTO_HREF)),
                then="LYRIC_AUTOLINK_CLOSE",
            ),
            branch(
                eq(val(PROSPERO), const(FIELD_AUTO_TEXT)),
                then="LYRIC_AUTOLINK_CLOSE",
            ),
            branch(
                eq(val(PROSPERO), const(FIELD_LINK_TITLE)),
                then="LYRIC_FIELD_TITLE_ENTRY_PAIR",
            ),
            branch(
                eq(val(PROSPERO), const(RESUME_IMAGE_TITLE)),
                then="LYRIC_REGION_RESUME",
            ),
            goto("LYRIC_FIELD_TITLE_TEST"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_FIELD_TITLE_ENTRY_PAIR",
            goto("LYRIC_FIELD_TITLE_CAPTURE"),
            anchor=HECATE,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_AUTOLINK_CLOSE",
            branch(
                eq(val(PROSPERO), const(FIELD_AUTO_TEXT)),
                then="LYRIC_AUTOLINK_TEXT_DONE",
            ),
            *_stream(*b'">'),
            let(PROSPERO, const(FIELD_AUTO_TEXT)),
            goto("LYRIC_AUTOLINK_CLOSE_DUPLICATE"),
            anchor=JULIET,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_AUTOLINK_CLOSE_DUPLICATE",
            push(HECATE, const(tokens.STREAM_END)),
            goto("LYRIC_AUTOLINK_TEXT_OPEN"),
            anchor=HECATE,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_AUTOLINK_TEXT_DONE",
            *_stream(*b"</a>"),
            let(LADY_MACBETH, const(CONT_NONE)),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=LADY_MACBETH,
        ),
        scene(
            "LYRIC_FIELD_TITLE_RESTORE",
            *_entity(*b">"),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_AUTOLINK_TEXT_OPEN",
            pop(LADY_MACBETH, recall="staged_stone"),
            branch(
                eq(val(LADY_MACBETH), const(tokens.STREAM_END)),
                then="LYRIC_AUTOLINK_FIELD_HEAD_PAIR",
            ),
            push(HECATE, val(LADY_MACBETH)),
            goto("LYRIC_AUTOLINK_TEXT_OPEN"),
            anchor=LADY_MACBETH,
            companion=HECATE,
        ),
        scene(
            "LYRIC_AUTOLINK_FIELD_HEAD_PAIR",
            goto("LYRIC_FIELD_HEAD"),
            anchor=ROMEO,
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_SOURCE_END",
            push(PUCK, const(tokens.TEXT_END)),
            goto("LYRIC_FIELD_SOURCE_END_LITERAL"),
            anchor=PUCK,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_FIELD_SOURCE_END_LITERAL",
            push(HECATE, const(tokens.STREAM_END)),
            goto("LYRIC_FIELD_LITERAL_REVERSE"),
            anchor=HECATE,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_FIELD_LITERAL_REVERSE",
            pop(ROMEO, recall="field_kept_mark"),
            branch(
                eq(val(ROMEO), const(tokens.STREAM_END)),
                then="LYRIC_FIELD_LITERAL_EMIT",
            ),
            push(HECATE, val(ROMEO)),
            goto("LYRIC_FIELD_LITERAL_REVERSE"),
            anchor=HECATE,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_FIELD_LITERAL_EMIT",
            pop(HECATE, recall="fields_first_glyph"),
            branch(
                eq(val(HECATE), const(tokens.STREAM_END)),
                then="LYRIC_FIELD_LITERAL_POP_PAIR",
            ),
            push(JULIET, val(HECATE)),
            goto("LYRIC_FIELD_LITERAL_EMIT"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_LITERAL_POP_PAIR",
            goto("LYRIC_POP_GLYPH"),
            anchor=JULIET,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_LINK_REGION",
            push(HORATIO, const(tokens.STREAM_END)),
            push(HORATIO, val(PUCK)),
            goto("LYRIC_LABEL_OPEN"),
            companion=HORATIO,
        ),
        scene(
            "LYRIC_LABEL_OPEN",
            pop(PUCK, recall="held_label_glyph"),
            branch(eq(val(PUCK), const(tokens.TEXT_END)), then="LYRIC_REGION_FALLBACK"),
            branch(eq(val(PUCK), _k(93)), then="LYRIC_DEST_OPEN"),
            push(HORATIO, val(PUCK)),
            goto("LYRIC_LABEL_OPEN"),
            anchor=PUCK,
            companion=HORATIO,
        ),
        scene(
            "LYRIC_DEST_OPEN",
            pop(PUCK, recall="field_first_glyph"),
            branch(eq(val(PUCK), _k(40)), then="LYRIC_REGION_TAG_OPEN"),
            goto("LYRIC_REGION_FALLBACK"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_REGION_TAG_OPEN",
            *_stream(*b'<a href="'),
            let(HECATE, const(FIELD_LINK_DEST)),
            goto("LYRIC_FIELD_RETRY"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_IMAGE_TEST",
            pop(PUCK, recall="held_alt_glyph"),
            branch(eq(val(PUCK), _k(91)), then="LYRIC_ALT_OPEN"),
            push(JULIET, _k(33)),
            push(PUCK, val(PUCK)),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_ALT_OPEN",
            push(HORATIO, const(tokens.STREAM_END)),
            goto("LYRIC_IMAGE_TEST_LABEL"),
            companion=HORATIO,
        ),
        scene(
            "LYRIC_IMAGE_TEST_LABEL",
            pop(PUCK, recall="held_alt_glyph"),
            branch(eq(val(PUCK), const(tokens.TEXT_END)), then="LYRIC_REGION_FALLBACK"),
            branch(eq(val(PUCK), _k(93)), then="LYRIC_IMAGE_DEST_START"),
            push(HORATIO, val(PUCK)),
            goto("LYRIC_IMAGE_TEST_LABEL"),
            anchor=PUCK,
            companion=HORATIO,
        ),
        scene(
            "LYRIC_IMAGE_DEST_START",
            pop(PUCK, recall="field_first_glyph"),
            branch(eq(val(PUCK), _k(40)), then="LYRIC_IMAGE_DEST_OPEN"),
            goto("LYRIC_REGION_FALLBACK"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_IMAGE_DEST_OPEN",
            *_stream(*b'<img src="'),
            let(HECATE, const(FIELD_IMAGE_DEST)),
            goto("LYRIC_FIELD_RETRY"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_TITLE_TEST",
            branch(eq(val(PROSPERO), const(FIELD_LINK_DEST)), then="LYRIC_TITLE_OPEN"),
            branch(eq(val(PROSPERO), const(FIELD_IMAGE_DEST)), then="LYRIC_TITLE_OPEN"),
            goto("LYRIC_REGION_FALLBACK"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_TITLE_OPEN",
            branch(eq(val(PUCK), _k(41)), then="LYRIC_FIELD_UNTERMINATED"),
            branch(eq(val(PUCK), _k(32)), then="LYRIC_FIELD_TITLE_CLOSE"),
            goto("LYRIC_REGION_FALLBACK"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_FIELD_TITLE_CLOSE",
            pop(PUCK, recall="field_first_glyph"),
            branch(eq(val(PUCK), _k(34)), then="LYRIC_FIELD_UNTERMINATED_PAIR"),
            goto("LYRIC_REGION_FALLBACK"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_FIELD_UNTERMINATED_PAIR",
            goto("LYRIC_FIELD_UNTERMINATED"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_FIELD_UNTERMINATED",
            branch(eq(val(PUCK), _k(41)), then="LYRIC_REQUEUE_OPEN"),
            branch(
                eq(val(PROSPERO), const(FIELD_IMAGE_DEST)),
                then="LYRIC_FIELD_UNTERMINATED_IMAGE",
            ),
            goto("LYRIC_GOTO_FIELD_UNTERMINATED_HEAD"),
            anchor=PUCK,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_GOTO_FIELD_UNTERMINATED_HEAD",
            goto("LYRIC_GOTO_FIELD_UNTERMINATED_TAIL"),
            anchor=PUCK,
            companion=JULIET,
        ),
        scene(
            "LYRIC_GOTO_FIELD_UNTERMINATED_TAIL",
            goto("LYRIC_FIELD_UNTERMINATED_LINK"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_UNTERMINATED_IMAGE",
            let(HECATE, const(FIELD_IMAGE_TITLE)),
            goto("LYRIC_FIELD_RETRY"),
            anchor=HECATE,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_FIELD_UNTERMINATED_LINK",
            *_stream(*b'" title="'),
            let(HECATE, const(FIELD_LINK_TITLE)),
            goto("LYRIC_FIELD_RETRY"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_FIELD_TITLE_CAPTURE",
            pop(PUCK, recall="field_first_glyph"),
            branch(eq(val(PUCK), _k(41)), then="LYRIC_FIELD_TITLE_REQUEUE_PAIR"),
            goto("LYRIC_REGION_FALLBACK"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_FIELD_TITLE_REQUEUE_PAIR",
            goto("LYRIC_REQUEUE_OPEN"),
            anchor=PUCK,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_REQUEUE_OPEN",
            push(LADY_MACBETH, const(tokens.STREAM_END)),
            push(LADY_MACBETH, val(HECATE)),
            push(LADY_MACBETH, val(MACBETH)),
            push(LADY_MACBETH, val(LADY_MACBETH)),
            branch(eq(val(PROSPERO), const(RESUME_EMPH)), then="LYRIC_LABEL_FALLBACK"),
            branch(
                eq(val(PROSPERO), const(RESUME_STRONG)),
                then="LYRIC_LABEL_FALLBACK",
            ),
            branch(
                eq(val(PROSPERO), const(RESUME_TRIPLE_EMPH)),
                then="LYRIC_LABEL_FALLBACK",
            ),
            branch(
                eq(val(PROSPERO), const(FIELD_LINK_DEST)),
                then="LYRIC_LABEL_REQUEUE",
            ),
            branch(
                eq(val(PROSPERO), const(FIELD_LINK_TITLE)),
                then="LYRIC_LABEL_REQUEUE",
            ),
            branch(
                eq(val(PROSPERO), const(FIELD_IMAGE_DEST)),
                then="LYRIC_ALT_REQUEUE",
            ),
            branch(
                eq(val(PROSPERO), const(FIELD_IMAGE_TITLE)),
                then="LYRIC_ALT_REQUEUE",
            ),
            goto("LYRIC_LABEL_FALLBACK"),
            anchor=LADY_MACBETH,
            companion=PUCK,
        ),
        scene(
            "LYRIC_LABEL_REQUEUE",
            *_stream(*b'">'),
            let(LADY_MACBETH, const(RESUME_LINK)),
            goto("LYRIC_LABEL_REQUEUE_END"),
            anchor=JULIET,
            companion=LADY_MACBETH,
        ),
        scene(
            "LYRIC_LABEL_REQUEUE_END",
            push(PUCK, const(tokens.TEXT_END)),
            goto("LYRIC_REQUEUE_DRAIN"),
            anchor=LADY_MACBETH,
            companion=PUCK,
        ),
        scene(
            "LYRIC_ALT_REQUEUE",
            *_stream(*b'" alt="'),
            branch(
                eq(val(PROSPERO), const(FIELD_IMAGE_TITLE)),
                then="LYRIC_ALT_REQUEUE_WITH_TITLE",
            ),
            goto("LYRIC_ALT_REQUEUE_SELECT"),
            anchor=JULIET,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_ALT_REQUEUE_SELECT",
            let(LADY_MACBETH, const(RESUME_IMAGE)),
            goto("LYRIC_ALT_REQUEUE_END"),
            anchor=LADY_MACBETH,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_ALT_REQUEUE_END",
            push(PUCK, const(tokens.TEXT_END)),
            goto("LYRIC_REQUEUE_DRAIN"),
            anchor=LADY_MACBETH,
            companion=PUCK,
        ),
        scene(
            "LYRIC_ALT_REQUEUE_WITH_TITLE",
            let(LADY_MACBETH, const(RESUME_IMAGE_TITLE)),
            push(PUCK, const(tokens.TEXT_END)),
            goto("LYRIC_REQUEUE_DRAIN"),
            anchor=LADY_MACBETH,
            companion=PUCK,
        ),
        scene(
            "LYRIC_LABEL_FALLBACK",
            let(LADY_MACBETH, val(PROSPERO)),
            push(PUCK, const(tokens.TEXT_END)),
            branch(
                eq(val(LADY_MACBETH), const(RESUME_TRIPLE_EMPH)),
                then="LYRIC_REQUEUE_TRIPLE_CLOSE",
            ),
            goto("LYRIC_REQUEUE_DRAIN"),
            anchor=LADY_MACBETH,
            companion=PUCK,
        ),
        scene(
            "LYRIC_REQUEUE_DRAIN",
            pop(HORATIO, recall="held_label_glyph"),
            branch(
                eq(val(HORATIO), const(tokens.STREAM_END)),
                then="LYRIC_RESUME_SPARE",
            ),
            push(PUCK, val(HORATIO)),
            goto("LYRIC_REQUEUE_DRAIN"),
            anchor=HORATIO,
            companion=PUCK,
        ),
        scene(
            "LYRIC_RESUME_SPARE",
            branch(
                eq(val(LADY_MACBETH), const(RESUME_TRIPLE_EMPH)),
                then="LYRIC_REQUEUE_TRIPLE_OPEN",
            ),
            goto("LYRIC_REQUEUE_POP_PAIR"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_REQUEUE_POP_PAIR",
            goto("LYRIC_POP_GLYPH"),
            anchor=JULIET,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_REQUEUE_TRIPLE_OPEN",
            push(PUCK, _k(42)),
            goto("LYRIC_REQUEUE_POP_PAIR"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_REQUEUE_TRIPLE_CLOSE",
            push(PUCK, _k(42)),
            goto("LYRIC_REQUEUE_DRAIN"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_EMPHASIS_OPEN",
            let(PROSPERO, val(PUCK)),
            let(HECATE, const(1)),
            goto("LYRIC_EMPHASIS_OPEN_BUFFER"),
            anchor=HECATE,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_EMPHASIS_OPEN_BUFFER",
            push(HORATIO, const(tokens.STREAM_END)),
            goto("LYRIC_EMPHASIS_COUNT_MORE"),
            anchor=HECATE,
            companion=HORATIO,
        ),
        scene(
            "LYRIC_EMPHASIS_COUNT_MORE",
            pop(PUCK, recall="answering_starlight"),
            branch(
                eq(val(PUCK), const(tokens.TEXT_END)),
                then="LYRIC_EMPHASIS_SOURCE_END_PAIR",
            ),
            branch(eq(val(PUCK), val(PROSPERO)), then="LYRIC_EMPHASIS_CAND_MORE"),
            goto("LYRIC_EMPHASIS_COUNT_HOLD"),
            anchor=PUCK,
            companion=HECATE,
        ),
        scene(
            "LYRIC_EMPHASIS_COUNT_HOLD",
            push(HORATIO, val(PUCK)),
            branch(eq(val(HECATE), const(1)), then="LYRIC_EMPHASIS_SPARE"),
            goto("LYRIC_EMPHASIS_SEEK"),
            anchor=PUCK,
            companion=HORATIO,
        ),
        scene(
            "LYRIC_EMPHASIS_SPARE",
            branch(eq(val(PUCK), _k(32)), then="LYRIC_EMPHASIS_SOURCE_END"),
            branch(eq(val(PUCK), _k(9)), then="LYRIC_EMPHASIS_SOURCE_END"),
            goto("LYRIC_EMPHASIS_SEEK"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_EMPHASIS_SOURCE_END_PAIR",
            push(PUCK, const(tokens.TEXT_END)),
            goto("LYRIC_EMPHASIS_SOURCE_END"),
            anchor=PUCK,
            companion=HECATE,
        ),
        scene(
            "LYRIC_EMPHASIS_CAND_MORE",
            let(HECATE, add(val(HECATE), const(1))),
            goto("LYRIC_EMPHASIS_COUNT_MORE"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "LYRIC_EMPHASIS_SEEK",
            pop(PUCK, recall="answering_starlight"),
            branch(
                eq(val(PUCK), const(tokens.TEXT_END)),
                then="LYRIC_EMPHASIS_SOURCE_END_PAIR",
            ),
            branch(eq(val(PUCK), val(PROSPERO)), then="LYRIC_EMPHASIS_CAND_COUNT"),
            goto("LYRIC_EMPHASIS_SEEK_HOLD"),
            anchor=PUCK,
            companion=HECATE,
        ),
        scene(
            "LYRIC_EMPHASIS_SEEK_HOLD",
            push(HORATIO, val(PUCK)),
            goto("LYRIC_EMPHASIS_SEEK"),
            anchor=PUCK,
            companion=HORATIO,
        ),
        scene(
            "LYRIC_EMPHASIS_CAND_COUNT",
            let(MACBETH, const(1)),
            goto("LYRIC_EMPHASIS_COMPARE"),
            anchor=MACBETH,
            companion=PUCK,
        ),
        scene(
            "LYRIC_EMPHASIS_COMPARE",
            pop(PUCK, recall="answering_starlight"),
            branch(eq(val(PUCK), val(PROSPERO)), then="LYRIC_EMPHASIS_MATCH_MORE"),
            branch(eq(val(MACBETH), val(HECATE)), then="LYRIC_EMPHASIS_MATCH"),
            branch(
                eq(val(PUCK), const(tokens.TEXT_END)),
                then="LYRIC_EMPHASIS_CAND_SOURCE_END",
            ),
            goto("LYRIC_EMPHASIS_FALLBACK"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_EMPHASIS_MATCH_MORE",
            let(MACBETH, add(val(MACBETH), const(1))),
            goto("LYRIC_EMPHASIS_COMPARE"),
            anchor=MACBETH,
            companion=PUCK,
        ),
        scene(
            "LYRIC_EMPHASIS_FALLBACK",
            push(HORATIO, val(PROSPERO)),
            goto("LYRIC_EMPHASIS_REPLAY"),
            companion=HORATIO,
        ),
        scene(
            "LYRIC_EMPHASIS_REPLAY",
            branch(
                eq(val(MACBETH), const(1)),
                then="LYRIC_EMPHASIS_CAND_KEEP_LOOKAHEAD",
            ),
            let(MACBETH, sub(val(MACBETH), const(1))),
            push(HORATIO, val(PROSPERO)),
            goto("LYRIC_EMPHASIS_REPLAY"),
            anchor=MACBETH,
            companion=HORATIO,
        ),
        scene(
            "LYRIC_EMPHASIS_CAND_KEEP_LOOKAHEAD",
            push(HORATIO, val(PUCK)),
            goto("LYRIC_GOTO_EMPHASIS_SEEK_HEAD"),
            companion=HORATIO,
        ),
        scene(
            "LYRIC_GOTO_EMPHASIS_SEEK_HEAD",
            goto("LYRIC_GOTO_EMPHASIS_SEEK_TAIL"),
            anchor=ROMEO,
            companion=PUCK,
        ),
        scene(
            "LYRIC_GOTO_EMPHASIS_SEEK_TAIL",
            goto("LYRIC_EMPHASIS_SEEK"),
            anchor=PUCK,
            companion=HECATE,
        ),
        scene(
            "LYRIC_EMPHASIS_CAND_SOURCE_END",
            push(PUCK, const(tokens.TEXT_END)),
            goto("LYRIC_EMPHASIS_SOURCE_END"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_EMPHASIS_MATCH",
            push(PUCK, val(PUCK)),
            branch(eq(val(HECATE), const(1)), then="LYRIC_EMPHASIS_EMIT_OPEN"),
            goto("LYRIC_EMPHASIS_MATCH_STRONG"),
            anchor=PUCK,
            companion=HECATE,
        ),
        scene(
            "LYRIC_EMPHASIS_MATCH_STRONG",
            branch(eq(val(HECATE), const(3)), then="LYRIC_EMPHASIS_TRIPLE_CLOSE"),
            let(PROSPERO, const(RESUME_STRONG)),
            goto("LYRIC_EMPHASIS_MATCH_OUTPUT"),
            anchor=PUCK,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_EMPHASIS_MATCH_OUTPUT",
            *_stream(*b"<strong>"),
            goto("LYRIC_REQUEUE_OPEN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_EMPHASIS_TRIPLE_CLOSE",
            let(PROSPERO, const(RESUME_TRIPLE_EMPH)),
            goto("LYRIC_EMPHASIS_TRIPLE_OUTPUT"),
            anchor=PUCK,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_EMPHASIS_TRIPLE_OUTPUT",
            *_stream(*b"<strong>"),
            goto("LYRIC_REQUEUE_OPEN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_EMPHASIS_EMIT_OPEN",
            let(PROSPERO, const(RESUME_EMPH)),
            goto("LYRIC_EMPHASIS_EMIT_OUTPUT"),
            anchor=PUCK,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_EMPHASIS_EMIT_OUTPUT",
            *_stream(*b"<em>"),
            goto("LYRIC_REQUEUE_OPEN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_EMPHASIS_SOURCE_END",
            push(HECATE, const(tokens.STREAM_END)),
            let(JULIET, val(PROSPERO)),
            push(JULIET, val(JULIET)),
            goto("LYRIC_EMPHASIS_LITERAL_REVERSE"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_EMPHASIS_LITERAL_REVERSE",
            pop(HORATIO, recall="held_label_glyph"),
            branch(
                eq(val(HORATIO), const(tokens.STREAM_END)),
                then="LYRIC_EMPHASIS_LITERAL_EMIT",
            ),
            push(HECATE, val(HORATIO)),
            goto("LYRIC_EMPHASIS_LITERAL_REVERSE"),
            anchor=HORATIO,
            companion=HECATE,
        ),
        scene(
            "LYRIC_EMPHASIS_LITERAL_EMIT",
            pop(HECATE, recall="fields_first_glyph"),
            branch(
                eq(val(HECATE), const(tokens.STREAM_END)),
                then="LYRIC_EMPHASIS_LITERAL_POP_PAIR",
            ),
            push(JULIET, val(HECATE)),
            goto("LYRIC_EMPHASIS_LITERAL_EMIT"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_EMPHASIS_LITERAL_POP_PAIR",
            goto("LYRIC_POP_GLYPH"),
            anchor=JULIET,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_REGION_FALLBACK",
            pop(HORATIO, recall="held_label_glyph"),
            branch(
                eq(val(HORATIO), const(tokens.STREAM_END)),
                then="LYRIC_RETURN_TO_SCAN",
            ),
            push(JULIET, val(HORATIO)),
            goto("LYRIC_REGION_FALLBACK"),
            anchor=JULIET,
            companion=HORATIO,
        ),
        scene(
            "LYRIC_RESUME_DISPATCH",
            let(PROSPERO, val(LADY_MACBETH)),
            goto("LYRIC_RESUME_POP_PARENT_SELECTOR"),
            anchor=LADY_MACBETH,
            companion=PROSPERO,
        ),
        scene(
            "LYRIC_RESUME_POP_PARENT_SELECTOR",
            pop(LADY_MACBETH, recall="staged_stone"),
            goto("LYRIC_RESUME_SAVE_PARENT_SELECTOR"),
            anchor=LADY_MACBETH,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_RESUME_SAVE_PARENT_SELECTOR",
            let(HORATIO, val(LADY_MACBETH)),
            goto("LYRIC_RESUME_POP_MACBETH"),
            anchor=HORATIO,
            companion=LADY_MACBETH,
        ),
        scene(
            "LYRIC_RESUME_POP_MACBETH",
            pop(LADY_MACBETH, recall="staged_stone"),
            goto("LYRIC_RESUME_RESTORE_MACBETH"),
            anchor=LADY_MACBETH,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_RESUME_RESTORE_MACBETH",
            let(MACBETH, val(LADY_MACBETH)),
            goto("LYRIC_RESUME_POP_HECATE"),
            anchor=LADY_MACBETH,
            companion=MACBETH,
        ),
        scene(
            "LYRIC_RESUME_POP_HECATE",
            pop(LADY_MACBETH, recall="staged_stone"),
            goto("LYRIC_RESUME_RESTORE_HECATE"),
            anchor=LADY_MACBETH,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_RESUME_RESTORE_HECATE",
            let(HECATE, val(LADY_MACBETH)),
            goto("LYRIC_RESUME_VERIFY_FLOOR"),
            anchor=LADY_MACBETH,
            companion=HECATE,
        ),
        scene(
            "LYRIC_RESUME_VERIFY_FLOOR",
            pop(LADY_MACBETH, recall="staged_stone"),
            branch(
                eq(val(LADY_MACBETH), const(tokens.STREAM_END)),
                then="LYRIC_RESUME_RESTORE_PARENT_SELECTOR",
                else_="LYRIC_RESUME_FLOOR_FAIL",
            ),
            anchor=LADY_MACBETH,
            companion=ROMEO,
        ),
        scene(
            "LYRIC_RESUME_RESTORE_PARENT_SELECTOR",
            let(LADY_MACBETH, val(HORATIO)),
            goto("LYRIC_RESUME_CLOSE_DISPATCH"),
            anchor=LADY_MACBETH,
            companion=HORATIO,
        ),
        scene(
            "LYRIC_RESUME_CLOSE_DISPATCH",
            branch(
                eq(val(PROSPERO), const(RESUME_LINK)),
                then="LYRIC_REGION_RESUME_PAIR",
            ),
            branch(
                eq(val(PROSPERO), const(RESUME_IMAGE)),
                then="LYRIC_REGION_RESUME_PAIR",
            ),
            branch(
                eq(val(PROSPERO), const(RESUME_IMAGE_TITLE)),
                then="LYRIC_IMAGE_TITLE_CLOSE",
            ),
            branch(
                eq(val(PROSPERO), const(RESUME_EMPH)),
                then="LYRIC_EMPHASIS_RESUME",
            ),
            branch(
                eq(val(PROSPERO), const(RESUME_STRONG)),
                then="LYRIC_EMPHASIS_RESUME",
            ),
            goto("LYRIC_EMPHASIS_RESUME"),
            anchor=PROSPERO,
            companion=LADY_MACBETH,
        ),
        scene(
            "LYRIC_REGION_RESUME_PAIR",
            goto("LYRIC_REGION_RESUME"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_REGION_RESUME",
            branch(
                eq(val(PROSPERO), const(RESUME_LINK)),
                then="LYRIC_REGION_LINK_CLOSE",
            ),
            *_stream(*b'" />'),
            goto("LYRIC_POP_GLYPH"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_REGION_LINK_CLOSE",
            *_stream(*b"</a>"),
            goto("LYRIC_POP_GLYPH"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_IMAGE_TITLE_CLOSE",
            *_stream(*b'" title="'),
            push(HECATE, const(tokens.STREAM_END)),
            goto("LYRIC_FIELD_REV"),
            anchor=JULIET,
            companion=HECATE,
        ),
        scene(
            "LYRIC_EMPHASIS_RESUME",
            branch(
                eq(val(PROSPERO), const(RESUME_EMPH)),
                then="LYRIC_EMPHASIS_CLOSE_EM",
            ),
            *_stream(*b"</strong>"),
            goto("LYRIC_POP_GLYPH"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_EMPHASIS_CLOSE_EM",
            *_stream(*b"</em>"),
            goto("LYRIC_POP_GLYPH"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_RESUME_FLOOR_FAIL",
            halt_act(),
            companion=PUCK,
        ),
        scene(
            "LYRIC_TEST_AMPERSAND",
            branch(
                eq(val(PUCK), _k(38)),  # '&'
                then="LYRIC_AMP_POP_NEXT",
                else_="LYRIC_TEST_LEFT_ANGLE",
            ),
            companion=PUCK,
        ),
        scene(
            "LYRIC_REFERENCE_POP_AFTER_OPEN",
            *_pop_glyph("brackets_first_petal"),
            branch(
                eq(val(PUCK), _k(108)),  # 'l'
                then="LYRIC_REFERENCE_LINK_POP_BODY",
                else_="LYRIC_REFERENCE_TEST_ATT_TEXT",
            ),
        ),
        scene(
            "LYRIC_REFERENCE_TEST_ATT_TEXT",
            branch(
                eq(val(PUCK), _k(65)),  # 'A'
                then="LYRIC_REFERENCE_ATT_POP_BODY",
                else_="LYRIC_LINK_REGION",
            ),
            companion=PUCK,
        ),
        scene(
            "LYRIC_REFERENCE_LINK_POP_BODY",
            *_pop_glyph("links_second_petal"),
            *_pop_glyph("links_third_petal"),
            *_pop_glyph("links_fourth_petal"),
            *_pop_glyph("links_closing_petal"),
            *_pop_glyph("links_following_air"),
            branch(
                eq(val(PUCK), _k(32)),  # ' '
                then="LYRIC_REFERENCE_ONE_POP_LABEL",
                else_="LYRIC_LINK_TEST_INLINE_OPEN",
            ),
        ),
        scene(
            "LYRIC_LINK_TEST_INLINE_OPEN",
            branch(
                eq(val(PUCK), _k(40)),  # '('
                then="LYRIC_INLINE_POP_FIRST_DESTINATION",
                else_="LYRIC_OPEN_OUTPUT_LINK_FALLBACK",
            ),
            companion=PUCK,
        ),
        scene(
            "LYRIC_INLINE_POP_FIRST_DESTINATION",
            *_pop_glyph("inline_paths_first_gate"),
            branch(
                eq(val(PUCK), _k(47)),  # '/'
                then="LYRIC_INLINE_DEST_DIRECT_CHECK",
                else_="LYRIC_INLINE_TEST_BRACKETED_DESTINATION",
            ),
        ),
        scene(
            "LYRIC_INLINE_TEST_BRACKETED_DESTINATION",
            branch(
                eq(val(PUCK), _k(60)),  # '<'
                then="LYRIC_INLINE_DEST_BRACKETED_POP",
                else_="LYRIC_OPEN_OUTPUT_LINK_FALLBACK",
            ),
            companion=PUCK,
        ),
        scene(
            "LYRIC_INLINE_DEST_DIRECT_CHECK",
            branch(
                eq(val(PUCK), _k(41)),  # ')'
                then="LYRIC_OPEN_OUTPUT_INLINE_LINK",
                else_="LYRIC_INLINE_DEST_DIRECT_KEEP",
            ),
            companion=PUCK,
        ),
        scene(
            "LYRIC_INLINE_DEST_DIRECT_KEEP",
            push(ROMEO, val(PUCK)),  # destination discard pile (quirk)
            *_pop_glyph("inline_paths_next_gate"),
            goto("LYRIC_INLINE_DEST_DIRECT_CHECK"),
        ),
        scene(
            "LYRIC_INLINE_DEST_BRACKETED_POP",
            *_pop_glyph("bracketed_paths_next_gate"),
            branch(
                eq(val(PUCK), _k(62)),  # '>'
                then="LYRIC_INLINE_DEST_BRACKETED_CLOSE",
                else_="LYRIC_INLINE_DEST_BRACKETED_KEEP",
            ),
        ),
        scene(
            "LYRIC_INLINE_DEST_BRACKETED_KEEP",
            push(ROMEO, val(PUCK)),  # destination discard pile (quirk)
            goto("LYRIC_INLINE_DEST_BRACKETED_POP"),
            companion=PUCK,
        ),
        scene(
            "LYRIC_INLINE_DEST_BRACKETED_CLOSE",
            *_pop_glyph("bracketed_paths_round_seal"),
            branch(
                eq(val(PUCK), _k(41)),  # ')'
                then="LYRIC_OPEN_OUTPUT_INLINE_LINK",
                else_="LYRIC_OPEN_OUTPUT_LINK_FALLBACK",
            ),
        ),
        # --- Output: (Puck, Juliet), anchor Juliet ---
        scene(
            "LYRIC_OPEN_OUTPUT_INLINE_LINK",
            goto("LYRIC_ANCHOR_INLINE"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_ANCHOR_INLINE",
            *_stream(
                tokens.ANCHOR_OPEN,
                *b"/script?foo=1&amp;bar=2",
                tokens.ANCHOR_TEXT,
                *b"link",
                tokens.ANCHOR_CLOSE,
            ),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        # --- Back in the scan pair for the reference-label pops ---
        scene(
            "LYRIC_REFERENCE_ONE_POP_LABEL",
            *_pop_glyph("first_shelfs_open_mark"),
            *_pop_glyph("first_shelfs_number"),
            *_pop_glyph("first_shelfs_close_mark"),
            goto("LYRIC_OPEN_CONSULT_REFERENCE_ONE"),
        ),
        scene(
            "LYRIC_REFERENCE_ATT_POP_BODY",
            *_pop_glyph("houses_second_petal"),
            *_pop_glyph("houses_ampersand"),
            *_pop_glyph("houses_last_petal"),
            *_pop_glyph("houses_closing_petal"),
            *_pop_glyph("houses_following_air"),
            *_pop_glyph("second_shelfs_open_mark"),
            *_pop_glyph("second_shelfs_number"),
            *_pop_glyph("second_shelfs_close_mark"),
            goto("LYRIC_OPEN_CONSULT_REFERENCE_TWO"),
        ),
        # --- Consult: (Puck, Rosalind), anchor Rosalind ---
        # Rosalind's anchor role here is compliance-constrained: her four
        # goto lines are the play's only Rosalind speeches
        # (test_reference_librarian_is_visible_in_reference_scenes).
        scene(
            "LYRIC_OPEN_CONSULT_REFERENCE_ONE",
            goto("LYRIC_CONSULT_REFERENCE_ONE"),
            anchor=ROSALIND,
            companion=PUCK,
        ),
        scene(
            "LYRIC_CONSULT_REFERENCE_ONE",
            pop(ROSALIND, recall="first_forest_seal"),
            pop(ROSALIND, recall="first_forest_path"),
            pop(ROSALIND, recall="first_forest_name"),
            goto("LYRIC_OPEN_OUTPUT_REFERENCE_ONE"),
            anchor=ROSALIND,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OPEN_OUTPUT_REFERENCE_ONE",
            goto("LYRIC_ANCHOR_REFERENCE_ONE"),
            anchor=ROSALIND,
            companion=PUCK,
        ),
        scene(
            "LYRIC_ANCHOR_REFERENCE_ONE",
            *_stream(
                tokens.ANCHOR_OPEN,
                *b"http://example.com/?foo=1&amp;bar=2",
                tokens.ANCHOR_TEXT,
                *b"link",
                tokens.ANCHOR_CLOSE,
            ),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OPEN_CONSULT_REFERENCE_TWO",
            goto("LYRIC_CONSULT_REFERENCE_TWO"),
            anchor=ROSALIND,
            companion=PUCK,
        ),
        scene(
            "LYRIC_CONSULT_REFERENCE_TWO",
            pop(ROSALIND, recall="second_forest_seal"),
            pop(ROSALIND, recall="second_forest_path"),
            pop(ROSALIND, recall="second_forest_name"),
            goto("LYRIC_OPEN_OUTPUT_REFERENCE_TWO"),
            anchor=ROSALIND,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OPEN_OUTPUT_REFERENCE_TWO",
            goto("LYRIC_ANCHOR_REFERENCE_TWO"),
            anchor=ROSALIND,
            companion=PUCK,
        ),
        scene(
            "LYRIC_ANCHOR_REFERENCE_TWO",
            *_stream(
                tokens.ANCHOR_OPEN,
                *b"http://att.com/",
                tokens.ANCHOR_TITLE,
                *b"AT&amp;T",
                tokens.ANCHOR_TEXT,
                *b"AT&amp;T",
                tokens.ANCHOR_CLOSE,
            ),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OPEN_OUTPUT_LINK_FALLBACK",
            goto("LYRIC_OUTPUT_LINK_FALLBACK"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OUTPUT_LINK_FALLBACK",
            *_stream(*b"[link("),  # current glyph dropped (quirk, as-is)
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        # --- Amp / angle dispatch tails: (Puck, Romeo) ---
        scene(
            "LYRIC_TEST_LEFT_ANGLE",
            branch(
                eq(val(PUCK), _k(60)),  # '<'
                then="LYRIC_LEFT_ANGLE_POP_NEXT",
                else_="LYRIC_OPEN_OUTPUT_CURRENT",
            ),
            companion=PUCK,
        ),
        scene(
            "LYRIC_AMP_POP_NEXT",
            *_pop_glyph("mornings_next_cut"),
            branch(
                eq(val(PUCK), _k(97)),  # 'a': "&a..." stays literal
                then="LYRIC_OPEN_OUTPUT_LITERAL_AMP_CURRENT",
                else_="LYRIC_OPEN_OUTPUT_AMP_ENTITY_CURRENT",
            ),
        ),
        scene(
            "LYRIC_LEFT_ANGLE_POP_NEXT",
            *_pop_glyph("mornings_next_cut"),
            branch(
                eq(val(PUCK), _k(47)),  # '/': "</" stays literal
                then="LYRIC_OPEN_OUTPUT_LITERAL_LEFT_CURRENT",
                else_="LYRIC_OPEN_OUTPUT_LT_ENTITY_CURRENT",
            ),
        ),
        # --- Glyph output scenes: (Puck, Juliet), anchor Juliet ---
        scene(
            "LYRIC_OPEN_OUTPUT_CURRENT",
            goto("LYRIC_OUTPUT_CURRENT"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OUTPUT_CURRENT",
            *_current(),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OPEN_OUTPUT_AMP_ENTITY_CURRENT",
            goto("LYRIC_OUTPUT_AMP_ENTITY_CURRENT"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OUTPUT_AMP_ENTITY_CURRENT",
            *_entity(*b"&amp;"),
            *_current(),  # the lookahead glyph popped in LYRIC_AMP_POP_NEXT
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OPEN_OUTPUT_LITERAL_AMP_CURRENT",
            goto("LYRIC_OUTPUT_LITERAL_AMP_CURRENT"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OUTPUT_LITERAL_AMP_CURRENT",
            *_entity(*b"&"),
            *_current(),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OPEN_OUTPUT_LT_ENTITY_CURRENT",
            goto("LYRIC_OUTPUT_LT_ENTITY_CURRENT"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OUTPUT_LT_ENTITY_CURRENT",
            *_entity(*b"&lt;"),
            *_current(),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OPEN_OUTPUT_LITERAL_LEFT_CURRENT",
            goto("LYRIC_OUTPUT_LITERAL_LEFT_CURRENT"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_OUTPUT_LITERAL_LEFT_CURRENT",
            *_entity(*b"<"),
            *_current(),
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_RETURN_TO_SCAN",
            goto("LYRIC_POP_GLYPH"),
            companion=PUCK,
        ),
        scene(
            "TRAVERSE_COPY_TERMINATOR",
            push(JULIET, const(tokens.TEXT_END)),
            goto("TRAVERSE_NEXT_TOKEN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        # --- Reverse phase: (Juliet, Puck), anchor Juliet ---
        scene(
            "LYRIC_OPEN_REVERSE",
            push(PUCK, const(tokens.STREAM_END)),
            goto("LYRIC_REVERSE_POP"),
            anchor=JULIET,
        ),
        scene(
            "LYRIC_REVERSE_POP",
            pop(JULIET, recall="roses_kept_word"),
            branch(
                eq(val(JULIET), const(tokens.STREAM_END)),
                then="ACT_III_DONE",
            ),
            push(PUCK, val(JULIET)),
            goto("LYRIC_REVERSE_POP"),
            anchor=JULIET,
        ),
        scene(
            "ACT_III_DONE",
            halt_act(),
            anchor=JULIET,
            companion=ROMEO,
        ),
    ],
)
