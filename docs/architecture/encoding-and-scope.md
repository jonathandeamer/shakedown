# Encoding and Scope

This document fixes the input/output scope that the selected architecture and implementation
planning should assume. It does not decide implementation structure.

## Encoding Facts

- The current pytest contract reads fixture files with Python text I/O and passes text to
  `./shakedown` through `subprocess.run(..., text=True)`.
- The 23 mdtest fixtures are ASCII-compatible, so the current corpus does not exercise
  Unicode normalization or conflicting file encodings.
- The local SPL interpreter emits `Speak your mind!` output as UTF-8 bytes for Unicode code
  points, as recorded in `docs/spl/verification-evidence.md`.
- `Speak your mind!` rejects invalid character codes such as `-1`; an SPL implementation must
  guard EOF sentinels before character output.

## Markdown Scope

Shakedown targets John Gruber's `Markdown.pl` v1.0.1 behaviour for the 23
`Markdown.mdtest` fixtures, plus documented parity mechanics in `docs/markdown/`.

In scope:

- Markdown.pl block and span behaviour needed by the fixture corpus.
- Strict local-oracle parity for deterministic behaviour claimed by the selected architecture.
- Entity-normalized email auto-link equivalence under an SPL-pure target.

Out of scope unless a future architecture explicitly expands it:

- Markdown extensions beyond Markdown.pl v1.0.1.
- Security filtering or HTML sanitization beyond Markdown.pl behaviour.
- CLI flags, config files, batch file inputs, or filesystem traversal.
- Byte-for-byte reproduction of randomized email auto-link encoding in pure SPL.
- Unicode normalization semantics not exercised by the current fixture corpus.

## Output Scope

stdout should contain only rendered HTML. Diagnostics, timings, and debug traces should go to
stderr or test logs so they do not alter fixture output.
