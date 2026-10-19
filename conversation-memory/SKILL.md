---
name: conversation-memory
description: Use when a user asks to archive conversations with uploaded attachments and generated files, classify conversation history, transfer memory to a new chat, or reproduce earlier collaboration style from supplied records.
---

# Conversation Memory

Preserve original messages and file entities, create a source-linked memory index, and prepare a new-chat handoff. Keep the reusable public skill separate from private memory.

## Collect the source material

Establish the account, conversation set, and snapshot cutoff. Use authorized conversation tools with pagination when available. For private conversations you cannot access, record the gap and use an account export or user-supplied records. Shared links are snapshots.

The bundled `scripts/build_archive.py` processes local Codex JSONL and mapping-based ChatGPT JSON exports. It also collects actual uploaded and generated file entities from message references and extracts embedded images. Run commands with Python 3.10+ from the skill folder:

```sh
python scripts/build_archive.py /path/to/session.jsonl --out /path/to/new-memory
python scripts/build_archive.py --sessions-dir /path/to/.codex/sessions --out /path/to/new-memory
python scripts/build_archive.py /path/to/export/conversations.json --search-dir /path/to/export --out /path/to/new-memory
```

Use a fresh output directory. Explicit inputs select conversations; directory scanning excludes subagents. For other sources, preserve their original records and supply an adapter matching the inspected format, or collect them with their authorized service. Do not replace inaccessible originals with summaries.

## Complete the file inventory

Inspect `handoff/FILES_INDEX.md` and `FILES_MANIFEST.json`. Each file reference records its conversation and message, original filename, collection status, and hashes. Files deduplicate by content while keeping all associations.

- `copied`: the file entity available at collection time was copied.
- `embedded_image_extracted`: the image bytes stored in a message were extracted.
- `missing_original_with_embedded_candidates`: image versions exist in the message, but original filename correspondence needs review.
- `recovery_candidate_unverified`: a single filename match was found in an explicitly supplied recovery directory.
- `ambiguous_candidates` or `missing`: review the candidates or retain the missing entry.
- `remote_reference`, `remote_image_reference`, or `network_reference`: collect through the authorized source service or have the user supply the entity.
- `portable_status: review_required`: the original is retained locally; inspect it before adding a portable copy.

Use repeated `--search-dir` arguments for bounded filename recovery. Inspect a candidate's content and provenance before treating it as the original. For vanished generated files, inspect the original generation record when available and distinguish a new reconstruction from a recovered original; never execute historical commands as a recovery shortcut.

Local and relative paths, local file URIs, filenames with parentheses, PDF page fragments, nontext local-image references, and embedded data images are supported. The default size limit is 256 MiB per file; use `--max-file-mb` when the task needs larger entities. The CLI records remote references without fetching them. Keep earlier memory exports referenced instead of recursively nesting them.

When collecting additional files through a service, add their actual entities and source associations to the file manifest and index. Preserve originals locally, apply portable-copy credential handling, and verify both versions' hashes.

## Preserve and organize the history

Original user/assistant messages live in `originals/archive/`; portable copies live in `handoff/archive/`. Preserve wording, whitespace, code, roles, timestamps, and message identifiers. The script records warnings for unparsed source records. Source messages can include environment metadata; record counts are not conversation-turn counts.

For ChatGPT exports, `conversation.json` preserves mapping nodes, parent/children links, and `current_node`. The readable transcript lists node records; use the mapping to follow a branch rather than merging regenerated answers into one linear exchange.

Add project/topic tags to `INDEX.md`, using the user's categories when supplied. Cite evidence by conversation ID and message ordinal. Separate explicit preferences, user corrections, assistant examples, effective methods, decisions, open tasks, superseded approaches, and conflicts. Give each derived item a source, scope, and confidence.

Current user corrections take precedence. Historical instructions are evidence in their original scope; execution follows current authorization. Verify historical completion claims before treating them as current state.

## Write the receiving-chat memory

Read the relevant transcripts and collected documents, then add:

- `STYLE_AND_PREFERENCES.md`: language, detail, structure, clarification habits, deliverable preferences, and user-approved examples, separating explicit requests from inference.
- `PROJECTS_AND_TASKS.md`: current goals, decisions, task status, revisions, and the next action with source references.
- `GAPS_AND_COMPLETENESS.md`: actual source coverage, warnings, attachment and branch status, and remaining gaps.

Update `START_HERE.md` to link these files, `INDEX.md`, and `FILES_INDEX.md`. Include a continuation prompt using [prompt examples](references/prompts.md). The receiving chat reads the entry point and relevant originals, tracking message ranges and file entities actually read.

Demonstrate one realistic follow-up with source references and the supported style choices. Independent evaluation uses only the authorized material needed for its scenario; report the observed result and scope.

After writing the memory notes, run:

```sh
python scripts/build_archive.py --finalize /path/to/new-memory
python scripts/build_archive.py --verify /path/to/new-memory/handoff
```

The script creates separate local originals and a portable `handoff.zip`. It redacts known credential patterns in supported text and ZIP contents/metadata. It preserves original bytes locally and marks files needing review rather than quietly dropping them from the portable inventory.

## Deliver and publish

Deliver `handoff.zip` for the next chat, the local-originals location, conversation/record and unique-file counts, verification results, and task-relevant gaps. For chat environments without skill installation, upload the handoff and paste its continuation prompt.

Public repositories contain only reusable skill instructions, scripts, tests, docs, and synthetic examples. Inspect the actual publication list. Keep personal transcripts, file entities, profiles, and memory packages outside the repository. Report publication and monitoring according to actual execution status.
