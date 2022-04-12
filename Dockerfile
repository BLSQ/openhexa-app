#
# ----------- Base -----------
FROM node:17-alpine as deps
WORKDIR /code
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
# copy project file
COPY package.json package.json
COPY package-lock.json package-lock.json
RUN npm set progress=false && \
    npm config set depth 0 && \
    npm ci

## ----------- Builder -----------
FROM node:17-alpine AS builder
WORKDIR /code
COPY . .
COPY --from=deps /code/node_modules ./node_modules

ARG RELEASE
ARG SENTRY_AUTH_TOKEN
ARG SENTRY_DSN
ARG SENTRY_ENVIRONMENT
ARG GRAPHQL_ENDPOINT

ENV SENTRY_RELEASE=${RELEASE}
ENV NEXT_PUBLIC_RELEASE=${RELEASE}
ENV NEXT_PUBLIC_SENTRY_DSN=${SENTRY_DSN}
ENV NEXT_PUBLIC_SENTRY_ENVIRONMENT=${SENTRY_ENVIRONMENT}
ENV NEXT_PUBLIC_GRAPHQL_ENDPOINT=${GRAPHQL_ENDPOINT}

RUN npm run build

#
## ----------- Runner -----------
FROM node:17-alpine AS runner
WORKDIR /code
ARG APP=/code
ENV APP_USER=runner
RUN addgroup -S $APP_USER \
    && adduser -S $APP_USER -G $APP_USER \
    && mkdir -p ${APP}

RUN chown -R $APP_USER:$APP_USER ${APP}

COPY --from=builder /code/package.json ./package.json
COPY --from=builder /code/next.config.js ./
COPY --from=builder /code/next-i18next.config.js ./
COPY --from=builder /code/public ./public
COPY --from=builder /code/.next ./.next
COPY --from=builder /code/node_modules ./node_modules

CMD [ "npm", "start" ]
