# Selected Architecture

The selected Shakedown architecture is:

`docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md`

Accepted amendments, read with the base spec:

- `docs/superpowers/specs/2026-07-11-completability-hardening-design.md` —
  structural stream grammar, executable stack contracts, early span spike,
  continuous performance gates, and all-fixture differential smoke reporting.

That spec is canonical for:

- runtime boundary and release/dev wrapper shape
- source layout, assembly, and scoped codegen
- four-act pipeline and state carriers
- implementation order and fixture-to-slice routing
- architecture validation spikes

Where the 2026-07-11 amendment changes staging or a halt condition, the
amendment takes precedence until its decisions are folded into the base spec
by plan 3M.

The rest of `docs/architecture/` remains canonical architecture input and supporting rationale.
If an input doc conflicts with the selected architecture, follow the selected architecture unless
the conflict is explicitly reopened in a later accepted design or implementation plan.
