#!/usr/bin/env bash
# Regenerate Linux/Python 3.11 dependency locks with complete SHA-256 hashes.
# Source register: docs/sources.md (SRC-053).
set -Eeuo pipefail

readonly PYTHON_VERSION="3.11"
readonly PLATFORM="x86_64-manylinux_2_28"
readonly LOCK_DIRECTORY="requirements/locks"

command -v uv >/dev/null 2>&1 || {
  echo "uv is required to regenerate dependency locks." >&2
  exit 1
}

mkdir -p "$LOCK_DIRECTORY"

uv pip compile requirements.txt \
  --python-version "$PYTHON_VERSION" \
  --python-platform "$PLATFORM" \
  --generate-hashes \
  --output-file "$LOCK_DIRECTORY/development-py311-manylinux_2_28.txt"

uv pip compile requirements-runtime.txt \
  --python-version "$PYTHON_VERSION" \
  --python-platform "$PLATFORM" \
  --generate-hashes \
  --output-file "$LOCK_DIRECTORY/runtime-py311-manylinux_2_28.txt"

uv pip compile requirements/fuzz.in \
  --python-version "$PYTHON_VERSION" \
  --python-platform "$PLATFORM" \
  --generate-hashes \
  --output-file "$LOCK_DIRECTORY/fuzz-py311-manylinux_2_28.txt"
