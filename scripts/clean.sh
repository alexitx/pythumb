#!/usr/bin/env bash

set -e

base_dir="$(readlink -f "$(dirname "$BASH_SOURCE")/../")"
cd "$base_dir"

files=(
    *.egg-info
    "./build/"
    "./dist/"
    "./pyinstaller/"
)

for f in "${files[@]}"; do
    echo "- $f"
    rm -rf "$f"
done

echo "Cleanup finished"
