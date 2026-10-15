#!/usr/bin/env python3
"""Reproducible, project-local macOS arm64 build of Scopy v2.2.1."""
import argparse, datetime, json, os, pathlib, shutil, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
LOCAL=ROOT/'local-macos'; STAGE=ROOT/'staging'; PREFIX=STAGE/'dependencies'; LOGS=LOCAL/'logs'
QT=pathlib.Path('/opt/homebrew/opt/qt@5'); BOOST=pathlib.Path('/opt/homebrew/opt/boost@1.85'); PYTHON=pathlib.Path('/opt/homebrew/opt/python@3.12/bin/python3.12')
NINJA=os.environ.get('SCOPY_NINJA') or shutil.which('ninja') or str(pathlib.Path.home()/'Qt/Tools/Ninja/ninja'); JOBS=os.environ.get('SCOPY_JOBS','10')
ENV=os.environ.copy()
ENV.update(PATH=f'{QT}/bin:/opt/homebrew/opt/bison/bin:/opt/homebrew/opt/python@3.12/libexec/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin',PKG_CONFIG_PATH=f'{PREFIX}/lib/pkgconfig:{BOOST}/lib/pkgconfig:/opt/homebrew/opt/python@3.12/lib/pkgconfig:/opt/homebrew/lib/pkgconfig:/opt/homebrew/share/pkgconfig',CMAKE_PREFIX_PATH=f'{PREFIX};{QT};{BOOST};/opt/homebrew',CC='/usr/bin/clang',CXX='/usr/bin/clang++',PYTHON=str(PYTHON),PYTHON3=str(PYTHON),HOMEBREW_NO_AUTO_UPDATE='1',HOMEBREW_NO_INSTALL_CLEANUP='1')
REPOS=[('libserialport','sigrokproject/libserialport','master'),('libiio','analogdevicesinc/libiio','v0.26'),('libad9361','analogdevicesinc/libad9361-iio','main'),('libm2k','analogdevicesinc/libm2k','main'),('gnuradio','analogdevicesinc/gnuradio','scopy2-maint-3.10'),('gr-scopy','analogdevicesinc/gr-scopy','3.10'),('gr-m2k','analogdevicesinc/gr-m2k','main'),('qwt','cseci/qwt','qwt-multiaxes-updated'),('libsigrokdecode','sigrokproject/libsigrokdecode','master'),('libtinyiiod','analogdevicesinc/libtinyiiod','master'),('KDDockWidgets','KDAB/KDDockWidgets','2.1'),('extra-cmake-modules','KDE/extra-cmake-modules','kf5'),('karchive','KDE/karchive','kf5'),('genalyzer','analogdevicesinc/genalyzer','main')]
for p in [LOCAL,STAGE,PREFIX,LOGS]:p.mkdir(parents=True,exist_ok=True)
def run(args,cwd=ROOT,log='build',env=None):
 print(datetime.datetime.now().isoformat(timespec='seconds'),log, ' '.join(map(str,args)),flush=True)
 with (LOGS/(log+'.log')).open('a') as out:
  out.write('\n$ '+' '.join(map(str,args))+'\n');out.flush()
  p=subprocess.run(list(map(str,args)),cwd=cwd,env=env or ENV,stdout=out,stderr=subprocess.STDOUT)
 if p.returncode:
  print((LOGS/(log+'.log')).read_text(errors='replace')[-9500:],flush=True)
  raise RuntimeError(f'{log} failed ({p.returncode}); see {LOGS/(log+".log")}')
def capture(args,cwd=ROOT):return subprocess.check_output(args,cwd=cwd,env=ENV,text=True).strip()
def fetch():
 for name,repo,branch in REPOS+[('iio-emu','analogdevicesinc/iio-emu','main')]:
  target=ROOT/name if name=='iio-emu' else STAGE/name
  if not (target/'.git').exists():run(['git','clone','--depth','1','--branch',branch,'--recurse-submodules',f'https://github.com/{repo}.git',target],log='fetch-'+name)
 manifest={name:{'repository':repo,'branch':branch,'commit':capture(['git','rev-parse','HEAD'],ROOT/name if name=='iio-emu' else STAGE/name)} for name,repo,branch in REPOS+[('iio-emu','analogdevicesinc/iio-emu','main')]}
 manifest['scopy']={'tag':'v2.2.1','commit':capture(['git','rev-parse','HEAD'])}
 (LOCAL/'source-revisions.json').write_text(json.dumps(manifest,indent=2)+'\n')
def common():return ['-G','Ninja','-DCMAKE_MAKE_PROGRAM='+NINJA,'-DCMAKE_BUILD_TYPE=RelWithDebInfo','-DCMAKE_OSX_ARCHITECTURES=arm64','-DCMAKE_OSX_DEPLOYMENT_TARGET=14.0','-DCMAKE_POLICY_VERSION_MINIMUM=3.5','-DCMAKE_INSTALL_PREFIX='+str(PREFIX),'-DCMAKE_PREFIX_PATH='+ENV['CMAKE_PREFIX_PATH'],'-DBOOST_ROOT='+str(BOOST),'-DBoost_ROOT='+str(BOOST),'-DBoost_DIR='+str(BOOST/'lib/cmake/Boost-1.85.0'),'-DPYTHON_EXECUTABLE='+str(PYTHON),'-DPython3_EXECUTABLE='+str(PYTHON),'-DPython3_ROOT_DIR=/opt/homebrew/opt/python@3.12','-DPython3_LIBRARY=/opt/homebrew/opt/python@3.12/Frameworks/Python.framework/Versions/3.12/lib/libpython3.12.dylib','-DPython3_INCLUDE_DIR=/opt/homebrew/opt/python@3.12/Frameworks/Python.framework/Versions/3.12/include/python3.12','-DIIO_INCLUDE_DIRS='+str(PREFIX/'include'),'-DCMAKE_INSTALL_RPATH='+str(PREFIX/'lib'),'-DCMAKE_CXX_FLAGS=-I'+str(QT/'include'),'-DCMAKE_C_FLAGS=-I'+str(QT/'include'),'-DCMAKE_C_COMPILER=/usr/bin/clang','-DCMAKE_CXX_COMPILER=/usr/bin/clang++']
def cmake(name,opts=(),install=True):
 src=ROOT/name if name=='iio-emu' else STAGE/name
 build=src/'build-m4'
 run(['cmake','-S',src,'-B',build,*common(),*opts],log=name)
 run(['cmake','--build',build,'--parallel',JOBS],log=name)
 if install:run(['cmake','--install',build],log=name)
 return build
def framework(name,framework_name,opts):
 build=cmake(name,opts,False)
 src=STAGE/name
 shutil.copy2(src/('iio.h' if name=='libiio' else 'ad9361.h'),PREFIX/'include')
 dest=PREFIX/'lib'/(framework_name+'.framework')
 if dest.exists():shutil.rmtree(dest)
 shutil.copytree(build/(framework_name+'.framework'),dest,symlinks=True)
 shutil.copy2(build/('libiio.pc' if name=='libiio' else 'libad9361.pc'),PREFIX/'lib/pkgconfig')
def patch_m2k():
 for p in (STAGE/'libm2k').rglob('CMakeLists.txt'):
  if '.git' in p.parts or 'build-m4' in p.parts:continue
  s=p.read_text();t=s.replace('set(CMAKE_OSX_ARCHITECTURES "x86_64")','# Respect CMAKE_OSX_ARCHITECTURES supplied by the caller (Apple Silicon).')
  if t!=s:p.write_text(t)
def qwt():
 src=STAGE/'qwt';p=src/'qwtconfig.pri';s=p.read_text()
 s=s.replace('QWT_INSTALL_PREFIX    = /usr/local/qwt-$$QWT_VERSION-ma','QWT_INSTALL_PREFIX    = '+str(PREFIX))
 s=s.replace('QWT_INSTALL_PLUGINS   = $${QWT_INSTALL_PREFIX}/plugins/designer','# QWT_INSTALL_PLUGINS disabled for local build')
 s=s.replace('QWT_CONFIG += QwtFramework','# QwtFramework disabled for local dylib build')
 s=s.replace('QWT_CONFIG     += QwtDesigner','# QwtDesigner disabled')
 p.write_text(s)
 p=src/'src/src.pro';s=p.read_text()
 if '\nmacx: QWT_SONAME=' not in s:s+='\nmacx: QWT_SONAME='+str(PREFIX/'lib/libqwt.dylib')+'\n'
 p.write_text(s)
 run([QT/'bin/qmake','qwt.pro','QMAKE_APPLE_DEVICE_ARCHS=arm64','QMAKE_MACOSX_DEPLOYMENT_TARGET=14.0'],cwd=src,log='qwt')
 run(['make','-j'+JOBS],cwd=src,log='qwt');run(['make','install'],cwd=src,log='qwt')
def autotools(name):
 src=STAGE/name
 if not (src/'configure').exists():run(['./autogen.sh'],cwd=src,log=name)
 extra=['--disable-doxygen-doc'] if name=='libsigrokdecode' else []
 run(['./configure','--prefix='+str(PREFIX),*extra],cwd=src,log=name)
 run(['make','-j'+JOBS],cwd=src,log=name);run(['make','install'],cwd=src,log=name)
def deps(start=None):
 names=[r[0] for r in REPOS]
 if start:names=names[names.index(start):]
 for name in names:
  if start is None and (LOCAL/(name+'.done')).exists():
   print('ALREADY BUILT',name,flush=True);continue
  print('DEPENDENCY',name,flush=True)
  (PREFIX/'include').mkdir(exist_ok=True);(PREFIX/'lib/pkgconfig').mkdir(parents=True,exist_ok=True)
  if name in ['libserialport','libsigrokdecode']:autotools(name)
  elif name=='libiio':framework(name,'iio',['-DWITH_TESTS=OFF','-DWITH_DOC=OFF','-DHAVE_DNS_SD=ON','-DENABLE_DNS_SD=ON','-DWITH_MATLAB_BINDINGS=OFF','-DCSHARP_BINDINGS=OFF','-DPYTHON_BINDINGS=OFF','-DINSTALL_UDEV_RULE=OFF','-DWITH_SERIAL_BACKEND=ON','-DWITH_NETWORK_BACKEND=ON','-DENABLE_IPV6=OFF'])
  elif name=='libad9361':framework(name,'ad9361',[])
  elif name=='libm2k':
   patch_m2k();cmake(name,['-DENABLE_PYTHON=OFF','-DENABLE_CSHARP=OFF','-DBUILD_EXAMPLES=OFF','-DENABLE_TOOLS=OFF','-DINSTALL_UDEV_RULES=OFF','-DENABLE_LOG=OFF'])
  elif name=='gnuradio':cmake(name,['-DENABLE_DEFAULT=OFF','-DENABLE_GNURADIO_RUNTIME=ON','-DENABLE_GR_ANALOG=ON','-DENABLE_GR_BLOCKS=ON','-DENABLE_GR_FFT=ON','-DENABLE_GR_FILTER=ON','-DENABLE_GR_IIO=ON','-DENABLE_POSTINSTALL=OFF','-DENABLE_PYTHON=OFF','-DENABLE_TESTING=OFF'])
  elif name=='gr-scopy':cmake(name,['-DWITH_PYTHON=OFF','-DENABLE_PYTHON=OFF'])
  elif name=='gr-m2k':cmake(name,['-DENABLE_PYTHON=OFF','-DDIGITAL=OFF'])
  elif name=='qwt':qwt()
  elif name=='libtinyiiod':cmake(name,['-DBUILD_EXAMPLES=OFF'])
  elif name=='KDDockWidgets':cmake(name,['-DKDDockWidgets_EXAMPLES=OFF','-DKDDockWidgets_TESTS=OFF','-DQt5_DIR='+str(QT/'lib/cmake/Qt5')])
  elif name=='extra-cmake-modules':cmake(name,['-DBUILD_TESTING=OFF','-DBUILD_HTML_DOCS=OFF','-DBUILD_MAN_DOCS=OFF','-DBUILD_QTHELP_DOCS=OFF'])
  elif name=='karchive':cmake(name,['-DBUILD_TESTING=OFF'])
  elif name=='genalyzer':
   build=cmake(name,['-DBUILD_TESTING=OFF','-DBUILD_SHARED_LIBS=ON','-DOSX_INSTALL_FRAMEWORKSDIR='+str(PREFIX/'lib')])
   fw=next(build.rglob('genalyzer.framework'),None)
   if fw and not (PREFIX/'lib/genalyzer.framework').exists():shutil.copytree(fw,PREFIX/'lib/genalyzer.framework',symlinks=True)
  (LOCAL/(name+'.done')).write_text(datetime.datetime.now().isoformat()+'\n')
def app():
 cmake('iio-emu',[],False)
 run(['cmake','-U_Python3_*','-S',ROOT,'-B',ROOT/'build',*common(),'-DENABLE_TESTING=OFF','-DCMAKE_STAGING_PREFIX='+str(PREFIX),'-DCMAKE_EXE_LINKER_FLAGS=-L'+str(PREFIX/'lib')],log='scopy')
 run(['cmake','--build',ROOT/'build','--parallel',JOBS],log='scopy')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['fetch','deps','app']);p.add_argument('--from-dep');a=p.parse_args()
 try:
  if a.phase=='fetch':fetch()
  elif a.phase=='deps':deps(a.from_dep)
  else:app()
 except Exception as e:print('BUILD STOPPED:',e,flush=True);sys.exit(1)
