#!/bin/sh
set -e

# Run the default Gitea entrypoint setup (directory creation, user mapping, etc.)
if [ "${USER}" != "git" ]; then
    sed -i -e "s/^git\:/${USER}\:/g" /etc/passwd
fi

for FOLDER in /data/gitea/conf /data/gitea/log /data/git /data/ssh; do
    mkdir -p ${FOLDER}
done

# Start Gitea in the background, wait for it to be ready, then create admin user
/bin/s6-svscan /etc/s6 &
S6_PID=$!

if [ -n "${GITEA_ADMIN_USER}" ]; then
    echo "Waiting for Gitea to start..."
    for i in $(seq 1 30); do
        if su-exec git gitea admin user list > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done

    # Create admin user if it doesn't already exist
    if ! su-exec git gitea admin user list 2>/dev/null | grep -q "${GITEA_ADMIN_USER}"; then
        echo "Creating Gitea admin user '${GITEA_ADMIN_USER}'..."
        su-exec git gitea admin user create \
            --username "${GITEA_ADMIN_USER}" \
            --password "${GITEA_ADMIN_PASSWORD}" \
            --email "${GITEA_ADMIN_EMAIL:-admin@openhexa.local}" \
            --admin \
            --must-change-password=false || true
    else
        echo "Gitea admin user '${GITEA_ADMIN_USER}' already exists."
    fi
fi

wait $S6_PID
