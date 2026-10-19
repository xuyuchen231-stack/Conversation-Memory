# Conversation Memory

Archive conversations, organize them by project, and carry context into a new chat.

Conversation Memory keeps original transcripts alongside a searchable index, an evidence-based style profile, decisions, and open tasks. A handoff package gives the next chat a clear starting point and references to the relevant history.

## Features

- Preserve individual conversations, message order, code, timestamps, and attachment references.
- Organize history by project and topic while keeping original transcripts intact.
- Capture preferences, corrections, decisions, and working patterns with source references.
- Generate a `START_HERE.md` entry point and reusable continuation prompts.
- Export local Codex conversation logs with file hashes and per-session manifests.
- Keep private memory packages separate from the reusable skill.

## Install

Copy the `conversation-memory` folder into your skills directory. For a local Codex installation:

```text
~/.codex/skills/conversation-memory/
```

Open a new chat and invoke the skill:

```text
Use $conversation-memory to archive these conversations and create a new-chat handoff package.
```

## Archive local Codex logs

```sh
python conversation-memory/scripts/archive_codex.py /path/to/session.jsonl --out /path/to/private-memory
```

Pass multiple source files to archive several sessions. Each session receives its own transcript, message records, and manifest. The converter handles local Codex JSONL logs; the skill also guides collection from accessible conversations and account exports.

## Continue in a new chat

Upload the handoff package and use this prompt:

```text
Read START_HERE.md and the conversation index. Load the original messages relevant to my task, follow my documented preferences and corrections, and continue from the latest decisions and open tasks.

My task: [describe what to continue]
```

See [prompt examples](conversation-memory/references/prompts.md) for archiving, continuation, and style review.

## Package layout

```text
START_HERE.md
INDEX.md
STYLE_AND_PREFERENCES.md
PROJECTS_AND_TASKS.md
GAPS_AND_COMPLETENESS.md
archive/
  session/
    messages.source.jsonl
    messages.json
    transcript.md
    manifest.json
```
