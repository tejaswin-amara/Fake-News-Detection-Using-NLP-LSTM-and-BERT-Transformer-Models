# Authorized Production Rollout and Rollback Runbook

## Scope and authority

This runbook defines the evidence and decision sequence for a release owner who has already selected and authorized a target Kubernetes environment. It **does not authorize a deployment**, create a cluster, call an external endpoint, issue a certificate, publish an image, or supply credentials. It must be completed by the named release owner and on-call owner in the target environment after the gates in [`production-readiness.md`](production-readiness.md) are satisfied.

Kubernetes readiness probes prevent unready Pods from receiving Service traffic, while Deployments retain revisions needed to roll back unstable Pod templates. Kubernetes also cautions that Secret data must be protected by access controls and appropriate encryption/secret-management controls rather than committed as a manifest.[^kubernetes]

[^kubernetes]: Kubernetes production-readiness, probe, Deployment, and Secret guidance is registered as [SRC-057](../sources.md#src-057--kubernetes-production-readiness-probes-and-secret-handling).

## Evidence package

Before the first internal smoke check, the release owner prepares a private evidence package outside this repository. The package contains the protected-main commit, immutable container-image digest, approved model artifact URI and SHA-256, signature-verification evidence, previous known-good image/artifact pair, target namespace, ingress host/TLS confirmation, secret-manager references, expected traffic/region profile, and named owners. It contains **no raw article text, credential value, private key, Redis password, model weight, or live request payload**.

| Evidence item | Acceptance rule | Retention boundary |
|---|---|---|
| Code and image | Exact merged commit and immutable image digest identify one release. | Release/change record. |
| Model package | Artifact location, SHA-256, signed-manifest verification, and compatibility result are recorded. | Governed artifact registry and private release record. |
| Secrets and TLS | References and responsible owner are recorded; values never enter the evidence package or Git. | Approved secret manager/certificate system. |
| Capacity plan | Expected request profile, regions, scaling bounds, Redis availability design, and safe test window are approved. | Private change/capacity record. |
| Observability | Dashboard/alert access, Prometheus scrape confirmation, on-call route, and incident contact are verified. | Operations record. |

## Preflight validation

The owner creates a private, untracked release contract from `deploy/production-release-contract.example.env` and renders the provider-specific Kubernetes overlay to a local YAML file. The base manifests are deliberately expected to fail this check because they use a sample image name and sample ingress hostname. The following read-only validation is permitted before the change window because it contacts no cluster and never echoes contract values:

```bash
python scripts/verify_production_readiness.py \
  --contract /secure/location/production-release-contract.env \
  --manifest /secure/location/rendered-production.yaml
```

The validation must pass without modifying the repository. A failure is a release stop, not a prompt to weaken the validator, remove signed-artifact verification, replace secret references with literals, or relax network/security controls.

| Required preflight condition | Stop condition |
|---|---|
| Rendered API image uses `@sha256:` digest, security context, startup/liveness/readiness probes, resource requests/limits, two or more HPA minimum replicas, and retained rollback revisions. | Mutable tag, absent resource/probe/security control, or configuration that permits an unavailable rolling update. |
| Real ingress host is mapped to a TLS Secret and the ingress implementation is owned. | Sample hostname, unvalidated certificate/renewal path, or unapproved metrics exposure. |
| Redis and artifact verification arrive via managed Secret references; `REQUIRE_SIGNED_ARTIFACT=true` remains set. | Plaintext/encoded values in repository or manifest, missing signature key, or unverified model. |
| Prometheus scraper reaches bounded `/metrics`; logs and metrics exclude raw article text and credentials. | Missing telemetry ownership, unsafe labels/logging, or no alert route. |

## Stage execution and approval gates

Every stage requires a named release-owner decision recorded outside Git. Stages never promote automatically, and a model-drift signal cannot trigger a retrain or model promotion without the governed ML evaluation process.

| Stage | Permitted exposure | Required observations | Approval to continue |
|---|---|---|---|
| Internal smoke | Operator-controlled, synthetic requests only. | TLS/probe behavior, artifact verification, bounded predict request, `/metrics` scrape, redacted logs, and Redis connection/circuit behavior. | Release owner and on-call owner confirm no stop condition. |
| Canary | Owner-approved minimal traffic share/time window. | Latency, error rate, 429/503 behavior, resource headroom, HPA response, drift queue depth, and alert delivery against owner-approved thresholds. | Release owner, on-call owner, and service owner agree evidence is within the approved threshold set. |
| Progressive rollout | Stepwise increase defined by the approved capacity plan. | All canary signals remain stable for each documented observation window; no telemetry/privacy regression. | Same owners explicitly approve each increase. |
| Broad release | Approved production traffic only. | Capacity reserve, rollback pair, on-call coverage, dashboard access, and incident contact remain available. | Service owner accepts the release record. |

## Stop, rollback, and incident response

The release owner stops promotion immediately for a model signature/checksum mismatch, readiness failure, unexpected error/rejection increase, resource exhaustion, unsafe logging/metric discovery, Redis degradation beyond the approved tolerance, missing alert visibility, certificate/network failure, or any suspected secret exposure. The first response is to preserve redacted operational evidence and notify the named on-call owner; it is not to disable a CI control, edit historical evidence, or expose diagnostic request bodies.

Rollback restores the documented previous immutable image digest and matching signed model artifact using the target environment's approved change procedure. The owner must verify readiness, safe telemetry, ingress/TLS, and the rollback artifact before resuming traffic. Kubernetes rollback behavior only restores a Deployment revision's Pod-template state, so the release record must keep the image and model artifact paired.[^kubernetes]

If secret exposure is suspected, follow [`../security/secret-handling.md`](../security/secret-handling.md) rather than adding an allowlist/baseline or discussing values publicly. If raw article text appears in an operational record, stop the affected flow, restrict access, preserve only the minimum private incident evidence, and correct the telemetry path before resuming.
