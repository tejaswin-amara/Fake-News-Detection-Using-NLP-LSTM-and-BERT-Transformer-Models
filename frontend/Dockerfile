# syntax=docker/dockerfile:1
# Stage 1: Dependency base
FROM node:22-alpine AS deps

WORKDIR /app

# Enable corepack and activate pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy dependency manifests
COPY package.json pnpm-lock.yaml ./
COPY patches/ ./patches/

# Install dependencies strictly with frozen lockfile
RUN pnpm install --frozen-lockfile

# Stage 2: Development with hot reloading
FROM deps AS dev
COPY . .
EXPOSE 5173
CMD ["pnpm", "exec", "vite", "--host", "0.0.0.0", "--port", "5173"]

# Stage 3: Build production React 19 SPA
FROM deps AS builder
COPY . .
RUN pnpm exec vite build

# Stage 4: Production Edge Runner with Caddy 2
FROM caddy:2-alpine AS runner
COPY --from=builder /app/dist/public /usr/share/caddy
COPY Caddyfile /etc/caddy/Caddyfile
EXPOSE 80
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
