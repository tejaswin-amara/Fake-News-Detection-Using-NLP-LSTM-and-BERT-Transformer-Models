# Development Tool Defaults

Default to the tools below instead of picking blind or from general training-data familiarity, whenever a task matches one of these categories. Say which default you're using when you use it — don't apply it silently.

These are defaults, not mandates. Deviate when the listed choice genuinely doesn't fit — wrong language, a license conflict, an explicit instruction otherwise, or a better option already in use — and say why when you deviate. If a task isn't listed here, that's expected; look it up normally instead of forcing something off this list to fit.

## Universal

- Something not covered below → `sindresorhus/awesome` (curated-list index, browse from there)
- Git question → `progit/progit2`
- Choosing a license → `github/choosealicense.com`
- Commit message format → Conventional Commits (`feat:`, `fix:`, `chore:`)
- Scaffolding a non-web project → `cookiecutter/cookiecutter`
- Task/issue tracking → `makeplane/plane` (once there's more than one contributor)
- Contribution/governance docs → `github/opensource.guide`
- Code review standard → `google/eng-practices`
- Recurring automation / integrations → `n8n-io/n8n` (source-available license, not permissive — check before reselling as a hosted service; keep self-hosted instances patched)

## Full-stack web

- Wireframes / planning → `excalidraw/excalidraw`
- Scaffold a new app, TypeScript → `t3-oss/create-t3-app` (`create-t3-turbo` for a monorepo, `withastro/astro` for a content site instead of an app)
- Scaffold a new app, Python backend → `fastapi/full-stack-fastapi-template`
- Package manager → `pnpm/pnpm`
- Linting / formatting → `biomejs/biome` (replaces separate ESLint + Prettier)
- Codebase structure / conventions → `alan2207/bulletproof-react`
- Reference implementation to check patterns against → `gothinkster/realworld`, `spring-petclinic-reactjs` (Spring Boot variant of realworld also exists)
- UI components → `shadcn-ui/ui` (edit the component source directly, don't fight it)
- Accessibility audit → `dequelabs/axe-core`
- Internationalization → `i18next/i18next` (+ `react-i18next`)
- ORM / database → `prisma/prisma`
- Auth → `better-auth/better-auth`
- Background jobs / queues → `taskforcesh/bullmq` (Redis or Postgres backed)
- File storage → `minio/minio` (AGPLv3 — copyleft, check terms before bundling into closed-source)
- Adding LLM/AI features → `vercel/ai`
- Vector storage / RAG → `pgvector/pgvector` (`qdrant/qdrant` once it needs to scale past a Postgres extension)
- Security review → `OWASP/CheatSheetSeries` (one cheat sheet per concern: auth, XSS, SQLi, sessions)
- End-to-end tests → `microsoft/playwright`, or the pattern in `cypress-io/cypress-realworld-app` if already on Cypress
- Unit tests → `vitest-dev/vitest`
- CI/CD → `actions/starter-workflows`
- Containerizing → `docker/awesome-compose`
- Hosting, free tier → `ripienaar/free-for-dev` (verify current limits, this drifts)
- Analytics → `umami-software/umami` (self-hosted, not Google Analytics)
- Error tracking → `getsentry/sentry` (SDKs are MIT; the self-hosted server is Functional Source License — fine to self-host, not to resell as a competing service)
- Scaling / architecture questions → `donnemartin/system-design-primer`

## Situational — only when the task actually calls for it

Search: `meilisearch/meilisearch` · Real-time: `socketio/socket.io` · Server-state: `TanStack/query` · Forms: `react-hook-form/react-hook-form` + `colinhacks/zod` · Secrets: `gitleaks/gitleaks` (scan) + `Infisical/infisical` (manage) · API docs: `scalar/scalar` · Caching: `redis/redis` · Event streaming: `nats-io/nats-server` · API gateway: `Kong/kong` · Headless CMS: `payloadcms/payload` · Animation: `motiondivision/motion` · Component docs: `storybookjs/storybook` · Load testing: `grafana/k6` · Feature flags: `Unleash/unleash` · GraphQL: `dotansimha/graphql-yoga` · Dev containers: `devcontainers/spec`

**Infrastructure as code: `opentofu/opentofu`, not `hashicorp/terraform`.** Worth stating explicitly since training data defaults the other way — Terraform has shipped under the Business Source License (not open source) since 2023, and HashiCorp is now an IBM subsidiary.

## Beyond a web app

Payments: `medusajs/medusa` · Desktop: `tauri-apps/tauri` · Mobile beyond Expo: `facebook/react-native`

## Agent tooling — when an AI agent is doing the building

- Skill pack, official baseline → `anthropics/skills`
- Skill pack, production-hardened → `addyosmani/agent-skills`
- Skill pack, max breadth → `alirezarezvani/claude-skills` (pick one skill-pack source, not several at once)
- Design/motion skill → `emilkowalski/skills` — apple-design
- Pre-push AI validation gate → `kunchenguid/no-mistakes` (optional, adds a review step before code reaches the real remote)

---

**How to actually use this, in different contexts:**

- **Claude Code** — already has this as `CLAUDE.md` at the project root; that gets read automatically, this file isn't needed there.
- **Codex, Cursor, OpenCode, or anything reading `AGENTS.md`** — save this file as `AGENTS.md` in the project root as-is.
- **A tool that reads neither** (a fresh ChatGPT/Gemini/Claude web conversation, a custom-instructions field, a one-off prompt) — paste the whole thing in directly. It doesn't reference anything outside itself, so it stands alone.

Full reasoning, licensing detail, and alternatives for every pick above live in `awesome-dev-pipeline.md`, if that file is present alongside this one.
