#!/bin/sh
# Renders the git-proxy nginx config, then starts nginx.
#
# nginx can't base64-encode, so we build the Forgejo Basic-auth value for the
# non-admin proxy service account here and substitute it (plus the upstreams)
# into the config template.
set -e

export FORGEJO_PROXY_AUTH="$(printf '%s:%s' "$GIT_PROXY_USERNAME" "$GIT_PROXY_PASSWORD" | base64 | tr -d '\n')"

envsubst '$APP_UPSTREAM $FORGEJO_UPSTREAM $FORGEJO_PROXY_AUTH' \
    < /etc/nginx/templates/git-proxy.conf.template \
    > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
