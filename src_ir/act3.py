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
from src_ir.cast import HECATE, JULIET, MACBETH, PUCK, ROMEO, ROSALIND
from src_ir.stream import RECIPES

# Traversal routes per arity shape: (payloads, has_text). Codes with neither
# payloads nor text copy through and loop; unknown shapes fail the build.
_ARITY_ROUTE = {
    (0, True): "TRAVERSE_OPEN_TEXT",
    (1, False): "TRAVERSE_COPY_PAYLOAD_NEXT",
    (1, True): "TRAVERSE_COPY_PAYLOAD_TEXT",
}


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
            push(JULIET, const(tokens.STREAM_END)),
            goto("TRAVERSE_NEXT_TOKEN"),
            anchor=JULIET,
            companion=PUCK,
        ),
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
                then="LYRIC_POP_GLYPH",
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
                then="TRAVERSE_COPY_TERMINATOR",
            ),
            branch(eq(val(PUCK), _k(96)), then="LYRIC_CODE_RUN"),  # '`'
            branch(
                eq(val(PUCK), _k(91)),  # '['
                then="LYRIC_REFERENCE_POP_AFTER_OPEN",
                else_="LYRIC_TEST_AMPERSAND",
            ),
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
            goto("LYRIC_CODE_TICKS"),
            anchor=JULIET,
        ),
        scene(
            "LYRIC_CODE_TICKS_DONE",
            goto("LYRIC_RETURN_TO_SCAN"),
            anchor=JULIET,
            companion=HECATE,
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
                else_="LYRIC_OPEN_REFERENCE_FALLBACK",
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
            anchor=JULIET,
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
            anchor=JULIET,
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
        scene(
            "LYRIC_OPEN_REFERENCE_FALLBACK",
            goto("LYRIC_REFERENCE_FALLBACK"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "LYRIC_REFERENCE_FALLBACK",
            push(JULIET, _k(91)),  # '['
            push(JULIET, val(PUCK)),
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
