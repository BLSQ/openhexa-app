FROM mcr.microsoft.com/devcontainers/javascript-node:22-bookworm

ARG TZ
ENV TZ="$TZ"
ENV DEVCONTAINER=true

RUN apt-get update && apt-get install -y --no-install-recommends \
      iptables \
      ipset \
      iproute2 \
      dnsutils \
      aggregate \
      jq \
      less \
      procps \
      sudo \
      zsh \
      fzf \
      man-db \
      unzip \
      gnupg2 \
      python3 \
      python3-venv \
      pipx \
      postgresql-client \
      ca-certificates \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Volume mount points, pre-created so the named volumes inherit node's ownership.
RUN mkdir -p /commandhistory /home/node/.claude \
  && touch /commandhistory/.bash_history \
  && chown -R node:node /commandhistory /home/node/.claude

COPY init-firewall.sh /usr/local/bin/init-firewall.sh
RUN chmod 0755 /usr/local/bin/init-firewall.sh \
  && echo "node ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/node-devcontainer \
  && chmod 0440 /etc/sudoers.d/node-devcontainer

USER node

ENV SHELL=/bin/zsh
ENV PATH="/home/node/.local/bin:${PATH}"
ENV HISTFILE=/commandhistory/.bash_history

RUN pipx install pre-commit

RUN npm install -g @anthropic-ai/claude-code

WORKDIR /workspace
