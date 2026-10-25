#!/usr/bin/env python3
"""Check the exact source publication manifest and reject local/private artifacts."""
from pathlib import Path
import argparse,ast,hashlib,json,os,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
DENY={'.nsp','.xci','.nca','.keys','.key','.pem','.p12','.tik','.cert','.nso','.nro','.bin','.elf','.metallib','.metal','.spv','.air','.pak','.ucas','.utoc','.uasset','.uexp','.ubulk','.locres','.nacp','.ttf','.otf','.png','.jpg','.jpeg','.icns','.log','.ips','.zip','.7z','.rar'}
ROOT_NAMES={'.gitignore','README.md','LICENSE','LICENSE-nxnative','THIRD_PARTY_NOTICES.md','requirements.txt','upstream.json','release-files.json'}
PREFIXES={'scripts/','patches/','profile/0100B8A026F14000/','launcher/','docs/'}
SECRET=re.compile(r'(?im)^\s*(?:master_key_[0-9a-f]{2}|titlekek_[0-9a-f]{2}|header_key|key_area_key_application_[0-9a-f]{2})\s*=\s*[0-9a-f]{32,}')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seal',action='store_true',help='Write a manifest of the reviewed source files');a=ap.parse_args()
    files=[];errors=[]
    for base,dirs,names in os.walk(ROOT,followlinks=False):
        dirs[:]=[d for d in dirs if d not in {'.git','.venv','__pycache__'}]
        for d in dirs:
            if (Path(base)/d).is_symlink():errors.append('Symlink: '+str((Path(base)/d).relative_to(ROOT)))
        for name in names:
            p=Path(base)/name;rel=p.relative_to(ROOT).as_posix()
            if p.is_symlink():errors.append('Symlink: '+rel);continue
            if name.endswith(('.pyc','.pyo')):continue
            if name=='release-files.json':continue
            if (rel not in ROOT_NAMES and not any(rel.startswith(pre) for pre in PREFIXES)) or p.suffix.lower() in DENY:errors.append('Unexpected or private artifact: '+rel);continue
            if p.stat().st_size>16*1024*1024:errors.append('Unexpectedly large source file: '+rel);continue
            try:text=p.read_text(encoding='utf-8')
            except UnicodeDecodeError:errors.append('Non-text artifact: '+rel);continue
            if re.search(r'/User[s]/[^/\s]+/',text):errors.append('Local personal path/name: '+rel)
            if SECRET.search(text):errors.append('Possible decryption key material: '+rel)
            if p.suffix=='.py':
                try:ast.parse(text,filename=rel)
                except SyntaxError as e:errors.append(f'Syntax error in {rel}: {e.msg}')
            files.append({'path':rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    files.sort(key=lambda x:x['path']);manifest=ROOT/'release-files.json'
    if not a.seal:
        if not manifest.exists():errors.append('Missing publication manifest; run --seal after reviewing source')
        elif json.loads(manifest.read_text()).get('files')!=files:errors.append('Files differ from the reviewed publication manifest')
    # Once this is its own Git repository, audit tracked files too, including any
    # force-added files under normally ignored directories.
    if (ROOT/'.git').exists():
        tracked=subprocess.check_output(['git','-C',str(ROOT),'ls-files','-z']).decode().split('\0')
        allowed={x['path'] for x in files}|{'release-files.json'}
        errors.extend('Tracked unreviewed file: '+p for p in tracked if p and p not in allowed)
    if errors:raise SystemExit('\n'.join(errors))
    if a.seal:manifest.write_text(json.dumps({'kind':'reviewed source-only file list','files':files},indent=2)+'\n')
    print(json.dumps({'source_files':len(files),'bytes':sum(x['bytes'] for x in files),'symlinks':0,'game_payloads':0,'credential_files':0,'python_syntax':'passed','manifest':'sealed' if a.seal else 'matches','clean_build_verified':False},indent=2))
if __name__=='__main__':main()
