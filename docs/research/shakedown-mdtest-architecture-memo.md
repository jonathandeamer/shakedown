# Shakedown Mdtest-Only Architecture Memo

This memo gives the next Shakedown design/planning agent one recommended build shape for a
mdtest-focused implementation.

It is not a design doc. Its purpose is to convert the existing feasibility results into one
planning stance so the next agent does not need to re-synthesize the architecture from scratch.

## Planning Stance

The target is to maximize passes and push toward the current mdtest ceiling rather than to
pre-declare fixtures out of scope.

## Recommended Build Shape

### Runtime

Use the cached-AST execution model validated in phase 2. The planning assumption should be
that Shakedown is run by parsing once, caching the AST, and executing test sessions from the
cached representation rather than paying full parse cost on every run.

### Block Dispatcher

Use a single-act block dispatcher. Shared-scene return-address routing should be treated as
the default consolidation pattern for common utility paths.

### Inline Processing

Treat inline handling as a mixed model:
- streaming logic for simple cases such as code spans, escapes, and basic HTML detection
- buffered scans for emphasis and reference-style constructs

The design should assume that exact Markdown.pl emphasis behavior is still a ceiling risk,
not a solved primitive.

### Lists

Design around tight-list handling and bounded 2-level nesting as the validated baseline.
Loose-list exactness should be treated as an unresolved risk to push against during
implementation.

### Nested Blocks

Use buffer-fed recursive dispatch plus sentinel-delimited frame management as the recommended
approach for blockquote/list and other nested compositions.

The design should assume that exact nested block composition output is still one of the
highest-risk mdtest areas.

### Divergence Handling

The planning assumption should continue to treat email autolink encoding as the clearest
known likely mdtest miss, because the feasibility work identifies it as a permanent SPL
divergence tied to missing randomness.

## What The Next Design Doc Should Treat As Fixed

- mdtest is the only success surface
- cached-AST runtime is the assumed execution model
- single-act dispatcher is the assumed control-flow shape
- recursive dispatch is the assumed nested-block mechanism
- buffered emphasis and reference-link handling are expected where needed
- loose lists, emphasis edge cases, and exact nested block compositions are the main ceiling risks

## What The Next Design Doc Should Still Decide

- the concrete build order across risky fixture groups
- the exact integration boundaries between block and inline phases
- the milestone sequence for chasing the mdtest ceiling
