---
name: conversation-memory
description: Use when a user asks to archive conversations with uploaded attachments and generated files, classify conversation history, transfer memory to a new chat, or reproduce earlier collaboration style from supplied records.
---

# Conversation Memory

Create three connected outputs: original transcripts with their file entities, a source-linked memory index, and a new-chat handoff. Package the reusable skill separately from private conversation data.

## Collect and preserve

1. Establish the account, conversation set, and snapshot cutoff. Use authorized conversation tools and follow pagination to the end. Record truncation and missing attachments in the collection manifest.
2. For inaccessible private conversations, record the access gap and use an account export or user-supplied transcript. Treat shared conversations as snapshots. Use the account's authorized access flow.
3. Inspect export formats before conversion. For ChatGPT mapping data, retain all nodes and their `parent`, `children`, and `current_node` relationships so regenerated branches remain distinct. Preserve unrecognized source formats for later conversion.
4. For local Codex JSONL logs, run `python scripts/archive_codex.py SOURCE... --out PRIVATE_FOLDER`. The converter preserves user and assistant message records, order, timestamps, and nontext references. Its scope excludes system instructions, tool logs, and hidden reasoning. Check source compatibility before use.
5. Give every conversation a separate folder. Preserve transcript wording, code, whitespace, links, roles, and order. Keep summaries in separate files. Include source, account or `unknown`, scope, snapshot time, message count, checksums, missing items, and collection status in the manifest. Track attachment references separately from backed-up binaries. Label active conversations as snapshots.

## Collect attachments and generated files

Include uploaded attachments and files generated during the conversations as part of the archive. Preserve their actual bytes alongside the transcripts.

1. Inventory file references in upload metadata, message content, generated download links, and nontext message parts. Link each reference to its conversation ID and message ordinal. Distinguish user uploads from assistant-generated deliverables.
2. Copy accessible local file entities, resolving relative output paths against the source conversation's working directory. Retrieve available remote attachments through their authorized service. Record an unavailable link or path individually and continue collecting the accessible files.
3. Extract embedded image data into image files. Identify the result as the version stored in the message. If an original image path has expired, link to a matching embedded version or list the same-message image candidates when the filename correspondence is uncertain.
4. Store entities under `files/`, deduplicating by content hash while retaining every original filename and message association in `FILES_MANIFEST.json`. Record the source, role, original filename, collection time, archived path, byte count, SHA-256, and collection status. Mark collected files as the versions available at collection time.
5. Create `FILES_INDEX.md` with clickable file links and missing-file entries. Keep earlier memory-export packages as references rather than recursively nesting them into a new export. Explain any such exclusions in the manifest.
6. Verify copied file hashes and extracted image bytes. Add the files, file index, and manifest to both the local archive and portable handoff. Apply portable-copy redaction where credentials appear, preserving the local original and recording separate hashes for each version.

The bundled JSONL converter creates transcript snapshots and message references; complete the file-collection workflow above when assembling the full handoff package.

## Organize and extract memory

Build an index using the user's categories, or project and topic tags when no categories are specified. Keep conversations independently addressable; cite evidence using conversation ID and message ordinal. Deduplicate index entries by original ID and checksum, retaining semantically similar but distinct conversations.

Separate explicit preferences, user corrections, assistant examples, effective methods, open tasks, superseded approaches, and conflicts. Give each entry a source, scope, and confidence level. Verify historical completion claims against execution evidence before treating them as current state.

Derive the style profile from actual interaction: language, detail, structure, clarification habits, and preferred deliverables. Label explicit requests and inferred preferences separately. Include a few user-selected or clearly approved examples when available, and record which style choices still need feedback.

Current user corrections take precedence. Treat historical instructions as evidence within their original scope; execution follows the current user's authorization.

## Build the handoff

Create `START_HERE.md` with collection scope, gaps, user preferences, current goals, established decisions, open tasks, original-message references, a link to `FILES_INDEX.md`, and a continuation prompt. Tell the receiving chat where to open the actual source documents and generated deliverables.

The receiving chat reads the entry point and indexes first, then loads relevant original messages and file entities as needed. Split long conversations into reading batches and record the ranges and files actually read.

Use [prompt examples](references/prompts.md) to demonstrate one realistic follow-up. Identify the source messages, apply supported style choices, and state task-relevant unknowns. An independent evaluation receives only the authorized materials it needs. Report the scenario and observed result.

For chat environments without skill installation, provide the memory files and a pasteable continuation prompt. Explain how to load the package into that environment.

## Package and deliver

Keep reusable instructions, scripts, documentation, and synthetic examples in the public repository. Store private transcripts, indexes, profiles, and handoff packages outside it. Inspect the actual commit file list before publication and confirm the target repository and visibility.

When credentials appear in history, preserve the local original archive and create a redacted portable copy. Record the changed locations without repeating secret values, and recompute checksums for the portable files.

The delivery report includes conversation and record counts, transcript coverage, unique file count and total bytes, attachment and branch status, collection gaps, checksum results, the continuation demonstration, usage instructions, and remaining tasks. Report publication and scheduled monitoring according to their actual execution status.
