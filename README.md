# Conversation Memory

**Version 0.3.1 · Python 3.10+ · Standard library only**

Archive conversations together with their uploaded attachments and generated files. Build an indexed memory package that another chat can read to continue your work and follow your documented preferences.

## Use it in a chat

Send this to Codex to install the skill directly from GitHub:

```text
Install the conversation-memory skill from:
https://github.com/xuyuchen231-stack/Conversation-Memory/tree/main/conversation-memory
```

Then use it in the old conversation:

```text
Use $conversation-memory to archive these conversations with their uploaded attachments and generated files. Organize them by project, capture my preferences and corrections with source references, and create a new-chat handoff package.
```

Provide the conversations, local session files, or an extracted ChatGPT export. The skill collects records and files, prepares a style and task handoff, and verifies the package.

For **multiple separate new chats**, upload `Conversation-Memory.zip` to the first receiving chat and say:

```text
Read START_HERE.md and MIGRATION_PLAN.json. Tell me which new chats to create, the exact ZIP to upload to each, and each full opening prompt. Keep old conversations separate unless I choose a suggested merge.
```

Extract the master ZIP on your computer. Manually create each listed chat, upload its `conversations/Sxxx.zip`, and paste the included `NEW_CHAT_PROMPT.txt`. Every inner ZIP works independently. If nested ZIPs cannot be opened in the chat, upload the extracted inner ZIP directly.

For **one chat accessing the whole archive**, upload `handoff.zip` and say:

```text
Read START_HERE.md, INDEX.md and FILES_INDEX.md. Read the source messages and files relevant to my task, follow my documented preferences and latest corrections, and continue with: [your task].
```

## What is included

- Original user and assistant messages, code, timestamps, and source references.
- Uploaded files and generated documents available from the supplied records.
- Images embedded in messages, exported as image files.
- A file index with content hashes, original filenames, source messages, and collection status.
- ChatGPT mapping nodes and parent/children relationships, preserving regenerated branches.
- Separate local originals and a portable handoff with known credential patterns redacted.
- Missing-file reports and bounded searches for relocated file candidates.
- One independent ZIP per conversation, containing its own messages, associated files, memory notes, and opening prompt.
- A master migration plan listing which chat to create and which ZIP and prompt to use.
- A verifier and a finalizer that refreshes both the full handoff and nested migration ZIPs.

## Try the included example

From the repository root:

```sh
python conversation-memory/scripts/build_archive.py examples/session.jsonl --out ../memory-demo
python conversation-memory/scripts/build_archive.py --verify ../memory-demo/handoff
```

Open `../memory-demo/handoff/START_HERE.md`, then `FILES_INDEX.md`. The example includes a real text attachment and a preference stated in the original messages.

## Build from your records

### Local Codex sessions

```sh
python conversation-memory/scripts/build_archive.py --sessions-dir /path/to/.codex/sessions --out /path/to/new-memory
```

On Windows, for example:

```powershell
python ./conversation-memory/scripts/build_archive.py --sessions-dir "$env:USERPROFILE\.codex\sessions" --out "D:\Memory\snapshot-001"
```

The directory scan skips subagent sessions. You can also pass one or more JSONL paths directly to select individual conversations.

### ChatGPT export

Extract the export, then use its mapping-based `conversations.json`:

```sh
python conversation-memory/scripts/build_archive.py /path/to/export/conversations.json --search-dir /path/to/export --out /path/to/new-memory
```

The importer supports a conversation list, a `conversations` list wrapper, or a single mapping-based conversation. Branch topology and the current node are preserved in `conversation.json`.

### Find relocated files

```sh
python conversation-memory/scripts/build_archive.py session.jsonl --search-dir /path/to/Downloads --search-dir /path/to/project/outputs --out /path/to/new-memory
```

Search is limited to the directories you provide. A unique filename match is included as an **unverified recovery candidate**; multiple matches are listed for review. A missing file remains listed as missing. Historical commands are never executed to recreate an original.

Local paths, relative paths, local `file://` links, and embedded images are processed directly. Remote references are recorded for collection through their service; the CLI does not connect to accounts or network shares. The default limit is 256 MiB per file; adjust it with `--max-file-mb`.

## Output

```text
new-memory/
  originals/                 Original records and file entities; keep locally
  handoff/
    START_HERE.md
    INDEX.md
    FILES_INDEX.md
    FILES_MANIFEST.json
    COVERAGE.json
    SHA256SUMS.json
    archive/S001/
      messages.json
      transcript.md
      manifest.json
    files/content-hash/filename.ext
  handoff.zip                All conversations for one receiving chat
  Complete-Archive.zip       Entire output directory in one private backup ZIP
  Conversation-Memory.zip    Master package for multiple new chats:
    START_HERE.md
    MIGRATION_PLAN.md
    MIGRATION_PLAN.json
    SHA256SUMS.json
    conversations/S001.zip   Independent package for the first chat
    conversations/S002.zip   Independent package for the second chat
```

Each inner ZIP includes `START_HERE.md`, `NEW_CHAT_PROMPT.txt`, its `archive/Sxxx/` folder, its associated `files/`, a scoped file inventory, and checksums. The skill writes `archive/Sxxx/MEMORY.md` for that conversation after reading its history. Shared preferences are copied into every inner ZIP when available; unrelated project notes stay separate. The master plan defaults to one old conversation per new chat.

`Complete-Archive.zip` includes the entire output directory: `originals/`, `handoff/`, `handoff.zip`, `Conversation-Memory.zip`, and other output files. It excludes itself and is regenerated by finalization. This complete backup contains unredacted originals; keep it privately and use the portable ZIPs above for chat transfers.

The skill adds source-linked preferences, project decisions, open tasks, and relevant collection gaps, then refreshes checksums and all three ZIPs:

```sh
python conversation-memory/scripts/build_archive.py --finalize /path/to/new-memory
python conversation-memory/scripts/build_archive.py --verify /path/to/new-memory/handoff
```

Use a new output directory for each snapshot. Identical conversation IDs and content hashes are deduplicated; changed revisions remain separate. File entities are deduplicated by content while every filename and message association stays in the manifest.

Known credential patterns are handled in UTF-8, BOM-marked UTF-16, and supported ZIP members and metadata. Files requiring additional inspection stay in `originals/` and receive a review status in the portable manifest. Review image or opaque binary contents before sharing sensitive material.

The older `archive_codex.py` command remains available for transcript-only exports.

## Tests

```sh
python -m unittest discover -s tests -v
```

See [validation results](VALIDATION.md) and [prompt examples](conversation-memory/references/prompts.md).
