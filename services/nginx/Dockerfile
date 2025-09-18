FROM nginx:stable

# Install iproute2 for IP manipulation
RUN apt-get update && \
    apt-get install -y iproute2 iputils-ping bash && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY setup_ips.sh .
COPY default.conf /etc/nginx/conf.d/default.conf
RUN chmod +x setup_ips.sh

ENTRYPOINT ["/app/setup_ips.sh"]

