#!/bin/bash
set -e

IP_FILE="/data/gateway_ips.txt"

if [ ! -f "$IP_FILE" ]; then
    echo "Error: $IP_FILE not found"
    exit 1
fi

declare -a ADDED_IPS

while IFS=: read -r iface ip; do
    if ! ip addr show "$iface" | grep -qw "${ip%/*}"; then
        ip addr add "$ip" dev "$iface"
        echo "Added IP $ip to $iface"
        ADDED_IPS+=("$iface:$ip")
    else
        echo "IP $ip already exists on $iface"
    fi
done < "$IP_FILE"

cleanup() {
    echo "Removing temporary IPs..."
    for entry in "${ADDED_IPS[@]}"; do
        iface="${entry%%:*}"
        ip="${entry#*:}"
        ip addr del "$ip" dev "$iface" || true
        echo "Removed IP $ip from $iface"
    done
}
trap cleanup SIGTERM SIGINT

