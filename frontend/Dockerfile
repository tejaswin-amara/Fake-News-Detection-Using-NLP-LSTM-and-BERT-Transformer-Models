FROM node:22-alpine

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml ./
COPY patches ./patches
RUN pnpm install --frozen-lockfile=false

COPY . .

ENV NODE_ENV=development
ENV PORT=3000
ENV LOCAL_DEMO_MODE=true
ENV FAKE_NEWS_INTEGRATION_MODE=live
ENV FAKE_NEWS_API_BASE_URL=http://ml-api:8000

EXPOSE 3000

CMD ["pnpm", "dev"]
