# Tool & Library Defaults

This project defaults to a pre-vetted set of tools instead of picking blind or from general training-data familiarity. When a task below comes up and no existing project convention already covers it, use the listed choice and say so ("using X per project defaults") so it's visible in the diff, not silent.

These are defaults, not mandates. Deviate when the listed choice doesn't fit — wrong language, a license conflict, an explicit instruction, or a better option already ships with the framework in use — and say why when you deviate. If a task isn't listed here at all, that's expected; look it up normally instead of forcing something off this list to fit.

This is an extract of the "Quick Reference" section of `awesome-dev-pipeline.md` — that file is the single source of truth (the full list, reasoning, and caveats behind every pick below); this file exists only because Claude Code specifically auto-loads something named `CLAUDE.md`. If the two ever disagree after an edit, the other file is the one that's current.

## Universal

| Task | Default | Note |
|---|---|---|
| Something not covered below | `sindresorhus/awesome` | curated-list index, browse from there |
| Git question | `progit/progit2` | |
| Choosing a license | `github/choosealicense.com` | |
| Commit message format | Conventional Commits (`feat:`, `fix:`, `chore:`) | enables changelog/version automation |
| Scaffolding a non-web project | `cookiecutter/cookiecutter` | |
| Task/issue tracking | `makeplane/plane` | once there's more than one contributor |
| Contribution/governance docs | `github/opensource.guide` | |
| Code review standard | `google/eng-practices` | |
| Recurring automation / integrations | `n8n-io/n8n` | source-available license, not permissive — check before reselling as a hosted service; keep self-hosted instances patched |

## Full-stack web

| Task | Default | Note |
|---|---|---|
| Wireframes / planning | `excalidraw/excalidraw` | |
| Scaffold a new app (TypeScript) | `t3-oss/create-t3-app` | `create-t3-turbo` for a monorepo, `withastro/astro` for a content site instead of an app |
| Scaffold a new app (Python backend) | `fastapi/full-stack-fastapi-template` | |
| Package manager | `pnpm/pnpm` | |
| Linting / formatting | `biomejs/biome` | replaces separate ESLint + Prettier setup |
| Codebase structure / conventions | `alan2207/bulletproof-react` | |
| Reference implementation to check patterns against | `gothinkster/realworld`, `spring-petclinic-reactjs` | Spring Boot variant of realworld also exists |
| UI components | `shadcn-ui/ui` | edit the component source directly, don't fight it |
| Accessibility audit | `dequelabs/axe-core` | |
| Internationalization | `i18next/i18next` (+ `react-i18next`) | |
| ORM / database | `prisma/prisma` | |
| Auth | `better-auth/better-auth` | |
| Background jobs / queues | `taskforcesh/bullmq` | Redis or Postgres backed |
| File storage | `minio/minio` | AGPLv3 — copyleft, check terms before bundling into closed-source |
| Adding LLM/AI features | `vercel/ai` | |
| Vector storage / RAG | `pgvector/pgvector` | `qdrant/qdrant` once it needs to scale past a Postgres extension |
| Security review | `OWASP/CheatSheetSeries` | one cheat sheet per concern (auth, XSS, SQLi, sessions) |
| End-to-end tests | `microsoft/playwright` | or `cypress-io/cypress-realworld-app` pattern if already on Cypress |
| Unit tests | `vitest-dev/vitest` | |
| CI/CD | `actions/starter-workflows` | |
| Containerizing | `docker/awesome-compose` | |
| Hosting (free tier) | `ripienaar/free-for-dev` | verify current limits, this drifts |
| Analytics | `umami-software/umami` | self-hosted, not Google Analytics |
| Error tracking | `getsentry/sentry` | SDKs are MIT; the self-hosted server is Functional Source License (fine to self-host, can't resell as a competing service) |
| Scaling / architecture questions | `donnemartin/system-design-primer` | |

## Agent tooling — when an agent is doing the building

| Task | Default | Note |
|---|---|---|
| Skill pack (baseline) | `anthropics/skills` | official, conservative |
| Skill pack (production-hardened) | `addyosmani/agent-skills` | fewer skills, more rigor |
| Skill pack (max breadth) | `alirezarezvani/claude-skills` | pick one skill-pack source, not several at once |
| Design/motion skill | `emilkowalski/skills` — apple-design | |
| Pre-push AI validation gate | `kunchenguid/no-mistakes` | optional, adds a review step before code reaches the real remote |

## Situational — only when the task actually calls for it

Search: `meilisearch/meilisearch` · Real-time: `socketio/socket.io` · Server-state: `TanStack/query` · Forms: `react-hook-form/react-hook-form` + `colinhacks/zod` · Secrets: `gitleaks/gitleaks` (scan) + `Infisical/infisical` (manage) · API docs: `scalar/scalar` · Caching: `redis/redis` · Event streaming: `nats-io/nats-server` · API gateway: `Kong/kong` · Headless CMS: `payloadcms/payload` · Animation: `motiondivision/motion` · Component docs: `storybookjs/storybook` · Load testing: `grafana/k6` · Feature flags: `Unleash/unleash` · GraphQL: `dotansimha/graphql-yoga` · Dev containers: `devcontainers/spec`

**Infrastructure as code: `opentofu/opentofu`, not `hashicorp/terraform`.** Worth stating explicitly since training data defaults the other way — Terraform has shipped under the Business Source License (not open source) since 2023, and HashiCorp is now an IBM subsidiary.

## Beyond a web app

Payments: `medusajs/medusa` · Desktop: `tauri-apps/tauri` · Mobile beyond Expo: `facebook/react-native`

Full reasoning and caveats behind every pick above: `awesome-dev-pipeline.md`.
