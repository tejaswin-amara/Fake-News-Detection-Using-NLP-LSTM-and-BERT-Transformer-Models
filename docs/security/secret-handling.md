# Secret Detection and Credential-Exposure Response

This repository treats secret scanning as a preventive control and a signal for private incident response. It does not create or store test credentials, use broad ignore files, add a baseline, or permit inline `gitleaks:allow` comments for repository content. The immutable weekly, push, pull-request, and manually dispatched workflow scans complete Git history without preserving checkout credentials.[SRC-054]

## Prevention boundary

Credentials, API tokens, private URLs, signing keys, DVC remote details, connection strings, session material, model artifacts, raw datasets, and raw article text must not be committed. Examples and tests use neutral placeholders that cannot authenticate. The workflow has read-only permissions, checks out with `persist-credentials: false`, and does not upload a finding artifact because even a redacted report is not a substitute for disciplined incident handling.

| Situation | Required action | Prohibited action |
|---|---|---|
| Local change may contain a credential | Stop before commit; remove the value, replace it with a neutral placeholder, and run the relevant local/review checks. | Do not add an ignore, baseline, or inline allow comment. |
| Workflow reports a potential secret | Treat it as sensitive; halt public discussion of the value, determine whether it can authenticate, and follow the private route in `SECURITY.md`. | Do not paste logs, the candidate value, or a report excerpt into an issue, pull request, commit, or chat. |
| Credential is confirmed or plausibly exposed | Revoke/rotate at the owning provider, invalidate dependent sessions, assess repository and artifact history, and document only redacted remediation evidence. | Do not rely on history rewrite, file deletion, or a scan suppression as proof that the credential is safe. |
| False positive is demonstrated | Improve the non-secret placeholder or surrounding text so it is unambiguous, then retain the scan. | Do not introduce broad config allowlists or a generic baseline. |

## Evidence and ownership

The repository owner controls provider credentials, GitHub secrets, branch-protection settings, and private incident coordination. Contributors supply a focused pull request with source-governed documentation and tests; they cannot claim that a credential is rotated, an alert is closed, or an independent reviewer approved a change without owner or GitHub evidence.

The workflow augments rather than replaces CodeQL, Bandit, pip-audit, hash locks, container scanning, ClusterFuzzLite, review, or standard secret-management practices. It must remain immutable-pinned, least-privilege, and free of unreviewed exceptions.[SRC-054]
