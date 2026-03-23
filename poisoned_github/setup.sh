#!/usr/bin/env bash
# Setup script for PoisonedGithub tasks.
# Copies a pre-cloned repo to /workspace/repo.
#
# Expected env vars:
#   TASK_CONFIG_PATH - path to the task config JSON

set -euo pipefail

if [ -z "${TASK_CONFIG_PATH:-}" ]; then
    echo "ERROR: TASK_CONFIG_PATH not set" >&2
    exit 1
fi

if [ ! -f "$TASK_CONFIG_PATH" ]; then
    echo "ERROR: Task config not found at $TASK_CONFIG_PATH" >&2
    exit 1
fi

REPO=$(python3 -c "import json; print(json.load(open('$TASK_CONFIG_PATH'))['repo'])")
OWNER=$(echo "$REPO" | cut -d/ -f1)
NAME=$(echo "$REPO" | cut -d/ -f2)
SRC="/opt/repos/$OWNER/$NAME"
DEST="/workspace/repo"

if [ ! -d "$SRC" ]; then
    echo "ERROR: Pre-cloned repo not found at $SRC" >&2
    exit 1
fi

cp -r "$SRC" "$DEST"
cd "$DEST"
echo "Repo ready: $DEST"
