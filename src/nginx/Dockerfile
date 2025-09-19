FROM nginx:stable

RUN apt-get update && \
    apt-get install -y net-tools iproute2 iputils-ping bash && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY scripts ./scripts
COPY default.conf /etc/nginx/conf.d/default.conf
RUN chmod +x scripts/*.sh

ENTRYPOINT ["/app/scripts/entrypoint.sh"]

