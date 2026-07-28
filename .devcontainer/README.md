# Claude Code devcontainer

An environment for running Claude Code unattended (`--dangerously-skip-permissions`)
against this repository without giving it your host machine.

## Getting started

1. Export `OPENHEXA_RO_GH_TOKEN` on the host first (see *Read-only GitHub*), then
   open the repo in VS Code → **Dev Containers: Reopen in Container**
   (or `devcontainer up --workspace-folder .` with the CLI).
   First build takes a while: it builds the whole compose stack inside the container.
2. Run `claude` once and log in. The credentials live in a named volume and
   survive rebuilds.
3. `docker compose up -d && docker compose run app fixtures`.
4. From then on, `claude --dangerously-skip-permissions`.

## How the isolation works

**Filesystem.** Only the repository is mounted, at `/workspace`. Your home
directory, SSH keys, other repos and the host Docker socket are not present.

**Docker.** The compose stack runs on a Docker daemon *inside* the container
(docker-in-docker). Because that daemon shares the container's filesystem, every
relative bind mount in `docker-compose.yaml` (`./docs`, `./.env`, the forgejo
entrypoint) resolves correctly with no `LOCAL_WORKSPACE_FOLDER` juggling — and
`app:8000`, `db:5432` are reachable by service name. `/var/lib/docker` is a named
volume, so images and `pgdata` survive container rebuilds.

**Network.** `init-firewall.sh` installs a default-deny egress allowlist covering
both this container and every container the inner daemon starts (via
`DOCKER-USER`). It runs on every container *start*, since iptables state is lost
on restart; `post-create.sh` runs once *before* it, which is why image pulls and
builds happen there.

## Read-only GitHub

The goal is that Claude can look up a PR but cannot open one, comment, or push a
branch. Three layers, only the first of which is a real boundary:

1. **The token.** `BLSQ/openhexa-app` is public, so a **classic PAT with no
   scopes ticked** can read public repository data and nothing else — writes are
   refused by GitHub itself, not by anything on this machine. It also lifts the
   API rate limit from 60 to 5000 requests/hour. Create one at
   <https://github.com/settings/tokens> (*Generate new token (classic)*, select
   **no** scopes), then on the host:

   ```sh
   export OPENHEXA_RO_GH_TOKEN=ghp_xxx   # in your shell profile
   ```

   `devcontainer.json` passes it in as `GH_TOKEN`. For a private repo a
   scopeless classic token is not enough — use a fine-grained token restricted
   to that repository with *Contents: read* and *Pull requests: read*. Note that
   the owning org must have fine-grained tokens enabled.

2. **No SSH.** The firewall rejects outbound tcp/22 to everything, so
   `git push git@github.com:...` cannot connect. `SSH_AUTH_SOCK` is blanked so
   the host's forwarded ssh-agent is unreachable even if the extension forwards
   it, and no key is mounted.

3. **No other credential.** `post-create.sh` clears every inherited git
   credential helper and installs one that returns `GH_TOKEN` and nothing else,
   with `GIT_TERMINAL_PROMPT=0` so an HTTPS push fails immediately rather than
   prompting. The SSH `origin` is rewritten to HTTPS so fetches still work.

So `gh pr view`, `gh pr list`, `gh api`, `git fetch` and `git pull` work;
`gh pr create`, `gh issue comment` and `git push` fail — the first two with a
403 from GitHub, the last with a 403 or no usable credential.

Layers 2 and 3 are local and could in principle be undone from inside the
container. **Layer 1 cannot**, which is why the token matters most: do not paste
a full-access token into the container, and do not run `gh auth login` there.

## Browser automation

The Playwright MCP server is installed in the image and registered for Claude at
user scope, so it is available in every session without further setup. Check it
with `claude mcp get playwright`.

It runs `--headless` (there is no display) and `--isolated` (the browser profile
is kept in memory). Chromium keeps its own sandbox — the privileged container
does not need `--no-sandbox`.

What it can reach is what the firewall allows: `127.0.0.0/8` and `172.16/12` are
accepted, so `http://localhost:3000` (frontend) and `http://localhost:8000`
(backend) work once `docker compose up -d` has published them. The wider web
does not, beyond the allowlist. This is for driving the local stack, not for
browsing.

Chromium is downloaded during the image build, since `cdn.playwright.dev` is not
allowlisted and nothing can be fetched at runtime. That is also why
`PLAYWRIGHT_MCP_VERSION` is pinned in the `Dockerfile` and the server is started
from the globally installed `playwright-mcp` binary rather than
`npx @playwright/mcp@latest`: a floating version eventually wants a browser build
that is not on disk, and then it cannot download it. To upgrade, bump the build
arg and rebuild the container.

## What this does not protect against

- **`privileged: true` is not a hard security boundary.** Docker-in-docker
  requires it, and a privileged container can reach host devices. This setup
  reliably prevents *accidents* — a bad `rm -rf`, an overwritten config, a
  runaway migration — not a deliberate exploit. It is strictly better than
  mounting the host Docker socket, which is plainly root-equivalent.
- **Allowlisting by DNS is approximate.** Registries behind CDNs rotate IPs, so
  a pull that worked yesterday may fail today. Re-running
  `sudo /usr/local/bin/init-firewall.sh` re-resolves everything.
- **`.env` is mounted.** `SECRET_KEY`, `ENCRYPTION_KEY` and the JWT private key
  are readable inside. The firewall and the read-only token together close the
  obvious exfiltration routes — there is no allowlisted host that accepts a
  write — but they do not hide the secrets from the agent.

## Adding a dependency

New host to reach → add it to `ALLOWED_DOMAINS` in `init-firewall.sh` and re-run
the script. New image to pull → same, or rebuild the container so the pull
happens in `post-create.sh` while the network is still open.

## Lighter alternative

Claude Code's built-in sandbox (`/sandbox`) already confines writes and network
on the host, with none of this setup. Reach for this devcontainer when you want
unattended runs with permission prompts off.
