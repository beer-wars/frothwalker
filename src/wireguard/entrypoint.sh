#!/bin/bash
set -e

WG_IFACE="${WG_IFACE:-wg0}"

ln -s /data/wireguard.conf /etc/wireguard/wg0.conf

echo "[+] Starting WireGuard on interface $WG_IFACE"
wg-quick up $WG_IFACE

exec tail -f /dev/null

