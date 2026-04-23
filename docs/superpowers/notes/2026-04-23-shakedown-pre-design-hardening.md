# Shakedown Pre-Design Hardening

## Reference Lookup Micro-Prototype

`uv run pytest tests/test_pre_design_probes.py -q -k reference` passed. The standalone SPL probe demonstrates that a document-scoped linear lookup can scan a stack-backed reference table and preserve non-matching records. This supports a no-wrapper strategy for reference links, with the expected trade-off that lookup is linear in the number of definitions.

## Setext Buffering Micro-Prototype

`uv run pytest tests/test_pre_design_probes.py -q -k setext` passed. The standalone SPL probe demonstrates that Phase 2 can delay committing a line until the next line is inspected. The detailed architecture spec should place setext recognition in the block phase and account for the buffering/reversal cost.

## List State Stack Micro-Prototype

`uv run pytest tests/test_pre_design_probes.py -q -k list` passed. The standalone SPL probe demonstrates that a dedicated stack-backed carrier can represent nested list frame state and distinguish tight from loose frames. The detailed architecture spec should use an explicit list-state carrier instead of encoding all list state into scalar phase flags.
