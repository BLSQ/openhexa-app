#
# ----------- Base -----------
FROM node:lts-alpine as base

FROM base as deps
WORKDIR /code
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN --mount=type=cache,target=/var/cache/apk/ \
     apk add libc6-compat python3 make g++

COPY package.json package-lock.json /code/
RUN npm ci --ignore-scripts --no-audit --no-fund

## ----------- Builder -----------
FROM base AS builder
WORKDIR /code

ARG RELEASE
ARG SENTRY_AUTH_TOKEN

ENV SENTRY_RELEASE=${RELEASE}
ENV NEXT_PUBLIC_RELEASE=${RELEASE}
ENV CI=1
ENV NEXT_TELEMETRY_DISABLED 1

COPY --link . /code/
RUN --mount=type=bind,from=deps,source=/code/node_modules,target=/code/node_modules \
    --mount=type=cache,target=/code/.next/cache \
    npm run build

# We do not want to have the cache in the final image
RUN rm -rf /code/.next/cache

#
## ----------- Runner -----------
FROM base AS runner

WORKDIR /code
ARG APP=/code
ENV APP_USER=runner
ENV NEXT_TELEMETRY_DISABLED 1
RUN addgroup -S $APP_USER \
    && adduser -S $APP_USER -G $APP_USER \
    && mkdir -p ${APP}

COPY --from=deps    --chown=${APP_USER}:${APP_USER} /code/node_modules ./node_modules
COPY --from=builder --chown=${APP_USER}:${APP_USER} /code/public ./public
COPY --from=builder --chown=${APP_USER}:${APP_USER} /code/package.json ./package.json
COPY --from=builder --chown=${APP_USER}:${APP_USER} /code/next.config.js ./
COPY --from=builder --chown=${APP_USER}:${APP_USER} /code/next-i18next.config.js ./
COPY --from=builder --chown=${APP_USER}:${APP_USER} /code/.next ./.next
COPY --from=builder --chown=${APP_USER}:${APP_USER} /code/server ./server

USER ${APP_USER}
ENV PORT 3000

CMD [ "npm", "start" ]
