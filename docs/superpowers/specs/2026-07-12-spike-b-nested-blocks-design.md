# Spike B Nested Containers — Accepted Design

**Date:** 2026-07-12  
**Status:** accepted for implementation by plan `2026-07-12-spike-b-nested-blocks.md`  
**Authority:** architecture §6.3, §7.4, and §8.2

## Decision

Spike B changes the shipped list-item encoding from an implicit, text-bearing
item to an explicit item boundary:

```text
document   := block*
block      := PARA | list | blockquote
list       := LIST_OPEN(kind) (LIST_ITEM(looseness) block* ITEM_CLOSE)+ LIST_CLOSE
blockquote := BLOCKQUOTE_OPEN block* BLOCKQUOTE_CLOSE
```

More precisely, a `LIST_ITEM` opens one item and has one fixed `looseness`
payload but **no text run**. `ITEM_CLOSE` (new code 15, zero payloads, no text)
closes it. A list requires at least one item, every item belongs to the most
recent open list, and `LIST_CLOSE` is legal only after its current item has
closed. `BLOCKQUOTE_OPEN` (7) and `BLOCKQUOTE_CLOSE` (8) become dispatched,
zero-payload container tokens. Existing numeric codes remain stable.

The list's looseness belongs to the item opening. Act IV therefore selects
`<li>` versus `<li><p>` when it receives `LIST_ITEM`, and emits each nested
block before consuming `ITEM_CLOSE`. This removes the old emitter's fragile
"look at the next token to infer item closure" rule.

## Why explicit boundaries

Keeping the old `LIST_ITEM(text)` representation would require a blockquote
to be smuggled through a text glyph run or would make the emitter infer two
independent nesting closures from lookahead. Both violate the validated
recursive grammar. An explicit closure makes all four required compositions
well-bracketed and lets the verification-only validator reject crossed closes
before HTML rendering.

The existing Macbeth frame stack remains the sequential container-frame owner.
Act II's recursive line scheduler may borrow it above a `STREAM_END` floor;
it must never use it as a ping-pong destination. Lady Macbeth/Puck remain the
stream carriers. No character is added.

## Exact spike corpus and reviewed final streams

The plan creates these four oracle-backed fixtures. Glyphs below stand for the
ASCII values of the displayed text, followed by `TEXT_END` (`0`); `SE` means
the terminal `STREAM_END` (`-1`). `u` is unordered kind `1`; `t` and `l` are
tight `1` and loose `2` item payloads.

| Fixture | Markdown | Required final Act-II stream |
|---|---|---|
| `list_quote_sibling` | `* alpha\n\n  > bravo\n* charlie\n` | `LIST_OPEN,u; LIST_ITEM,l; PARA,alpha,0; BLOCKQUOTE_OPEN; PARA,bravo,0; BLOCKQUOTE_CLOSE; ITEM_CLOSE; LIST_ITEM,l; PARA,charlie,0; ITEM_CLOSE; LIST_CLOSE; SE` |
| `quote_list_then_paragraph` | `> * alpha\n> * bravo\n>\n> charlie\n` | `BLOCKQUOTE_OPEN; LIST_OPEN,u; LIST_ITEM,t; PARA,alpha,0; ITEM_CLOSE; LIST_ITEM,t; PARA,bravo,0; ITEM_CLOSE; LIST_CLOSE; PARA,charlie,0; BLOCKQUOTE_CLOSE; SE` |
| `loose_list_quote` | `* alpha\n\n  > bravo\n\n* charlie\n` | `LIST_OPEN,u; LIST_ITEM,l; PARA,alpha,0; BLOCKQUOTE_OPEN; PARA,bravo,0; BLOCKQUOTE_CLOSE; ITEM_CLOSE; LIST_ITEM,l; PARA,charlie,0; ITEM_CLOSE; LIST_CLOSE; SE` |
| `closes_to_text` | `* alpha\n\n  > bravo\n\noutside\n` | `LIST_OPEN,u; LIST_ITEM,l; PARA,alpha,0; BLOCKQUOTE_OPEN; PARA,bravo,0; BLOCKQUOTE_CLOSE; ITEM_CLOSE; LIST_CLOSE; PARA,outside,0; SE` |

The two first rows preserve §7.4's original two structures; the last two add
the §7.4 acceptance-contract boundary cases. The committed `.dump` files use
one integer per line and are the mechanical form of this review. A rendered
fixture passes only when its dump validates against this grammar as well.

## Pass and rendering boundaries

1. Act II's list recognizer records list/item frames and emits `LIST_OPEN`,
   `LIST_ITEM`, and `ITEM_CLOSE`; it does not flatten an item to a text run.
2. The following blockquote pass recursively removes one `> ` prefix within
   its current container frame, runs the existing list recognition over the
   quoted payload, and emits a matched `BLOCKQUOTE_OPEN`/`BLOCKQUOTE_CLOSE`.
   A blank quoted line remains inside that frame; an unquoted line closes all
   quote frames before ordinary paragraph formation resumes.
3. Paragraph formation turns every raw text region into `PARA(text)`, including
   text inside an item or quote. It must not create a paragraph around a child
   list or blockquote token.
4. Act III copies all new structural codes and their fixed payloads unchanged.
5. Act IV maintains an explicit container/item context stack. It emits the
   Markdown.pl byte layout for the four snippets, including `\n\n` between
   block-level children and the two-space indentation inside blockquotes.

## Rejected alternatives

- **Keep `LIST_ITEM(text)` and encode quotes as glyphs:** impossible to prove
  the required nesting grammar and makes Act III process structural bytes as
  span text.
- **Add a parallel quote-specific emitter outside the token stream:** breaks
  the four-act ownership boundary and cannot compose with existing lists.
- **Allocate a new stack-owning character:** premature; §6.3 requires a
  container-grammar/scheduling revision before reconsidering stack partition.

## Halt rule

If any reviewed stream cannot be produced or cannot render byte-identically,
stop Spike B. First revise this container grammar and Act II's recursive pass
scheduling. Reconsider character-stack partitioning only with evidence that a
valid bracketed stream cannot be realized using Macbeth's sequential frame
stack.
