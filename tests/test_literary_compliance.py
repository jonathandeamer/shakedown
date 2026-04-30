from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO = Path(__file__).parent.parent
SRC = REPO / "src"
ASSEMBLED = REPO / "shakedown.spl"
LITERARY_TOML = SRC / "literary.toml"

PLAY_TITLE = "Shakedown: A Most Excellent Tragicomedy of Glyph and Line."
ACT_TITLES = {
    "act1": "Wherein the witches sort raw matter into shelves and seals.",
    "act2": "Wherein the kingdom of blocks is shaped, and each form named.",
    "act3": "Wherein the lovers gild the line with light and rose.",
    "act4": "Wherein Prospero, his work done, inscribes and releases all.",
}

SCENE_RE = re.compile(r"Scene\s+@(?P<label>[A-Z_][A-Z0-9_]*)\s*:\s*(?P<title>.+)")
RECALL_RE = re.compile(r"^(?P<speaker>[A-Z][A-Za-z ]+):\s*Recall\s+(?P<body>.+)$")
SPEAKER_ONLY_RE = re.compile(r"^(?P<speaker>[A-Z][A-Za-z ]+):$")
BAD_BIG_CAT_RE = re.compile(r"\ba big(?: big){3,} cat\b")
ACT_ROMAN = {"act1": "I", "act2": "II", "act3": "III", "act4": "IV"}
HIGH_VALUE_ATOMS = (
    "a normal little furry black cat",
    "a rural little green sweet flower",
    "a warm fair golden sunny summer's day",
    "a proud mighty bold noble hero",
    "a warm fine golden noble angel",
)
MAX_REPEATED_HIGH_VALUE_ATOM = 3
ARITHMETIC_OPERATORS = (
    "the sum of",
    "the product of",
    "the square of",
    "the difference between",
)
MAX_ARITHMETIC_OPERATORS_PER_STATEMENT = 4
MAX_LOGICAL_STATEMENT_CHARS = 220

CHARACTER_KEY = {
    "Hecate": "hecate",
    "Horatio": "horatio",
    "Juliet": "juliet",
    "Lady Macbeth": "lady_macbeth",
    "Macbeth": "macbeth",
    "Prospero": "prospero",
    "Puck": "puck",
    "Romeo": "romeo",
    "Rosalind": "rosalind",
}


def _production_source() -> str:
    return "\n".join(path.read_text() for path in sorted(SRC.glob("[0-9]*.spl")))


def _literary() -> dict[str, object]:
    with LITERARY_TOML.open("rb") as f:
        return tomllib.load(f)


def _is_inline_character_dialogue(line: str) -> bool:
    speaker, separator, body = line.strip().partition(":")
    return bool(separator) and speaker in CHARACTER_KEY and bool(body.strip())


def test_locked_play_title_and_act_titles() -> None:
    assembled = ASSEMBLED.read_text()
    data = _literary()

    assert assembled.splitlines()[0] == PLAY_TITLE
    play = data["play"]
    assert isinstance(play, dict)
    assert play["title"] == PLAY_TITLE

    acts = data["acts"]
    assert isinstance(acts, dict)
    for key, title in ACT_TITLES.items():
        assert acts[key]["title"] == title
        assert f"Act {ACT_ROMAN[key]}: {title}" in assembled


def test_scene_titles_have_toml_entries_and_match_source() -> None:
    data = _literary()
    scenes = data["scenes"]
    assert isinstance(scenes, dict)

    source_titles = {
        match["label"]: match["title"].strip()
        for match in SCENE_RE.finditer(_production_source())
    }
    assert source_titles
    assert set(source_titles) == set(scenes)
    for label, title in source_titles.items():
        scene = scenes[label]
        assert isinstance(scene, dict)
        assert scene["title"] == title
        assert scene["pattern"] in {
            "wherein",
            "bare_statement",
            "scene_of_character",
            "iconic_echo",
            "cross_character",
            "locale",
        }


def test_recall_phrases_are_in_speaker_pools() -> None:
    data = _literary()
    characters = data["characters"]
    assert isinstance(characters, dict)

    current_speaker: str | None = None
    for line in _production_source().splitlines():
        stripped = line.strip()
        speaker_only = SPEAKER_ONLY_RE.match(stripped)
        if speaker_only:
            current_speaker = speaker_only["speaker"]
            continue

        inline_match = RECALL_RE.match(stripped)
        if inline_match:
            speaker = inline_match["speaker"]
            recall = f"Recall {inline_match['body'].strip()}"
        elif stripped.startswith("Recall ") and current_speaker is not None:
            speaker = current_speaker
            recall = stripped
        else:
            continue

        key = CHARACTER_KEY[speaker]
        pool = characters[key].get("recall_pool", [])
        assert isinstance(pool, list)
        assert recall in pool, f"{speaker} missing recall pool entry {recall!r}"


def test_no_production_big_big_big_big_cat_atoms() -> None:
    source = _production_source()
    assert not BAD_BIG_CAT_RE.search(source)


def test_no_repeated_high_value_atom_chains() -> None:
    statements = re.split(r"\n\s*\n", _production_source())
    for statement in statements:
        compact = " ".join(statement.split())
        for atom in HIGH_VALUE_ATOMS:
            assert compact.count(atom) <= MAX_REPEATED_HIGH_VALUE_ATOM, (
                atom,
                compact,
            )


def test_numeric_recipe_complexity_stays_bounded() -> None:
    statements = re.split(r"\n\s*\n", _production_source())
    for statement in statements:
        compact = " ".join(statement.split())
        operator_count = sum(compact.count(op) for op in ARITHMETIC_OPERATORS)
        assert operator_count <= MAX_ARITHMETIC_OPERATORS_PER_STATEMENT, compact
        assert len(compact) <= MAX_LOGICAL_STATEMENT_CHARS, compact


def test_speaker_colon_layout_is_removed_when_supported() -> None:
    source = _production_source()
    layout_exceptions = _literary().get("layout_exceptions", {})
    assert isinstance(layout_exceptions, dict)
    if "speaker_colon_inline" in layout_exceptions:
        return
    offenders = [
        line for line in source.splitlines() if _is_inline_character_dialogue(line)
    ]
    assert not offenders[:10]
