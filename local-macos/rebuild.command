#!/bin/bash
set -euo pipefail
SCOPY_LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCOPY_LOCAL_DIR/.."
/opt/homebrew/opt/python@3.12/bin/python3.12 local-macos/build.py app
/opt/homebrew/opt/python@3.12/bin/python3.12 local-macos/package.py
open dist/Scopy.app
