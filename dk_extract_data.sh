#!/usr/bin/env bash
set -euo pipefail

[[ $# -ge 1 ]] || { echo "Usage: $0 <SCENES_DIR> [more_dirs...]"; exit 1; }

for ROOT in "$@"; do
  find "$ROOT" -type f -name "video.vrs" -print0 |
  while IFS= read -r -d '' vrs_file; do
    scene_dir=$(dirname "$vrs_file")
    echo "----------------------------------------"
    echo "Scene: $scene_dir"
    echo "File : $(basename "$vrs_file")"
    (
      cd "$scene_dir"
      vrs extract-all "$(basename "$vrs_file")"
      cd ".."
    )
    echo "----------------------------------------"
  done
done