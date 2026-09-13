# Production Readiness and Staged Deployment Gate

## Decision status

> **Status: release candidate ready; production deployment not yet authorized.**

The repository has passed protected-main CI, CodeQL, secret detection, container validation, and Scorecard for the current codebase. It is technically prepared for a **configured Kubernetes cluster**, not yet certified for unrestricted mass traffic. The missing information is intentionally owner-controlled: a real deployment target, domain and TLS authority, secret manager, governed model-artifact source, expected load, regional/data-residency needs, and named operational ownership.

The committed Kubernetes baseline starts at two API replicas and can scale to ten based on 75% CPU utilization. At the declared requests, that is 1 CPU and 1 GiB at the minimum replica count; at the declared limits, the ten-pod ceiling can consume up to 10 CPU and 10 GiB. These are scheduling bounds, not a traffic-capacity promise. The final capacity value must be measured against the approved model artifact, ingress, Redis, and real target environment before any broad rollout.

## Hosting boundary

| Option | Suitability | Decision |
|---|---|---|
| Existing or newly provisioned Kubernetes cluster | Supports the committed Deployment, HPA, network policy, ingress, ServiceMonitor, Redis, read-only filesystem, and production-scale resource controls. | **Required production boundary.** Owner must identify the provider/account/cluster and responsible operator. |
| Local or on-premises Kubernetes | Suitable for controlled/private deployments when the owner supplies TLS, monitoring, backup, registry, artifact storage, and operator responsibility. | Allowed after the same readiness gates. |
| Single-process managed web hosting | Inadequate for this Python/Docker/Kubernetes workload and the committed multi-replica scaling contract. | Not selected for mass deployment. |
| Default sandbox | Hibernates and has no production ingress, secret-management, or service-level guarantee. | Development/validation only. |

## Non-negotiable pre-deployment gates

| Gate | Required evidence | Owner action |
|---|---|---|
| Target ownership | Named cluster, namespace, environment classification, operator, and change-approval route. | Select and authorize the target; do not use an unowned cluster. |
| Immutable release | Container image digest from the successful protected-main build, SBOM/image metadata, and exact Git commit. | Publish or authorize access to the digest in an approved registry. |
| Model integrity | Governed artifact location, SHA-256/manifest, signature verification key, compatibility evidence, and documented rollback artifact. | Publish approved artifact/version and private verification material. |
| Secret handling | External secret manager or cluster-secret process for Redis credentials, artifact verification public key, TLS material, and any provider credentials. | Create values outside Git; grant least privilege; confirm rotation owner. |
| Network and TLS | Real DNS name, certificate issuance/renewal owner, ingress class, HTTPS validation, metrics access policy, and network-policy compatibility. | Configure domain/certificate/ingress; never apply the example hostname. |
| Data and privacy | Confirm raw article text is transient only; define legal/data-residency scope and approved log/metric retention. | Approve the data classification and retention boundary. |
| Capacity and resilience | Authorized synthetic-only k6 run, Redis failure exercise, model warm-up/readiness check, HPA observation, and rollback drill. | Supply approved target and capacity window; review results. |
| Operations | Named on-call owner, alert routing, dashboard access, incident contact, backup/restore responsibility, and change window. | Record ownership and approval evidence. |

## Configuration contract

The base manifests intentionally contain deployment examples and must not be applied unchanged. A provider-specific production overlay must replace the image tag with an immutable digest, the ingress example hostname/TLS secret, persistent-volume assumptions, resource sizing, namespace, and any registry pull configuration. It must not introduce plaintext values for `REDIS_PASSWORD`, `REDIS_URL`, `ARTIFACT_PUBLIC_KEY_B64`, certificate material, provider tokens, or model data.

The runtime must keep `REQUIRE_SIGNED_ARTIFACT=true`, a non-empty signed artifact verification key supplied from a secret, explicit CORS origins, bounded request/queue limits, offline transformer configuration when the model bundle is expected in the image/artifact volume, and a Redis circuit-breaker configuration. Health and readiness endpoints must be reachable only through the designed probe/ingress path; `/metrics` must receive an explicit network/authentication policy before external exposure.

## Staged rollout procedure

| Stage | Maximum exposure | Required pass condition | Immediate rollback condition |
|---|---|---|---|
| 0. Preflight | No user traffic | All gates above have evidence; manifests validate; image digest and artifact verify; TLS/probes/metrics work. | Any unresolved secret, artifact, network, or ownership gate. |
| 1. Internal smoke | Approved operator traffic only | Synthetic bounded `/predict`, `/ready`, and metrics checks succeed; no raw text appears in protected telemetry. | Readiness failure, unexpected error, secret warning, or privacy violation. |
| 2. Canary | Explicitly approved small traffic share | Latency/error/rejection/drift queue remain within owner-approved thresholds; Redis circuit behavior is observed safely. | Sustained error/rejection regression, resource saturation, artifact mismatch, or alert escalation. |
| 3. Progressive scale | Stepwise traffic/replica increase | HPA, ingress, Redis, artifact mount, and Prometheus signals remain stable across a documented observation window. | Any canary rollback condition or loss of observability. |
| 4. Broad release | Owner-approved traffic | On-call, rollback target, dashboards, and capacity reserve are confirmed. | Owner invokes rollback or a defined safety threshold is breached. |

No stage automatically promotes to the next stage. Drift is a human-review signal and does not authorize automatic retraining or model promotion.

## Rollback and incident contract

Rollback means routing traffic back to the prior verified image digest and matching signed model artifact, then preserving redacted operational evidence. It does not mean deleting logs, suppressing alerts, rewriting history, or exposing secrets. If an artifact, secret, or raw-text handling issue is suspected, stop promotion, use the private security process, rotate/revoke the affected credential if applicable, and do not publish diagnostic payloads.

## Before requesting a production deployment

The owner must provide the target type (existing Kubernetes cluster, named cloud provider, or on-premises cluster), the anticipated request rate and regions, the domain/certificate owner, the artifact store, and a named release/on-call owner. Only then can a provider-specific overlay and an authorized deployment run be designed. This repository does not execute production deployment, DNS, certificate issuance, cloud-resource creation, or payment actions from this document.

The detailed evidence sequence and stop/rollback rules are in [`production-rollout.md`](production-rollout.md). The release-contract checker is a local, non-networked guard; it validates only the sanitized contract and rendered manifest supplied by the owner.
