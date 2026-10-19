# Validation

Version 0.2.0 · 2026-10-19

## Automated tests

```sh
python -m unittest discover -s tests -v
```

25 integration tests passed on Windows with Python 3.10. They exercise:

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

## Independent review

A separate reviewer used synthetic inputs to reproduce and recheck the file, encoding, path and ZIP-metadata fixes. The reviewer also exercised memory-note edits, verification, finalization and ZIP refresh, and checked that an unsupported ZIP compression method preserved the local original with a portable review status. No remaining release blocker was found in that review.

## Local smoke test

The executable builder processed three authorized local user sessions, producing 54 message records and 20 unique file entities. The handoff verifier passed. Private sources and generated smoke-test bundles are kept outside this repository.

## Execution environment

Executed on Windows with Python 3.10. Linux portability received code review and cross-platform-path tests; a native Linux execution has not been performed.
