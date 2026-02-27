#!/bin/bash
# 假的 mc-image-helper，禁用自动下载

if [[ "$1" == "mcopy" ]]; then
    echo "[INFO] Skipping config download (disabled in AnotherYou image)"
    exit 0
fi

exec /usr/local/bin/mc-image-helper.orig "$@"
