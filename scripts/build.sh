#!/usr/bin/env bash

set -e

base_dir="$(readlink -f "$(dirname "$BASH_SOURCE")/../")"
cd "$base_dir"
. scripts/config.sh

download_upx_win() {
    echo "Downloading UPX for Windows"
    mkdir -p ./upx/
    tmp="$(mktemp -d)"
    curl -LJSso $tmp/upx.zip "$upx_url_win"
    unzip -od ./upx/ $tmp/upx.zip
    rm -rf $tmp
}

download_upx_linux() {
    echo "Downloading UPX for Linux"
    mkdir -p ./upx/
    curl -LSs "$upx_url_linux" | tar -xJf - -C ./upx/
}

build() {
    echo "Starting build process"
    eval "$pyi_cmd"
    echo "Build finished"
}

pyi_cmd_base="pyinstaller --distpath ./pyinstaller/dist --workpath ./pyinstaller/build --clean"
pyi_cmd="$pyi_cmd_base"

case "$1" in
    win)
        echo "Selected OS: Windows"
        if [ -z "$(command -v upx.exe)" ]; then
            if [ ! -f ./upx/$upx_name_win/upx.exe ]; then
                download_upx_win
            fi
            pyi_cmd="${pyi_cmd} --upx-dir ./upx/$upx_name_win"
        fi
        pyi_cmd="${pyi_cmd} ${spec_win}"
        build
        ;;
    linux)
        echo "Selected OS: Linux"
        if [ -z "$(command -v upx)" ]; then
            if [ ! -f ./upx/$upx_name_linux/upx ]; then
                download_upx_linux
            fi
            pyi_cmd="${pyi_cmd} --upx-dir ./upx/$upx_name_linux"
        fi
        pyi_cmd="${pyi_cmd} ${spec_linux}"
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
