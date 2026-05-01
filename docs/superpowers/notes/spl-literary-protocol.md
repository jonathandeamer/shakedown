# SPL Literary Protocol

Use this block in any run-loop prompt or implementation plan that asks an agent
to edit `src/*.spl`, `scripts/assemble.py`, `scripts/codegen_html.py`, or any
future SPL code generator.

Before editing, read:

- `docs/spl/literary-spec.md`
- `docs/spl/style-lexicon.md`
- `docs/spl/codegen-style-guide.md`
- `src/literary.toml`

Rules:

- Classify new prose before writing it: Critical, Stable Utility, Incidental,
  Recall, title, scene title, or dramatic tag.
- Controlled surfaces belong in `src/literary.toml` and are referenced from SPL
  or codegen by key.
- Do not invent recurring literary surfaces inline when TOML already owns the
  category.
- Use `docs/spl/style-lexicon.md` and `docs/spl/codegen-style-guide.md` for
  Incidental prose that remains hand-authored.
- Run the exact compliance tests named by the active plan after changing SPL,
  assembler, or codegen behavior. Do not write "literary compliance" as a
  generic placeholder for test commands.
