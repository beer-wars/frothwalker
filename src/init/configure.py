#!/usr/bin/env python3

import yaml
import psutil
import ipaddress


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


def build_peer_gateway_ips(config):
    iface = config["gateway"]["interface"]
    prefixlen = get_interface_subnet(iface)

    cidrs = []
    for peer_name, peer_cfg in config.get("peers", {}).items():
        gw_ip = peer_cfg["gateway_ip"]
        cidr = f"{gw_ip}/{prefixlen}"
        cidrs.append(cidr)

    return cidrs


def main():
    config = load_config()
    gateway_ips = build_peer_gateway_ips(config)

    with open("/data/nginx/gateway_ips.txt", "w") as f:
        for gateway_ip in gateway_ips:
            f.write(f"{config['gateway']['interface']}:{gateway_ip}\n")

    print(f"Wrote {len(gateway_ips)} gateway IPs")


if __name__ == "__main__":
    main()

