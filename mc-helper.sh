#!/bin/bash
# 假的 mc-image-helper，禁用自动下载

# 无论什么命令，如果是下载配置的，都跳过
if [[ "$1" == "mcopy" ]] || [[ "$1" == "sync" ]] || [[ "$1" == "get" ]]; then
    echo "[INFO] Skipping download: $1 (disabled in AnotherYou image)"
    exit 0
fi

# 其他命令调用原始程序
exec /usr/local/bin/mc-image-helper.orig "$@"
