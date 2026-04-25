# Shakedown Pre-Design Hardening

## Reference Lookup Micro-Prototype

`uv run pytest tests/test_pre_design_probes.py -q -k reference` passed. The standalone SPL probe demonstrates that a document-scoped linear lookup can scan a stack-backed reference table and preserve non-matching records. This supports a no-wrapper strategy for reference links, with the expected trade-off that lookup is linear in the number of definitions.

## Setext Buffering Micro-Prototype

`uv run pytest tests/test_pre_design_probes.py -q -k setext` passed. The standalone SPL probe demonstrates that Phase 2 can delay committing a line until the next line is inspected. The detailed architecture spec should place setext recognition in the block phase and account for the buffering/reversal cost.

## List State Stack Micro-Prototype

`uv run pytest tests/test_pre_design_probes.py -q -k list` passed. The standalone SPL probe demonstrates that a dedicated stack-backed carrier can represent nested list frame state and distinguish tight from loose frames. The detailed architecture spec should use an explicit list-state carrier instead of encoding all list state into scalar phase flags.

## Final Pre-Design Decision Register

| Decision | Status | Evidence | Detailed-spec requirement |
|---|---|---|---|
| `./shakedown` mdtest pass is oracle-stub evidence, not SPL evidence | closed | entrypoint inspection plus mdtest target | The spec must not cite oracle-stub success as implementation proof. |
| Reference lookup | closed for mechanics | `reference-lookup.spl` | Use document-scoped linear lookup unless a later implementation proves it too slow. |
| Setext lookahead | closed for mechanics | `setext-buffering.spl` | Keep setext recognition in the block phase with delayed line commitment. |
| List looseness / nesting state | closed for mechanics | `list-state-stack.spl` | Use a dedicated stack-backed list-state carrier. |
| Emphasis backtracking | not a forced divergence | `tests/prototype` known xfail plus Markdown.pl strong-then-emphasis substitution order | Detailed spec should implement strong before emphasis if Markdown.pl parity remains the target. |
| Nested blockquote closer quirk | parity requirement | `docs/markdown/oracle-mechanics.md` plus `docs/markdown/divergences.md` | Detailed spec must reproduce the local Markdown.pl byte sequence when strict parity is required. |
| P1: SPL cost at 1k/4k | closed (measured) | `spl-cost-1k.spl` + `spl-cost-4k.spl` via `measure_spl_cost.py` | Budget <= B14's observed numbers for performance-sensitive decisions; re-measure on first realistic port build. |
| P2: emphasis two-pass mechanics | closed | `emphasis-two-pass.spl` | Parity design should implement strong-then-emphasis substitution over a buffered span. |
| P3: nested-dispatch mechanics | closed | `nested-dispatch.spl` | Recursive dispatch with frame-sentinel stack is a supported mechanic; architecture planning may rely on it. |
| P4: reference-lookup at fixture scale | closed | `reference-lookup-scale.spl` + B17 timing | Stack-backed linear scan is tractable at fixture scale; reconsider only if B17 shows alarm. |
| P5: scene-count-per-act | closed | `scene-count.spl` + B18 timing | Single-act scene-count is not a dominant cost driver at ~200 scenes; architecture planning may extend prior-attempt's ~130-scene pattern with headroom. |

## 2026-04-24 Pre-Architecture Hardening Probes

The five pre-architecture hardening probes (P1-P5) have been added to the
pre-design evidence set. See B14, B15, B16, B17, B18 in
`docs/verification-plan.md` for commands, observed numbers, and dispositions.

These probes close the runtime-sensitive and parity-critical evidence gaps
identified in the 2026-04-24 audit. Architecture planning in the next session
should treat their results as current-repo measurements, not prior-attempt
retrospectives.

## Detailed Architecture Go/No-Go

Proceed to detailed architecture only if the spec explicitly carries the two-pass emphasis implementation requirement, strict nested-block parity requirement, and email-autolink entity-normalized exception. All other pre-design implementation risks have either executable SPL mechanics evidence or are correctly classified as non-SPL oracle-stub evidence.
