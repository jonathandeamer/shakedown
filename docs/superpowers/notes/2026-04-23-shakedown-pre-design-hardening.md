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
| Emphasis backtracking | policy decision remains | `tests/prototype` known xfail plus prior two-pass finding | Detailed spec must choose two-pass parity or documented divergence before implementation planning. |
| Nested blockquote closer quirk | policy decision remains | `docs/markdown/divergences.md` | Detailed spec must choose byte parity or structural validity. |
