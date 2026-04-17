# Shakedown Mdtest Fixture Matrix

This document maps the 23 `Markdown.mdtest` fixtures to the current Shakedown SPL planning outlook.

It is a planning input, not a design doc and not a final implementation commitment. The goal is
to help the next agent aim for the mdtest ceiling rather than re-deriving fixture risk from the
feasibility summaries.

**Prediction labels**
- `likely pass`
- `uncertain`
- `likely fail`

| Fixture | Prediction | Primary Mechanism | Primary Risk | Confidence | Rationale |
|---|---|---|---|---|---|
| `ATX Headers` | `likely pass` | Slice-1 block structure already proven | none dominant | high | ATX headings were already implemented in the recovered SPL work and are not called out as architectural risks in the feasibility studies. |
| `Setext Headers` | `likely pass` | Slice-1 block structure already proven | none dominant | high | Setext handling is part of the proven block-level baseline from the recovered implementation. |
| `Paragraphs and Simple Blocks` | `likely pass` | Slice-1 block dispatcher | none dominant | high | Paragraph emission is already in the prior Shakedown implementation and not listed as a ceiling risk. |
| `Horizontal Rules` | `likely pass` | Slice-1 block structure already proven | none dominant | high | Horizontal rules were already implemented during Slice 1. |
| `Indented Code Blocks` | `likely pass` | Slice-1 block structure already proven | nested-block interaction only | medium | Plain indented code blocks are already proven; only nested interactions raise risk. |
| `Blockquotes` | `likely pass` | Recursive dispatch | nested block composition | medium | Blockquotes were previously implemented, and recursive dispatch is now a validated build pattern. |
| `Code Spans` | `likely pass` | streaming inline toggle | none dominant | medium | The feasibility work treats simple inline spans as compatible with the single-act architecture. |
| `Emphasis` | `uncertain` | buffered inline scan | emphasis backtracking | medium | Simple emphasis is validated, but Markdown.pl backtracking semantics remain only partially reproduced. |
| `Strong Emphasis` | `uncertain` | buffered inline scan | emphasis backtracking | medium | Strong emphasis is plausible, but exact Markdown.pl pairing behavior remains a known risk area. |
| `Inline Links` | `likely pass` | buffered inline sub-dispatch | inline complexity | low | The studies imply links are architecturally feasible, but they were not validated as directly as simple spans. |
| `Reference Links` | `uncertain` | two-pass buffered lookup | O(n×m) lookup and exactness | medium | Reference links are considered feasible but expensive and more complex than simple inline cases. |
| `Inline Images` | `likely pass` | same machinery as inline links | inline complexity | low | The round-1 summary treats images as structurally the same class as links. |
| `Reference Images` | `uncertain` | same machinery as reference links | O(n×m) lookup and exactness | medium | Reference-style image resolution inherits the same risks as reference links. |
| `Auto Links` | `likely fail` | autolink handling with known divergence | email autolink encoding | high | The feasibility studies identify email autolink obfuscation as a permanent divergence because SPL lacks the needed randomness primitive. |
| `Backslash Escapes` | `likely pass` | one-byte lookahead | none dominant | medium | The feasibility work treats escapes as a straightforward streaming case. |
| `Inline HTML` | `likely pass` | streaming inline detect | none dominant | medium | Inline HTML is listed as a straightforward fit for the single-act inline architecture. |
| `Ordered Lists` | `uncertain` | list parser with bounded nesting | loose-list exactness | medium | Simple list markers look feasible, but exact list behavior still depends on the unresolved loose-list risk. |
| `Unordered Lists` | `uncertain` | list parser with bounded nesting | loose-list exactness | medium | Tight lists validate cleanly, but loose-list formatting remains only partial. |
| `Nested Lists` | `uncertain` | bounded 2-level nesting | loose-list exactness and nesting interactions | medium | Two-level nesting is validated, but exact combined behavior is still a planning risk rather than a solved case. |
| `HTML Blocks` | `likely pass` | raw HTML block pass-through | low direct evidence | low | HTML blocks were part of the original project scope, but the feasibility set gives less direct validation than for block structure or simple inline spans. |
| `Ampersands and Angle Brackets` | `likely pass` | inline escaping / code-path encoding | none dominant | medium | Entity-sensitive escaping is part of the intended inline layer and not singled out as a ceiling risk except for email autolinks. |
| `Nested Block Structures` | `uncertain` | recursive dispatch with sentinels | exact nested blockquote/list compositions | medium | Recursive dispatch is viable, but exact nested composition output remains one of the clearest residual risks from phase 2. |
| `Markdown Documentation - Syntax` | `uncertain` | full integrated architecture | combined ceiling risks | high | Both summaries call this out as the largest integrated fixture and a likely place where emphasis, list, and nested-structure edge cases converge. |
