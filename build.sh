#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATE=$(date +"%b%d")
RESUME_NAME="${RESUME_NAME:-Resume}"

build_resume() {
  local dir="$1"
  local tex_file="$SCRIPT_DIR/$dir/resume.tex"

  if [[ ! -f "$tex_file" ]]; then
    echo "SKIP: $tex_file not found"
    return
  fi

  local position
  position=$(grep -m1 '% POSITION:' "$tex_file" | sed 's/.*POSITION: *//')

  if [[ -z "$position" ]]; then
    echo "WARN: No % POSITION: comment in $tex_file, using directory name"
    position="$dir"
  fi

  echo "==> Building $dir/ (Position: $position, Date: $DATE) ..."
  cd "$SCRIPT_DIR/$dir"
  tectonic resume.tex

  local output="${RESUME_NAME}_${position}_${DATE}.pdf"
  mv resume.pdf "$output"
  echo "    Done → $dir/$output"
}

build_resume "pm"
build_resume "engineer"

echo ""
echo "All resumes built successfully."
