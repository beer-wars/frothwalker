FROM ubuntu:noble

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wireguard \
        iproute2 \
        iptables \
        iputils-ping \
        bash && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/wireguard

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 51820/udp

CMD ["/entrypoint.sh"]

