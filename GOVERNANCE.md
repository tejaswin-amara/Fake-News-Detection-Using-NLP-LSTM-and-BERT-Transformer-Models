# Governance

## Purpose

This governance model keeps repository decisions traceable, reproducible, and aligned with the documented ML-engineering and course-compliance boundaries. It favors small, reviewable changes over undocumented policy or architecture changes.

## Roles

| Role | Responsibility | Decision scope |
|---|---|---|
| Repository owner | Maintains repository settings and protected branch policy | Final merge and release decisions |
| Maintainers | Review code, documentation, security implications, and reproducibility evidence | Approve, request revision, defer, or decline changes |
| Contributors | Propose, implement, test, and document focused changes | Open pull requests and RFC-style proposals |
| Reviewers | Provide evidence-based feedback within their expertise | Recommend acceptance, revision, or alternatives |

The repository does not currently define a separate technical steering committee, formal voting body, or automated release manager. Roles are assigned by repository access and participation rather than a public roster.

## Decision process

Routine fixes and documentation changes are proposed through focused pull requests. Material changes to data provenance, split policy, model architecture, evaluation protocol, serving contract, monitoring threshold, artifact format, or deployment topology should begin with an RFC-style GitHub issue. The issue should state the problem, decision drivers, considered options, risks, migration path, tests, documentation impact, and source-register changes.

Maintainers record accepted irreversible or cross-cutting decisions in `docs/ADR/`. The initial technology decision is [`docs/ADR/0001-initial-tech-stack.md`](docs/ADR/0001-initial-tech-stack.md). Superseding decisions should reference the earlier ADR rather than silently rewriting history.

## Consensus and escalation

The preferred outcome is documented consensus after maintainers have considered evidence and reviewer feedback. When consensus is not reached, the repository owner makes the final decision and records the rationale in the pull request, issue, or ADR. Security reports follow [`SECURITY.md`](SECURITY.md) and are not handled through public RFCs.

## References

This governance policy is constrained by the contribution process in [`CONTRIBUTING.md`](CONTRIBUTING.md), the source-governance register in [`docs/sources.md`](docs/sources.md), and the course evidence matrix [SRC-003].
