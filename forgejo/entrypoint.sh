#!/bin/bash
set -e

/usr/bin/entrypoint &
FORGEJO_PID=$!

echo "Waiting for Forgejo to be ready..."
until curl -sf http://localhost:3000/api/v1/version > /dev/null 2>&1; do
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
