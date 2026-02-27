# AnotherYou Minecraft Server
# 基于 itzg/minecraft-server，但禁用自动配置下载

FROM itzg/minecraft-server:java21

# 设置环境变量
ENV EULA=TRUE
ENV TYPE=PAPER
ENV VERSION=1.20.4
ENV SKIP_GENERIC_PACK_UPDATE_CHECK=true
ENV DISABLE_HEALTHCHECK=true

# 创建假的 mc-image-helper 脚本，禁用自动下载
RUN mv /usr/local/bin/mc-image-helper /usr/local/bin/mc-image-helper.orig

# 创建替换脚本，跳过下载操作
RUN cat > /usr/local/bin/mc-image-helper << 'EOF'
#!/bin/bash
# 假的 mc-image-helper，禁用自动下载

# 检查是否是 mcopy 命令（下载配置文件的命令）
if [[ "$1" == "mcopy" ]]; then
    echo "[INFO] Skipping config download (disabled in AnotherYou image)"
    exit 0
fi

# 其他命令调用原始程序
exec /usr/local/bin/mc-image-helper.orig "$@"
EOF

RUN chmod +x /usr/local/bin/mc-image-helper

# 预下载 Paper 服务器到镜像中（避免运行时下载）
RUN mkdir -p /data && \
    curl -L -o /data/paper.jar \
    "https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/499/downloads/paper-1.20.4-499.jar"

# 暴露端口
EXPOSE 25565

# 启动命令
ENTRYPOINT ["/start"]
