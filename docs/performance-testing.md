# Bounded Performance Testing

The repository provides one **manually dispatched** k6 smoke profile at `tests/performance/api_smoke.js`. It is not a pull-request, scheduled, or production-default workload. The profile sends exactly three requests through one virtual user, has a 30-second maximum duration, uses synthetic text only, and retains no raw article body, token, or response payload. k6 scenarios bound workload shape, while thresholds make the configured response/error criteria affect the process exit status.[SRC-056]

## Authorization boundary

The workflow requires both an explicit target URL and a manual `yes` authorization input. The person dispatching it must own the target or have written authorization, verify available capacity, confirm the service is intended for this test, and ensure that test traffic cannot cause retention of real article text or credentials. Do not target a third-party service, shared production system, or a local address that GitHub-hosted runners cannot reach.

| Profile | Workload | Permitted use | Escalation requirement |
|---|---|---|---|
| `metadata_only_smoke` | 1 virtual user, 3 synthetic `/predict` requests, 30-second maximum duration | Contract and baseline responsiveness check against an authorized controlled endpoint | None beyond the workflow authorization inputs and documented capacity review |
| Any stronger profile | More users, requests, duration, endpoints, or a production target | Not included by default | New ADR, target owner consent, capacity plan, privacy review, explicit rate/duration bounds, and protected-main review |

The profile asserts successful JSON responses, zero HTTP failures, and a bounded 95th-percentile request duration. These are smoke-test thresholds, not a production SLO or a performance claim. Environment, model artifact, runner, and target network conditions materially affect measured latency.[SRC-056]

## Local execution

Install k6 through an approved local package route, start an authorized local FastAPI instance, and run only with explicit environment variables:

```bash
K6_TARGET_URL=http://127.0.0.1:8000 \
K6_AUTHORIZE_TARGET=yes \
k6 run tests/performance/api_smoke.js
```

The script rejects absent/non-HTTP targets and refuses to run without `K6_AUTHORIZE_TARGET=yes`. Do not replace the synthetic fixture with a real article, user-submitted text, credential, or production example.
