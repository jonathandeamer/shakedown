# Shakedown Before Design

Use this as the short reminder before writing another Shakedown design doc or plan.

## What The Repo Already Taught

- `shakedown` in SPL proved the target is not blocked by Markdown.pl itself, but by SPL's shape for this workload.
- SPL's act-boundary rules force the main loop into one act, which made the block handler architecture brittle and duplicative.
- The SPL interpreter was too slow on this hardware for the Huntley loop to stay practical.
- The useful Shakedown lesson is not "try harder"; it is "design around the constraints that already showed up."
- The mdtest ceiling is the real planning target, not abstract SPL completeness.

## What To Carry Forward

- Start from the validated block-level baseline, not from the original multi-act wish list.
- Treat recursive dispatch, cached execution, and buffered inline handling as the working shape until proven otherwise.
- Keep the design mdtest-only and fixture-driven.
- Treat email autolink encoding, emphasis backtracking, loose lists, and exact nested block composition as the main ceiling risks.

## What Not To Re-Litigate

- Do not reopen the question of whether SPL can be made to work at all for Markdown.pl.
- Do not re-argue the old six-character-budget framing; the correction note already replaces it.
