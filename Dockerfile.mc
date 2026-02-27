# AnotherYou Minecraft Server
# 基于 itzg/minecraft-server，但禁用自动配置下载

FROM itzg/minecraft-server:java21

# 设置环境变量
ENV EULA=TRUE
ENV TYPE=PAPER
ENV VERSION=1.20.4
ENV SKIP_GENERIC_PACK_UPDATE_CHECK=true
ENV DISABLE_HEALTHCHECK=true

# 备份原始的 mc-image-helper
RUN mv /usr/local/bin/mc-image-helper /usr/local/bin/mc-image-helper.orig

# 创建替换脚本，跳过下载操作
RUN echo '#!/bin/bash' > /usr/local/bin/mc-image-helper && \
    echo '# 假的 mc-image-helper，禁用自动下载' >> /usr/local/bin/mc-image-helper && \
    echo '' >> /usr/local/bin/mc-image-helper && \
    echo 'if [[ "$1" == "mcopy" ]]; then' >> /usr/local/bin/mc-image-helper && \
    echo '    echo "[INFO] Skipping config download (disabled in AnotherYou image)"' >> /usr/local/bin/mc-image-helper && \
    echo '    exit 0' >> /usr/local/bin/mc-image-helper && \
    echo 'fi' >> /usr/local/bin/mc-image-helper && \
    echo '' >> /usr/local/bin/mc-image-helper && \
    echo 'exec /usr/local/bin/mc-image-helper.orig "$@"' >> /usr/local/bin/mc-image-helper && \
    chmod +x /usr/local/bin/mc-image-helper

# 预下载 Paper 服务器到镜像中（避免运行时下载）
RUN mkdir -p /data && \
    curl -L -o /data/paper.jar \
    "https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/499/downloads/paper-1.20.4-499.jar"

# 暴露端口
EXPOSE 25565

# 启动命令
ENTRYPOINT ["/start"]
