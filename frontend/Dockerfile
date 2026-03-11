# syntax=docker/dockerfile:1

FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . ./

# Bake a placeholder into the JS bundle so docker-entrypoint.sh can swap it at
# runtime with the real NEXT_PUBLIC_API_URL value via sed.
ARG NEXT_PUBLIC_API_URL=__NEXT_PUBLIC_API_URL__
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ARG NEXT_PUBLIC_AUTH_MODE
ENV NEXT_PUBLIC_AUTH_MODE=${NEXT_PUBLIC_AUTH_MODE}

RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ARG NEXT_PUBLIC_AUTH_MODE

# If provided at runtime, Next will expose NEXT_PUBLIC_* to the browser as well
# (but note some values may be baked at build time).
ENV NEXT_PUBLIC_API_URL=auto
ENV NEXT_PUBLIC_AUTH_MODE=${NEXT_PUBLIC_AUTH_MODE}

# Create non-root user before COPY so --chown can reference it.
# Using COPY --chown avoids a slow recursive chown on overlay2 (docker/for-linux#388).
RUN addgroup -S appgroup && adduser -S -G appgroup appuser \
  && chown appuser:appgroup /app

# Standalone output: Next.js bundles server + minimal node_modules into .next/standalone.
COPY --from=builder --chown=appuser:appgroup /app/.next/standalone ./
# Static assets and pre-rendered pages are not included in standalone output.
COPY --from=builder --chown=appuser:appgroup /app/.next/static ./.next/static
# `public/` is optional in Next.js apps; repo may not have it.
# Copy it when present so static files (favicon, images) are served correctly.
COPY --from=builder --chown=appuser:appgroup /app/package.json ./package.json
COPY --chown=appuser:appgroup docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh

USER appuser

EXPOSE 3000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD []
