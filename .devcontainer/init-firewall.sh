#!/bin/bash
# Default-deny egress for the devcontainer *and* for every container started by
# the inner Docker daemon. Re-run on every container start: iptables state is
# not preserved across restarts.
set -euo pipefail
IFS=$'\n\t'

if [ "$(id -u)" -ne 0 ]; then
    echo "init-firewall.sh must run as root (use sudo)" >&2
    exit 1
fi

CHAIN="CLAUDE-EGRESS"
SET="claude-allowed"

# Destinations reachable by hostname. Anything not listed here is rejected, so
# adding a dependency to the project usually means adding a line below.
ALLOWED_DOMAINS=(
    # Claude Code
    "api.anthropic.com"
    "console.anthropic.com"
    "claude.ai"
    "statsig.com"
    "sentry.io"
    # Package registries
    "registry.npmjs.org"
    "pypi.org"
    "files.pythonhosted.org"
    "deb.debian.org"
    "security.debian.org"
    # Container registries for the images in docker-compose.yaml
    "registry-1.docker.io"
    "index.docker.io"
    "auth.docker.io"
    "production.cloudflare.docker.com"
    "codeberg.org"
    "mcr.microsoft.com"
    "ghcr.io"
    "pkg-containers.githubusercontent.com"
)

# Private ranges the inner containers live on. Docker's default address pool
# (172.17-172.31) sits inside 172.16/12; the host LAN stays unreachable.
readonly PRIVATE_NETS=("127.0.0.0/8" "172.16.0.0/12")

echo "==> Tearing down previous rules"
# Detach before destroying, otherwise the ipset is still referenced.
while iptables -C OUTPUT -j "$CHAIN" 2>/dev/null; do iptables -D OUTPUT -j "$CHAIN"; done
while iptables -C DOCKER-USER -j "$CHAIN" 2>/dev/null; do iptables -D DOCKER-USER -j "$CHAIN"; done
if iptables -L "$CHAIN" -n >/dev/null 2>&1; then
    iptables -F "$CHAIN"
    iptables -X "$CHAIN"
fi
ipset destroy "$SET" 2>/dev/null || true

echo "==> Building allowlist"
ipset create "$SET" hash:net

# GitHub publishes its ranges; resolving github.com alone is not enough.
gh_ranges=$(curl -s --max-time 20 https://api.github.com/meta)
if ! echo "$gh_ranges" | jq -e '.web and .api and .git' >/dev/null 2>&1; then
    echo "ERROR: could not fetch GitHub IP ranges" >&2
    exit 1
fi
while read -r cidr; do
    [[ "$cidr" =~ ^[0-9.]+/[0-9]{1,2}$ ]] || continue
    ipset add "$SET" "$cidr" -exist
done < <(echo "$gh_ranges" | jq -r '(.web + .api + .git)[]' | aggregate -q)

for domain in "${ALLOWED_DOMAINS[@]}"; do
    ips=$(dig +short A "$domain" | grep -E '^[0-9.]+$' || true)
    if [ -z "$ips" ]; then
        echo "WARNING: could not resolve $domain, skipping" >&2
        continue
    fi
    while read -r ip; do
        ipset add "$SET" "$ip" -exist
    done <<< "$ips"
done

echo "==> Installing rules"
iptables -N "$CHAIN"
iptables -A "$CHAIN" -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A "$CHAIN" -o lo -j ACCEPT
iptables -A "$CHAIN" -p udp --dport 53 -j ACCEPT
iptables -A "$CHAIN" -p tcp --dport 53 -j ACCEPT
# No SSH to anywhere. This is what stops `git push` over git@github.com, and it
# comes before the allowlist so it covers GitHub too.
iptables -A "$CHAIN" -p tcp --dport 22 -j REJECT --reject-with tcp-reset
for net in "${PRIVATE_NETS[@]}"; do
    iptables -A "$CHAIN" -d "$net" -j ACCEPT
done
# Allowlisted hosts on HTTP/HTTPS only. Port 80 is needed because Debian's apt
# sources are plain http.
iptables -A "$CHAIN" -p tcp -m multiport --dports 80,443 -m set --match-set "$SET" dst -j ACCEPT
iptables -A "$CHAIN" -j REJECT --reject-with icmp-port-unreachable

# Traffic originating in this container.
iptables -I OUTPUT 1 -j "$CHAIN"

# Traffic routed out of the inner containers. DOCKER-USER is the chain Docker
# reserves for user rules and never rewrites.
iptables -N DOCKER-USER 2>/dev/null || true
iptables -C FORWARD -j DOCKER-USER 2>/dev/null || iptables -I FORWARD 1 -j DOCKER-USER
iptables -I DOCKER-USER 1 -j "$CHAIN"

# No IPv6 allowlist is maintained, so close IPv6 rather than leave a bypass.
if command -v ip6tables >/dev/null 2>&1; then
    ip6tables -F OUTPUT 2>/dev/null || true
    ip6tables -A OUTPUT -o lo -j ACCEPT 2>/dev/null || true
    ip6tables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true
    ip6tables -A OUTPUT -j REJECT 2>/dev/null || true
fi

echo "==> Verifying"
if curl -s --max-time 5 https://example.com >/dev/null 2>&1; then
    echo "ERROR: example.com is reachable, the allowlist is not being enforced" >&2
    exit 1
fi
if ! curl -s --max-time 15 https://api.github.com/zen >/dev/null 2>&1; then
    echo "ERROR: api.github.com is unreachable, the allowlist is too strict" >&2
    exit 1
fi
if timeout 5 bash -c 'exec 3<>/dev/tcp/github.com/22' 2>/dev/null; then
    echo "ERROR: ssh to github.com is reachable, pushes over SSH are not blocked" >&2
    exit 1
fi
echo "Firewall active: $(ipset list "$SET" | grep -c '^[0-9]') entries allowed."
