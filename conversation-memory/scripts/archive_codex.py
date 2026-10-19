"""Archive observed user/assistant messages from local Codex JSONL snapshots.

Standard library only. No network, account access, summarization or publication.
"""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone


def archive(source, out):
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    records, messages, warnings = [], [], []
    for number, line in enumerate(data.decode('utf-8-sig').splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            warnings.append(f'Unparsed line {number}; source may be actively writing.')
            continue
        payload = row.get('payload', {})
        if (row.get('type') != 'response_item' or
                payload.get('type') != 'message' or
                payload.get('role') not in ('user', 'assistant')):
            continue
        if payload.get('channel') == 'analysis':
            continue
        records.append(line)
        parts = payload.get('content', [])
        text = ''.join(p.get('text', '') for p in parts
                       if isinstance(p, dict) and p.get('type') in ('input_text', 'output_text', 'text'))
        nontext = [p for p in parts if not isinstance(p, dict) or
                   p.get('type') not in ('input_text', 'output_text', 'text')]
        messages.append({'ordinal': len(messages) + 1, 'source_line': number,
                         'role': payload['role'], 'timestamp': row.get('timestamp'),
                         'id': payload.get('id'), 'text': text, 'nontext': nontext})
    if not messages:
        raise ValueError(f'No supported messages: {source.name}')
    folder = out / (source.stem + '-' + digest[:12])
    folder.mkdir(parents=True, exist_ok=False)
    raw = ('\n'.join(records) + '\n').encode('utf-8')
    (folder / 'messages.source.jsonl').write_bytes(raw)
    (folder / 'messages.json').write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding='utf-8')
    # JSON holds authoritative text. Markdown is a readable view, not round-trip storage.
    view = '\n\n'.join(f"## {m['ordinal']} | {m['role']} | {m['timestamp']}\n\n{m['text']}" for m in messages)
    (folder / 'transcript.md').write_text(view, encoding='utf-8')
    manifest = {'source_name': source.name, 'source_sha256': digest,
                'source_bytes': len(data), 'snapshot_utc': datetime.now(timezone.utc).isoformat(),
                'account': 'unknown', 'scope': 'observed_user_assistant_message_records',
                'status': 'snapshot_unverified_end_to_end', 'message_count': len(messages),
                'nontext_message_count': sum(bool(m['nontext']) for m in messages),
                'missing': ['Attachment binaries not collected',
                            'Source historical completeness not independently verified',
                            'Other accounts and non-local conversations not collected'],
                'warnings': warnings,
                'files_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in folder.iterdir() if p.is_file()}}
    (folder / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('sources', nargs='+', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    results = [archive(p, args.out) for p in args.sources]
    print(json.dumps({'snapshots': len(results), 'messages': sum(r['message_count'] for r in results),
                      'warnings': sum(len(r['warnings']) for r in results)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
