#!/bin/bash
set -e

ADMIN_USERNAME="${GIT_SERVER_ADMIN_USERNAME:-openhexa-admin}"
ADMIN_PASSWORD="${GIT_SERVER_ADMIN_PASSWORD:-openhexa}"
ADMIN_EMAIL="${GIT_SERVER_ADMIN_EMAIL:-admin@openhexa.org}"

mkdir -p /data/gitea/conf

cat > /data/gitea/conf/app.ini <<EOF
[server]
ROOT_URL = http://localhost:3000
[service]
DISABLE_REGISTRATION = true
EOF

/usr/bin/entrypoint &
FORGEJO_PID=$!

echo "Waiting for Forgejo to become ready..."
for i in $(seq 1 60); do
    if curl -sf http://localhost:3000/api/v1/version > /dev/null 2>&1; then
        echo "Forgejo is ready."
        break
    fi
    if [ "$i" -eq 60 ]; then
        echo "Forgejo did not become ready in time."
        exit 1
    fi
    sleep 1
done

if ! forgejo admin user list --admin 2>/dev/null | grep -q "$ADMIN_USERNAME"; then
    echo "Creating admin user: $ADMIN_USERNAME"
    forgejo admin user create \
        --admin \
        --username "$ADMIN_USERNAME" \
        --password "$ADMIN_PASSWORD" \
        --email "$ADMIN_EMAIL" \
        --must-change-password=false
else
    echo "Admin user '$ADMIN_USERNAME' already exists."
fi

wait $FORGEJO_PID
