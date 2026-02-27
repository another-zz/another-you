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

# 复制自定义脚本
COPY mc-helper.sh /usr/local/bin/mc-image-helper
RUN chmod +x /usr/local/bin/mc-image-helper

# 预下载 Paper 服务器到镜像中（避免运行时下载）
RUN mkdir -p /data && \
    curl -L -o /data/paper.jar \
    "https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/499/downloads/paper-1.20.4-499.jar"

# 暴露端口
EXPOSE 25565

# 启动命令
ENTRYPOINT ["/start"]
