FROM node:17-alpine

ARG NEXT_PUBLIC_GRAPHQL_ENDPOINT
ARG NEXT_PUBLIC_SENTRY_DSN
ARG SENTRY_AUTH_TOKEN
ARG SENTRY_RELEASE

RUN mkdir /code
WORKDIR /code

COPY package.json package.json
COPY package-lock.json package-lock.json
RUN npm ci --only=production
COPY . .

# https://nextjs.org/docs/messages/sharp-missing-in-production
RUN npm i sharp

RUN npm run build

CMD [ "npm", "start" ]