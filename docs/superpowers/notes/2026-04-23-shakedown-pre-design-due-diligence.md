# Shakedown Pre-Design Due Diligence

## Questions To Close

| Question | Why it matters | Evidence sources | Probe command(s) | Decision threshold | Status |
|---|---|---|---|---|---|
| Reference-link strategy | Reference links are the biggest remaining architectural risk because they require label lookup across the document. | `docs/markdown/target.md`; `docs/prior-attempt/architecture-lessons.md`; `docs/verification-plan.md` | `uv run pytest tests/test_mdtest.py -k 'reference' -q` | The selected strategy must explain how labels are resolved without hand-wavy global state. | open for SPL; the mdtest reference fixtures are green only through the current oracle stub |
| Lists and nested blocks | Tight/loose exactness and nested composition can break the block pipeline if they are not designed together. | `docs/markdown/fixture-outlook.md`; `docs/prior-attempt/feasibility-lessons.md` | `uv run pytest tests/test_mdtest.py -k 'list or blockquote' -q` | The design must reproduce tight/loose behavior and nested block quirks needed for Markdown.pl parity. | open for SPL beyond simple blockquote; the mdtest list fixtures are green only through the current oracle stub |
| Setext lookahead and HTML boundaries | Setext headings need line-level buffering and raw HTML needs clear boundary rules. | `docs/markdown/target.md`; `docs/markdown/fixture-outlook.md` | `uv run pytest tests/test_mdtest.py -k 'setext or html' -q` | The design must say where line lookahead lives and how far it reaches. | open for SPL mechanics; the mdtest setext and HTML fixtures are green only through the current oracle stub |
| Emphasis backtracking | Markdown.pl overlap semantics require a two-pass inline design rather than P2's single toggle. | `docs/superpowers/notes/2026-04-18-p2-evidence.md`; `docs/superpowers/notes/2026-04-19-findings-for-detailed-spec.md`; `docs/markdown/divergences.md` | `uv run pytest tests/prototype -q`; `uv run pytest tests/test_mdtest.py -k 'strong' -q` | The design should reproduce exact overlap semantics with strong before emphasis; divergence would be a scope cut, not a forced limitation. | still xfailed in the prototype because P2 intentionally uses a single toggle; the mdtest strong fixture is green only through the current oracle stub |
| Timing budget | The loop only matters if the assembled SPL stays workable on this machine. | `docs/superpowers/notes/2026-04-18-p1-evidence.md`; `docs/superpowers/notes/2026-04-18-p2-evidence.md` | `time ./shakedown-dev < /dev/null`; `time ./shakedown-dev < tests/prototype/fixtures/p2_blockquote_input.md`; `uv run pytest tests/test_mdtest.py -q` | The measured runtime must be low enough for a fixture-by-fixture loop. | closed for prototype scale; the current SPL prototype is slow but workable |

## Evidence Notes

The current `./shakedown` entry point passes the entire mdtest corpus because it delegates to the Markdown.pl oracle:

- `uv run pytest tests/test_mdtest.py -q` -> `23 passed in 1.44s`
- `uv run pytest tests/test_mdtest.py -k 'reference' -q` -> `3 passed in 0.26s`
- `uv run pytest tests/test_mdtest.py -k 'setext or html' -q` -> `3 passed, 20 deselected in 0.13s`
- `uv run pytest tests/test_mdtest.py -k 'strong' -q` -> `1 passed, 22 deselected in 0.09s`

That result validates the current `./shakedown` oracle-stub contract. It does not prove the SPL prototype handles the full mdtest corpus, because `./shakedown` currently execs `~/markdown/Markdown.pl`. SPL evidence comes from `./shakedown-dev`, `tests/prototype`, and the standalone probes listed below.

Current SPL prototype evidence:

- `uv run pytest tests/prototype -q` -> `3 passed, 1 xfailed in 10.07s`
- `time ./shakedown-dev < /dev/null` -> `real 0m8.940s`
- `time ./shakedown-dev < tests/prototype/fixtures/p2_blockquote_input.md` -> `real 0m8.727s`

What this implies:

- Reference links, list composition, setext headings, and HTML boundaries are proven by the oracle stub but still need SPL mechanics evidence before the detailed spec treats them as closed.
- The emphasis-backtracking XFAIL is a prototype limitation. The detailed spec should spend the extra pass to close it if Markdown.pl parity remains the target.
- The timing budget is acceptable for a fixture-by-fixture loop, but not cheap enough to justify indiscriminate whole-suite repetition during inner-loop work.

## Decisions Carried Forward

- Carry document-scoped reference lookup into the hardening probes; the oracle-stub corpus result is not enough to close the SPL lookup strategy.
- Carry list composition into the hardening probes; list looseness and nested list composition are not SPL-proven yet.
- Carry nested block composition as a strict parity requirement; emitting cleaner HTML is a scope cut, not the default target.
- Keep setext lookahead at the line level and keep HTML boundaries explicit; the detailed spec should encode these rules only after SPL mechanics evidence or an explicit design assumption.
- Keep emphasis backtracking as an explicit two-pass implementation requirement, not an accidental property of the implementation; the prototype still marks the hard overlap case xfailed because P2 uses a single toggle.
- Treat the measured runtime as workable but not cheap, which means the next implementation plan should preserve narrowly targeted inner-loop tests and avoid forcing a full corpus run on every tiny edit.

## Detailed-Design Inputs

1. Treat the oracle-stub mdtest pass as contract evidence, not SPL implementation evidence.
2. Run standalone SPL mechanics probes before closing reference lookup, setext buffering, and list-state stack risks.
3. Carry the emphasis-backtracking XFAIL into the detailed spec as evidence for the second-pass implementation requirement.
4. Keep the timing budget assumption conservative: fixture-by-fixture loops are fine, but wide re-runs are expensive enough to stay deliberate.
5. Leave build-order, phase-boundary, and representation choices open only where SPL evidence or an explicit design decision supports the answer.
