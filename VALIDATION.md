# Validation

Validated on 2026-10-19.

## Skill structure

The skill passes the frontmatter and naming validator. Validation runs in Python UTF-8 mode on Windows.

## Archive converter

Checks cover:

- Exact preservation of Unicode text, newlines, code blocks, and whitespace.
- Preservation of nontext references.
- User and assistant message selection.
- Explicit reporting of malformed records.
- Output checksums and protection against overwriting existing snapshots.

## Continuation workflow

A separate evaluator read a handoff package and its source messages, carried forward the user's documented preferences and corrections, and identified missing source material. Evaluation covered collection scope, source references, and continuation behavior.

## Converter scope

The included script processes local Codex JSONL message records. Account export conversion and attachment backup use the collection workflow in SKILL.md.
