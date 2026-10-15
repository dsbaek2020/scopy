# Scopy v2.2.1 — Windows Codex 인계서

작성일: 2026-10-15 (Asia/Seoul)
대상: AMD Ryzen AI MAX+ 395 / Windows x64

## Windows Codex가 달성할 목표

사용자는 Windows의 Qt Creator에서 프로젝트를 열고 **Run 또는 Debug 버튼을 눌러 빌드·실행·디버깅**하기를 원한다. 이 문서를 읽는 Windows Codex가 의존성 설치/빌드와 IDE 초기 설정을 준비한다. 사용자의 기존 Windows 프로젝트와 Qt/Qwt 환경은 보존한다.

맥에서 수행한 것은 소스와 인계 자료 준비다. **Windows 빌드 성공, Windows 실행 파일/DLL 준비, Qt Creator Kit 설정 완료를 의미하지 않는다.** Windows Codex는 아래 절차를 실제 머신에서 수행하고 확인된 결과만 보고한다. 현재 대화의 사용자가 직접 Run/Debug할 계획이므로, 계측 시작·신호 출력·펌웨어 업데이트·드라이버 교체를 임의로 실행하지 않는다.

## Windows Codex에 전달할 첫 메시지

> 첨부한 WINDOWS_CODEX_HANDOFF.md를 읽고 Scopy v2.2.1을 이 Windows AI MAX+ 395 머신에서 준비해 줘. 내가 Qt Creator의 Run/Debug 버튼을 사용할 수 있도록 Windows x64 의존성, GCC/Qt 5/GDB Kit, Debug 및 RelWithDebInfo 빌드, 프로젝트 전용 DLL/Python 경로까지 구성해 줘. 기존 개발 환경과 Qwt는 보존하고, 공식 GitHub에는 푸시하지 마. 맥용 빌드 결과와 CMake 캐시는 재사용하지 말고 Windows에서 실제 경로와 버전을 확인해. GitHub 저장소 생성이나 푸시는 이번 작업에 포함하지 않는다. 처음부터 다시 조사하기 전에 이 문서의 확정 사실과 첨부 패치를 활용해 줘.

## 확정된 소스 기준

- 원본: https://github.com/analogdevicesinc/scopy
- 릴리스: **v2.2.1**, Qt 5 사용.
- 정확한 커밋: `299d9f150fd8ecb722701d5f615a74877878e4b0`.
- 이번 맥 소스: `/Users/baegdaeseong/SCOPY_Mac/scopy-v2.2.1-m4`.
- 맥 로컬 브랜치: `codex/macos-arm64-v2.2.1`.
- 원본 main/개발판으로 무심코 전환하지 않는다. 이번 목표는 v2.2.1이다.
- 이번 수정과 인계 자료를 게시하는 브랜치: `dsbaek2020/scopy`의 `codex/v2.2.1-macos-m4-windows-handoff`.
- 이 브랜치에는 아래 3개 소스 수정이 이미 적용되어 있다.

### 첨부 ZIP과 패치의 관계

`scopy-v2.2.1-windows-handoff.zip`은 위 커밋의 추적 소스에 아래 3개 수정 파일을 덮어쓴 **소스 스냅샷**이다. `.git`은 없다. ZIP에는 `local-windows/` 자료도 들어 있다.

`local-windows/mac-local-source-fixes.patch`는 원본 v2.2.1에 적용하는 패치다. **ZIP의 소스에는 이미 적용되어 있으므로 다시 적용하면 안 된다.** 새로 Git clone한 원본에만 `git apply --check` 후 적용한다.

맥의 `build/`, `dist/`, `staging/`, `.user`, `CMakeUserPresets.json`, 개인 설정 백업과 로그는 ZIP에서 제외했다. Windows x64용 의존성은 별도로 빌드한다.

Git을 사용하는 개발에는 아래 새 clone 경로가 적합하다. 네트워크를 사용할 수 없다면 ZIP 자체를 이용하되, upstream 스크립트 일부가 `git rev-parse`를 사용한다는 점을 처리한다.

## GitHub: 확인된 계정/저장소와 금지 사항

인증 계정은 **dsbaek2020**이다.

| 저장소 | 확인된 상태 |
|---|---|
| https://github.com/dsbaek2020/scopy | 공개 포크. GitHub API의 fork=true, parent/source=analogdevicesinc/scopy |
| https://github.com/dsbaek2020/scopy_Apple_Mac_M4_ARM | 과거 Mac 작업용 비공개 저장소 |
| https://github.com/dsbaek2020/scopy_M4maxArmApple_Qt5brew | 초기 Qt 5/M4 작업용 비공개 저장소 |

이번 작업은 개인 포크의 새 `codex/v2.2.1-macos-m4-windows-handoff` 브랜치로 공유한다. 기존 main/gh-pages와 다른 개인 저장소를 초기화/덮어쓰기하지 않는다.

맥 clone의 fetch origin은 공식 GitHub이고, pushurl은 `/dev/null/SCOPY_OFFICIAL_PUSH_DISABLED`로 차단되어 있다. **Git remote 설정은 clone/ZIP을 통해 자동 전달되지 않는다.** Windows에서도 별도로 차단해야 한다. 단순히 개인 포크가 존재한다는 사실만으로 이번 로컬 clone이 개인 포크와 연결된 것은 아니다.

### Windows에서 게시된 브랜치를 가져오기

PowerShell에서 새 경로에 실행한다. 기존 경로가 있다면 먼저 상태를 확인한다.

```powershell
git clone --single-branch --branch codex/v2.2.1-macos-m4-windows-handoff https://github.com/dsbaek2020/scopy.git C:/Dev/scopy-v2.2.1-win
Set-Location C:/Dev/scopy-v2.2.1-win
git log -1 --oneline
git remote -v
```

이 clone의 origin은 본인 포크다. 아래 3개 수정과 인계 자료가 이미 들어 있으므로 **첨부 패치를 다시 적용하지 않는다.** Windows Codex는 이 브랜치를 기준으로 새 로컬 작업 브랜치를 만들어도 된다. 기존 GitHub 브랜치를 변경하거나 새로 푸시하는 일은 Windows 준비 작업에 포함하지 않는다.

공식 소스를 비교할 연결이 필요하면 가져오기 전용 upstream을 추가한다.

```powershell
git remote add upstream https://github.com/analogdevicesinc/scopy.git
git config --local remote.upstream.pushurl https://push-disabled.invalid/analogdevicesinc/scopy.git
```

원본 v2.2.1을 별도로 clone한 경우에만 아래 패치를 사용한다. 먼저 `git rev-parse HEAD`가 위 원본 커밋인지 확인한다.

```powershell
git apply --check local-windows/mac-local-source-fixes.patch
git apply local-windows/mac-local-source-fixes.patch
```

## 맥에서 이미 적용한 3개 소스 수정

1. `packages/m2k/plugins/m2k/m2k-gui/CMakeLists.txt`
   - `find_package(Volk REQUIRED)`와 PUBLIC `Volk::volk` 연결 추가.
   - 공개 헤더의 `volk/volk_alloc.hh` include 의존성 누락 보정.
2. `core/CMakeLists.txt`
   - ARM 교차 컴파일에만 Python Development 단독 탐색 분기를 적용.
   - 네이티브 빌드는 Interpreter + Development를 함께 탐색.
3. `main.cpp`
   - `__APPLE__` 조건에서 `PYTHONDONTWRITEBYTECODE=1` 설정.
   - 서명된 macOS 앱 안에 Python 캐시가 생성되는 문제 방지. Windows에는 실행되지 않는 분기다.

새 소스에는 초기 보정(calibration) 우회 패치를 적용하지 않았다.

## 1. Windows 머신을 먼저 조사

`local-windows/preflight.ps1`은 OS/CPU/RAM/도구 경로/일반적인 MSYS2·Qt 경로/디스크 여유를 읽기만 한다. 시스템 PATH, 실행 정책, 설치 상태를 변경하지 않는다. 사용자의 정책을 우회하지 말고 가능한 방식으로 실행하거나 같은 정보를 터미널에서 읽는다.

추가로 확인할 것:

- Windows 버전/에디션, Qt Creator 실제 경로와 버전.
- Qt 5/Qt 6 설치와 GCC/MinGW/MSVC 툴체인 목록.
- MSYS2의 설치 위치, `MSYSTEM`, MINGW64/UCRT64 구분.
- gcc/g++/gdb/qmake/cmake/ninja/python/pkg-config의 절대 경로와 버전.
- 기존 프로젝트가 사용하는 Qt/Qwt 경로. 공유 설치를 덮어쓰지 않기 위한 기준이다.
- USB M2K 드라이버 상태는 읽기 전용으로 확인. 기존 드라이버를 임의로 교체하지 않는다.

## 2. 툴체인 선택: 무조건 최신 패키지 설치부터 하지 말 것

AI MAX+ 395의 목표 아키텍처는 **x86_64**, 맥 M4의 arm64와 다르다.

v2.2.1의 공식 Windows 스크립트는 **MSYS2 MINGW64/GCC + Qt 5**를 대상으로 한다. Qt Online Installer의 MSVC 또는 Qt 6 Kit를 그대로 연결하면 이 의존성과 맞지 않는다.

현재 MSYS2 문서에는 **2026-03-15 MINGW64 deprecated**가 명시되어 있다. 최신 기본 UCRT64를 기존 `/mingw64` 스크립트에 섞으면 안 된다. 실제 머신과 배포 가능 패키지에 따라 아래 중 하나를 선택하고 이유와 버전을 기록한다.

- 호환되는 MINGW64 패키지/빌드 환경을 프로젝트 전용 설치에 재현.
- 전체 Windows 의존성 스크립트를 UCRT64로 일관되게 이식하고 실제 빌드로 검증.

MinGW와 UCRT, MSVC 라이브러리/정적 import 라이브러리/Qt 빌드를 혼합하지 않는다. 기존 MSYS2를 일괄 업그레이드하거나 전역 PATH를 바꾸지 않는다. 예를 들어 별도 `C:/scopy-msys64` 설치와 프로젝트 전용 의존성 prefix를 사용할 수 있으나, 실제 경로는 머신 조사 후 정한다.

공식 CI의 Docker 이미지를 선택한다면 Windows 컨테이너 지원/호스트 에디션/이미지 버전도 확인해야 한다. 현재 `latest` 이미지가 릴리스 v2.2.1과 호환된다고 가정하지 않는다.

## 3. 의존성을 준비

기준 파일:

- `ci/windows/README.md`
- `ci/windows/mingw_toolchain.sh`
- `ci/windows/windows_build_process.sh`
- `ci/windows/build_and_create_installer.sh`
- `.github/workflows/mingwbuild.yml`

Qt 5와 기본 FFTW, ORC, libxml2, libzip, libffi, GLib, zlib, libusb, matio, Boost, Python/Mako 등의 패키지가 필요하다. 소스 의존성 순서는 원본 스크립트를 기준으로 한다:

1. libserialport
2. libiio **v0.26**
3. libad9361-iio
4. libm2k
5. spdlog
6. libsndfile
7. Volk
8. Analog Devices GNU Radio `scopy2-maint-3.10`
9. gr-scopy `3.10`
10. gr-m2k
11. cseci/qwt `qwt-multiaxes-updated`
12. libsigrokdecode + Windows 패치
13. libtinyiiod (Windows 릴리스 스크립트의 버전 확인)
14. KDDockWidgets `2.1`
15. extra-cmake-modules `kf5`
16. karchive `kf5`
17. genalyzer

Qt/Qwt는 같은 Windows 툴체인으로 빌드한다. Qwt의 저장소/브랜치는 일반 Qwt 패키지로 무심코 바꾸지 않는다. 완료된 의존성을 무조건 다시 빌드하지 말고 각 단계의 로그/성공 상태/정확한 Git 커밋과 패키지 버전을 남긴다.

### 원본 스크립트에서 실제로 확인한 점검 항목

- `USE_STAGING=OFF`: 해당 MSYS2 prefix에 설치한다. 기존 공유 환경에서 그대로 실행하지 않는다.
- `build_libiio()`의 따옴표 안 CMake 옵션 문자열에 `# Windows resource compiler` 같은 주석이 들어 있다. 셸 인자 전달을 점검/수정해야 한다.
- 여러 `GR_PYTHON_DIR==...python3.10...` 값은 등호 중복과 Python 버전 고정 문제를 확인해야 한다.
- Qt 5, Boost `system` 구성요소, Python ABI와 libsigrokdecode는 최신 패키지에서 달라질 수 있다. 패키지 버전을 확인하고 호환성을 실제로 해결한다.
- 일부 함수가 `git clean -xdf`, `git reset --hard`를 사용한다. 의존성의 별도 checkout에만 적용하고, 사용자 소스/기존 작업물을 대상으로 실행하지 않는다.
- 스크립트 마지막에는 무조건 `build_deps` 호출이 있다. 특정 함수만 재실행하려면 전체 스크립트 호출 동작을 먼저 점검한다.

위 항목은 정적 검토 결과이며, Windows에서 이미 수정·검증했다는 의미가 아니다.

## 4. Qt Creator에서 Run/Debug가 가능하도록 구성

실제 Windows 경로를 확인한 뒤 머신별 **CMakeUserPresets.json을 새로 생성**한다. 맥의 파일을 복사하지 않는다. 기존 파일이 있다면 보존하고 이번 Scopy 설정만 추가/병합한다.

필수 구성:

- `windows-x64-debug`: `CMAKE_BUILD_TYPE=Debug`, 별도 `build/windows-x64-debug`.
- `windows-x64-relwithdebinfo`: `CMAKE_BUILD_TYPE=RelWithDebInfo`, 별도 `build/windows-x64-relwithdebinfo`.
- GCC x64 + 해당 Qt 5 + GDB가 같은 툴체인 prefix를 사용.
- Ninja 또는 검증된 make generator. CMake, compiler, make/ninja, qmake 절대 경로 고정.
- CMAKE_PREFIX_PATH에 프로젝트 의존성 prefix와 Qt 5 prefix 지정.
- 필요 시 `CMAKE_POLICY_VERSION_MINIMUM=3.5` 지정.
- Python Interpreter/Development/실행 DLL 모두 같은 ABI와 버전으로 고정.
- `ENABLE_TESTING=OFF`를 초기 일반 앱 빌드에 적용하되, 하위 프로젝트가 별도 테스트를 추가할 수 있음을 확인.
- Qt Creator preset vendor debugger 항목 또는 전용 Kit에 실제 GDB 경로 연결.
- 기본 Run 대상은 **`scopy` / Scopy.exe**. 테스트 실행 파일을 기본으로 선택하지 않는다.
- 작업 디렉터리는 해당 Windows 빌드의 실행 파일 디렉터리.

### 실행 환경이 특히 중요

Run과 Debug 양쪽 모두 **프로젝트 전용** PATH에 의존성 DLL과 Qt 5 bin 경로가 있어야 한다. 전역 Windows PATH 변경으로 해결하지 않는다.

프로젝트의 `core/src/scopymainwindow.cpp::initPythonWIN32()`는 실행 디렉터리의 `python<major>.<minor>` 경로와 `SCOPY_PYTHONPATH`를 사용한다. `PYTHON_VERSION`은 CMake 캐시에 있으므로 버전을 바꿨다면 오래된 캐시도 점검한다.

실행 시 확인할 파일/경로:

- Qt 5 platform plugin과 qt.conf의 실제 탐색 경로.
- libiio/libm2k/Qwt/GNU Radio/Volk/Boost/Python 등 Windows DLL.
- 빌드된 Scopy 플러그인 DLL과 packages 리소스.
- `decoders` 폴더: Windows 경로는 상대 경로를 사용하므로 작업 디렉터리에 맞게 배치.
- Python 표준 라이브러리/lib-dynload/site-packages와 버전에 맞는 DLL.
- style/translations, 필요한 Qt 3D renderers/sceneparsers.

필요한 런타임 리소스 복사는 CMake post-build 등으로 자동화해서, 소스를 수정한 후 사용자가 매번 별도 수작업을 하지 않도록 한다. `SCOPY_DEV_MODE`는 자동 연결 등 추가 동작을 활성화하므로 Python 경로 문제만 해결하려고 무심코 켜지 않는다.

Qt Creator의 `.user`는 해당 Windows에서 생성/저장한다. 다른 프로젝트의 전역 Kit를 바꾸지 않고 Scopy용 Kit만 추가한다.

## 5. 완료 기준과 보고

Windows Codex는 아래를 확인한 후 사용자에게 준비 완료라고 보고한다.

- 실제 Windows 의존성 빌드/앱 링크가 성공하고 결과 파일이 존재.
- Qt Creator를 재실행해도 이번 프로젝트와 Debug/RelWithDebInfo Kit가 유지.
- 기본 Run 실행 파일과 작업 디렉터리가 올바름.
- Run/Debug에서 같은 의존성 prefix와 Python 런타임을 사용.
- Scopy.exe에 디버그 심볼이 있고 GDB가 실행 파일을 인식. 가능하면 main 중단점으로 확인하되 사용자의 직접 실행 계획을 존중.
- 공식 저장소 push가 차단되어 있고 새 푸시/PR/저장소 생성이 없음.
- 기존 Windows 프로젝트와 기존 Qt/Qwt를 변경하지 않았음을 확인.
- GUI/USB/계측을 실제로 테스트하지 않았다면 구분해서 보고. 계측 정확도까지 검증했다고 표현하지 않는다.

Windows 머신에 파일을 넘긴 것만으로, 또는 preset JSON 문법만 확인한 것으로 이 완료 기준을 충족했다고 보고하지 않는다.

## 맥에서 확인한 결과와 남아 있는 문제

맥에서는 14개 의존성, IIO emulator, 앱과 21개 플러그인을 빌드했다. Qt Creator의 Qt 5.15.17 Kit로 네이티브 arm64 빌드·실행을 확인했고, USB M2K와 오실로스코프 UI도 열었다.

첫 IDE 실행에서 M2K 설정 복원 중 `Cannot set the number of kernel buffers` 예외로 종료됐다. 재실행에서는 연결과 오실로스코프 화면이 열렸다. 원인은 미확정이며 Windows에서도 해결되어 있을 것이라고 가정하지 않는다. 실제 파형 취득/출력/정확도 검증은 수행하지 않았다.

맥의 두 기존 프로젝트와 JellyDAQView는 이번 새 Scopy 작업에서 보존했다. 맥 Scopy의 Qwt는 프로젝트의 Qt 5용 Qwt 6.4이고, JellyDAQView의 Qt 6용 Qwt 6.3 프레임워크와 별개다. Windows에서도 이 분리 원칙을 유지한다.

## 참고 문서

- Scopy Windows: https://analogdevicesinc.github.io/scopy/user_guide/build_instructions/windowsBuild.html
- MSYS2 환경과 MINGW64 변경: https://www.msys2.org/docs/environments/
- Qt Creator CMake presets/GDB: https://doc.qt.io/qtcreator/creator-build-settings-cmake-presets.html
- Qt Creator 프로젝트별 실행 환경: https://doc.qt.io/qtcreator/creator-how-set-project-environment.html
