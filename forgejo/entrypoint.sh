#!/bin/bash
set -e

/usr/bin/entrypoint &
FORGEJO_PID=$!

echo "Waiting for Forgejo to be ready..."
until curl -so /dev/null -w '%{http_code}' http://localhost:3000/api/v1/version 2>/dev/null | grep -qE '200|403'; do
    sleep 1
done
echo "Forgejo is ready."

if ! su-exec git forgejo admin user list --admin 2>/dev/null | grep -q "$GIT_SERVER_ADMIN_USERNAME"; then
    echo "Creating admin user '$GIT_SERVER_ADMIN_USERNAME'..."
    su-exec git forgejo admin user create \
        --admin \
        --username "$GIT_SERVER_ADMIN_USERNAME" \
        --password "$GIT_SERVER_ADMIN_PASSWORD" \
        --email "admin@openhexa.org" \
        --must-change-password=false
    echo "Admin user created."
else
    echo "Admin user '$GIT_SERVER_ADMIN_USERNAME' already exists."
fi

wait $FORGEJO_PID
