#!/bin/bash
# Runs once, at container creation, while the network is still unrestricted.
# Everything that needs to reach a registry belongs here rather than in
# post-start.sh, which runs behind the firewall.
set -euo pipefail

cd /workspace

echo "==> Configuring git for read-only GitHub access"
git config --global --add safe.directory /workspace

# origin is an SSH remote and SSH is blocked by the firewall, so rewrite to
# HTTPS, where the only credential available is the read-only token.
git config --global url."https://github.com/".insteadOf "git@github.com:"
git config --global url."https://github.com/".insteadOf "ssh://git@github.com/"

# Drop any credential helper inherited from the image or injected by the VS Code
# dev containers extension (an empty helper resets the list), then allow only
# GH_TOKEN. Without it, an HTTPS push has no credential to try at all.
git config --global --unset-all credential.helper 2>/dev/null || true
git config --global --add credential.helper ""
if [ -n "${GH_TOKEN:-}" ]; then
    git config --global --add credential.helper \
        '!f() { echo username=x-access-token; echo "password=${GH_TOKEN}"; }; f'
else
    echo "    GH_TOKEN is empty: gh will be unauthenticated (60 requests/hour)."
    echo "    Set a read-only token on the host, see .devcontainer/README.md."
fi

if [ ! -f .env ]; then
    echo "==> No .env found, copying .env.dist (review it: it contains placeholders)"
    cp .env.dist .env
fi

# The app container binds this path and hands it to the pipelines runner as the
# bind path on the Docker host, which here is this container. Creating the same
# path keeps compose self-consistent without editing .env.
STORAGE_DIR=$(sed -n 's/^WORKSPACE_STORAGE_LOCATION=//p' .env | tail -1 | tr -d "\"'")
STORAGE_DIR=${STORAGE_DIR:-/data/openhexa}
echo "==> Creating workspace storage at $STORAGE_DIR"
sudo mkdir -p "$STORAGE_DIR"
sudo chown -R node:node "$STORAGE_DIR"

echo "==> Creating the openhexa docker network"
docker network create openhexa 2>/dev/null || true

echo "==> Pulling and building images (this is the slow part)"
docker compose pull --ignore-buildable || echo "WARNING: some images could not be pulled"
docker compose build

echo "==> Installing frontend dependencies"
# frontend/node_modules is a named volume, so it starts empty and root-owned.
sudo chown node:node frontend/node_modules
(cd frontend && npm ci) || echo "WARNING: npm ci failed, run it manually"

echo "==> Warming the pre-commit hook environments"
pre-commit install-hooks || echo "WARNING: pre-commit hooks not installed"

cat <<'EOF'

Ready.

  1. claude                                   # log in once, the volume keeps it
  2. docker compose up -d                     # start the stack
  3. docker compose run app fixtures          # seed the database

Then, for unattended runs:

  claude --dangerously-skip-permissions

New images cannot be pulled once the firewall is up. Rebuild the container, or
add the registry to ALLOWED_DOMAINS in .devcontainer/init-firewall.sh.
EOF
