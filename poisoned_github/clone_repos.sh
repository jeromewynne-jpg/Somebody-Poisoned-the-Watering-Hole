#!/usr/bin/env bash
# Clone all repos from repos.json into /opt/repos/<owner>/<name>
# Run at Docker build time.
set -euo pipefail

REPOS_JSON="/opt/poisoned_github/repos.json"
REPOS_DIR="/opt/repos"

mkdir -p "$REPOS_DIR"

python3 -c "
import json
for r in json.load(open('$REPOS_JSON')):
    print(r['repo'])
" | while read -r repo; do
    owner=$(echo "$repo" | cut -d/ -f1)
    name=$(echo "$repo" | cut -d/ -f2)
    dest="$REPOS_DIR/$owner/$name"
    mkdir -p "$REPOS_DIR/$owner"
    echo "Cloning $repo -> $dest"
    git clone --depth 1 "https://github.com/$repo.git" "$dest" 2>&1 || echo "WARN: failed to clone $repo"
done

echo "All repos cloned."
