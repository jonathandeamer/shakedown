# Intentional Divergences from Markdown.pl

This file documents where Shakedown deliberately differs from Markdown.pl and why.

| Feature | Markdown.pl behaviour | Shakedown behaviour | Reason |
|---|---|---|---|
| Email auto-links | Each character randomly encoded as decimal or hex HTML entity (e.g. `&#109;`, `&#x61;`) | Plain `<a href="mailto:address">address</a>` with literal characters | SPL has no randomness primitive — the language provides no equivalent of Perl's `rand` |
| Nested blockquote closing | For input `> Outer.\n>\n> > Inner.`, the outer `</blockquote>` is emitted as `<p></blockquote></p>` — a malformed tag inside a paragraph | The outer `</blockquote>` is emitted as a bare closing tag at the correct nesting level | The Markdown.pl output is a rendering artefact/quirk; emitting structurally valid HTML is the correct behaviour |
