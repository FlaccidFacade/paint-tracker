#!/usr/bin/env bash
# build_and_publish.sh – Build the frontend, bundle it into the Python package,
# then (optionally) publish to PyPI.
#
# Prerequisites:
#   - Node.js / npm installed (to build the React frontend)
#   - pip install build
#
# Usage:
#   bash scripts/build_and_publish.sh              # build + publish to PyPI (requires twine + credentials)
#   bash scripts/build_and_publish.sh --build-only # build only, skip publish (used in CI with OIDC)
#   bash scripts/build_and_publish.sh --test       # build + upload to TestPyPI (local use; requires twine)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATIC_DIR="$ROOT/paint_tracker/static"
FRONTEND_DIR="$ROOT/frontend"
ARG="${1:-}"

info()    { echo "ℹ️  $*"; }
success() { echo "✅  $*"; }

# ── 1. Build React frontend ───────────────────────────────────────────────────
info "Installing frontend dependencies …"
cd "$FRONTEND_DIR"
npm ci --silent

info "Building frontend → $STATIC_DIR …"
npm run build   # vite.config.js already sets outDir to paint_tracker/static

success "Frontend built."

# ── 2. Build Python wheel + sdist ────────────────────────────────────────────
cd "$ROOT"
info "Building Python distribution …"
python3 -m build --wheel --sdist

success "Build complete. Artifacts in dist/."

# ── 3. Publish ────────────────────────────────────────────────────────────────
if [[ "$ARG" == "--build-only" ]]; then
    info "Build-only mode – skipping publish."
elif [[ "$ARG" == "--test" ]]; then
    info "Uploading to TestPyPI …"
    python3 -m twine upload --repository testpypi dist/*
    success "Uploaded to TestPyPI."
    echo "Install with: pip install --index-url https://test.pypi.org/simple/ paint-tracker"
else
    info "Uploading to PyPI …"
    python3 -m twine upload dist/* --verbose
    success "Uploaded to PyPI."
    echo "Install with: pip install paint-tracker"
fi
