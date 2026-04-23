# Shakedown Pre-Design Due Diligence

## Questions To Close

| Question | Why it matters | Evidence sources | Probe command(s) | Decision threshold | Status |
|---|---|---|---|---|---|
| Reference-link strategy | Reference links are the biggest remaining architectural risk because they require label lookup across the document. | `docs/markdown/target.md`; `docs/prior-attempt/architecture-lessons.md`; `docs/verification-plan.md` | `uv run pytest tests/test_mdtest.py -k 'reference' -q` | The selected strategy must explain how labels are resolved without hand-wavy global state. | closed for the mdtest corpus; the current binary passes the reference fixtures |
| Lists and nested blocks | Tight/loose exactness and nested composition can break the block pipeline if they are not designed together. | `docs/markdown/fixture-outlook.md`; `docs/prior-attempt/feasibility-lessons.md` | `uv run pytest tests/test_mdtest.py -k 'list or blockquote' -q` | The design must state whether exact loose-list behavior is required or a documented divergence. | closed for the mdtest corpus; the current binary passes the list and blockquote fixtures |
| Setext lookahead and HTML boundaries | Setext headings need line-level buffering and raw HTML needs clear boundary rules. | `docs/markdown/target.md`; `docs/markdown/fixture-outlook.md` | `uv run pytest tests/test_mdtest.py -k 'setext or html' -q` | The design must say where line lookahead lives and how far it reaches. | closed for the mdtest corpus; the current binary passes the setext and HTML fixtures |
| Emphasis backtracking | Markdown.pl overlap semantics are still the hardest oracle-parity edge case. | `docs/superpowers/notes/2026-04-18-p2-evidence.md`; `docs/superpowers/notes/2026-04-19-findings-for-detailed-spec.md`; `docs/markdown/divergences.md` | `uv run pytest tests/prototype -q`; `uv run pytest tests/test_mdtest.py -k 'strong' -q` | The design must choose exact overlap reproduction or an explicit divergence. | still open at the prototype level; mdtest is green, but the prototype backtracking probe remains xfailed |
| Timing budget | The loop only matters if the assembled SPL stays workable on this machine. | `docs/superpowers/notes/2026-04-18-p1-evidence.md`; `docs/superpowers/notes/2026-04-18-p2-evidence.md` | `time ./shakedown-dev < /dev/null`; `time ./shakedown-dev < tests/prototype/fixtures/p2_blockquote_input.md`; `uv run pytest tests/test_mdtest.py -q` | The measured runtime must be low enough for a fixture-by-fixture loop. | closed; the current build is slow but workable and the corpus stays green |

## Evidence Notes

The full current binary passes the entire mdtest corpus:

- `uv run pytest tests/test_mdtest.py -q` -> `23 passed in 1.44s`
- `uv run pytest tests/test_mdtest.py -k 'reference' -q` -> `3 passed in 0.26s`
- `uv run pytest tests/test_mdtest.py -k 'setext or html' -q` -> `3 passed, 20 deselected in 0.13s`
- `uv run pytest tests/test_mdtest.py -k 'strong' -q` -> `1 passed, 22 deselected in 0.09s`
- `uv run pytest tests/prototype -q` -> `3 passed, 1 xfailed in 10.07s`
- `time ./shakedown-dev < /dev/null` -> `real 0m8.940s`
- `time ./shakedown-dev < tests/prototype/fixtures/p2_blockquote_input.md` -> `real 0m8.727s`

What this implies:

- Reference links, list composition, setext headings, and HTML boundaries are no longer open architectural questions for the current corpus.
- The remaining live question is whether the detailed spec should keep the prototype's emphasis-backtracking XFAIL as a documented divergence or spend the extra pass to close it.
- The timing budget is acceptable for a fixture-by-fixture loop, but not cheap enough to justify indiscriminate whole-suite repetition during inner-loop work.

## Decisions Carried Forward

- Use a document-scoped reference lookup strategy, not a global mutable hash, because the corpus now demonstrates the lookup problem is tractable without a separate runtime cache.
- Treat list composition and nested block composition as solved current-corpus behavior, but keep explicit policy language in the detailed spec so the implementation does not regress on tight versus loose list output.
- Keep setext lookahead at the line level and keep HTML boundaries explicit; the current binary already passes those fixtures, so the detailed spec should encode the rule rather than rediscover it.
- Keep emphasis backtracking as an explicit decision point, not an accidental property of the implementation; the prototype still marks the hard overlap case xfailed even though the mdtest corpus is green.
- Treat the measured runtime as workable but not cheap, which means the next implementation plan should preserve narrowly targeted inner-loop tests and avoid forcing a full corpus run on every tiny edit.

## Detailed-Design Inputs

1. Freeze the current mdtest green path as the regression target for the detailed architecture spec.
2. Preserve the existing reference, list, setext, and HTML behavior as non-negotiable corpus coverage.
3. Decide whether the emphasis backtracking XFAIL remains a deliberate divergence or gets a second-pass implementation before the detailed spec is written.
4. Keep the timing budget assumption conservative: fixture-by-fixture loops are fine, but wide re-runs are expensive enough to stay deliberate.
5. Leave build-order, phase-boundary, and representation choices open only where the corpus evidence still does not force the answer.
