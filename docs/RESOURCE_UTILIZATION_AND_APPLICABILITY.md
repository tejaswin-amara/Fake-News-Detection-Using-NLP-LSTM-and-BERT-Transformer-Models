# Supplied Resource Utilization & Applicability Register

This register accounts for the resources supplied in `Pasted markdown(2).md` (Awesome Dev Pipeline) while keeping the **Machine Learning 25SC2107E handout** as the academic source of truth. The supplied list explicitly says situational tools should be added only when the project needs the problem they solve. Therefore, “accounted for” does not mean “force every web/mobile tool into an ML repository.”

## Handout references — required academic foundation

The attached `Machine Learning handout.pdf` defines six outcomes and six modules: M1 lifecycle, M2 linear supervised learning, M3 tree-based supervised learning, M4 unsupervised learning, M5 evaluation/selection/calibration, and M6 ML engineering. fileciteturn19file0L53-L69 fileciteturn19file0L70-L103 fileciteturn19file0L108-L131

| Handout resource | How it is used |
|---|---|
| Géron, *Hands-On Machine Learning* (2022) | Practical supervised learning, preprocessing, neural-network, evaluation and pipeline patterns. |
| Hastie, Tibshirani & Friedman, *ESL* (2017) | Regularization, trees, ensembles, resampling and statistical reasoning. |
| James et al., *ISL with Applications in Python* (2023) | Supervised/unsupervised learning, resampling, regularization and evaluation explanations. |
| Bishop, *PRML* (2006) | Probabilistic/statistical foundations and model interpretation. |
| Huyen, *Designing ML Systems* (2022) | Lifecycle, training-serving skew, monitoring, deployment and retraining. |
| Ameisen, *Building ML Powered Applications* (2020) | Model-to-product workflow, error analysis and deployment. |
| Burkov, *Machine Learning Engineering* (2020) | Production ML engineering, testing and monitoring. |

These seven books are explicitly listed by the handout as the reference books. fileciteturn19file0L132-L168

## Supplied engineering resources

### Universal resources

| Resource | Disposition | Concrete project use |
|---|---|---|
| `sindresorhus/awesome` | Reference | Used as the discovery index when an uncovered engineering concern appears; no dependency on the repository. |
| `progit/progit2` | Used | Git branching, commit/review workflow and release hygiene. |
| `github/choosealicense.com` | Used | License selection/checking and dependency-license review. |
| `conventional-commits/conventionalcommits.org` | Used | Commit convention for hardening/release work. |
| `cookiecutter/cookiecutter` | Reference | Reproducible scaffolding pattern; existing repository is not regenerated because it already has a mature structure. |
| `makeplane/plane` | Not forced | Project management is outside the runtime; GitHub Issues remain the repository-native execution record. |
| `github/opensource.guide` | Used | Contribution, issue, PR and governance patterns. |
| `google/eng-practices` | Used | Review checklist and change-review standard. |
| `n8n-io/n8n` | Not forced | Automation is not required for the core ML lifecycle; license/security caveats are recorded in the supplied resource list. |

### Full-stack resources that are applicable to the serving surface

| Resource | Disposition | Concrete project use |
|---|---|---|
| `excalidraw/excalidraw` | Used as design/reference | Architecture and lifecycle diagrams should be authored using the same diagram-first practice; exported diagrams are kept in documentation. |
| `fastapi/full-stack-fastapi-template` | Reference | FastAPI REST serving patterns; the project already has a dedicated Python ML service and does not need the template's unrelated frontend/database scaffold. |
| `alan2207/bulletproof-react` | Not applicable | No React frontend is required by the ML handout. |
| `gothinkster/realworld` | Reference only | API/CRUD conventions are a reference for REST completeness, not a required application domain. |
| `spring-petclinic/spring-petclinic-reactjs` | Not applicable | Java/Spring/React is outside this Python ML service. |
| `gothinkster/spring-boot-realworld-example-app` | Not applicable | Same reason: no Spring backend in the handout project. |
| `shadcn-ui/ui` | Not applicable | No frontend UI is required for CO6. |
| `dequelabs/axe-core` | Not applicable | No browser UI is part of the required ML service. |
| `i18next/i18next` / `react-i18next` | Not applicable | No browser UI/i18n requirement. |
| `prisma/prisma` | Not applicable | No relational application database is required for the core lifecycle. |
| `better-auth/better-auth` | Not applicable | Authentication is not a handout requirement; API security is handled at the service boundary where needed. |
| `taskforcesh/bullmq` | Not applicable | The service uses Python-native bounded/asynchronous mechanisms; adding a Node/Redis queue solely to consume a resource would add needless complexity. |
| `minio/minio` | Not applicable | No object-storage requirement; model/data artifacts are governed through DVC and artifact manifests. |
| `vercel/ai` | Not applicable | No LLM feature is part of the handout; BERT is a supervised Transformer classifier, not a generative feature. |
| `OWASP/CheatSheetSeries` | **Used** | API validation, authentication boundary, CORS, error handling, secrets, container and deployment security reviews. |
| `cypress-io/cypress-realworld-app` | Reference | E2E testing patterns inform API/integration test organization; browser-specific payment flows are not copied. |
| `actions/starter-workflows` | Used as reference | GitHub Actions structure and CI/CD conventions. |
| `docker/awesome-compose` | Used as reference | Multi-service Compose conventions for FastAPI/Redis/MLflow. |
| `ripienaar/free-for-dev` | Reference | Deployment-cost research only; not a runtime dependency. |
| `umami-software/umami` | Not applicable | Product analytics is outside the academic ML service scope. |
| `codecrafters-io/build-your-own-x` | Learning/reference | Used for engineering understanding of underlying systems, not embedded in production code. |
| `calcom/cal.diy` | Reference only | Production-scale application architecture study; not a dependency. |
| `donnemartin/system-design-primer` | Used | Scaling, caching, reliability and architecture trade-off reference for the serving layer. |

### Situational resources

The supplied list explicitly says these are to be added **only as needed**. fileciteturn19file1L349-L351

| Resource/category | Disposition |
|---|---|
| Meilisearch / Typesense | Not needed: no search product is required. |
| Socket.IO / Soketi | Not needed: no realtime browser feature. |
| TanStack Query / SWR | Not needed: no React client. |
| React Hook Form / Zod | Not needed: FastAPI/Pydantic handles request validation. |
| Gitleaks | **Used**: secret scanning is part of CI/security gates. |
| Infisical | Reference: production secret-manager option; repository does not require a hosted secret manager for local academic execution. |
| Scalar / Swagger UI | **Used via FastAPI/OpenAPI boundary**: API documentation is generated from the serving contract; a separate UI is optional. |
| Redis | **Used**: distributed rate limiting/circuit breaking/queue-related serving resilience where configured. |
| NATS / Kafka | Not needed: no event-streaming requirement in the handout. |
| Kong | Not needed for the single-service academic deployment; can sit in front of multiple production replicas if an API gateway becomes necessary. |
| Payload / Strapi | Not needed: no CMS. |
| Motion / GSAP | Not needed: no browser UI. |
| Storybook | Not needed: no component library. |
| OpenTofu / Terraform / Pulumi | Reference only: infrastructure-as-code is useful for a real cloud deployment but is not required for the handout's introductory M6 scope. |
| k6 | **Used**: load/performance testing of the REST service. |

### Beyond-web-app resources

| Resource | Disposition |
|---|---|
| Medusa / Lago | Not applicable: no payment/billing domain. |
| Tauri / Electron | Not applicable: no desktop application. |
| React Native / Flutter | Not applicable: no mobile application. |

### ML/data resources

| Resource | Disposition | Project use |
|---|---|---|
| `mlflow/mlflow` | **Used** | Experiment tracking, artifact metadata and model lifecycle evidence. |
| `apache/airflow` | Reference | Scheduling concept for retraining; actual academic pipeline remains DVC/scripts so the repository does not introduce an unnecessary orchestrator. |
| `dbt-labs/dbt-core` | Not applicable | The project is not a SQL warehouse transformation pipeline. |

### Agent resources

The supplied document recommends choosing one skill collection rather than installing all overlapping collections. fileciteturn19file1L458-L469

| Resource | Disposition |
|---|---|
| `anthropics/skills` | Reference for agent-assisted engineering. |
| `addyosmani/agent-skills` | Reference for production-hardened agent practices. |
| `alirezarezvani/claude-skills` | Reference only; not installed wholesale because it overlaps other skill packs. |
| `emilkowalski/skills` | Reference for design/interaction work; no UI is required. |
| `nextlevelbuilder/ui-ux-pro-max-skill` | Not needed: no UI deliverable. |
| `DietrichGebert/ponytail` | Reference for YAGNI/agent discipline. |
| `microsoft/agent-governance-toolkit` | Reference for agent governance; not part of runtime. |
| `DeusData/codebase-memory-mcp` | Reference for large-repository agent workflows. |
| `kunchenguid/no-mistakes` | Reference for pre-push AI validation; GitHub CI remains authoritative. |
| `Panniantong/Agent-Reach` | Not used: scraping social platforms is unrelated to the handout and introduces ToS risk. |
| `nexu-io/open-design` | Not needed: no design artifact is required for the ML backend. |

## Academic boundary

The supplied engineering list is a **software-development reference**, not an instruction to turn a fake-news ML project into a full-stack commerce/mobile application. The handout itself defines M6 as introductory production-style ML engineering: feature stores conceptually, training-serving skew, model packaging, ONNX, REST/gRPC, monitoring, retraining, MLflow and DVC. fileciteturn19file0L121-L130

Accordingly, the project uses the resources that solve an actual lifecycle problem and records the rest as explicitly considered/not applicable. This is the correct way to use the supplied list without violating the handout's scope.
