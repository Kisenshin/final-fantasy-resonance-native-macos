#!/usr/bin/env python3
"""Experimental HK 1.0.1 Mac builder. Default is a plan; --build runs the pipeline."""
from pathlib import Path
import argparse,fcntl,hashlib,importlib.util,json,os,platform,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
GAME='0100B8A026F14000'

def source_check(runtime,cfg):
    pin=subprocess.check_output(['git','-C',str(runtime),'rev-parse','HEAD'],text=True).strip()
    if pin!=cfg['commit']:raise ValueError('Runtime is not at the pinned upstream commit')
    for rel,want in cfg['runtime_source_sha256'].items():
        if hashlib.sha256((runtime/rel).read_bytes()).hexdigest()!=want:raise ValueError('Runtime source differs from the release overlay: '+rel)
    for p in (ROOT/'profile'/GAME).iterdir():
        if p.is_file() and (runtime/'dm/games'/GAME/p.name).read_bytes()!=p.read_bytes():raise ValueError('Profile source differs from release: '+p.name)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime',type=Path,help='Pinned runtime prepared with prepare_runtime.py')
    ap.add_argument('--base',type=Path,help='User-owned HK base NSP')
    ap.add_argument('--update',type=Path,help='User-owned HK 1.0.1 update NSP')
    ap.add_argument('--keys',type=Path,help='Path to the user\'s own prod.keys; contents are never printed')
    ap.add_argument('--dlc',action='append',default=[],help='Optional owned DLC: decimal-index=/path/file.nsp, e.g. 2=/path/starter.nsp')
    ap.add_argument('--work',type=Path,help='Private build directory, preferably on an external APFS SSD')
    ap.add_argument('--output',type=Path,help='New .app path; existing applications are never overwritten')
    ap.add_argument('--compiler-bin',type=Path,help='Optional directory with metal and metallib; otherwise xcrun resolves them')
    ap.add_argument('--jobs',type=int,default=4)
    ap.add_argument('--build',action='store_true',help='Execute extraction, rewrite, shaders and packaging; can use substantial disk space')
    a=ap.parse_args()
    if not 1<=a.jobs<=8:ap.error('--jobs must be 1..8')
    steps=['check dependencies and pinned sources','extract base + 1.0.1 update with integrity checks','verify title and module build IDs','rewrite main/subsdk0/sdk','decode IoStore shader archives with the user-supplied game decoder','split shaders and check identifier tables','compile all Metal shaders and generate reflection tables','patch the original game FPS menu using user-extracted assets','extract optional owned DLC','package and locally sign a Mac app']
    if not a.build:
        print(json.dumps({'mode':'plan only; no files created, downloaded or decrypted','game_id':GAME,'supported_version':'HK 1.0.1','clean_build_verified':False,'steps':steps},indent=2));return
    missing=[n for n in ('runtime','base','update','keys','work') if getattr(a,n) is None]
    if missing:ap.error('Required with --build: '+', '.join('--'+n for n in missing))
    if sys.version_info<(3,12):ap.error('Python 3.12 or newer is required')
    if platform.system()!='Darwin' or platform.machine()!='arm64':ap.error('Use native arm64 Python on an Apple Silicon Mac')
    if int(platform.mac_ver()[0].split('.')[0])<26:ap.error('macOS 26 or newer is required by the Metal 4 runtime')
    for name in ('runtime','base','update','keys','work'):
        setattr(a,name,getattr(a,name).expanduser().resolve())
    runtime,work=a.runtime,a.work
    if work==ROOT or ROOT in work.parents:ap.error('Keep private game files and build output outside the public source directory')
    if runtime==work or runtime in work.parents or work in runtime.parents:ap.error('Use separate runtime and private build directories')
    for p in (a.base,a.update,a.keys):
        if not p.is_file():ap.error('Input file does not exist: '+str(p))
        if work==p.parent or work in p.parents:ap.error('Keep original inputs outside the private build directory')
    dlc=[]
    for item in a.dlc:
        index,sep,name=item.partition('=')
        if not sep or not index.isdecimal() or not 0<=int(index)<4096:ap.error('DLC must be decimal-index=/path/file.nsp')
        p=Path(name).expanduser().resolve()
        if not p.is_file():ap.error('DLC file does not exist: '+str(p))
        dlc.append((int(index),p))
    if len({i for i,p in dlc})!=len(dlc):ap.error('Duplicate DLC index')
    cfg=json.loads((ROOT/'upstream.json').read_text());source_check(runtime,cfg)
    env={k:v for k,v in os.environ.items() if not k.startswith(('DM_','DMSH_','XLATE','IOSOUT'))}
    env.update(DM_GAME=GAME,DM_ROOT=str(work),DM_LANG='zh-Hans',J=str(a.jobs),DOTNET_CLI_TELEMETRY_OPTOUT='1',DOTNET_NOLOGO='1',xcrun_nocache='1',FFR_PYTHON=sys.executable)
    env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
    if a.compiler_bin:env['PATH']=str(a.compiler_bin.expanduser().resolve())+os.pathsep+env['PATH']
    for name in ('git','make','clang','xcrun','dotnet','spirv-cross','zstd','codesign','sips','iconutil'):
        if not shutil.which(name,path=env['PATH']):ap.error('Missing tool: '+name)
    for name in ('metal','metallib'):
        if subprocess.run(['xcrun','-sdk','macosx','--find',name],env=env,capture_output=True).returncode:ap.error('Xcode Metal toolchain is missing '+name)
    for name in ('lz4.block','capstone','fontTools'):
        try:__import__(name)
        except ImportError:ap.error('Missing Python dependency: '+name)
    if not Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf').is_file():ap.error('Required macOS Arial Unicode font is unavailable')
    if subprocess.check_output(['dotnet','--version'],env=env,text=True).split('.')[0]!='10':ap.error('Select the .NET 10 SDK for the extractor')
    work.mkdir(parents=True,exist_ok=True)
    lock=(work/'build.lock').open('a')
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:ap.error('Another build holds this private work directory')
    inputs={str(p):{'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for p in (a.base,a.update,a.keys,*[p for i,p in dlc])}
    inputs['dlc_indices']=[i for i,p in dlc]
    record=work/'private-inputs.json'
    if record.exists() and json.loads(record.read_text())!=inputs:ap.error('Inputs changed; use a new private work directory')
    record.write_text(json.dumps(inputs,indent=2)+'\n');os.chmod(record,0o600)
    (work/'tmp').mkdir(exist_ok=True);env['TMPDIR']=str(work/'tmp');env['WORK']=str(work/'tmp')
    sys.path.insert(0,str(runtime/'dm/games'));import game
    g=game.load(GAME)
    spec=importlib.util.spec_from_file_location('upstream_build',runtime/'scripts/build_ipa_from_nsp.py')
    api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
    api.PROG.mode='lines';api.PROG.plan(len(steps));logs=work/'logs';logs.mkdir(exist_ok=True)
    nx=api.build_nx_extract(runtime,work,logs,env)
    ex=work/'extract';ex.mkdir(exist_ok=True)
    d=api.extract(nx,a.keys,ex,'v65536',a.base,a.update,None,logs,g)
    with (d/'ExeFS/main').open('rb') as f:header=f.read(0x50)
    if header[:4]!=b'NSO0' or header[0x40:0x50].hex()!=cfg['main_build_id']:raise ValueError('Only HK 1.0.1 main is supported')
    mismatches=api.build_mismatch(d,'v65536',g)
    if mismatches:raise ValueError('Unsupported module build IDs: '+', '.join(mismatches))
    extract_log=(logs/'extract_v65536.log').read_text(errors='replace').lower()
    if 'title 0100b8a026f14000, update 0100b8a026f14800' not in extract_log:raise ValueError('Wrong base/update title IDs')
    patched=work/'rewritten';api.rewrite(sys.executable,runtime,d/'ExeFS',patched,env,logs,g)
    api.chain_header(sys.executable,runtime,env,logs)
    if api.chain_of(runtime)!=cfg['shader_chain']:raise ValueError('Unexpected shader chain version')
    # Decode and split before modifying the settings container so restarts see the
    # same source archives. Upstream helpers retain successful extraction/rewrite.
    api.decode_ue_shaders(runtime,{'v65536':d},'v65536',patched,work,env,logs,g)
    shaders=work/'shader'
    api.split_shaders(sys.executable,runtime,[d/'RomFS'],[d/'ExeFS/main'],shaders/'pkg',env,logs,g)
    api.run([sys.executable,runtime/'dm/gfx/tools/own_compilers.py',shaders/'pkg',shaders/'cache'],logs/'metal_shaders.log',env=env,cwd=runtime)
    host=api.build_mac_host(runtime,work/'tools/nativehost',env,logs,g)
    from patch_fps_menu import apply
    apply(d/'RomFS',runtime,host,patched,env)
    aoc=work/'aoc' if dlc else None
    for index,p in dlc:
        dest=aoc/str(index);done=aoc/(str(index)+'.done')
        if done.exists():continue
        if dest.exists():raise ValueError('Incomplete DLC output exists; preserve logs and use a fresh work directory')
        log=logs/f'dlc_{index}.log';api.run([nx,a.keys,'--aoc',p,dest],log,env=env)
        expected=f'add-on content {int(GAME,16)+0x1000+index:016x}'
        if expected not in log.read_text(errors='replace').lower():raise ValueError('DLC title does not match the selected HK index')
        done.write_text('complete\n')
    from package_app import package
    output=(a.output.expanduser().resolve() if a.output else work/'最终幻想共鸣.app')
    if output==ROOT or ROOT in output.parents:ap.error('Keep the generated game application outside the public source directory')
    package(runtime,work,host,patched,d/'RomFS',shaders/'cache',g.dir,output,env,aoc)
    print('End-to-end clean reconstruction has not been independently validated. Test your local build before relying on it.')

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('Build stopped:',e,file=sys.stderr);sys.exit(1)
