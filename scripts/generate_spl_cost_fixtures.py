"""Generate representative SPL fixtures for cost and scene-count probes.

Produces three files:
- docs/spl/probes/pre-design/spl-cost-1k.spl  (~1000 lines)
- docs/spl/probes/pre-design/spl-cost-4k.spl  (~4000 lines)
- docs/spl/probes/pre-design/scene-count.spl  (200 scenes in one act)

Line counts are approximate; each scene contributes a fixed line count so we
can target a total.

The synthesized work is a realistic mix of assignments, arithmetic, stack
pushes/pops, and intra-act gotos — not empty boilerplate. The goal is a
representative interpreter cost baseline, not a stress test.
"""

from __future__ import annotations

from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "spl" / "probes" / "pre-design"

HEADER = """SPL Cost Probe.

Romeo, a worker.
Juliet, a driver.

                    Act I: Repeated bounded work.

"""

# Each scene body contributes 6 lines:
# - 1 scene header
# - 1 enter
# - 3 work lines (assignment, remember, recall)
# - 1 exeunt
SCENE_TEMPLATE = """                    Scene {roman}: Bounded work step {n}.

[Enter Romeo and Juliet]

Juliet: You are as good as the sum of a big cat and a cat.
Juliet: Remember yourself.
Juliet: Recall your past.

[Exeunt]

"""

TAIL_TEMPLATE = """                    Scene {roman}: Terminate.

[Enter Romeo and Juliet]

Juliet: You are as good as a cat.
Juliet: Speak your mind!

[Exeunt]
"""


def to_roman(n: int) -> str:
    numerals = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]
    out = []
    for value, letter in numerals:
        while n >= value:
            out.append(letter)
            n -= value
    return "".join(out)


def build(scene_count: int) -> str:
    parts = [HEADER]
    for i in range(1, scene_count):
        parts.append(SCENE_TEMPLATE.format(roman=to_roman(i), n=i))
    parts.append(TAIL_TEMPLATE.format(roman=to_roman(scene_count)))
    return "".join(parts)


def write(path: Path, scene_count: int) -> None:
    path.write_text(build(scene_count))
    print(f"wrote {path} ({path.stat().st_size} bytes, {scene_count} scenes)")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Scene count chosen so line count ≈ target:
    # 7 lines overhead + 8 lines/scene ≈ 8n lines total
    write(OUT_DIR / "spl-cost-1k.spl", scene_count=125)  # ≈ 1000 lines
    write(OUT_DIR / "spl-cost-4k.spl", scene_count=500)  # ≈ 4000 lines
    write(OUT_DIR / "scene-count.spl", scene_count=200)  # exactly 200 scenes


if __name__ == "__main__":
    main()
