from __future__ import annotations

import re
import tomllib
from collections import Counter
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
PROSPERO_EQUALITY_RE = re.compile(r"\bYou are (as [a-z-]+ as)\b")
BAD_BIG_CAT_RE = re.compile(r"\ba big(?: big){3,} cat\b")
VALUE_ATOM_RE = re.compile(
    r"\b(?:a|an)\s+(?P<adjectives>[a-z][a-z' -]*?)\s+"
    r"(?P<noun>cat|flower|day|rose|hero|angel|tree|brother)\b",
    re.IGNORECASE,
)
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
SCENE_TITLE_WORD_LIMITS = {
    "wherein": (6, 12),
    "bare_statement": (4, 10),
    "scene_of_character": (5, 10),
    "iconic_echo": (3, 8),
    "cross_character": (6, 14),
    "locale": (3, 7),
}

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
REFERENCE_SCENES = {
    "LYRIC_OPEN_CONSULT_REFERENCE_ONE",
    "LYRIC_CONSULT_REFERENCE_ONE",
    "LYRIC_OPEN_OUTPUT_REFERENCE_ONE",
    "LYRIC_OPEN_CONSULT_REFERENCE_TWO",
    "LYRIC_CONSULT_REFERENCE_TWO",
    "LYRIC_OPEN_OUTPUT_REFERENCE_TWO",
}
JULIET_NIGHT_WORDS = {"night", "star", "stars", "starlit", "silver"}
IMPLEMENTATION_META_WORDS = {
    "adjective",
    "adjectives",
    "codegen",
    "implementation",
    "mechanism",
    "token",
    "tokens",
}
ACT_IV_DULL_VERBS = {"tests", "opens", "closes"}
MAX_ACT_IV_DULL_VERB_USES = 2


def _production_source() -> str:
    return "\n".join(path.read_text() for path in sorted(SRC.glob("[0-9]*.spl")))


def _literary() -> dict[str, object]:
    with LITERARY_TOML.open("rb") as f:
        return tomllib.load(f)


def _is_inline_character_dialogue(line: str) -> bool:
    speaker, separator, body = line.strip().partition(":")
    return bool(separator) and speaker in CHARACTER_KEY and bool(body.strip())


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text))


def _speaker_counts(source: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in source.splitlines():
        match = SPEAKER_ONLY_RE.match(line.strip())
        if match and match["speaker"] in CHARACTER_KEY:
            counts[match["speaker"]] += 1
    return counts


def _scene_blocks(source: str) -> dict[str, str]:
    matches = list(SCENE_RE.finditer(source))
    blocks: dict[str, str] = {}
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(source)
        blocks[match["label"]] = source[start:end]
    return blocks


def _scene_titles() -> dict[str, str]:
    return {
        match["label"]: match["title"].strip()
        for match in SCENE_RE.finditer(_resolved_production_source())
    }


def _words(text: str) -> set[str]:
    return {word.lower() for word in re.findall(r"[A-Za-z']+", text)}


def _preamble_character_lines(source: str) -> set[str]:
    preamble = _resolved_production_source().split("Act I:", maxsplit=1)[0]
    return {
        character
        for character in CHARACTER_KEY
        if re.search(rf"^{re.escape(character)},", preamble, re.MULTILINE)
    }


def _resolved_production_source() -> str:
    data = _literary()
    source = _production_source()

    def replace(match: re.Match[str]) -> str:
        current: object = data
        key = match.group(1)
        for part in key.split("."):
            assert isinstance(current, dict), key
            current = current[part]
        assert isinstance(current, str), key
        return current

    return re.sub(r"@LIT\.([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*)", replace, source)


def _recall_values(character: dict[str, object]) -> set[str]:
    recall = character.get("recall")
    if isinstance(recall, dict):
        return {value for value in recall.values() if isinstance(value, str)}
    recall_pool = character.get("recall_pool")
    if isinstance(recall_pool, list):
        return {value for value in recall_pool if isinstance(value, str)}
    return set()


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

    source_titles = _scene_titles()
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


def test_scene_titles_fit_declared_pattern_lengths() -> None:
    scenes = _literary()["scenes"]
    assert isinstance(scenes, dict)
    for label, scene in scenes.items():
        assert isinstance(scene, dict)
        pattern = scene["pattern"]
        title = scene["title"]
        assert isinstance(pattern, str)
        assert isinstance(title, str)
        low, high = SCENE_TITLE_WORD_LIMITS[pattern]
        assert low <= _word_count(title) <= high, (label, pattern, title)


def test_recall_phrases_are_in_speaker_pools() -> None:
    data = _literary()
    characters = data["characters"]
    assert isinstance(characters, dict)

    current_speaker: str | None = None
    for line in _resolved_production_source().splitlines():
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
        character = characters[key]
        assert isinstance(character, dict)
        pool = _recall_values(character)
        assert recall in pool, f"{speaker} missing recall pool entry {recall!r}"


def test_prospero_assignment_equalities_use_his_pool() -> None:
    data = _literary()
    characters = data["characters"]
    assert isinstance(characters, dict)
    prospero = characters["prospero"]
    assert isinstance(prospero, dict)
    soft = prospero["soft_variation"]
    assert isinstance(soft, dict)
    equality_pool = soft["equality"]
    assert isinstance(equality_pool, list)

    current_speaker: str | None = None
    for line in _production_source().splitlines():
        stripped = line.strip()
        speaker_only = SPEAKER_ONLY_RE.match(stripped)
        if speaker_only:
            current_speaker = speaker_only["speaker"]
            continue
        if current_speaker != "Prospero":
            continue
        match = PROSPERO_EQUALITY_RE.search(stripped)
        if match:
            assert match.group(1) in equality_pool, stripped


def test_no_production_big_big_big_big_cat_atoms() -> None:
    source = _production_source()
    assert not BAD_BIG_CAT_RE.search(source)


def test_value_atoms_do_not_repeat_adjectives() -> None:
    for match in VALUE_ATOM_RE.finditer(_production_source()):
        adjectives = match["adjectives"].lower().split()
        assert len(adjectives) == len(set(adjectives)), match.group(0)


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


def test_named_production_characters_have_speaking_lines() -> None:
    source = _production_source()
    counts = _speaker_counts(source)
    introduced = _preamble_character_lines(source)
    silent = [character for character in introduced if counts[character] == 0]
    assert not silent


def test_reference_librarian_is_visible_in_reference_scenes() -> None:
    blocks = _scene_blocks(_production_source())
    reference_text = "\n".join(blocks[label] for label in sorted(REFERENCE_SCENES))
    assert reference_text.count("Rosalind:") >= 4


def test_juliet_surfaces_include_night_or_star_imagery() -> None:
    data = _literary()
    characters = data["characters"]
    assert isinstance(characters, dict)
    juliet = characters["juliet"]
    assert isinstance(juliet, dict)

    titles = _scene_titles()
    juliet_titles = " ".join(
        title
        for title in titles.values()
        if "Juliet" in title or _words(title) & {"rose", "evening"}
    )
    surfaces = f"{juliet['blurb']} {juliet_titles}"
    assert _words(surfaces) & JULIET_NIGHT_WORDS


def test_act_iv_scene_titles_use_ceremonial_verb_variety() -> None:
    titles = _scene_titles()
    act_iv_titles = [
        title
        for label, title in titles.items()
        if label.startswith("SCRIBE_") or label == "ACT_IV_DONE"
    ]
    words = Counter(
        word
        for title in act_iv_titles
        for word in re.findall(r"[A-Za-z']+", title.lower())
    )
    overused = {
        verb: words[verb]
        for verb in ACT_IV_DULL_VERBS
        if words[verb] > MAX_ACT_IV_DULL_VERB_USES
    }
    assert not overused


def test_character_blurbs_avoid_implementation_meta_language() -> None:
    data = _literary()
    characters = data["characters"]
    assert isinstance(characters, dict)
    offenders: dict[str, set[str]] = {}
    for key, character in characters.items():
        assert isinstance(character, dict)
        blurb = character["blurb"]
        assert isinstance(blurb, str)
        meta_words = _words(blurb) & IMPLEMENTATION_META_WORDS
        if meta_words:
            offenders[key] = meta_words
    assert not offenders


def test_dramatic_moments_are_visible_in_scene_surfaces() -> None:
    data = _literary()
    moments = data["dramatic_moments"]
    assert isinstance(moments, dict)
    titles = _scene_titles()
    blocks = _scene_blocks(_production_source())

    missing: list[str] = []
    for name, moment in moments.items():
        assert isinstance(moment, dict)
        scene = moment["scene"]
        character = moment["character"]
        assert isinstance(scene, str)
        assert isinstance(character, str)
        title_words = _words(titles[scene])
        block_words = _words(blocks[scene])
        character_words = _words(character)
        if not (title_words & character_words or block_words & character_words):
            missing.append(name)
    assert not missing


def test_active_character_motifs_are_visible() -> None:
    data = _literary()
    characters = data["characters"]
    production_motifs = data["production_motifs"]
    assert isinstance(characters, dict)
    assert isinstance(production_motifs, dict)
    titles = " ".join(_scene_titles().values())
    source = _production_source()
    active_keys = {
        CHARACTER_KEY[character] for character in _preamble_character_lines(source)
    }

    missing: dict[str, set[str]] = {}
    for key in active_keys & set(production_motifs):
        character = characters[key]
        motifs = production_motifs[key]
        assert isinstance(character, dict)
        assert isinstance(motifs, list)
        assert all(isinstance(motif, str) for motif in motifs)
        blurb = character["blurb"]
        assert isinstance(blurb, str)
        surfaces = f"{blurb} {titles}"
        motif_set = set(motifs)
        motif_hits = _words(surfaces) & motif_set
        if not motif_hits:
            missing[key] = motif_set
    assert not missing


def test_controlled_surfaces_use_literary_placeholders_in_source() -> None:
    source = _production_source()
    assert "@LIT.play.title" in source
    for act in ACT_TITLES:
        assert f"@LIT.acts.{act}.title" in source
    assert "@LIT.scenes." in source
    assert "@LIT.characters." in source


def test_all_literary_placeholders_in_source_resolve() -> None:
    source = _production_source()
    resolved = _resolved_production_source()
    assert "@LIT." in source
    assert "@LIT." not in resolved
    assert "@LIT." not in ASSEMBLED.read_text()


def test_scene_ledger_matches_source_scene_labels() -> None:
    data = _literary()
    scenes = data["scenes"]
    assert isinstance(scenes, dict)
    source_labels = {
        match["label"] for match in SCENE_RE.finditer(_production_source())
    }
    assert set(scenes) == source_labels


def test_controlled_literals_are_not_duplicated_inline() -> None:
    data = _literary()
    source = _production_source()
    assembled = ASSEMBLED.read_text()

    play = data["play"]
    assert isinstance(play, dict)
    assert play["title"] in assembled
    assert play["title"] not in source

    acts = data["acts"]
    assert isinstance(acts, dict)
    for act in acts.values():
        assert isinstance(act, dict)
        title = act["title"]
        assert isinstance(title, str)
        assert title in assembled
        assert title not in source
