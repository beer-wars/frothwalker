#!/usr/bin/env python3

import yaml
import psutil
import ipaddress
from pathlib import Path


def load_config(path="/data/config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_interface_subnet(interface):
    addrs = psutil.net_if_addrs().get(interface, [])
    for addr in addrs:
        if addr.family == 2:
            ip = ipaddress.ip_interface(f"{addr.address}/{addr.netmask}")
            print(f"Found {interface}: {addr.address}/{addr.netmask}")
            print(f"{interface} prefix length is {ip.network.prefixlen}")
            return ip.network.prefixlen
    raise RuntimeError(f"Could not determine subnet for interface {interface}")


def generate_gateway_ips(config):
    iface = config["gateway"]["interface"]
    prefixlen = get_interface_subnet(iface)

    gateway_ips = []
    for peer_name, peer_cfg in config.get("peers", {}).items():
        gw_ip = peer_cfg["gateway"]["ip"]
        gateway_ip = f"{gw_ip}/{prefixlen}"
        gateway_ips.append(gateway_ip)

    with open("/data/nginx/gateway_ips.txt", "w") as f:
        for gateway_ip in gateway_ips:
            f.write(f"{config['gateway']['interface']}:{gateway_ip}\n")

    print(f"Wrote {len(gateway_ips)} gateway IPs")


def generate_gateway_nginx_conf(config):
    conf_blocks = ["stream {"]
    for peer_name, peer in config.get("peers", {}).items():
        tunnel_ip = peer["tunnel"]["ip"]
        gateway_ip = peer["gateway"]["ip"]
        ports = peer["gateway"].get("ports", [80, 443])

        listen_lines = "\n    ".join(f"listen {gateway_ip}:{port};" for port in ports)

        for port in ports:
            block = f"""
server {{
    listen {gateway_ip}:{port};
    proxy_pass {tunnel_ip}:{port};
}}"""
            conf_blocks.append(block.strip())

    conf_blocks.append("}\n")
    conf_text = "\n\n".join(conf_blocks)
    output_path = Path("/data/nginx/nginx/gateway.conf")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(conf_text)


def generate_proxy_nginx_conf(config):
    http_blocks = []
    stream_blocks = []

    for name, svc in config.get("services", {}).items():
        source = svc["source"]
        dest = svc["dest"]

        listen_port = source["port"]
        forward_port = dest["port"] if port in dest else source["port"]

        listen_domain = source.get("domain")
        forward_domain = dest["domain"] if domain in dest else source["domain"]

        # http services
        if listen_domain:
            tls_block = ""
            tls = source.get("tls")
            if tls:
                tls_block = f"""
    ssl_certificate {tls['crt']};
    ssl_certificate_key {tls['key']};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
"""

            block = f"""
server {{
    listen {listen_port}{' ssl' if tls else ''};
    server_name {listen_domain};

    {tls_block.strip() if tls else ''}

    location / {{
        proxy_pass http://{dest['domain']}:{forward_port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
            http_blocks.append(block.strip())

        # tcp services
        else:
            block = f"""
server {{
    listen {listen_port};
    proxy_pass {dest['domain']}:{forward_port};
}}
"""
            stream_blocks.append(block.strip())

    if http_blocks:
        http_conf = "\n\n".join(http_blocks)
        http_path = Path("/data/nginx/nginx/proxies-http.conf")
        http_path.parent.mkdir(parents=True, exist_ok=True)
        http_path.write_text(http_conf)

    if stream_blocks:
        stream_conf = "stream {\n" + "\n\n".join(stream_blocks) + "\n}"
        stream_path = Path("/data/nginx/nginx/proxy-streams.conf")
        stream_path.parent.mkdir(parents=True, exist_ok=True)
        stream_path.write_text(stream_conf)


def main():
    config = load_config()
    generate_gateway_ips(config)
    generate_gateway_nginx_conf(config)
    generate_proxy_nginx_conf(config)


if __name__ == "__main__":
    main()

