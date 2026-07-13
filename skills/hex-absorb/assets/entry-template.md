---
id: kebab-case-id
title: Short human title
tag: mechanical
since: 1.60.0
until: ''
supersedes: ''
provenance: ai-tools:hexalith-llm-instructions.md#section
verified: ''
drained: na
---

# Short human title

## Statement

The rule, stated normatively — what a conformant Hexalith module does.

## Why

The rationale. Downstream skills need it to apply the rule to cases nobody foresaw.

## Conformant example

Minimal code, or a pointer into framework source or a reference module (`repo@ref:path`).

<!--
Field legend — this comment never appears in real entries:

id          must equal the filename without .md
tag         mechanical (pattern-checkable, analyzer territory) | judgment (needs reasoning, LLM territory)
since       framework version where this convention starts applying
until       framework version where it was superseded; empty = current convention.
            Superseded entries are hex-migrate's from-states — never delete them.
supersedes  comma-separated ids of the entries this convention replaces
provenance  where this claim came from: ai-tools:<file>#<section> | framework:<repo>@<ref> | authored:<who>
verified    YYYY-MM-DD this Statement was last verified against framework source; empty = never
drained     yes | no | na — 'no' means Hexalith.AI.Tools still holds this content
            (drain pending); 'na' means the entry never came from AI.Tools.

Frontmatter is flat 'key: value' only — no nesting, no inline comments
(provenance values contain '#'). kb.py validate enforces all of this.
-->
