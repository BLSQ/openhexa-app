#!/bin/bash
# Runs on every container start, after the inner Docker daemon is up.
set -euo pipefail

docker network create openhexa 2>/dev/null || true

sudo /usr/local/bin/init-firewall.sh
