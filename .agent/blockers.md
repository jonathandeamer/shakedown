# Active blockers (MCO loop)

No active blockers. Amendment A15 (2026-07-19) to
`docs/superpowers/plans/2026-07-18-slice-5-documentation-aggregates.md`
(binding design Amendment A14) resolved the Task-3 Step-3 TOML-shape
contradiction: every spare label installs under `[spares.LABEL]` instead of
`[scenes.LABEL]`, so the mandatory `test_scene_titles_have_toml_entries_and_match_source`
/`test_scene_ledger_matches_source_scene_labels` scene-ledger equality holds
with zero spares in `data["scenes"]`. The separable Setext/ATX/code-line IR
reconstruction may now proceed from this corrected TOML shape; the working
tree's preserved `tests/test_act2_slice4.py` and `tests/test_splc_validate.py`
edits and the untracked `scripts/release_entry.py` remain as before.
