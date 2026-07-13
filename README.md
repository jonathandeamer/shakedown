# Shakedown

This repository is the working home for the next SPL implementation attempt at Markdown.pl.

It keeps the lineage and docs close by so design and planning can stay grounded in the earlier Shakedown, Snarkdown, and Quackdown work.

If you have a sibling `quackdown` checkout locally, it can be used as a convenience reference for the historical research docs. This repo is self-contained, but the sibling checkout remains the provenance source for the original story.

Start with [`docs/README.md`](docs/README.md).

That docs index is the canonical entry point for new sessions and architecture work.

## Autonomous workflow

`./agent-loop` is the active MCO-backed roadmap executor. It reads the sole
in-flight plan (or writes the next Superpowers-style plan), runs one step per
iteration, switches eligible providers on rate limits or zero progress, and
owns the final full-suite/23-fixture parity gate.
Successful iterations create conventional commits at logical checkpoints and
push the current branch for GitHub visibility.

```bash
npm install -g @tt-a1i/mco@0.10.8
./agent-loop --dry-run   # show classified action and selected executor
./agent-loop --once      # execute one MCO iteration
./agent-loop             # continue until interrupted or genuinely complete
```

Model policy and fallbacks live in `agent-loop.toml`. The legacy `run-loop`
driver and its prompt have been removed; they survive only in git history
and `docs/archive/`.
