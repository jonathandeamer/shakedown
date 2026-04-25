# Markdown.pl Parity Exceptions

This file documents behavior that cannot be byte-identical under an SPL-pure Markdown.pl parity goal, plus prior divergence candidates that are no longer accepted.

## Active Exception

| Feature | Markdown.pl behaviour | Shakedown parity target | Reason |
|---|---|---|---|
| Email auto-links | Each character is randomly encoded as decimal or hex HTML entity by `_EncodeEmailAddress` | Entity-normalized equivalence for href and visible text | SPL has no verified randomness primitive, so byte-identical random choices are not available in a pure SPL implementation |

## Email Auto-Link Equivalence Rule

The "entity-normalized equivalence" target for email auto-links is defined concretely as:

1. Apply `_decode_entities` from `tests/test_mdtest.py` to both the Shakedown output and the oracle output for the same input. This decodes all `&#NNN;` decimal numeric character references and `&#xNN;` hex numeric character references to their literal characters.
2. Byte-compare the two decoded strings.

If they match, Shakedown passes the email-autolink equivalence check. Because `Markdown.pl` randomizes the entity choice per-character in `_EncodeEmailAddress`, byte-identical output is not available in pure SPL. Decoding before comparison collapses the random entity space to a canonical form.

The mdtest `Auto links` fixture already applies this decoding via the test harness's `_decode_entities` function. Any additional email-autolink parity testing outside that fixture should use the same decoder.

## Rejected Divergence Candidates

| Feature | Prior Shakedown behavior | Markdown.pl parity requirement | Reason |
|---|---|---|---|
| Nested blockquote closing | Emit a structurally cleaner bare `</blockquote>` for the outer close | Reproduce the local Markdown.pl output, including malformed paragraph-wrapped close tags where the oracle emits them | SPL can emit the exact byte sequence; choosing valid HTML would be a scope cut, not a language limitation |
| Emphasis backtracking | Treat overlapping `<em>/<strong>` as unsupported by the P2 single-toggle prototype | Implement Markdown.pl's strong-before-emphasis substitution order | The XFAIL is a prototype limitation, not a forced divergence |
