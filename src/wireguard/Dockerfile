FROM ubuntu:noble

# Install WireGuard tools and iproute2
RUN apt-get update && \
    apt-get install -y wireguard iproute2 iputils-ping bash && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY setup_ips.sh .
RUN chmod +x setup_ips.sh

ENTRYPOINT ["/app/setup_ips.sh"]