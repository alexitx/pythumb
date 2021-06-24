#!/usr/bin/env bash

set -e

base_dir="$(readlink -f "$(dirname "$BASH_SOURCE")/../")"
cd "$base_dir"

build() {
    echo "Starting build process"
    eval "$pyi_cmd"
    echo "Build finished"
}

pyi_cmd_base="pyinstaller --distpath pyi-dist --workpath pyi-build -y --clean"

case "$1" in
    win)
        echo "Selected OS: Windows"
        pyi_cmd="${pyi_cmd_base} build-win.spec"
        build
        ;;
    linux)
        echo "Selected OS: Linux"
        pyi_cmd="${pyi_cmd_base} build-linux.spec"
        build
        ;;
    *)
        echo "Usage:"
        echo "  build.sh <os>"
        echo "Arguments:"
        echo "  os {win, linux}"
        exit 1
        ;;
esac
