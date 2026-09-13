# API Security, Privacy, and Observability Operations

The FastAPI service is a bounded classification interface, not a claim-verification authority or a raw-text storage service. The service's public contract, request validation, generic errors, CORS configuration, rate limits, security headers, readiness, structured logging, and metrics implement a narrow defense-in-depth layer informed by OWASP API, REST, and logging guidance.[SRC-055]

## Public API boundary

| Surface | Contract | Privacy and security rule |
|---|---|---|
| `/health` | Returns non-sensitive service state and public model metadata. | Never exposes artifact paths, exception details, provider configuration, credentials, or raw input. |
| `/ready` | Returns `200` only after model load and warm-up; otherwise returns a generic `503`. | Readiness failures remain diagnosable through protected logs, not client-visible exception text. |
| `/predict` and `/predict/batch` | Accept strict bounded JSON models only. | Require `application/json`, reject unknown fields/control characters/oversize inputs, and do not log request text. |
| `/monitoring/drift` | Queues bounded statistical monitoring. | Drift is a human-review signal, not automatic retraining; queue identifiers and aggregate results do not authorize retention of request bodies. |
| `/metrics` | Exposes Prometheus-format aggregate metrics. | Excluded from OpenAPI and requires deployment-level access control when exposed outside a trusted network. |

Every finalized API response includes a request identifier, measured process time, `Cache-Control: no-store`, anti-framing headers, no-referrer policy, and MIME-sniffing protection. CORS origins are configuration-controlled; wildcards cannot be combined with credentials. These headers complement, but do not replace, TLS termination, ingress policy, authentication, network boundaries, and operator-configured secrets.[SRC-055]

## Metrics and logging contract

| Signal | Meaning | Allowed labels/fields | Explicit exclusions |
|---|---|---|---|
| `fake_news_http_request_latency_seconds` | Request latency by method, normalized route, and status. | Method, normalized route, status. | Query strings, raw URL values, request body, client text, token, identity. |
| `fake_news_inference_latency_seconds` | Native/ONNX inference latency. | Endpoint class and serving mode. | Input text, prediction body, model path, artifact signature. |
| `fake_news_inference_queue_depth` | Current bounded inference admission backlog. | None. | Caller identity and payload. |
| `fake_news_drift_queue_depth` and `fake_news_drift_monitoring_errors` | Bounded drift-worker capacity and errors. | None. | Drift request texts, numeric arrays, exceptions, job payloads. |
| `fake_news_rate_limiter_rejections` | Aggregate rate/admission rejection reason. | Controlled reason enum. | Client IP, request ID, raw path/query, header value. |
| Structured request logs | Request lifecycle and security-relevant events. | Request ID, method, normalized route, status, latency, controlled reason. | Article body/title, authorization/API keys, cookies, connection strings, stack traces in client responses. |

The request identifier supports correlation of protected logs for one interaction. It is sanitized and length-bounded before use. A request ID is operational metadata, not an authentication credential or an invitation to persist client payloads. Log/metric changes must be reviewed for cardinality and privacy before merge. **Raw article text is categorically excluded** from the telemetry contract.[SRC-055]

## Operational response guide

| Signal or event | First action | Escalation boundary |
|---|---|---|
| `/ready` returns `503` | Check protected deployment logs for model-load/warm-up status and verify signed artifact/configuration availability. | Do not reveal the exception, artifact path, or signing material to API clients. Roll back to a verified artifact if recovery requires it. |
| Sustained `429` from rate or inference admission | Confirm expected traffic, configured rate/window/inflight limits, and resource saturation. | Scale or tune only through reviewed deployment/config changes; do not disable bounded admission control. |
| Drift queue full or error counter rises | Inspect worker health and aggregate queue conditions. | Treat drift output as a review signal; never auto-promote/retrain a model from this event. |
| Redis circuit opens | Confirm dependency health while inference fails open as designed. | Restore Redis/circuit configuration through reviewed change; retain the critical structured signal. |
| Potential credential or raw-text disclosure | Stop broader disclosure and follow `docs/security/secret-handling.md` and `SECURITY.md`. | Rotate/revoke actual credentials with the owner/provider; never use an ignore or log deletion as closure. |

## Platform-adoption gate

The current service does not need an external queue, gateway, analytics product, object store, scheduler, or event bus merely to collect metrics. Any proposed platform must satisfy the trigger and ADR process in [`docs/developer-pipeline-adoption.md`](../developer-pipeline-adoption.md), including ownership, capacity, authentication, retention, licensing, and raw-text exclusion. A monitoring need is not by itself permission to persist raw prediction or drift payloads.
