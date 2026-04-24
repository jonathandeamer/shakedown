# List Mechanics

This document records Markdown.pl list behaviour that architecture planning must preserve or
explicitly test. It is based on local `~/markdown/Markdown.pl` v1.0.1, especially `_DoLists`
and `_ProcessListItems`.

## Pipeline Position

Lists are processed in `_RunBlockGamut` after headers and horizontal rules, but before code
blocks and blockquotes. This order matters: list items may contain nested blocks, and indented
content can be interpreted differently once it is inside a list item.

## Marker Recognition

Markdown.pl recognizes:

- unordered markers: `*`, `+`, `-`
- ordered markers: one or more digits followed by `.`
- marker indentation: up to three leading spaces
- required whitespace after the marker

The first item marker determines whether the rendered list is `<ul>` or `<ol>`.

## Top-Level vs Nested Lists

Markdown.pl uses a global list-level counter.

At top level, a list must start at the beginning of the document or after a blank line. This is
why hard-wrapped paragraph lines such as `8. Oops` are not always treated as lists.

Inside a list, matching is more permissive so sublists can be recognized after outdenting item
content. This difference is intentional Markdown.pl behaviour, not incidental parser style.

## Tight vs Loose Items

Before item processing, Markdown.pl turns double newlines inside the matched list into triple
newlines. During `_ProcessListItems`:

- an item with a leading blank line, or with blank lines inside the item, is loose and runs
  `_RunBlockGamut` after outdenting;
- otherwise the item is tight: Markdown.pl recursively runs `_DoLists`, chomps the result, then
  runs `_RunSpanGamut`.

This loose/tight split determines whether paragraph tags appear inside `<li>` elements.

## List End Boundaries

The list match ends at the document end or at a blank-line boundary followed by a non-space
character that is not another list marker. This is one source of list exactness risk because
nearby paragraphs, sublists, and indented content can change the captured list body.

## Fixtures That Exercise This Area

| Fixture | Coverage |
|---|---|
| `Ordered and unordered lists` | Tight lists, loose lists, all unordered markers, ordered lists, multi-paragraph items, nested lists. |
| `Hard-wrapped paragraphs with list-like lines` | Top-level ambiguity between paragraph continuation and ordered-list marker. |
| `Markdown Documentation - Basics` | Documentation examples with simple lists. |
| `Markdown Documentation - Syntax` | Large mixed fixture with lists, nesting, code, and blockquotes. |

## Architecture Inputs

A future design should state:

- where list-level state is stored;
- how item bodies are buffered or delimited;
- how loose/tight classification is represented;
- how nested-list recursion or equivalent processing returns to the enclosing item;
- which fixture slices prove exactness before the large documentation fixtures are attempted.

`tests/test_pre_design_probes.py` confirms stack-backed nested list-state mechanics, but full
Markdown list parsing remains production work.
