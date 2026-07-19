# Shakedown

A port of John Gruber’s [`Markdown.pl`](https://daringfireball.net/projects/markdown/)
(v1.0.1) to the
[Shakespeare Programming Language](https://github.com/zmbc/shakespearelang)
(SPL). The program is a play — *Shakedown: A Most Excellent Tragicomedy of Glyph
and Line* — that reads Markdown on stdin and writes HTML on stdout.

## Quick demo

You only need the [shakespearelang](https://github.com/zmbc/shakespearelang)
CLI on your `PATH` and the committed play. **uv is not required** for this.

```bash
pip install 'shakespearelang>=0.6'   # or pipx, etc. — any install of the CLI
echo 'Hello *world*' | shakespeare run shakedown.spl
```

Expected:

```text
<p>Hello <em>world</em></p>
```

Same via the release wrapper (uses `shakespeare` on `PATH` if present, otherwise
falls back to `uv run` from this project; treats SPL parse/runtime errors on
stderr as failure even when the CLI exits `0`):

```bash
echo 'Hello *world*' | ./shakedown
```

Cold start is slow (each run boots a fresh interpreter). That is expected.

## Dependencies

### To run the play (demo)

| Need | Role |
|---|---|
| **`shakespeare` CLI** | From the [`shakespearelang`](https://github.com/zmbc/shakespearelang) package (`pip install shakespearelang`, etc.) |
| **Committed `shakedown.spl`** | The play / release artefact (no assemble step to *run*) |

No Markdown test suite, no `Markdown.pl`, and no uv are required for the quick
demo above.

### To run the full test / oracle suite

Neither the classic fixtures nor the Perl oracle are vendored in this repo.
Obtain them upstream, put them anywhere on disk, then point the harnesses at
those paths.

| Resource | Upstream | What to use |
|---|---|---|
| **Behavior target / project** | [Daring Fireball – Markdown](https://daringfireball.net/projects/markdown/) | Gruber’s original Markdown; we match **`Markdown.pl`** behaviour (not CommonMark) |
| **Oracle binary** | Same project (`Markdown.pl` from the Markdown distribution) | A local `Markdown.pl` on disk; run with **perl** on `PATH` |
| **Fixture corpus** | [michelf/mdtest](https://github.com/michelf/mdtest) → [`Markdown.mdtest/`](https://github.com/michelf/mdtest/tree/master/Markdown.mdtest) | The classic 23-pair suite (`.text` + `.xhtml`/`.html`). Other suites in that repo (PHP Markdown, Extra) are out of scope |

**Example setup** (paths are yours to choose):

```bash
git clone https://github.com/michelf/mdtest.git /path/to/mdtest
# Download or copy Markdown.pl from the Markdown project into e.g. /path/to/Markdown.pl

export SHAKEDOWN_MDTEST=/path/to/mdtest/Markdown.mdtest
export SHAKEDOWN_MARKDOWN_PL=/path/to/Markdown.pl

uv run pytest tests/test_mdtest.py
uv run python scripts/strict_parity_harness.py
```

| Env var | Meaning |
|---|---|
| `SHAKEDOWN_MDTEST` | Directory of `*.text` / expected HTML pairs (`Markdown.mdtest`) |
| `SHAKEDOWN_MARKDOWN_PL` | Path to the `Markdown.pl` executable script |

If unset, tools fall back to a local convenience layout used on the original
dev machine — `~/mdtest/Markdown.mdtest` and `~/markdown/Markdown.pl`. That is
**not** required; prefer the env vars on any new checkout.

This project is an independent port. “Markdown” names the language and oracle;
it does not imply endorsement by the Markdown project or MDTest authors.

## License and credits

Shakedown is released under the [MIT License](LICENSE). See [NOTICE](NOTICE)
for third-party acknowledgements.

| Project | Role |
|---|---|
| [Markdown](https://daringfireball.net/projects/markdown/) / `Markdown.pl` (John Gruber) | Behavior oracle this port targets |
| [michelf/mdtest](https://github.com/michelf/mdtest) (`Markdown.mdtest`) | External fixture corpus (not vendored) |
| [shakespearelang](https://github.com/zmbc/shakespearelang) (MIT) | SPL interpreter used to run the play |

## Entry points

| Command | What it does |
|---|---|
| **`shakespeare run shakedown.spl`** | **Primary.** Run the committed play with any install of the SPL CLI. |
| **`./shakedown`** | Same play + error handling; `shakespeare` on `PATH`, else `uv run`. No assembly. |
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

Contributor tooling uses [uv](https://docs.astral.sh/uv/) and `pyproject.toml`
(tests, ruff, pyright, assemble). That is separate from the demo path above.

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
