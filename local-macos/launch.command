#!/bin/bash
set -euo pipefail
SCOPY_LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"
open "$SCOPY_LOCAL_DIR/../dist/Scopy.app"
