#!/bin/bash
# Restore PDFs from data/pdfs/ (OneDrive export) back to data/books/*/pdf/
#
# Usage:
#   ./scripts/restore-pdfs.sh                # restore from ./data/pdfs/
#   ./scripts/restore-pdfs.sh /path/to/pdfs  # restore from custom path

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="${1:-$REPO_ROOT/data/pdfs}"

if [ ! -d "$SOURCE" ]; then
  echo "Error: PDF source directory not found: $SOURCE"
  echo "Download the pdfs/ folder from OneDrive and place it at data/pdfs/,"
  echo "or pass the path as an argument."
  exit 1
fi

echo "Restoring PDFs from: $SOURCE"
echo "Restoring to:        $REPO_ROOT/data/books/*/pdf/"
echo ""

count=0
for book_dir in "$SOURCE"/*/; do
  book=$(basename "$book_dir")
  target="$REPO_ROOT/data/books/$book/pdf"
  mkdir -p "$target"

  # Copy PDFs (top-level)
  for pdf in "$book_dir"*.pdf; do
    [ -f "$pdf" ] || continue
    cp "$pdf" "$target/"
    count=$((count + 1))
  done

  # Copy subdirectories (e.g., siyar split/)
  for subdir in "$book_dir"*/; do
    [ -d "$subdir" ] || continue
    sub=$(basename "$subdir")
    mkdir -p "$target/$sub"
    for pdf in "$subdir"*.pdf; do
      [ -f "$pdf" ] || continue
      cp "$pdf" "$target/$sub/"
      count=$((count + 1))
    done
  done
done

echo "Restored $count PDFs across $(ls -d "$SOURCE"/*/ | wc -l | tr -d ' ') books."
echo "Total size: $(du -sh "$REPO_ROOT/data/books/*/pdf" 2>/dev/null | tail -1 | awk '{print $1}' || echo 'check manually')"
