# Security Policy

## Supported version

Security fixes are assessed for the latest code on the `main` branch. Historical commits and locally modified deployments are not separately supported. Operators remain responsible for their infrastructure, DVC remote, model artifacts, environment variables, ingress/TLS configuration, and access controls.

## Reporting a vulnerability

Please use the repository’s GitHub-native private **Report a vulnerability** flow to submit a report. Do not publish an issue, proof-of-concept exploit, token, private dataset fragment, or artifact-signing material before maintainers have reviewed the report. The report should describe the affected revision or component, the preconditions, a safe reproduction path, impact, and any suggested mitigation.

The project does not publish a security email address. Status and remediation discussions will occur through GitHub’s private vulnerability-reporting workflow where available. No response-time or disclosure-date commitment is made in this policy.

## Security boundaries in scope

| Boundary | Implemented control |
|---|---|
| HTTP serving | Pydantic validation, bounded payloads and batches, deny-by-default CORS, rate limiting, structured errors, and request-ID logging |
| Artifact loading | Package manifests, SHA-256 verification, optional Ed25519 signatures, native/ONNX parity checks, and explicit sparse/dense boundaries |
| Runtime resilience | Readiness-gated warm-up, bounded inference concurrency, bounded asynchronous drift queue, and Redis circuit-breaker fail-open behavior |
| Containers | Rootless `appuser`, multi-stage build, read-only controls where configured, and a CI critical-vulnerability container gate |
| Kubernetes | Read-only filesystem and seccomp controls, resource probes, internal Redis policy, TLS ingress declaration, and manifest schema validation |
| Supply chain | Pinned Python dependencies, Ruff, mypy, Bandit, pip-audit, source audit, test coverage gate, and CI artifact capture |

The detailed implementation and operator assumptions are documented in [`docs/security_hardening.md`](docs/security_hardening.md) and [`ARCHITECTURE.md`](ARCHITECTURE.md). The presence of a control does not eliminate deployment-specific risk; do not use model output as the sole basis for high-impact decisions.

## References

Repository security design is mapped to the course and operational evidence in [`docs/compliance_matrix.md`](docs/compliance_matrix.md) [SRC-003] and [`docs/sources.md`](docs/sources.md).
