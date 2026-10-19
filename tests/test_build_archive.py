import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / 'conversation-memory/scripts/build_archive.py'
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/l9sAAAAASUVORK5CYII=')


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.project = self.root/'project'
        self.project.mkdir()
        self.out = self.root/'memory'

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(BUILDER), *map(str,args)],
                              capture_output=True, text=True, encoding='utf-8')

    def source(self, messages, name='session.jsonl', subagent=False):
        meta = {'type':'session_meta','payload':{'id':name,'cwd':str(self.project),
                'source':{'subagent':'test'} if subagent else 'vscode','thread_source':'subagent' if subagent else 'user'}}
        rows=[meta]
        for role,text,nontext in messages:
            rows.append({'timestamp':'2026-10-19T00:00:00Z','type':'response_item',
                         'payload':{'type':'message','role':role,'content':[{'type':'input_text' if role=='user' else 'output_text','text':text}]+nontext}})
        p=self.root/name
        p.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows),encoding='utf-8')
        return p

    def report(self):
        return json.loads((self.out/'handoff/FILES_MANIFEST.json').read_text(encoding='utf-8'))

    def test_split_packages_are_independent_and_refresh_after_notes(self):
        (self.project/'one.txt').write_text('first attachment')
        (self.project/'two.txt').write_text('second attachment')
        p=self.source([('user','[one](one.txt)',[])],name='first.jsonl')
        q=self.source([('user','[two](two.txt)',[])],name='second.jsonl')
        r=self.run_cli(p,q,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertTrue((self.out/'Conversation-Memory.zip').exists())
        (self.out/'handoff/archive/S001/MEMORY.md').write_text('Only first project decision')
        (self.out/'handoff/STYLE_AND_PREFERENCES.md').write_text('Shared explicit preference')
        r=self.run_cli('--finalize',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        with zipfile.ZipFile(self.out/'Conversation-Memory.zip') as outer:
            self.assertIsNone(outer.testzip())
            plan=json.loads(outer.read('MIGRATION_PLAN.json'))
            self.assertEqual(len(plan['conversations']),2)
            self.assertEqual(plan['conversations'][0]['package'],'conversations/S001.zip')
            for key,expected,excluded in [('S001',b'first attachment',b'second attachment'),('S002',b'second attachment',b'first attachment')]:
                import io
                with zipfile.ZipFile(io.BytesIO(outer.read(f'conversations/{key}.zip'))) as inner:
                    self.assertIsNone(inner.testzip())
                    self.assertIn('NEW_CHAT_PROMPT.txt',inner.namelist())
                    self.assertIn('STYLE_AND_PREFERENCES.md',inner.namelist())
                    self.assertIn(f'archive/{key}/messages.json',inner.namelist())
                    self.assertEqual(len(json.loads(inner.read('FILES_MANIFEST.json'))['references']),1)
                    contents=[inner.read(n) for n in inner.namelist()]
                    self.assertIn(expected,contents)
                    self.assertNotIn(excluded,contents)
                    self.assertEqual(f'archive/{key}/MEMORY.md' in inner.namelist(),key=='S001')
                    for name,digest in json.loads(inner.read('SHA256SUMS.json')).items():
                        self.assertEqual(hashlib.sha256(inner.read(name)).hexdigest(),digest)

    def test_complete_backup_contains_entire_output_and_refreshes(self):
        p=self.source([('user','Keep the original and portable records.',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        backup=self.out/'Complete-Archive.zip'
        self.assertTrue(backup.is_file())
        (self.out/'handoff/archive/S001/MEMORY.md').write_text('Updated continuation')
        r=self.run_cli('--finalize',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        with zipfile.ZipFile(backup) as z:
            self.assertIsNone(z.testzip())
            expected={p.relative_to(self.out).as_posix() for p in self.out.rglob('*') if p.is_file() and p!=backup}
            self.assertEqual(set(z.namelist()),expected)
            self.assertNotIn('Complete-Archive.zip',z.namelist())
            self.assertIn('originals/archive/S001/messages.json',z.namelist())
            self.assertIn('handoff.zip',z.namelist())
            self.assertIn('Conversation-Memory.zip',z.namelist())
            for name in z.namelist():
                self.assertEqual(z.read(name),(self.out/name).read_bytes())

    def test_complete_build_preserves_messages_and_file_entities(self):
        (self.project/'outputs').mkdir()
        original=b'PDF fixture bytes\x00\xff'
        (self.project/'outputs/report (1).pdf').write_bytes(original)
        p=self.source([('user','中文\n\n```py\nx = 1\n```\n  trailing  ',[]),
                       ('assistant','[report](<outputs/report (1).pdf>)',[]),
                       ('user','image',[{'type':'input_image','image_url':'data:image/png;base64,'+base64.b64encode(PNG).decode()}])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        messages=json.loads(next((self.out/'originals/archive').glob('*/messages.json')).read_text(encoding='utf-8'))
        self.assertEqual(messages[0]['text'],'中文\n\n```py\nx = 1\n```\n  trailing  ')
        report=self.report()
        self.assertEqual(report['unique_files'],2)
        files=[self.out/'handoff'/x['archived_path'] for x in report['references'] if x.get('archived_path')]
        self.assertIn(original,[p.read_bytes() for p in files])
        self.assertIn(PNG,[p.read_bytes() for p in files])
        with zipfile.ZipFile(self.out/'handoff.zip') as z:
            self.assertIsNone(z.testzip())
            self.assertIn('START_HERE.md',z.namelist())

    def test_same_bytes_keep_both_filenames_and_message_links(self):
        for n in ('one.txt','two.txt'):
            (self.project/n).write_bytes(b'same content')
        p=self.source([('user','[one](one.txt)',[]),('assistant','[two](two.txt)',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        report=self.report()
        self.assertEqual(report['unique_files'],1)
        self.assertEqual({x['original_filename'] for x in report['references']},{'one.txt','two.txt'})
        self.assertEqual({x['message'] for x in report['references']},{1,2})

    def test_missing_file_is_reported_without_reconstruction(self):
        p=self.source([('assistant','[site](outputs/3MF预览网站.zip)',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        row=self.report()['references'][0]
        self.assertEqual(row['status'],'missing')
        self.assertNotIn('archived_path',row)

    def test_recovery_search_returns_candidate_not_verified_original(self):
        recover=self.root/'recover'
        recover.mkdir()
        (recover/'lost.pdf').write_bytes(b'relocated')
        p=self.source([('user','[lost](outputs/lost.pdf)',[])])
        r=self.run_cli(p,'--search-dir',recover,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        row=self.report()['references'][0]
        self.assertEqual(row['status'],'recovery_candidate_unverified')
        self.assertEqual((self.out/'handoff'/row['archived_path']).read_bytes(),b'relocated')

    def test_ambiguous_recovery_does_not_choose_a_file(self):
        recover=self.root/'recover'
        for d in ('a','b'):
            (recover/d).mkdir(parents=True)
            (recover/d/'lost.pdf').write_text(d)
        p=self.source([('user','[lost](lost.pdf)',[])])
        r=self.run_cli(p,'--search-dir',recover,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        row=self.report()['references'][0]
        self.assertEqual(row['status'],'ambiguous_candidates')
        self.assertEqual(len(row['candidates']),2)
        self.assertNotIn('archived_path',row)

    def test_portable_copy_redacts_token_and_retains_local_original(self):
        token='sk-test_'+('A'*40)
        (self.project/'settings.txt').write_text('token='+token,encoding='utf-8')
        p=self.source([('user','Use '+token+' [settings](settings.txt)',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        original=next((self.out/'originals/archive').glob('*/messages.json')).read_text(encoding='utf-8')
        self.assertIn(token,original)
        for f in (self.out/'handoff').rglob('*'):
            if f.is_file():
                self.assertNotIn(token.encode(),f.read_bytes(),str(f))
        self.assertEqual(self.run_cli('--verify',self.out/'handoff').returncode,0)

    def test_chatgpt_branches_are_preserved(self):
        mapping={
          'root':{'id':'root','parent':None,'children':['u'],'message':None},
          'u':{'id':'u','parent':'root','children':['a','b'],'message':{'id':'u','author':{'role':'user'},'content':{'content_type':'text','parts':['question']}}},
          'a':{'id':'a','parent':'u','children':[],'message':{'id':'a','author':{'role':'assistant'},'content':{'content_type':'text','parts':['first version']}}},
          'b':{'id':'b','parent':'u','children':[],'message':{'id':'b','author':{'role':'assistant'},'content':{'content_type':'text','parts':['second version']}}},
        }
        p=self.root/'conversations.json'
        p.write_text(json.dumps([{'id':'c1','title':'Branch example','mapping':mapping,'current_node':'b'}]),encoding='utf-8')
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        graph=json.loads(next((self.out/'originals/archive').glob('*/conversation.json')).read_text())
        self.assertEqual(graph['mapping']['u']['children'],['a','b'])
        self.assertEqual(graph['current_node'],'b')
        ms=json.loads(next((self.out/'originals/archive').glob('*/messages.json')).read_text())
        self.assertEqual({m['text'] for m in ms},{'question','first version','second version'})
        self.assertEqual({m['node_id'] for m in ms},{'u','a','b'})

    def test_unknown_json_format_has_clear_error(self):
        p=self.root/'unknown.json'
        p.write_text('{"unrelated":42}')
        r=self.run_cli(p,'--out',self.out)
        self.assertNotEqual(r.returncode,0)
        self.assertIn('Unsupported',r.stderr)

    def test_sessions_directory_skips_subagents(self):
        self.source([('user','main',[])])
        self.source([('user','agent',[])],name='agent.jsonl',subagent=True)
        r=self.run_cli('--sessions-dir',self.root,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(len(list((self.out/'handoff/archive').iterdir())),1)

    def test_existing_output_is_not_overwritten(self):
        self.out.mkdir()
        sentinel=self.out/'keep.txt'
        sentinel.write_text('keep')
        p=self.source([('user','hello',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertNotEqual(r.returncode,0)
        self.assertEqual(sentinel.read_text(),'keep')

    def test_integrity_verifier_detects_tampering(self):
        p=self.source([('user','hello',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        (self.out/'handoff/START_HERE.md').write_text('changed')
        r=self.run_cli('--verify',self.out/'handoff')
        self.assertNotEqual(r.returncode,0)
        self.assertIn('checksum',r.stderr.lower())

    def test_malformed_jsonl_is_reported_while_valid_messages_survive(self):
        p=self.source([('user','valid',[])])
        with p.open('a',encoding='utf-8') as f:
            f.write('\n{incomplete')
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        manifest=json.loads(next((self.out/'handoff/archive').glob('*/manifest.json')).read_text())
        self.assertTrue(manifest['warnings'])

    def test_windows_utf16_attachment_is_redacted_in_portable_copy(self):
        token='sk-test_'+('B'*40)
        (self.project/'settings.txt').write_text('token='+token,encoding='utf-16')
        p=self.source([('user','[settings](settings.txt)',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        row=self.report()['references'][0]
        portable=(self.out/'handoff'/row['archived_path']).read_bytes()
        self.assertNotIn(token,portable.decode('utf-16'))

    def test_zip_member_names_and_text_are_redacted(self):
        token='ghp_'+('C'*40)
        src=self.project/'project.zip'
        with zipfile.ZipFile(src,'w') as z:
            info=zipfile.ZipInfo(token+'.txt')
            info.comment=token.encode()
            z.writestr(info,'token='+token)
            z.comment=token.encode()
        p=self.source([('user','[project](project.zip)',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        row=self.report()['references'][0]
        with zipfile.ZipFile(self.out/'handoff'/row['archived_path']) as z:
            self.assertFalse(any(token in n for n in z.namelist()))
            self.assertFalse(any(token.encode() in z.read(n) for n in z.namelist()))
            self.assertNotIn(token.encode(),z.comment)
            self.assertFalse(any(token.encode() in i.comment for i in z.infolist()))

    def test_local_file_uri_is_collected(self):
        file=self.project/'local (1).pdf'
        file.write_bytes(b'local file URI')
        p=self.source([('user','[document](<'+file.as_uri()+'>)',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.report()['references'][0]['status'],'copied')

    def test_nontext_local_image_uri_is_copied(self):
        file=self.project/'image.png'
        file.write_bytes(PNG)
        p=self.source([('user','image',[{'type':'input_image','image_url':file.as_uri()}])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.report()['references'][0]['status'],'copied')

    def test_pdf_fragment_does_not_hide_existing_file(self):
        (self.project/'guide.pdf').write_bytes(b'PDF fixture')
        p=self.source([('user','[guide](guide.pdf#page=2)',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.report()['references'][0]['status'],'copied')

    def test_extensionless_uploaded_file_is_collected(self):
        (self.project/'README').write_bytes(b'instructions')
        p=self.source([('user','[readme](README)',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.report()['unique_files'],1)

    def test_non_utf8_ascii_token_is_not_leaked(self):
        token='sk-'+('D'*40)
        (self.project/'settings.txt').write_bytes(('café token='+token).encode('cp1252'))
        p=self.source([('user','[settings](settings.txt)',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        row=self.report()['references'][0]
        portable=self.out/'handoff'/row.get('archived_path','not-present')
        if portable.is_file():
            self.assertNotIn(token.encode(),portable.read_bytes())
        else:
            self.assertEqual(row['portable_status'],'review_required')

    def test_windows_reference_recovers_by_basename_on_any_host(self):
        recover=self.root/'recover'
        recover.mkdir()
        (recover/'guide.pdf').write_bytes(b'candidate')
        p=self.source([('user',r'[guide](C:\Users\Alice\Downloads\guide.pdf)',[])])
        r=self.run_cli(p,'--search-dir',recover,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.report()['references'][0]['status'],'recovery_candidate_unverified')

    def test_sandbox_reference_uses_explicit_recovery_directory(self):
        recover=self.root/'recover'
        recover.mkdir()
        (recover/'guide.pdf').write_bytes(b'candidate')
        p=self.source([('assistant','[guide](sandbox:/mnt/data/guide.pdf)',[])])
        r=self.run_cli(p,'--search-dir',recover,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.report()['references'][0]['status'],'recovery_candidate_unverified')

    def test_network_share_is_recorded_without_connecting(self):
        p=self.source([('user',r'[guide](\\example.invalid\share\guide.pdf)',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.report()['references'][0]['status'],'network_reference')

    def test_previous_memory_zip_is_not_nested(self):
        with zipfile.ZipFile(self.project/'old-memory.zip','w') as z:
            z.writestr('START_HERE.md','old memory')
            z.writestr('archive/S001/messages.json','[]')
        p=self.source([('user','[memory](old-memory.zip)',[])])
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(self.report()['references'][0]['status'],'nested_export_excluded')
        self.assertEqual(self.report()['unique_files'],0)

    def test_chatgpt_code_content_is_readable_and_preserved(self):
        p=self.root/'conversations.json'
        code='print("hello")\n'
        p.write_text(json.dumps([{'id':'code','title':'Code','mapping':{'a':{'id':'a','parent':None,'children':[],
                     'message':{'id':'a','author':{'role':'assistant'},'content':{'content_type':'code','text':code}}}}}]))
        r=self.run_cli(p,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        msgs=json.loads(next((self.out/'handoff/archive').glob('*/messages.json')).read_text())
        self.assertEqual(msgs[0]['text'],code)

    def test_duplicate_exports_are_deduplicated_without_merging_revisions(self):
        def conv(text):
            return {'id':'same-id','title':'Revision','mapping':{'a':{'id':'a','parent':None,'children':[],
                    'message':{'id':'a','author':{'role':'user'},'content':{'parts':[text]}}}}}
        inputs=[]
        for n,text in enumerate(('first','first','changed')):
            p=self.root/f'export-{n}.json'
            p.write_text(json.dumps([conv(text)]))
            inputs.append(p)
        r=self.run_cli(*inputs,'--out',self.out)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(len(list((self.out/'handoff/archive').iterdir())),2)


if __name__=='__main__':
    unittest.main()
