# Shared splc IR Compilation Idioms

This document summarizes the core compilation idioms established by Amendment A2 to fit complex Acts inside Shakespeare Programming Language (SPL) constraints.

## 1. Bounded Scan Pipeline (`LYRIC_FIELD_*`)
HTML tags, autolink URLs, link destinations, and titles are compiled via a shared scan pipeline. 
Instead of dedicating separate scenes for each call site, we parameterize a single scanner on Juliet using a call-site register (`HECATE`).
* The caller sets a unique call-site code in `HECATE` and jumps to `LYRIC_FIELD_OPEN`.
* The shared pipeline processes characters and uses conditional branches based on `HECATE` to exit back to the correct caller continuation.

## 2. Capture-Hold-Requeue (Horatio Hold)
When content must be processed (e.g., strong/emphasis scans inside link label text) but output in a different order (e.g., link label appears after the `href` attribute in HTML), we capture raw input characters onto `HORATIO`'s stack first.
* Destination and titles are processed and written directly to `JULIET`.
* The held raw characters are then pushed back onto `PUCK`'s source buffer under a private resume sentinel.
* Ordinary top-level scan dispatch is resumed, processing entities and emphasis for free without duplicating any logic.

## 3. Duplicate-on-Reverse
For autolinks, the URL is emitted twice (once into `href`, once into the link text).
During the stack reverse operation in `LYRIC_FIELD_REV_KEEP`, a second copy is pushed back onto `ROMEO`'s stack when the call-site code specifies it. This allows re-draining the capture buffer without executing a second scan of the source.
