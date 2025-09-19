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
        gw_ip = peer_cfg["gateway_ip"]
        gateway_ip = f"{gw_ip}/{prefixlen}"
        gateway_ips.append(gateway_ip)

    with open("/data/nginx/gateway_ips.txt", "w") as f:
        for gateway_ip in gateway_ips:
            f.write(f"{config['gateway']['interface']}:{gateway_ip}\n")

    print(f"Wrote {len(gateway_ips)} gateway IPs")


def generate_gateway_nginx_conf(config):
    conf_blocks = ["stream {"]
    for peer_name, peer in config.get("peers", {}).items():
        gateway_ip = peer["gateway_ip"]
        tunnel_ip = peer["tunnel_ip"]
        ports = peer.get("ports", [80, 443])

        listen_lines = "\n    ".join(f"listen {gateway_ip}:{port};" for port in ports)

        for port in ports:
            block = f"""
server {{
    listen {gateway_ip}:{port};
    proxy_pass {tunnel_ip}:{port};
}}"""
            conf_blocks.append(block.strip())

    conf_blocks.append("}")
    conf_text = "\n\n".join(conf_blocks)
    output_path = Path("/data/nginx/nginx/gateway.conf")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(conf_text)


def main():
    config = load_config()
    generate_gateway_ips(config)
    generate_gateway_nginx_conf(config)


if __name__ == "__main__":
    main()

