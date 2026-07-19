# Shakedown

A port of John Gruber’s [`Markdown.pl`](https://daringfireball.net/projects/markdown/)
(v1.0.1) to the
[Shakespeare Programming Language](https://github.com/zmbc/shakespearelang)
(SPL). The program is a play — *Shakedown: A Most Excellent Tragicomedy of Glyph
and Line* — that reads Markdown on stdin and writes HTML on stdout.

## Quick demo

Requires [uv](https://docs.astral.sh/uv/) (pulls `shakespearelang` from
`pyproject.toml`).

```bash
uv sync
echo 'Hello *world*' | uv run shakespeare run shakedown.spl
```

Expected:

```text
<p>Hello <em>world</em></p>
```

Same thing via the release wrapper (resolves the CLI through `uv`, fails on SPL
parse/runtime errors that the bare CLI sometimes exits `0` for):

```bash
echo 'Hello *world*' | ./shakedown
```

Cold start is slow (each run boots a fresh interpreter). That is expected.

## Dependencies

| Need | Role |
|---|---|
| **uv** + Python ≥ 3.12 | Project env; `shakespearelang` is declared in `pyproject.toml` |
| **`shakespearelang`** | SPL interpreter (`shakespeare run`) — installed by `uv sync` |
| **Committed `shakedown.spl`** | The play / release artefact (no assemble step to *run*) |

Optional, for the full test / oracle suite only:

| Need | Default path | Override |
|---|---|---|
| Markdown.mdtest fixtures (23 pairs) | `~/mdtest/Markdown.mdtest` | `SHAKEDOWN_MDTEST` |
| `Markdown.pl` oracle | `~/markdown/Markdown.pl` | `SHAKEDOWN_MARKDOWN_PL` |
| **perl** | on `PATH` | — |

```bash
export SHAKEDOWN_MDTEST=/path/to/Markdown.mdtest
export SHAKEDOWN_MARKDOWN_PL=/path/to/Markdown.pl
uv run pytest tests/test_mdtest.py
uv run python scripts/strict_parity_harness.py
```

## Entry points

| Command | What it does |
|---|---|
| **`uv run shakespeare run shakedown.spl`** | **Primary.** Run the committed play with the SPL CLI. |
| **`./shakedown`** | Same play, via `uv` + error handling. No assembly. |
| **`./shakedown-dev`** | Rebuild `shakedown.spl` from `src/` (via `scripts/assemble.py`), then `./shakedown`. |
| **`./shakedown-debug`** | Assemble with the Act IV token-dump fragment; run that play (`SHAKEDOWN_SPL`). |

Override which play file `./shakedown` runs:

```bash
SHAKEDOWN_SPL=/path/to/other.spl ./shakedown
```

### How the test suite stays fast

| Command | Role |
|---|---|
| **`./shakedown-parity`** | Fast harness entry: IR interpreter + Slice-3 link/reference rewrite (`python -m scripts.release_runtime`). Used by pytest, strict parity, and smoke. |
| **`./shakedown`** | Public art path: real `shakespeare run` on the committed play. |

Cold `shakespeare` boots are too slow for the full 23-fixture suite on every
commit. The **public artefact** remains the play; the parity entry is test
infrastructure, not a second Markdown dialect.

## Develop

```bash
uv sync
git config core.hooksPath .githooks   # conventional commits

# Edit IR / literary surfaces, then rebuild the play:
uv run python -m scripts.splc
uv run python scripts/assemble.py

uv run pytest                        # default suite
uv run ruff check .
uv run pyright
```

Agent/session conventions live in `CLAUDE.md` (also linked as `AGENTS.md`).
Deep docs start at [`docs/README.md`](docs/README.md).

## Parity note

Target is **Markdown.pl**, not CommonMark. Strict checks compare against a local
oracle. The only intentional SPL-pure exception is **email auto-links** (entity
encoding is random in Perl); see [`docs/markdown/divergences.md`](docs/markdown/divergences.md).
