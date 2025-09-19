#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sleep 2

$SCRIPT_DIR/add_gateway_ips.sh
$SCRIPT_DIR/build_nginx_config.sh

ln -s /data/nginx/gateway.conf /etc/nginx/stream.d/gateway.conf

cat /etc/nginx/stream.d/gateway.conf

nginx -g "daemon off;"

