# ADR 0007: Production Deployment Boundary and Staged Release Gate

**Status:** Accepted on 2026-08-23.

## Context

The repository now provides a reproducible container, Kubernetes manifests, an HPA, ingress, network policy, ServiceMonitor, runtime hardening, complete dependency locks, and protected-main validation. Those assets make the project suitable for a configured Kubernetes environment; they do not identify a cloud account, cluster owner, domain, certificate issuer, secret manager, model-artifact publisher, traffic forecast, or production approval.

The service is an ML workload with a 1 GiB per-pod memory limit and an HPA that can scale from two to ten replicas. It therefore exceeds the low-resource, single-process profile appropriate for the dashboard's managed web hosting. A managed or self-managed Kubernetes environment with owned ingress, secrets, metrics, and artifact storage is the production deployment boundary. This ADR deliberately does not select a cloud provider or create resources.

## Decision

Production release uses a **staged Kubernetes deployment** only after all owner-controlled gates in [`docs/deployment/production-readiness.md`](../deployment/production-readiness.md) have recorded real evidence. The committed `k8s/base` files are an application baseline, not an authorization to apply placeholders such as `fake-news.example.com`, `fake-news-detection:phase5`, or undeclared persistent volumes.

The release path is build-by-digest, signed-artifact verified, secret-manager supplied, TLS terminated, network restricted, and progressively rolled out. Real model/article data must never enter source control, CI logs, load-test payloads, metrics labels, drift job retention, or public deployment discussions. Production traffic, capacity changes, DNS, certificates, cloud resources, and secret values remain owner actions.

## Consequences

The repository can provide a deterministic deployment package and objective acceptance criteria without fabricating a deployed endpoint or a scale claim. A provider-specific overlay, infrastructure-as-code module, or automated rollout is deferred until the owner identifies the cluster/account, network model, certificate manager, artifact store, data classification, and on-call responsibility. That future work must update the developer-pipeline adoption matrix and use a focused protected-main pull request.
