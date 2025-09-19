FROM nginx:stable

RUN apt-get update && \
    apt-get install -y net-tools iproute2 iputils-ping bash && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN rm /etc/nginx/conf.d/default.conf \
  && mkdir -p /etc/nginx/stream.d \
  && echo "include /etc/nginx/stream.d/*.conf;" >> /etc/nginx/nginx.conf

COPY scripts ./scripts
RUN chmod +x scripts/*.sh

ENTRYPOINT ["/app/scripts/entrypoint.sh"]

