# SPL-pure rewrite inventory (2026-07-19)

Evidence-only note for plan row 9 Task 1. Lists mdtest fixtures where
`rewrite_task3_markdown(text) != text`, and the first semantic class of change
observed by sampling `difflib` of raw vs rewritten text.

Fixture set matches `tests/test_spl_pure_inventory.py` (`_REWRITE_TOUCHED`).

| Fixture | First semantic class of rewrite change |
|---|---|
| Amps and angle encoding | Reference + inline links rewritten to pre-emitted `<a href=…>` with `&amp;` in URLs/titles; reference definition lines stripped |
| Images | Inline images normalized (empty title `""`, angle-bracket dest unwrapped); reference images resolved to inline form; reference defs stripped; one bare link rewritten to `<a>` |
| Links, inline style | Inline `[text](url)` (titles, angle brackets, empty dest, parens in URL) → pre-emitted `<a href=…>` |
| Links, reference style | Reference links (full/collapsed/spaced, nested brackets, indent rules) → `<a>`; definition lines stripped |
| Links, shortcut references | Shortcut/collapsed refs and multi-word/line-break labels → `<a>`; definition lines stripped |
| Literal quotes in titles | Reference + inline links with quotes in titles → `<a title="…&quot;…">`; def lines stripped |
| Markdown Documentation - Basics | Reference links in prose → `<a>`; trailing reference definition block stripped |
| Markdown Documentation - Syntax | TOC and body reference/inline links → `<a>`; reference defs stripped; images/links throughout doc body rewritten |

**Pure-path red contract:** IR interpreter fed raw fixture text (no
`rewrite_task3_markdown`) is expected wrong until Act I owns strip and Act III
owns link/image resolution (Tasks 2–4). Witnesses live in
`test_raw_ir_matches_oracle_without_rewrite` as strict xfails while
`PURE_SPL_REWRITE_RETIRED` is false.
