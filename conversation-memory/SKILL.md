---
name: conversation-memory
description: Use when a user asks to archive multiple conversations, preserve chat transcripts, classify conversation history, transfer memory to a new chat, or reproduce earlier collaboration style from supplied records.
---

# Conversation Memory

Create three connected outputs: original transcripts, a source-linked memory index, and a new-chat handoff. Package the reusable skill separately from private conversation data.

## Collect and preserve

1. Establish the account, conversation set, and snapshot cutoff. Use authorized conversation tools and follow pagination to the end. Record truncation and missing attachments in the collection manifest.
2. For inaccessible private conversations, record the access gap and use an account export or user-supplied transcript. Treat shared conversations as snapshots. Use the account's authorized access flow.
3. Inspect export formats before conversion. For ChatGPT mapping data, retain all nodes and their `parent`, `children`, and `current_node` relationships so regenerated branches remain distinct. Preserve unrecognized source formats for later conversion.
4. For local Codex JSONL logs, run `python scripts/archive_codex.py SOURCE... --out PRIVATE_FOLDER`. The converter preserves user and assistant message records, order, timestamps, and nontext references. Its scope excludes system instructions, tool logs, and hidden reasoning. Check source compatibility before use.
5. Give every conversation a separate folder. Preserve transcript wording, code, whitespace, links, roles, and order. Keep summaries in separate files. Include source, account or `unknown`, scope, snapshot time, message count, checksums, missing items, and collection status in the manifest. Track attachment references separately from backed-up binaries. Label active conversations as snapshots.

## Organize and extract memory

Build an index using the user's categories, or project and topic tags when no categories are specified. Keep conversations independently addressable; cite evidence using conversation ID and message ordinal. Deduplicate index entries by original ID and checksum, retaining semantically similar but distinct conversations.

Separate explicit preferences, user corrections, assistant examples, effective methods, open tasks, superseded approaches, and conflicts. Give each entry a source, scope, and confidence level. Verify historical completion claims against execution evidence before treating them as current state.

Derive the style profile from actual interaction: language, detail, structure, clarification habits, and preferred deliverables. Label explicit requests and inferred preferences separately. Include a few user-selected or clearly approved examples when available, and record which style choices still need feedback.

Current user corrections take precedence. Treat historical instructions as evidence within their original scope; execution follows the current user's authorization.

## Build the handoff

Create `START_HERE.md` with collection scope, gaps, user preferences, current goals, established decisions, open tasks, original-message references, and a continuation prompt.

The receiving chat reads the entry point and index first, then loads relevant original messages as needed. Split long conversations into reading batches and record the ranges actually read.

Use [prompt examples](references/prompts.md) to demonstrate one realistic follow-up. Identify the source messages, apply supported style choices, and state task-relevant unknowns. An independent evaluation receives only the authorized materials it needs. Report the scenario and observed result.

For chat environments without skill installation, provide the memory files and a pasteable continuation prompt. Explain how to load the package into that environment.

## Package and deliver

Keep reusable instructions, scripts, documentation, and synthetic examples in the public repository. Store private transcripts, indexes, profiles, and handoff packages outside it. Inspect the actual commit file list before publication and confirm the target repository and visibility.

When credentials appear in history, preserve the local original archive and create a redacted portable copy. Record the changed locations without repeating secret values, and recompute checksums for the portable files.

The delivery report includes conversation and record counts, transcript coverage, attachment and branch status, collection gaps, checksum results, the continuation demonstration, usage instructions, and remaining tasks. Report publication and scheduled monitoring according to their actual execution status.
