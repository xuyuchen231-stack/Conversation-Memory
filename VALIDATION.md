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

## File collection workflow

An archive assembly run exercised local uploaded-file and generated-file collection, embedded image extraction, content-hash deduplication, source-message indexing, missing-path reporting, and portable-copy credential checks. Collected entities passed SHA-256 checks in the local archive and portable package; both resulting ZIP archives passed integrity checks.

The file collector used for that run was an archive-specific assembly helper. The reusable skill documents the collection steps; the bundled JSONL script remains the transcript converter.
