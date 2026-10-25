#!/usr/bin/env python3
"""Fetch the pinned runtime and apply this source-only overlay to a new directory."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--destination',type=Path,required=True)
    args=ap.parse_args(); dst=args.destination.expanduser().resolve()
    if dst==ROOT or ROOT in dst.parents:ap.error('Keep the runtime checkout outside the public source directory')
    if dst.exists():ap.error('Destination must not exist; use a fresh runtime directory')
    cfg=json.loads((ROOT/'upstream.json').read_text())
    subprocess.run(['git','init',str(dst)],check=True)
    subprocess.run(['git','-C',str(dst),'remote','add','origin',cfg['repository']],check=True)
    subprocess.run(['git','-C',str(dst),'fetch','--depth','1','origin',cfg['commit']],check=True)
    subprocess.run(['git','-C',str(dst),'checkout','--detach','FETCH_HEAD'],check=True)
    got=subprocess.check_output(['git','-C',str(dst),'rev-parse','HEAD'],text=True).strip()
    if got!=cfg['commit']:raise RuntimeError('Upstream commit mismatch')
    patch=ROOT/'patches/runtime.patch'
    subprocess.run(['git','-C',str(dst),'apply','--check',str(patch)],check=True)
    subprocess.run(['git','-C',str(dst),'apply',str(patch)],check=True)
    for rel,want in cfg['runtime_source_sha256'].items():
        if hashlib.sha256((dst/rel).read_bytes()).hexdigest()!=want:raise RuntimeError('Patched source mismatch: '+rel)
    profile=dst/'dm/games'/cfg['game_id']
    if profile.exists():raise RuntimeError('Unexpected existing HK profile')
    shutil.copytree(ROOT/'profile'/cfg['game_id'],profile)
    print('Prepared pinned runtime with HK source adaptations:',dst)
    print('No game files or keys have been read. Full clean build remains unverified.')

if __name__=='__main__':main()
