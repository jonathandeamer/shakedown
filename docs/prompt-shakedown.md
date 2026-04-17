@docs/lineage.md
@docs/research/project-history.md
@docs/research/shakedown-before-design.md
@docs/research/shakedown-spl-feasibility-assumption-corrections.md
@docs/research/shakedown-mdtest-fixture-matrix.md
@docs/research/shakedown-mdtest-architecture-memo.md
@docs/research/feasibility-summary.md
@docs/research/feasibility-summary-2.md
@docs/research/spl-act-architecture.md
@docs/research/slow-machine-spl-workflow.md
@docs/research/spl-feasibility-resumption-context.md
@docs/research/shakedown-divergences.md

Write a fresh Shakedown design doc and implementation plan for a Markdown.pl port in SPL.

Treat the research docs as evidence from a prior attempt, not prescriptions. Every architectural choice (file layout, orchestration, inner-loop tooling, AST caching, dispatch strategy, what "done" means) should be justified against the current state of the interpreter, the machine, and the test surface — not inherited. Where the design disagrees with prior conclusions, say so and why.

Keep the design mdtest-focused, preserve the lineage context, and do not write implementation code yet.
