"""Package user-generated files into a local, ad-hoc-signed Mac application."""
from pathlib import Path
import ctypes,json,os,plistlib,shutil,subprocess,uuid
ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN={'.nsp','.xci','.nca','.tik','.cert','.keys','.key','.pem','.p12'}

def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    fn=getattr(ctypes.CDLL(None,use_errno=True),'clonefile',None)
    if fn is None or fn(os.fsencode(src),os.fsencode(dst),0):shutil.copy2(src,dst)

def tree(src,dst,skip=()):
    for p in sorted(src.rglob('*')):
        if p.is_symlink():raise ValueError('Symlinks cannot be packaged: '+str(p))
        if not p.is_file() or p.suffix in skip:continue
        if p.suffix.lower() in FORBIDDEN:raise ValueError('Package/key file in runtime resources: '+str(p))
        copy(p,dst/p.relative_to(src))

def package(runtime,work,host,rewritten,romfs,cache,profile,output,env,aoc=None):
    if output.exists():raise ValueError('Refusing to overwrite existing application: '+str(output))
    if output.suffix!='.app':raise ValueError('Output must end with .app')
    cfg=json.loads((ROOT/'upstream.json').read_text());lib=cache/('b-'+cfg['shader_chain'])
    built=json.loads((lib/'_b_build.json').read_text())
    expected={c[3] for l in (profile/'shader_map.tsv').read_text().splitlines() if len(c:=l.split('\t'))>4 and c[0].endswith('.bin')}
    if {r['key'] for r in built}!=expected or any(r.get('st')!='ok' for r in built):raise ValueError('Incomplete shader build; inspect shader logs before packaging')
    stamp=dict(l.split('\t',1) for l in (lib/'inputs.tsv').read_text().splitlines() if '\t' in l)
    if stamp.get('game')!=cfg['game_id'] or not stamp.get('inputs'):raise ValueError('Shader stamp has wrong game or missing input digest')
    for name in ('c1_full.tsv','cb_extent.tsv'):
        if not (profile/name).read_text().splitlines()[0].startswith(f"# chain {lib.name} inputs {stamp['inputs']} "):raise ValueError('Stale generated table: '+name)
    fonts=work/'font';fonts.mkdir(exist_ok=True)
    subprocess.run([env['FFR_PYTHON'],str(runtime/'dm/tools/make_ext_font.py'),str(fonts/'nintendo_ext.ttf')],env=env,check=True)
    launch=work/'FFRLauncher'
    subprocess.run(['xcrun','clang','-fobjc-arc','-Wall','-Wextra','-Werror','-arch','arm64','-mmacosx-version-min=26.0','-framework','Cocoa',str(ROOT/'launcher/FFRLauncher.m'),'-o',str(launch)],env=env,check=True)
    output.parent.mkdir(parents=True,exist_ok=True)
    stage=output.with_name('.'+output.name+'.staging-'+uuid.uuid4().hex);res=stage/'Contents/Resources'
    try:
        copy(host,stage/'Contents/MacOS/nativehost');copy(launch,stage/'Contents/MacOS/FFRLauncher')
        for m in ('main','subsdk0','sdk'):
            for suffix in ('patched.bin','fixups.tsv','gates.tsv'):copy(rewritten/f'{m}.{suffix}',res/'rewritten'/f'{m}.{suffix}')
        tree(romfs,res/'romfs');tree(lib,res/'msl-cache'/lib.name,skip={'.metal'})
        for p in profile.glob('*.tsv'):copy(p,res/'profile'/p.name)
        copy(fonts/'nintendo_ext.ttf',res/'font/nintendo_ext.ttf')
        if aoc and aoc.is_dir():
            for p in sorted(aoc.iterdir()):
                if p.is_dir() and p.name.isdecimal():tree(p,res/'aoc'/p.name)
        for name in ('controls-guide.txt','controls-hints.json'):copy(ROOT/'launcher'/name,res/name)
        (res/'frame-rate-options.json').write_text(json.dumps({'game_menu':True,'targets':[30,60],'persistence':'original OptionSaveData'})+'\n')
        copy(runtime/'LICENSE',res/'licenses/LICENSE-nxnative')
        copy(ROOT/'LICENSE',res/'licenses/LICENSE-FFRNative')
        # Preserve dependency notices, not whole dependency source trees in the app.
        for p in (runtime/'dm/third_party').rglob('*'):
            if p.is_file() and (p.name.upper().startswith(('LICENSE','COPYING','NOTICE','PATENTS')) or p.name=='README.md'):
                copy(p,res/'licenses/third-party'/p.relative_to(runtime/'dm/third_party'))
        icon=romfs.parent/'icon.jpg';icon_key={}
        if icon.is_file():
            iconset=work/'AppIcon.iconset';iconset.mkdir(exist_ok=True)
            for n in (16,32,128,256,512):
                for suffix,px in (('',n),('@2x',n*2)):
                    subprocess.run(['sips','-s','format','png','-z',str(px),str(px),str(icon),'--out',str(iconset/f'icon_{n}x{n}{suffix}.png')],check=True,stdout=subprocess.DEVNULL)
            subprocess.run(['iconutil','-c','icns',str(iconset),'-o',str(res/'AppIcon.icns')],check=True)
            icon_key={'CFBundleIconFile':'AppIcon'}
        info={'CFBundleName':'最终幻想共鸣','CFBundleDisplayName':'最终幻想共鸣','CFBundleIdentifier':'local.ffrnative.hk','CFBundleExecutable':'FFRLauncher','CFBundlePackageType':'APPL','CFBundleShortVersionString':'1.0.1','CFBundleVersion':'65540','LSMinimumSystemVersion':'26.0','LSApplicationCategoryType':'public.app-category.games','NSHighResolutionCapable':True,'CFBundleDevelopmentRegion':'zh-Hans','CFBundleLocalizations':['zh-Hans','en'],'NSHumanReadableCopyright':'Personal build containing user-supplied game files.',**icon_key}
        (stage/'Contents/Info.plist').write_bytes(plistlib.dumps(info))
        (res/'package-manifest.json').write_text(json.dumps({'game_id':cfg['game_id'],'shader_chain':cfg['shader_chain'],'upstream_commit':cfg['commit'],'build_status':'experimental; clean end-to-end reconstruction unverified'},indent=2)+'\n')
        subprocess.run(['codesign','--force','--sign','-',str(stage)],check=True)
        subprocess.run(['codesign','--verify','--deep','--strict',str(stage)],check=True)
        plan=json.loads(subprocess.check_output([str(stage/'Contents/MacOS/FFRLauncher'),'--inspect'],text=True))
        if plan['host_started'] or plan['user_directories_created']:raise ValueError('Launcher inspection unexpectedly executed the game')
        stage.rename(output)
    except BaseException:
        if stage.exists():shutil.rmtree(stage)
        raise
    print('Built local personal application:',output)
