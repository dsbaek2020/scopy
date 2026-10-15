#!/usr/bin/env python3
"""Bundle local Scopy dependencies and ad-hoc sign for Apple Silicon."""
import collections, json, os, pathlib, plistlib, shutil, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1];LOCAL=ROOT/'local-macos';LOG=LOCAL/'logs/package.log';PREFIX=ROOT/'staging/dependencies';APP=pathlib.Path(os.environ.get('SCOPY_BUNDLE_PATH',str(ROOT/'dist/Scopy.app'))).resolve();CONT=APP/'Contents';FW=CONT/'Frameworks';BIN=CONT/'MacOS/Scopy'
ORIG={};DONE=set();SYSTEM=('/System/Library/','/usr/lib/');SEARCH=[PREFIX/'lib',ROOT/'build/Scopy.app/Contents/Frameworks',pathlib.Path('/opt/homebrew/opt/qt@5/lib'),pathlib.Path('/opt/homebrew/opt/boost@1.85/lib'),pathlib.Path('/opt/homebrew/lib')]
def run(args,check=True):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 if str(args[0]) not in ['otool','lipo'] or p.returncode:
  with LOG.open('a') as f:f.write('$ '+' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
 if check and p.returncode:raise RuntimeError(' '.join(map(str,args))+'\n'+p.stderr[-3500:])
 return p.stdout
def macho(p):
 try:return not p.is_symlink() and p.is_file() and p.open('rb').read(4) in [b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xca\xfe\xba\xbe',b'\xca\xfe\xba\xbf']
 except OSError:return False
def deps(p):return [l.strip().split(' (compatibility version')[0] for l in run(['otool','-L',p]).splitlines()[1:]]
def rpaths(p):
 lines=run(['otool','-l',p]).splitlines();out=[]
 for i,l in enumerate(lines):
  if l.strip()=='cmd LC_RPATH':out.append(lines[i+2].strip().split('path ',1)[1].split(' (offset')[0])
 return out
def expanded(s,origin):return s.replace('@loader_path',str(origin.parent)).replace('@executable_path',str(ROOT/'build/Scopy.app/Contents/MacOS'))
def resolve(dep,origin,local):
 if dep.startswith(SYSTEM):return None
 if dep.startswith('/'):candidates=[pathlib.Path(dep)]
 elif dep.startswith('@rpath/'):
  rest=dep[len('@rpath/'):];candidates=[pathlib.Path(expanded(r,origin))/rest for r in rpaths(origin)]+[d/rest for d in SEARCH]+[FW/rest]
 elif dep.startswith('@loader_path/') or dep.startswith('@executable_path/'):
  candidates=[pathlib.Path(dep.replace('@loader_path',str(local.parent)).replace('@executable_path',str(BIN.parent))),pathlib.Path(expanded(dep,origin))]
 else:candidates=[origin.parent/dep]+[d/dep for d in SEARCH]+[FW/dep]
 for p in candidates:
  if p.exists():return p.resolve()
 raise RuntimeError(f'Cannot resolve {dep} from {local}')
def install(src):
 try:return src.relative_to(APP.resolve())
 except ValueError:pass
 parts=src.parts;index=next((i for i,s in enumerate(parts) if s.endswith('.framework')),None)
 if index is not None:
  base=pathlib.Path(*parts[:index+1]);dest=FW/base.name
  if not dest.exists():
   print('BUNDLE',base.name,flush=True);shutil.copytree(base,dest,symlinks=True)
   for p in dest.rglob('*'):
    if macho(p):ORIG[str(p.resolve())]=base/p.relative_to(dest)
  target=dest/pathlib.Path(*parts[index+1:])
 else:
  target=FW/src.name
  if not target.exists():
   print('BUNDLE',src.name,flush=True);shutil.copy2(src,target);ORIG[str(target.resolve())]=src
 target.chmod(target.stat().st_mode|0o200)
 return target.relative_to(APP)
def closure():
 while True:
  todo=[p for p in APP.rglob('*') if macho(p) and str(p.resolve()) not in DONE]
  if not todo:break
  for p in todo:
   key=str(p.resolve());DONE.add(key);origin=ORIG.get(key,p)
   ident=run(['otool','-D',p],False).splitlines()
   ident=ident[1].strip() if len(ident)>1 else None
   for dep in deps(p):
    if dep==ident or dep.startswith(SYSTEM):continue
    src=resolve(dep,origin,p)
    rel=install(src)
    inside=APP/rel
    runtime='@executable_path/../Frameworks/'+str(inside.relative_to(FW)) if inside.is_relative_to(FW) else '@executable_path/'+str(inside.relative_to(BIN.parent))
    if runtime!=dep:
     p.chmod(p.stat().st_mode|0o200);run(['install_name_tool','-change',dep,runtime,p])
   if ident and p.is_relative_to(FW):
    run(['install_name_tool','-id','@executable_path/../Frameworks/'+str(p.relative_to(FW)),p])
   # Remove absolute development paths and duplicate runtime paths.
   seen=set()
   for rp in rpaths(p):
    if rp.startswith(('/Users/','/opt/')) or rp in seen:run(['install_name_tool','-delete_rpath',rp,p],False)
    seen.add(rp)
def normalize_layout():
 # Homebrew's Python framework lacks the top-level links codesign expects.
 for fw in FW.glob('*.framework'):
  versions=fw/'Versions'
  if versions.is_dir():
   real_versions=[p for p in versions.iterdir() if p.is_dir() and not p.is_symlink()]
   if not (versions/'Current').exists() and len(real_versions)==1:
    (versions/'Current').symlink_to(real_versions[0].name)
   current=versions/'Current'
   if current.exists():
    for name in [fw.stem,'Resources','Headers']:
     if not (fw/name).exists() and (current/name).exists():(fw/name).symlink_to('Versions/Current/'+name)
  if fw.name=='Python.framework':
   for site in fw.glob('Versions/*/lib/python*/site-packages'):
    if site.is_symlink():site.unlink();site.mkdir()
  tools=fw/'Tools'
  if tools.is_dir() and not any(tools.iterdir()):tools.rmdir()
 # Keep upstream runtime paths working through links, with resources sealed
 # in the standard bundle Resources directory instead of the executable dir.
 for name in ['style','translations','decoders','packages']:
  src=CONT/'MacOS'/name;dest=CONT/'Resources'/name
  if src.is_dir() and not src.is_symlink():
   if dest.exists():shutil.rmtree(dest)
   shutil.move(str(src),str(dest));src.symlink_to('../Resources/'+name)
def main():
 if '--verify-only' in sys.argv:
  verify();return
 processes=subprocess.check_output(['ps','-axo','command='],text=True).splitlines()
 names={str(BIN),os.path.relpath(BIN,ROOT)}
 if any(line.strip().split(None,1) and line.strip().split(None,1)[0] in names for line in processes):
  raise RuntimeError('Close this Scopy app before replacing its bundle; the running app was preserved.')
 LOG.write_text('')
 if APP.exists():
  # Only replace this script's own generated bundle, never source or staging.
  shutil.rmtree(APP)
 APP.parent.mkdir(exist_ok=True)
 shutil.copytree(ROOT/'build/Scopy.app',APP,symlinks=True)
 emu=ROOT/'iio-emu/build-m4/iio-emu'
 shutil.copy2(emu,CONT/'MacOS/iio-emu')
 for name in ['translations','style']:
  src=ROOT/'build'/name
  if src.exists():shutil.copytree(src,CONT/'MacOS'/name,dirs_exist_ok=True)
 FW.mkdir(exist_ok=True)
 for category in ['renderers','sceneparsers','geometryloaders']:
  src=pathlib.Path('/opt/homebrew/opt/qt@5/plugins')/category
  if src.exists():shutil.copytree(src,CONT/'plugins'/category,dirs_exist_ok=True)
 closure()
 run(['/opt/homebrew/opt/qt@5/bin/macdeployqt',APP,'-always-overwrite','-verbose=1'])
 DONE.clear();closure()
 normalize_layout()
 # The build uses current macOS 26 Homebrew bottles; do not claim older compatibility.
 info=CONT/'Info.plist'
 with info.open('rb') as f:data=plistlib.load(f)
 data.update(CFBundleIdentifier='org.adi.Scopy.M4.v221',CFBundleShortVersionString='2.2.1',CFBundleVersion='2.2.1',LSMinimumSystemVersion='26.0')
 with info.open('wb') as f:plistlib.dump(data,f)
 for p in sorted((p for p in APP.rglob('*') if macho(p) and p!=BIN),key=lambda x:len(x.parts),reverse=True):
  run(['codesign','--force','--sign','-','--timestamp=none',p])
 for p in sorted(APP.rglob('*.framework'),key=lambda x:len(x.parts),reverse=True):run(['codesign','--force','--sign','-','--timestamp=none',p])
 run(['codesign','--force','--deep','--sign','-','--timestamp=none',APP])
 run(['codesign','--verify','--deep','--strict','--verbose=2',APP])
 verify()
def verify():
 missing=[];external=[];arch=[];count=0
 for p in APP.rglob('*'):
  if not macho(p):continue
  count+=1
  own=run(['otool','-D',p],False).splitlines()
  ident=own[1].strip() if len(own)>1 else None
  a=run(['lipo','-archs',p]).strip()
  if 'arm64' not in a.split():arch.append([str(p),a])
  for dep in deps(p):
   if dep==ident or dep.startswith(SYSTEM):continue
   if dep.startswith(('/opt/','/Users/')):external.append([str(p),dep])
   elif dep.startswith('@executable_path/') and not pathlib.Path(dep.replace('@executable_path',str(BIN.parent))).exists():missing.append([str(p),dep])
 result={'app':str(APP),'macho_files':count,'missing':missing,'external':external,'wrong_arch':arch}
 (LOCAL/'bundle-verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2),flush=True)
 if missing or external or arch:raise RuntimeError('Bundle verification failed')
if __name__=='__main__':
 try:main()
 except Exception as e:print('PACKAGE STOPPED:',e,flush=True);sys.exit(1)
