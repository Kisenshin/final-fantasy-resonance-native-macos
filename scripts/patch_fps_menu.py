#!/usr/bin/env python3
"""Apply the checked HK 1.0.1 FPS-menu edits to a private extracted RomFS."""
from pathlib import Path
import argparse,ctypes,hashlib,json,os,shutil,struct,sys
from parse_settings_asset import fps_table
from blake3_reference import digest
ROOT=Path(__file__).resolve().parents[1]

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def clone(src,dst):
    fn=getattr(ctypes.CDLL(None,use_errno=True),'clonefile',None)
    if fn is None or fn(os.fsencode(src),os.fsencode(dst),0):shutil.copy2(src,dst)

def edit_assets(graphic,fps):
    cfg=json.loads((ROOT/'patches/fps-menu-checks.json').read_text())
    for raw,row in zip((graphic,fps),cfg['chunks']):
        if hashlib.sha256(raw).hexdigest()!=row['original_sha256']:raise ValueError('Unexpected settings asset; wrong game version')
    graphic=bytearray(graphic)
    if graphic[0x11f0]!=0:raise ValueError('Unexpected Switch visibility flag')
    graphic[0x11f0]=1
    parsed=fps_table(fps)
    if [r['label'] for r in parsed['rows']]!=['30','60','120','144','RadioButton_Limitless']:raise ValueError('Unexpected FPS options')
    end=parsed['rows'][1]['end']; shortened=bytearray(fps[:end]+fps[-4:])
    struct.pack_into('<I',shortened,parsed['count_offset'],2)
    struct.pack_into('<Q',shortened,parsed['export_map_offset']+8,end-parsed['header_size'])
    if [r['label'] for r in fps_table(shortened)['rows']]!=['30','60']:raise ValueError('FPS edit readback failed')
    for raw,row in zip((graphic,shortened),cfg['chunks']):
        if hashlib.sha256(raw).hexdigest()!=row['patched_sha256']:raise ValueError('Patched asset checksum mismatch')
    return bytes(graphic),bytes(shortened)

def apply(romfs,runtime,host,rewritten,env):
    sys.path.insert(0,str(runtime/'dm/gfx/tools'));from uepak import Toc,OodleHost
    cfg=json.loads((ROOT/'patches/fps-menu-checks.json').read_text())
    toc_path=romfs/'FFRS/Content/Paks/FFRS-Switch.utoc';ucas=toc_path.with_suffix('.ucas')
    current=sha(toc_path)
    if current==cfg['patched_utoc_sha256']:
        if sha(ucas)!=cfg['patched_ucas_sha256']:raise ValueError('Patched UCAS checksum mismatch')
        print('FPS-menu patch already applied');return
    if current!=cfg['original_utoc_sha256']:raise ValueError('Unsupported IoStore TOC; only original HK 1.0.1 is supported')
    # The original prefix remains byte-identical. A prior interrupted append may
    # have left an unused tail, which the private candidate omits before retrying.
    with ucas.open('rb') as f:
        h=hashlib.sha256();left=cfg['original_ucas_bytes']
        while left:
            b=f.read(min(left,8*1024*1024))
            if not b:raise ValueError('Truncated UCAS')
            h.update(b);left-=len(b)
    if h.hexdigest()!=cfg['original_ucas_sha256']:raise ValueError('Original UCAS prefix checksum mismatch')
    t=Toc(str(toc_path));dec=OodleHost(str(host),rewritten,env)
    try:original=[t.read(row['chunk_index'],dec) for row in cfg['chunks']]
    finally:dec.close()
    changed=edit_assets(*original);toc=bytearray(toc_path.read_bytes())
    hsz,n,nb,bs,nm,ml=struct.unpack_from('<6I',toc,20)
    seeds=struct.unpack_from('<I',toc,84)[0];overflow=struct.unpack_from('<I',toc,96)[0]
    bt=hsz+n*22+seeds*4+overflow*4;ranges=hsz+n*12;metadata=len(toc)-n*24
    candidate=ucas.with_name(ucas.name+'.fps-candidate')
    candidate_toc=toc_path.with_name(toc_path.name+'.fps-candidate')
    if candidate.exists() or candidate_toc.exists():raise ValueError('Incomplete FPS candidate exists; preserve logs and remove only .fps-candidate files before retrying')
    try:
        clone(ucas,candidate)
        with candidate.open('r+b') as f:
            f.truncate(cfg['original_ucas_bytes']);f.seek(0,2)
            for row,before,after in zip(cfg['chunks'],original,changed):
                i=row['chunk_index'];off,length=t.ranges[i];block=off//t.block_size
                if t.ids[i].hex()!=row['chunk_id'] or off%t.block_size or (off+length-1)//t.block_size!=block:raise ValueError('Unexpected chunk layout')
                if toc[metadata+i*24:metadata+i*24+20]!=digest(before)[:20]:raise ValueError('Original chunk metadata mismatch')
                at=(f.tell()+15)&~15;f.write(b'\0'*(at-f.tell()));f.write(after)
                toc[bt+block*12:bt+(block+1)*12]=at.to_bytes(5,'little')+len(after).to_bytes(3,'little')*2+b'\0'
                toc[ranges+i*10+5:ranges+(i+1)*10]=len(after).to_bytes(5,'big')
                toc[metadata+i*24:metadata+i*24+20]=digest(after)[:20];toc[metadata+i*24+20]&=~1
            f.flush();os.fsync(f.fileno())
        candidate_toc.write_bytes(toc)
        if sha(candidate)!=cfg['patched_ucas_sha256'] or sha(candidate_toc)!=cfg['patched_utoc_sha256']:raise ValueError('Final container checksums differ from the tested patch')
        # Replacing UCAS first is safe: every original chunk remains in its prefix.
        os.replace(candidate,ucas);os.replace(candidate_toc,toc_path)
    finally:
        for p in (candidate,candidate_toc):
            if p.exists():p.unlink()
    print('Original-game FPS menu enabled; only 30 and 60 remain')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('romfs','runtime','host','rewritten'):ap.add_argument('--'+name,type=Path,required=True)
    a=ap.parse_args();env={k:v for k,v in os.environ.items() if not k.startswith('DM_')}
    apply(a.romfs.resolve(),a.runtime.resolve(),a.host.resolve(),a.rewritten.resolve(),env)
