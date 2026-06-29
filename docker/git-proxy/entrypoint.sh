#!/bin/sh
# Renders the git-proxy nginx config, then starts nginx.
#
# nginx can't base64-encode, so we build the Forgejo admin Basic-auth value here
# and substitute it (plus the upstreams) into the config template.
set -e

export FORGEJO_ADMIN_AUTH="$(printf '%s:%s' "$GIT_SERVER_ADMIN_USERNAME" "$GIT_SERVER_ADMIN_PASSWORD" | base64 | tr -d '\n')"

envsubst '$APP_UPSTREAM $FORGEJO_UPSTREAM $FORGEJO_ADMIN_AUTH' \
    < /etc/nginx/templates/git-proxy.conf.template \
    > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
