# Scopy v2.2.1 — macOS M4 arm64 build

Base: official v2.2.1, commit `299d9f150fd8ecb722701d5f615a74877878e4b0`.
Personal fork branch: `dsbaek2020/scopy`,
`codex/v2.2.1-macos-m4-windows-handoff`.

## Build environment

Validated on Apple M4 Max arm64, macOS 26.5.1 with AppleClang.
Qt 5.15.17: `/opt/homebrew/opt/qt@5`.
Boost 1.85: `/opt/homebrew/opt/boost@1.85` (beside the existing Boost).
Python 3.12: `/opt/homebrew/opt/python@3.12/bin/python3.12`.
CMake 4.1.1 and Ninja are required. `SCOPY_NINJA` may select a Ninja binary;
otherwise the runner searches PATH, then `~/Qt/Tools/Ninja/ninja`.

The final app minimum is macOS 26 because some Homebrew runtime libraries
require it. Earlier upstream deployment flags do not establish macOS 14/15
compatibility. Dependency source commits are recorded in source-revisions.json.
`fetch` resolves moving branches for new clones; that file records the tested
revision set, rather than locking future fetches automatically.

## Build and run

Run from the repository root:

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 local-macos/build.py fetch
/opt/homebrew/opt/python@3.12/bin/python3.12 local-macos/build.py deps
/opt/homebrew/opt/python@3.12/bin/python3.12 local-macos/build.py app
/opt/homebrew/opt/python@3.12/bin/python3.12 local-macos/package.py
open dist/Scopy.app
```

The runner builds dependencies into this checkout's `staging/dependencies`.
It does not install Qwt into the global framework directory. Dependency stages
already marked complete are skipped; `deps --from-dep NAME` rebuilds that
stage and subsequent ones. Logs and status files remain local.

`local-macos/rebuild.command` builds, packages, signs and opens the app.
`local-macos/launch.command` opens the existing packaged app.
Close a running app before replacing its bundle; package.py rejects replacing
the same running executable. The package step updates `dist/Scopy.app`.
Use `package.py --verify-only` to inspect bundled library paths/architectures.

## Qt Creator

After the first command-line build, open the top-level CMakeLists.txt and import
the existing `build` directory using Qt 5.15.17 and the actual GCC/Clang kit
for this Mac. The validated kit used AppleClang and RelWithDebInfo.
Use Cmd+B to build and Cmd+R to run the `scopy` target. The running build
uses this checkout's dependency libraries through Qt Creator's library search
path option. A separate package.py run refreshes the standalone dist app.

CMakeUserPresets.json and CMakeLists.txt.user are machine-specific and are not
published. Do not transfer their absolute paths or the build cache to Windows.

## Local source changes

- Link `Volk::volk` publicly in the M2K GUI to expose its header dependency.
- Request matching Python Interpreter and Development for native ARM builds;
  reserve the Development-only path for ARM cross-compilation.
- Disable Python bytecode writes on macOS so decoder imports preserve the
  signed app bundle. No calibration bypass was added.

Packaging collects non-system dependencies, Qt plugins, the IIO emulator and
runtime resources, rewrites library paths and ad-hoc signs the final bundle.
The app uses Scopy's usual user settings location. Keep a settings backup
when moving between different Scopy versions.

## Validation and limits

On the tested Mac, the dependency stack, emulator, app and 21 plugin libraries
built successfully. The packaged app contained 232 arm64-capable Mach-O files
with no missing/external non-system library references in the scan; strict
codesign verification passed after decoder loading. Qt Creator also built
and launched the native app. USB M2K detection and the Oscilloscope UI worked.

An initial session reported USB READ/WRITE -9 and GNU Radio alignment warnings.
An IDE session aborted while restoring M2K settings with
`Cannot set the number of kernel buffers`; the next launch connected and
opened the Oscilloscope UI. Its cause is unresolved. Acquisition accuracy,
all output modes and long-running hardware stability have not been verified.

Windows preparation is described in ../local-windows/WINDOWS_CODEX_HANDOFF.md.
Windows compilation and Qt Creator/GDB setup still require the Windows host.
