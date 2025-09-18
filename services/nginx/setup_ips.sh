#!/bin/bash
set -e

# Host interface name
IFACE=eth0

# IPs to temporarily add
IP_LIST=("192.168.8.81/22" "192.168.8.82/22")

# Add IPs
for ip in "${IP_LIST[@]}"; do
    if ! ip addr show "$IFACE" | grep -q "${ip%/*}"; then
        echo "Adding IP $ip to $IFACE"
        ip addr add "$ip" dev "$IFACE"
    else
        echo "IP $ip already exists on $IFACE"
    fi
done

# Function to remove IPs on exit
cleanup() {
    echo "Removing temporary IPs..."
    for ip in "${IP_LIST[@]}"; do
        ip addr del $ip dev $IFACE || true
    done
}
trap cleanup EXIT

# Keep container running (or run your service here)
exec "$@"
