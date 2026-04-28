# Dispatch Token-Code Allocation

**Status:** Pre-Slice-1 deliverable per architecture spec §7.1 #3.
**Constraint:** literary-spec §8.1 atom cap (2-4 word target, 6 word max);
single-atom forms preferred when legal.

These codes are *Critical* in the codegen-style-guide sense: every speaker uses
the canonical phrase repo-wide for a given dispatch value. Per-character Stable
Utility variation does not apply to these.

## Block-token allocation

| Name | Code | Canonical SPL phrase |
|---|---:|---|
| PARA | 1 | `a cat` |
| HEADER | 2 | `a big cat` |
| HR | 3 | `the sum of a big cat and a cat` |
| LIST_OPEN | 4 | `a big big cat` |
| LIST_ITEM | 5 | `the sum of a big big cat and a cat` |
| LIST_CLOSE | 6 | `the sum of a big big cat and a big cat` |
| BLOCKQUOTE_OPEN | 7 | `the sum of a big big cat and the sum of a big cat and a cat` |
| BLOCKQUOTE_CLOSE | 8 | `a big big big cat` |
| CODE_BLOCK | 9 | `the sum of a big big big cat and a cat` |
| RAW_HTML_HASH | 10 | `the sum of a big big big cat and a big cat` |

**Atoms used:** `a cat` (1, 2 words), `a big cat` (2, 3 words),
`a big big cat` (4, 4 words), `a big big big cat` (8, 5 words).
All atoms are at most 6 words.

**Compound-only codes (3, 5, 6, 7, 9, 10):** unavoidable because adjective
doubling jumps 1 -> 2 -> 4 -> 8; these values cannot be reached as single
atoms. Compound length is uncapped per §8.1; each atom still obeys the cap.

## How To Extend

Slice 3 onward may need additional tokens. Append rows here and validate with
`uv run pytest tests/test_token_codes.py`. Document any conflict between a
mechanical demand and the atom cap inline at the row, per literary-spec §10 #6.

## References

- `docs/spl/literary-spec.md` §8.1 (atom cap), §8.2 (Critical recipe).
- `docs/spl/codegen-style-guide.md` (Critical/Stable/Incidental partition).
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` §4.2 and §7.1 #3.
