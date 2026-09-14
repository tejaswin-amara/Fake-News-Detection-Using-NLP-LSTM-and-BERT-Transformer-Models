# Awesome Dev Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)
![GitHub Repo stars](https://img.shields.io/github/stars/tejaswin-amara/awesome-dev-pipeline?style=social)

A curated, honestly-caveated list of GitHub repos covering software development start to end — universal practices first, then the full-stack web pipeline, then AI-agent tooling. Every entry has actually been checked, not just copied from another list: licensing terms are called out when they're not permissive, terms-of-service risk is flagged where it exists, and entries that only got a shallow pass say so instead of pretending otherwise.

This is the all-in-one version: the list, the operational quick-reference, the contribution guidelines, and the license, merged into a single file. **One real trade-off worth knowing:** Claude Code specifically auto-loads a file literally named `CLAUDE.md` at a project's root at the start of every session — a merged file under a different name doesn't get that automatic behavior. If that matters, copy the [Quick Reference](#quick-reference-for-an-ai-coding-agent) section below into its own `CLAUDE.md`; everything else is fine staying here.

*Verified as of August 2026. Star counts, pricing, and licensing terms drift — treat exact figures as approximate, not current fact six months out. See [Contributing](#contributing) to help keep it that way.*

Three parts: practices that apply to any project regardless of language or platform, then the specific pipeline for full-stack web apps (with a situational extension for search, real-time, payments-adjacent infrastructure, and the rest of what a *given* project might need), then what's genuinely beyond a web app entirely. Minimum path if you only have time for one pass: pick a license → Git → scaffold → structure → frontend → database → auth → testing → CI/CD → deploy. Everything past that is real and worth knowing, but situational rather than required.

## Contents

**Part 1 — Universal**
The gateway to everything else · Version control, properly · Pick a license before anyone else touches the code · Commit message conventions · Scaffold literally any kind of project · Manage the actual work · Structure it so others can contribute · Review code well · Automate the recurring parts

**Part 2 — The full-stack web pipeline**
Plan and sketch it out · Scaffold a new web project · Package manager and code quality · Structure it so it survives growth · See the same app built different ways · Frontend and component layer · Accessibility · Internationalization · Database · Auth · Background jobs and queues · File storage · Add AI features to what you built · Vector storage · Security · Testing · CI/CD · Containerize it · Deploy and host it · Understand usage after launch · Catch errors after launch · Go one level deeper than the app · Study a real production-scale app · Scale it once it's live

*→ Situational (add only as needed):* search · real-time/WebSockets · server-state management · forms · secrets management · API documentation · caching · event streaming · API gateway · headless CMS · animation · component documentation · infrastructure as code · load testing · feature flags · GraphQL · reproducible dev environments

**Part 3 — Beyond a web app**
Payments · Desktop apps · Native mobile beyond Expo

**Meta** — a roadmap and a practice ground
**Bonus** — skill collections, agent infrastructure, agent utilities
**Adjacent** — ML and data tooling (arguably out of scope, included anyway)
**[Quick Reference](#quick-reference-for-an-ai-coding-agent)** — the condensed, operational version of everything above
**[Contributing](#contributing)** · **[License](#license)**

---

## Part 1 — Universal: applies to any project, any language

### The gateway to everything else

- **[sindresorhus/awesome](https://github.com/sindresorhus/awesome)** — the master list of curated lists. Mobile, ML, a specific language, DevOps, embedded, game dev — whatever this document doesn't cover, this is where you start looking.

### Version control, properly

- **[progit/progit2](https://github.com/progit/progit2)** — the free, official Pro Git book. Every project needs this regardless of stack; most people only ever learn the six commands they use daily and never the rest.

### Pick a license before anyone else touches the code

- **[github/choosealicense.com](https://github.com/github/choosealicense.com)** — GitHub's own non-judgmental guide to open source licenses, in plain language instead of legalese.

### Commit message conventions

- **[conventional-commits/conventionalcommits.org](https://github.com/conventional-commits/conventionalcommits.org)** — the spec behind `feat:`, `fix:`, `chore:` commit prefixes, which is what lets tools auto-generate changelogs and version bumps later.

### Scaffold literally any kind of project

- **[cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter)** — language-agnostic project templating: Python packages, Rust, Terraform, ML research repos, documentation sites, whatever you find yourself rebuilding by hand each time.

### Manage the actual work

- **[makeplane/plane](https://github.com/makeplane/plane)** — the most-starred open source project management tool on GitHub (46k+ stars). Self-hosted Jira/Linear alternative: issues, sprints, roadmaps. Useful the moment a project has more than one contributor or more than a week of runway.

### Structure it so others can contribute

- **[github/opensource.guide](https://github.com/github/opensource.guide)** — how to write a CONTRIBUTING.md, set up issue templates, handle your first pull requests, and run a project once it's not just you anymore.

### Review code well

- **[google/eng-practices](https://github.com/google/eng-practices)** — Google's own internal code review guidelines, for both the author and the reviewer side. Language-agnostic; the single most effective bug-catching practice there is, ahead of testing and static analysis.

### Automate the recurring parts

- **[n8n-io/n8n](https://github.com/n8n-io/n8n)** — 200k+ stars, workflow automation with native AI/MCP support: wire together the boring 80% (lead intake, reporting, notifications, cross-app glue) instead of hand-coding every integration. Two honest notes: it's source-available under the Sustainable Use License, not permissively open source like the rest of this list, and it had a critical unauthenticated RCE (CVE-2026-21858) patched earlier this year — keep a self-hosted instance updated.

---

## Part 2 — The full-stack web pipeline

The order: plan → scaffold → structure → build → audit → ship → scale.

### Plan and sketch it out

- **[excalidraw/excalidraw](https://github.com/excalidraw/excalidraw)** — a virtual whiteboard for wireframes, flowcharts, and system diagrams before you write a line of code. 130k stars, used internally at Netflix, Meta, Stripe, and Supabase.

### Scaffold a new web project

*Pick one based on what you're actually building, not all three: create-t3-app for a single web app, create-t3-turbo only once there's a real second target (mobile, a shared package) to justify a monorepo, the FastAPI template when the backend needs to be Python rather than TypeScript.*

- **[t3-oss/create-t3-app](https://github.com/t3-oss/create-t3-app)** — one CLI command to a type-safe Next.js + tRPC + Prisma/Drizzle + Auth.js + Tailwind app.
- **[t3-oss/create-t3-turbo](https://github.com/t3-oss/create-t3-turbo)** — the same stack as a Turborepo monorepo, sharing a tRPC API between a Next.js web app and an Expo mobile app.
- **[fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)** — the Python-backend equivalent: FastAPI + React + SQLModel + PostgreSQL + Docker Compose + GitHub Actions, maintained by FastAPI's creator. The natural pick when the backend needs to be Python instead of TypeScript.
- **[withastro/astro](https://github.com/withastro/astro)** — a genuinely different kind of project from the other three: content-first (blogs, docs, marketing sites) rather than app-first, ships zero JS by default and only hydrates the interactive pieces. Pick this over create-t3-app when most of the site is content someone reads, not an app someone operates.

### Structure it so it survives growth

- **[alan2207/bulletproof-react](https://github.com/alan2207/bulletproof-react)** — folder structure, state management, testing setup, and linting conventions for a React codebase that won't collapse once it's past 20 files.

### Package manager and code quality

- **[pnpm/pnpm](https://github.com/pnpm/pnpm)** — the package manager every monorepo entry above (create-t3-turbo, Turborepo) already assumes; faster installs and a content-addressable store instead of npm's duplication.
- **[biomejs/biome](https://github.com/biomejs/biome)** — linting and formatting in one fast Rust-based tool, instead of running ESLint and Prettier as two separate, sometimes-conflicting steps.

### See the same app built different ways

*Browse gothinkster/realworld itself to compare stacks in general; go straight to the Spring Boot variant or spring-petclinic-reactjs if Java/Spring specifically is what you're building against.*

- **[gothinkster/realworld](https://github.com/gothinkster/realworld)** — a shared spec (auth, CRUD, pagination, routing) implemented across 100+ frontend/backend combinations.
- **[gothinkster/spring-boot-realworld-example-app](https://github.com/gothinkster/spring-boot-realworld-example-app)** — the same spec in Spring Boot + MyBatis, with DDD-style layering and both REST and GraphQL endpoints.
- **[spring-petclinic/spring-petclinic-reactjs](https://github.com/spring-petclinic/spring-petclinic-reactjs)** — the official Spring PetClinic reference app with a React front end instead of Thymeleaf.

### Frontend and component layer

- **[shadcn-ui/ui](https://github.com/shadcn-ui/ui)** — component code lives as real files in your own repo instead of being compiled away inside node_modules, so you can edit the actual source directly. Ships its own MCP server for live component lookup.

### Accessibility

- **[dequelabs/axe-core](https://github.com/dequelabs/axe-core)** — the accessibility testing engine behind Chrome DevTools and Lighthouse, used in 13 million+ GitHub projects. Catches roughly 57% of WCAG issues automatically, on average — before a screen reader user does.

### Internationalization

- **[i18next/i18next](https://github.com/i18next/i18next)** — the standard JS i18n framework, paired with **[i18next/react-i18next](https://github.com/i18next/react-i18next)** for React specifically. MIT-licensed, ~10k stars each, works the same in Node/Deno on the backend as it does in the browser.

### Database

- **[prisma/prisma](https://github.com/prisma/prisma)** — the type-safe ORM most of the repos above already assume. Schema-first modeling, migrations, and a query builder that autocompletes against your actual database shape.

### Auth

- **[better-auth/better-auth](https://github.com/better-auth/better-auth)** — framework-agnostic TypeScript auth with 2FA, passkeys, SSO, and multi-tenancy built in, instead of hand-rolling session logic.

### Background jobs and queues

- **[taskforcesh/bullmq](https://github.com/taskforcesh/bullmq)** — Redis- or Postgres-backed job queues for anything that shouldn't block a request: emails, PDF generation, batch processing. MIT-licensed, 9k+ stars, the standard pick once "just await it" stops being fast enough.

### File storage

- **[minio/minio](https://github.com/minio/minio)** — S3-compatible object storage you self-host instead of paying AWS for it. One real caveat: it's AGPLv3, a copyleft license — check the terms before shipping it inside a closed-source commercial product, unlike everything else infrastructure-related in this list.

### Add AI features to what you built

- **[vercel/ai](https://github.com/vercel/ai)** — the standard TypeScript toolkit for adding LLM features to an app you've already built: streaming, tool calling, and one API across Anthropic, OpenAI, Google, and 100+ other models instead of a bespoke integration per provider. 26k+ stars, from the Next.js team.

### Vector storage (for RAG / embeddings)

- **[pgvector/pgvector](https://github.com/pgvector/pgvector)** — a Postgres extension for vector similarity search; the default here specifically because it sits inside the same Postgres/Prisma database already used above instead of adding a whole separate system.
- **[qdrant/qdrant](https://github.com/qdrant/qdrant)** — a dedicated vector database, worth reaching for once similarity search needs to scale past what a Postgres extension comfortably handles.

### Security

- **[OWASP/CheatSheetSeries](https://github.com/OWASP/CheatSheetSeries)** — the official OWASP reference for securing what you just built: auth, session management, input validation, SQL/XSS prevention, one focused cheat sheet per topic instead of a 40-page PDF.

### Testing

*Pick one E2E framework, not both — Cypress if the project is already committed to its ecosystem, Playwright as the more modern default otherwise.*

- **[cypress-io/cypress-realworld-app](https://github.com/cypress-io/cypress-realworld-app)** — a full-stack Express/React payment app built specifically to teach end-to-end testing patterns: local auth, database seeding, and a working CI pipeline included.
- **[microsoft/playwright](https://github.com/microsoft/playwright)** — cross-browser (including Safari/WebKit, which Cypress doesn't cover as well) and generally the more modern default for new projects.
- **[vitest-dev/vitest](https://github.com/vitest-dev/vitest)** — unit testing, a different job from either of the above: fast, Vite-native, Jest-compatible API. Nothing above this line actually covers unit tests specifically.

### CI/CD

- **[actions/starter-workflows](https://github.com/actions/starter-workflows)** — GitHub's own official workflow templates: CI for most languages/frameworks plus deployment templates for Pages, Next.js, containers, and more.

### Containerize it

- **[docker/awesome-compose](https://github.com/docker/awesome-compose)** — official Docker Compose samples wiring up real multi-service stacks so you're not guessing at your first Compose file.

### Deploy and host it

- **[ripienaar/free-for-dev](https://github.com/ripienaar/free-for-dev)** — a long-maintained catalog of free hosting, database, CI/CD, and monitoring tiers, organized by category so you can compare real limits before committing to one.

### Understand usage after launch

- **[umami-software/umami](https://github.com/umami-software/umami)** — privacy-first, cookieless analytics you self-host instead of handing to Google. MIT-licensed, light enough to run on the same Railway/Vercel setup you're already deploying to.

### Catch errors after launch

- **[getsentry/sentry](https://github.com/getsentry/sentry)** — the standard for error tracking and performance monitoring. Licensing is genuinely two-tiered: the client SDKs you actually embed in your app (`sentry-javascript`, `sentry-python`, etc.) are plain MIT, while the server you'd self-host is under the Functional Source License — free to self-host and use, restricted only from reselling it as a competing hosted service. This is the GitHub-native fill for a gap an earlier pass left open (GlitchTip, the other well-known option, is primarily developed on GitLab).

### Go one level deeper than the app

- **[codecrafters-io/build-your-own-x](https://github.com/codecrafters-io/build-your-own-x)** — currently the single most-starred repo on GitHub (500k+ stars). Rebuild your own Git, Redis, Docker, HTTP server, and database from scratch.

### Study a real production-scale app

- **[calcom/cal.diy](https://github.com/calcom/cal.diy)** — Cal.com's free code, relaunched under the MIT license in April 2026 after the commercial edition went fully closed-source. A large, real scheduling app on Next.js, tRPC, React, Tailwind, and Prisma — no toy shortcuts.

### Scale it once it's live

- **[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)** — how to think about scaling, caching, and architecture tradeoffs before you actually hit them, with flashcards and interview-style prep.

---

### Situational — pull these in only when the project actually needs them

Real, vetted, and worth knowing — but nothing below is a default the way the pipeline above is. Add each one only when its specific problem actually shows up.

**Search**

- **[meilisearch/meilisearch](https://github.com/meilisearch/meilisearch)** — fast, typo-tolerant, easy to self-host. Near-equivalent to Typesense below; pick whichever client library fits the stack better.
- **[typesense/typesense](https://github.com/typesense/typesense)** — same category as Meilisearch, with a slightly different query API and built-in geo-search.

**Real-time / WebSockets**

- **[socketio/socket.io](https://github.com/socketio/socket.io)** — the ecosystem-standard, batteries-included choice for chat, live updates, presence.
- **[soketi/soketi](https://github.com/soketi/soketi)** — a lighter, Pusher-protocol-compatible alternative; pick this specifically if something already in the stack expects the Pusher protocol.

**Server-state management**

- **[TanStack/query](https://github.com/TanStack/query)** — caching, refetching, and sync between the API and the components. Framework-agnostic core (React, Vue, Solid, Svelte).
- **[vercel/swr](https://github.com/vercel/swr)** — the lighter alternative, from the Next.js team: fewer features, faster to learn.

**Forms**

- **[react-hook-form/react-hook-form](https://github.com/react-hook-form/react-hook-form)** — the standard form library, minimal re-renders, works with any validation library.
- **[colinhacks/zod](https://github.com/colinhacks/zod)** — the schema validator it's most commonly paired with; also used for API input validation independent of forms.

**Secrets management**

- **[gitleaks/gitleaks](https://github.com/gitleaks/gitleaks)** — scans commits for secrets that already leaked. Run it in CI, not instead of the next entry.
- **[Infisical/infisical](https://github.com/Infisical/infisical)** — an actual secrets manager: injects env vars at runtime instead of `.env` files sitting in a repo.

**API documentation**

- **[scalar/scalar](https://github.com/scalar/scalar)** — a modern OpenAPI reference UI, faster and better-looking than the incumbent below.
- **[swagger-api/swagger-ui](https://github.com/swagger-api/swagger-ui)** — the older, more ubiquitous standard; still what most tooling expects by default.

**Caching**

- **[redis/redis](https://github.com/redis/redis)** — the layer the background-jobs and rate-limiting entries above already assume, made explicit. Earns its place on its own merits, not just as another tool's dependency.

**Event streaming / pub-sub at scale**

- **[nats-io/nats-server](https://github.com/nats-io/nats-server)** — lightweight messaging; the right choice once BullMQ's job-queue model isn't the right shape anymore.
- **[apache/kafka](https://github.com/apache/kafka)** — the heavier, enterprise-scale standard. Reach for this once NATS genuinely isn't enough, not by default.

**API gateway / rate limiting**

- **[Kong/kong](https://github.com/Kong/kong)** — the standard open source API gateway: rate limiting, auth, routing, all as plugins in front of the actual services.

**Headless CMS**

- **[payloadcms/payload](https://github.com/payloadcms/payload)** — TypeScript-native, code-first; fits naturally alongside the rest of this list's TypeScript defaults.
- **[strapi/strapi](https://github.com/strapi/strapi)** — the older, larger-ecosystem alternative, with a bigger plugin marketplace.

**Animation**

- **[motiondivision/motion](https://github.com/motiondivision/motion)** — formerly Framer Motion, the declarative default for React. MIT-licensed.
- **[greensock/GSAP](https://github.com/greensock/GSAP)** — framework-agnostic and considerably more powerful for complex, timeline-driven sequences. The design principles in `emilkowalski/skills` (Bonus) apply to either.

**Component documentation**

- **[storybookjs/storybook](https://github.com/storybookjs/storybook)** — isolated component development and living documentation, once a shadcn-based design system outgrows ad hoc screenshots.

**Infrastructure as code**

- **[opentofu/opentofu](https://github.com/opentofu/opentofu)** — the genuinely open source pick: MPL 2.0, Linux Foundation-governed, and has shipped features (state encryption, provider `for_each`) Terraform's own CLI still lacks.
- **[hashicorp/terraform](https://github.com/hashicorp/terraform)** — still what most tutorials and job postings assume, and OpenTofu remains wire-compatible with it — but Terraform has shipped under the Business Source License since 2023 (not OSI-recognized as open source), and HashiCorp is now an IBM subsidiary. Know this before defaulting to it out of habit.
- **[pulumi/pulumi](https://github.com/pulumi/pulumi)** — same job, using an actual programming language (TypeScript, Python, Go) instead of HCL.

**Load testing**

- **[grafana/k6](https://github.com/grafana/k6)** — the modern standard for load testing, from Grafana Labs.

**Feature flags**

- **[Unleash/unleash](https://github.com/Unleash/unleash)** — the most popular open source feature-flagging platform, self-hosted, 15+ official SDKs. One caveat worth tracking: the free "Edge" component (for scaling flag evaluation across many frontend clients) is being deprecated in favor of a paid Enterprise Edge in late 2026 — the core server and SDKs stay open, that specific scaling piece doesn't.

**GraphQL (instead of REST)**

- **[dotansimha/graphql-yoga](https://github.com/dotansimha/graphql-yoga)** — a batteries-included, spec-compliant GraphQL server; the lighter-weight default.
- **[apollographql/apollo-server](https://github.com/apollographql/apollo-server)** — the more established, larger-ecosystem alternative, with a correspondingly bigger surface area to learn.

**Reproducible dev environments**

- **[devcontainers/spec](https://github.com/devcontainers/spec)** — the open specification behind "Dev Containers" (VS Code, GitHub Codespaces, JetBrains): define a project's exact toolchain once in `devcontainer.json` so it doesn't matter whose machine it's cloned onto.

---

## Part 3 — Beyond a web app

The rest of this document assumes a browser-based product. These three categories are for when the project genuinely isn't one.

### Payments

- **[medusajs/medusa](https://github.com/medusajs/medusa)** — an open source commerce platform: products, carts, checkout, and payment-provider integrations, not just a payment button. Honest caveat: Stripe itself isn't open source, and there's no clean "repo" equivalent for it the way there is for auth or storage in this list — Medusa is the closest thing, not a drop-in replacement for reading Stripe's own docs.
- **[getlago/lago](https://github.com/getlago/lago)** — a narrower, different job: open source usage-based billing and metering, for subscription pricing rather than a full storefront.

### Desktop apps

- **[tauri-apps/tauri](https://github.com/tauri-apps/tauri)** — a web frontend wrapped in a Rust shell instead of a bundled Chromium. Smaller binaries, lower memory, and it stays inside this list's actual web stack. Pick this by default.
- **[electron/electron](https://github.com/electron/electron)** — more mature, a far larger ecosystem, and still what most existing desktop apps built this way use. Pick this specifically when Tauri's smaller plugin ecosystem is missing something a project needs.

### Native mobile beyond Expo

- **[facebook/react-native](https://github.com/facebook/react-native)** — the framework `create-t3-turbo`'s Expo layer is built on. Go here directly instead of through Expo once a project needs native modules Expo's managed workflow doesn't expose.
- **[flutter/flutter](https://github.com/flutter/flutter)** — a genuine alternative, not a variant of the above: Dart instead of JS/TS, and a different rendering model (Flutter draws its own UI rather than using native platform widgets). Consider this specifically when consistent pixel-perfect rendering across iOS and Android matters more than sharing code with an existing React codebase.

---

## Adjacent: ML and data tooling

Arguably out of scope for a *web* pipeline document — real gaps only if this list's scope quietly expands to cover research work too.

- **[mlflow/mlflow](https://github.com/mlflow/mlflow)** — experiment tracking, model registry, and reproducibility for ML work, the way Git tracks code.
- **[apache/airflow](https://github.com/apache/airflow)** — orchestrating data pipelines and ETL jobs as DAGs; the standard once a script chain needs scheduling, retries, and monitoring.
- **[dbt-labs/dbt-core](https://github.com/dbt-labs/dbt-core)** — data transformation specifically: SQL-based, version-controlled, testable — the "T" in ETL/ELT.

---

## Meta: a roadmap and a practice ground

- **[kamranahmedse/developer-roadmap](https://github.com/kamranahmedse/developer-roadmap)** — 326k stars, the source behind roadmap.sh. Full Stack, DevOps, and dozens of other role-specific tracks.
- **[practical-tutorials/project-based-learning](https://github.com/practical-tutorials/project-based-learning)** — 275k+ stars, global rank #13. Curated "build X from zero" tutorials across languages and domains, not just web.

## Bonus: for when an AI agent is doing the building

*The four Skill collections below overlap in purpose — use one, not all four. anthropics/skills is the official baseline; addyosmani/agent-skills is smaller and more production-hardened; alirezarezvani/claude-skills is the widest net across the most tools; emilkowalski/skills is worth adding on top of whichever you pick, specifically for its design skill.*

**Skill collections**

- **[anthropics/skills](https://github.com/anthropics/skills)** — 166k stars. Anthropic's own baseline: a frontend-design skill for aesthetic direction before code, plus others. Start here if you want one official, conservative set.
- **[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)** — maintained by Addy Osmani (Google Chrome team), with real supply-chain hardening against the npm postinstall-worm pattern built in. Pick this if you want fewer, more rigorously engineered skills over sheer breadth.
- **[alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)** — 330+ skills, 70+ commands, 30+ agents, across Claude Code, Codex, Gemini CLI, Cursor, and more. Pick this if you want maximum coverage and are willing to sort signal from noise yourself.
- **[emilkowalski/skills](https://github.com/emilkowalski/skills)** — from the creator of Vaul and Sonner. The **[apple-design](https://github.com/emilkowalski/skills/blob/main/skills/apple-design/SKILL.md)** skill specifically is an unusually deep, WWDC-sourced writeup of spring physics, interruptible gestures, velocity handoff, and translucent materials, translated line-by-line into CSS and Pointer Events.
- **[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)** — design-intelligence skill specifically for UI/UX. Worth knowing it has a paid "premium" tier attached, which none of the others above do.
- **[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)** — a discipline skill rather than a knowledge one: pushes an agent to justify every line before writing it, YAGNI-enforced. Genuinely active, if oddly branded. Stacks with any of the above rather than competing with them.

**Agent infrastructure**

- **[microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit)** — policy enforcement, sandboxing, and identity for autonomous agents, scored against the OWASP Agentic Top 10. Verified only at the level of "official Microsoft org repo, plausible content" rather than individually deep-checked like the entries above.
- **[DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)** — an MCP server that indexes a codebase into a queryable knowledge graph, so an agent isn't re-reading the whole repo on every call. Same lighter-verification caveat as above.
- **[kunchenguid/no-mistakes](https://github.com/kunchenguid/no-mistakes)** — a local git proxy: push to it instead of origin, and it runs an AI review/test/lint pipeline in a disposable worktree, only forwarding to your real remote and opening a clean PR once everything passes. Agent-agnostic (Claude, Codex, Copilot, Cursor). Real documentation site and independent press coverage, confirmed on this pass — upgraded from an earlier, thinner read.

**Agent utilities**

- **[Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach)** — gives an agent read access to Twitter/X, Reddit, YouTube, and more from one CLI. Worth knowing it works by wrapping scrapers rather than official APIs, which sits outside most of those platforms' terms of service.
- **[nexu-io/open-design](https://github.com/nexu-io/open-design)** — a local-first design-prototyping tool for agents. Markets itself as a Claude Design alternative; that framing is the vendor's, not a claim independently verified here.

---

## Quick Reference (for an AI coding agent)

This project defaults to a pre-vetted set of tools instead of picking blind or from general training-data familiarity. When a task below comes up and no existing project convention already covers it, use the listed choice and say so ("using X per project defaults") so it's visible in the diff, not silent.

These are defaults, not mandates. Deviate when the listed choice doesn't fit — wrong language, a license conflict, an explicit instruction, or a better option already ships with the framework in use — and say why when you deviate. If a task isn't listed here at all, that's expected; look it up normally instead of forcing something off this list to fit.

*If you want Claude Code to load this section automatically at the start of every session, copy this "Quick Reference" section alone into its own `CLAUDE.md` at the project root — see the note at the top of this document.*

### Universal

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

### Full-stack web

| Task | Default | Note |
|---|---|---|
| Wireframes / planning | `excalidraw/excalidraw` | |
| Scaffold a new app (TypeScript) | `t3-oss/create-t3-app` | `create-t3-turbo` if it needs to be a monorepo |
| Scaffold a new app (Python backend) | `fastapi/full-stack-fastapi-template` | |
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
| Security review | `OWASP/CheatSheetSeries` | one cheat sheet per concern (auth, XSS, SQLi, sessions) |
| End-to-end tests | pattern from `cypress-io/cypress-realworld-app` | |
| CI/CD | `actions/starter-workflows` | |
| Containerizing | `docker/awesome-compose` | |
| Hosting (free tier) | `ripienaar/free-for-dev` | verify current limits, this drifts |
| Analytics | `umami-software/umami` | self-hosted, not Google Analytics |
| Scaling / architecture questions | `donnemartin/system-design-primer` | |

### Agent tooling — when an agent is doing the building

| Task | Default | Note |
|---|---|---|
| Skill pack (baseline) | `anthropics/skills` | official, conservative |
| Skill pack (production-hardened) | `addyosmani/agent-skills` | fewer skills, more rigor |
| Skill pack (max breadth) | `alirezarezvani/claude-skills` | pick one skill-pack source, not several at once |
| Design/motion skill | `emilkowalski/skills` — apple-design | |
| Pre-push AI validation gate | `kunchenguid/no-mistakes` | optional, adds a review step before code reaches the real remote |

### Situational — only when the task actually calls for it

Search: `meilisearch/meilisearch` · Real-time: `socketio/socket.io` · Server-state: `TanStack/query` · Forms: `react-hook-form/react-hook-form` + `colinhacks/zod` · Secrets: `gitleaks/gitleaks` (scan) + `Infisical/infisical` (manage) · API docs: `scalar/scalar` · Caching: `redis/redis` · Event streaming: `nats-io/nats-server` · API gateway: `Kong/kong` · Headless CMS: `payloadcms/payload` · Animation: `motiondivision/motion` · Component docs: `storybookjs/storybook` · Load testing: `grafana/k6`

**Infrastructure as code: `opentofu/opentofu`, not `hashicorp/terraform`.** Worth stating explicitly since training data defaults the other way — Terraform has shipped under the Business Source License (not open source) since 2023, and HashiCorp is now an IBM subsidiary.

### Beyond a web app

Payments: `medusajs/medusa` · Desktop: `tauri-apps/tauri` · Mobile beyond Expo: `facebook/react-native`

Alternatives to any pick above, plus the full reasoning and caveats behind each: see the full sections earlier in this document.

---

## Contributing

This list stays useful only if every entry has actually been checked. Star counts get inflated, "AI agent skill" repos are currently a genuine gold-rush category with a lot of hype-driven noise mixed in with real tools, and licenses change without warning (see: n8n, Cal.com, Terraform). Contributing here means doing that checking, not just proposing a repo that sounds good.

### Before opening a PR

1. **Confirm it's real.** Open the repo itself, not just a blog post about it. A star count quoted in a README or a third-party roundup isn't verification — cross-check it against the repo's own GitHub page.
2. **Confirm it fits a real gap.** Every entry answers a specific question ("how do I containerize this," "what do I use for background jobs"). If it doesn't map to an actual stage in the pipeline or a universal practice, it probably belongs in a different list.
3. **Check the license.** If it's not a standard permissive license (MIT, Apache-2.0, BSD), say so explicitly in the entry — don't let a reader assume "open source" means "no strings attached." `n8n-io/n8n` (Sustainable Use License), `minio/minio` (AGPLv3), and `hashicorp/terraform` (Business Source License) are the existing examples of how to phrase this.
4. **Flag anything else non-obvious.** A paid tier bolted onto an "open source" tool, a terms-of-service risk (scraping platforms without their API), a security incident in the project's history, documentation thin enough that you can't actually describe what it does — all of these get a one-line caveat in the same bullet, not a separate warning section.
5. **If two entries do the same job, say which one to pick.** Don't just add a fourth option to a category that already has three undifferentiated ones — see how "Scaffold a new web project" and "Skill collections" handle this.

### What gets rejected

- Repos with no real public documentation to describe accurately (a one-line README with no further detail is not enough to write an honest entry).
- Repos whose actual GitHub org doesn't match what's claimed (verify the URL, not just the name — `fastapi/full-stack-fastapi-template` moved orgs once already).
- Anything that only fits by stretching the category ("any project" is broad, but not infinite — see Part 3 for where the line landed on payments, desktop, and mobile).

### Format

Match the existing style: `**[owner/repo](url)** — what it does, in one sentence, then the caveat if there is one, in the same sentence or the next.` No separate ratings, no star emoji, no "10/10 must-have" language. If you're adding an entry, update the Contents block at the top and the Quick Reference table to match — they're meant to stay in sync with the full list.

### Removing an entry

Licenses change, projects go unmaintained, security incidents happen. If you're proposing a removal, link to the evidence (a commit, a release note, an archived-repo banner) in the PR description.

---

## License

MIT License

Copyright (c) 2026 Tejaswin Amara

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This license covers the list itself, not the licenses of the projects it links to. Check each project's own license before depending on it; several entries above are explicitly *not* MIT (`n8n-io/n8n`, `minio/minio`, `hashicorp/terraform`) and this document says so at the point of use.
