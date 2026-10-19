# Validation

Version 0.3.0 · 2026-10-19

## Automated tests

```sh
python -m unittest discover -s tests -v
```

26 integration tests passed on Windows with Python 3.10. They exercise:

- Exact message, Unicode, code and whitespace preservation.
- Actual attachment and generated-file copying, including extensionless files.
- Embedded image extraction and nontext local-image file URIs.
- Local paths, local file URIs, filenames with parentheses, PDF fragments and Windows filename recovery.
- Content-hash deduplication with separate filename/message associations.
- Missing files, unique unverified recovery candidates, and ambiguous candidates.
- ChatGPT branch topology and code messages.
- Conversation deduplication that preserves changed revisions.
- Original/portable separation and known credential patterns in UTF-8, UTF-16, ZIP contents, member names and comments.
- Review status for unsupported-encoding content containing a known credential pattern.
- Network-reference reporting without connecting to shares.
- Previous memory-export exclusion, subagent filtering, malformed-record warnings, overwrite protection, and tamper detection.

- Nested migration packaging: two isolated chats, correct file associations, shared preference propagation, refreshed per-chat memory notes, readable routing plan, inner ZIP integrity and per-file hashes.

## Independent review

A separate reviewer used synthetic inputs to reproduce and recheck the file, encoding, path and ZIP-metadata fixes. The reviewer also exercised memory-note edits, verification, finalization and ZIP refresh, and checked that an unsupported ZIP compression method preserved the local original with a portable review status. No remaining release blocker was found in that review.

## Multiple-chat forward test

An independent evaluator used two unrelated synthetic chats, four message records, and two actual attachments. After adding per-chat memory notes and shared preferences, finalization produced a master migration package with exactly two inner ZIPs. Each inner ZIP contained only its own records and attachment, the shared preference, its memory notes, and its opening prompt. Plan prompts matched the inner prompts. CLI verification passed for the handoff (20 files), extracted master (5 files), and each extracted inner package (11 files).

## Local smoke test

The executable builder processed three authorized local user sessions, producing 54 message records and 20 unique file entities. The handoff verifier passed. Private sources and generated smoke-test bundles are kept outside this repository.

## Execution environment

Executed on Windows with Python 3.10. Linux portability received code review and cross-platform-path tests; a native Linux execution has not been performed.
