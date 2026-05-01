# Changelog

## [0.1.0] - 2026-05-01

### Bug Fixes

- Restore shakedown wrapper
- Harden run-loop recovery state
- Self-heal repeated claude temp pressure
- Harden run-loop failure recovery
- Fail fast on missing default run-loop prompt
- Reset run-loop claude failure streaks on progress
- Retry run-loop after cooldown
- Retry run-loop after cooldown
- Reset run-loop claude failure streaks on progress
- Detect committed run-loop progress
- Correct SPL semantics in cost-probe generator
- Tighten run-loop and setup harness behavior
- Pass codex run-loop prompt on stdin
- Correct Slice 1 stream counters
- Propagate SPL runtime failures

### Experiments

- P2 inline emphasis via toggle state
- P2 attempt emphasis backtracking; mark as divergence candidate
- Blockquote via Phase 2 raw-tag push + P2 evidence
- Prove SPL reference lookup mechanics
- Prove SPL setext buffering mechanics
- Prove SPL list state stack mechanics
- Add emphasis two-pass mechanics probe
- Add nested-dispatch mechanics probe
- Add reference-lookup scale probe
- Add pre-Slice-1 cache feasibility spike

### Features

- Add minimal src/ fragment assembler
- Resolve scene labels to Roman numerals per act
- Add preamble and smoke SPL fragments for build pipeline check
- Phase 1 reads stdin into Romeo's stack
- Walking skeleton emits HTML for paragraphs and code spans
- Add dispatch token-code allocation table
- Add iconic-moment maps with single-surface validator
- Add src/literary.toml schema with Slice 1 stable-utility entries
- Add HTML byte-literal codegen with round-trip test
- Add dev-mode wrapper skeleton for shakedown
- Add strict shakedown-vs-Markdown.pl parity harness
- Add run-loop prompt for autonomous implementation
- Replace SPL preamble cast
- Add empty four-act fragments
- Generate SPL speech lines for HTML literals
- Add Act IV paragraph literal smoke
- Verify Act IV byte-literal emission
- Route shakedown entrypoint to SPL artifact
- Add Slice 1 Act I read loop
- Add Act I reference probe
- Add Slice 1 paragraph token stream
- Expose Slice 1 paragraph-count probe
- Add Slice 1 raw text encoding
- Add Slice 1 reference link spans
- Add Slice 1 inline link spans
- Verify Slice 1 span payload probe
- Emit Slice 1 token stream HTML

### Refactoring

- Scan Slice 1 references by delimiter
- Parse Slice 1 inline destinations by delimiter
- Move Slice 1 anchor framing to emitter


