# Code-Scanning and Scorecard Remediation Ledger

## Purpose and evidence boundary

This ledger records the repository's **evidence-based** disposition of supply-chain and code-scanning findings. It does not suppress, waive, or fabricate review evidence for any finding. The comparison uses the initial Scorecard SARIF evidence and the current SARIF published by the successful [OpenSSF Scorecard run][1] for main commit `13fd56d55183035bccf6cacc3ce82dc24bcb229f` on 2026-08-23. The current run contains **6** advisory entries, down from **30** in the initial SARIF: the Fuzzing finding was removed, all 23 PinnedDependencies advisories were removed, and the Vulnerabilities score increased from 0 to 9. The remaining entries are described below exactly as reported by Scorecard.

| Evidence item | Initial state | Final state | Disposition |
|---|---:|---:|---|
| SARIF advisory entries | 30 | 6 | Measured reduction of 24 entries; no SARIF finding was filtered or dismissed. |
| `FuzzingID` | 1 | 0 | Resolved through a real ClusterFuzzLite Python/Atheris integration. |
| `PinnedDependenciesID` | 23 | 0 | Automated pip installs now use complete, reviewed Linux/Python 3.11 transitive hash locks. |
| `VulnerabilitiesID` | 1 | 1 | Score improved from 0 to 9; one upstream-constrained cryptography advisory remains. |
| `SASTID`, `CITestsID`, `CodeReviewID`, `MaintainedID`, `CIIBestPracticesID` | 5 | 5 | Historical, governance, age, or external-program controls requiring time or owner action. |

## Implemented remediation record

The following pull requests were merged through protected main after their required CI, CodeQL, and container checks passed. The actions are traceable through GitHub pull requests #17–#23; their current result is independently captured in the current Scorecard run.[1]

| Finding family | Root cause | Implemented remediation | Validation evidence | Current disposition |
|---|---|---|---|---|
| Mutable GitHub Actions and Python container base | Version tags and a mutable image tag allowed supply-chain drift. | Every active action now uses a verified 40-character commit reference, and each Python 3.11-slim stage uses an immutable digest. Regression tests verify every active `uses:` line and base-image digest. | PR #17; final Scorecard has no mutable-action advisory. | **Resolved.** |
| Vulnerable direct dependencies | Initial pins were within documented OSV-affected ranges. | Updated compatible direct pins, including MLflow 3.15.1, ONNX 1.22.0, PyTorch 2.13.0, FastAPI 0.141.1, TensorFlow CPU 2.21.0, python-multipart 0.0.32, and the highest MLflow-compatible cryptography release, 49.0.0. Removed unused `torchaudio` and `torchvision` pins. | PRs #18 and #21; development/runtime resolver checks; final Scorecard vulnerability score 9. | **Substantially remediated; one upstream-constrained advisory remains.** |
| MLflow 3 local-file-store incompatibility discovered during dependency remediation | MLflow 3 rejects filesystem metadata stores by default. | Local tracking, report generation, and the CI fixture now use SQLite metadata with file artifacts; regression tests cover the fixture and report path. | PR #21; protected-main quality job passed. | **Resolved.** |
| Scorecard Fuzzing | A deterministic parser fuzz job was not recognized as coverage-guided fuzzing by Scorecard. | Added a bounded ClusterFuzzLite Python/Atheris metadata fuzzer with an immutable action pin, immutable builder digest, weekly/manual trigger, and 60-second budget. It handles synthetic in-memory ClaimReview metadata only. | PR #20; final SARIF omits `FuzzingID`; implementation guidance is registered as [SRC-051](../sources.md#src-051--clusterfuzzlite-python-integration). | **Resolved.** |
| Complete dependency integrity locks | Seven automated `pip` commands were directly pinned but lacked complete, transitive hash coverage. | Added reviewed Linux x86_64/Python 3.11 `uv`-generated SHA-256 locks for development, runtime, and synthetic parser fuzzing. The Docker build, CI, deterministic fuzz workflow, and ClusterFuzzLite builder use `--require-hashes`; runtime/fuzzing also use `--only-binary=:all:`. The required source-only ANTLR development package remains hash-verified and is explicitly documented. | PR #23; Linux/Python 3.11 dry-run resolver checks; 142 local regression tests at 95.02% coverage; protected-main CI, CodeQL, and rootless container scan all passed; current SARIF omits `PinnedDependenciesID`. Lock maintenance is documented in [SRC-053](../sources.md#src-053--complete-python-dependency-hash-locks). | **Resolved.** |

## Remaining final-SARIF entries

`VulnerabilitiesID` now reports only [PYSEC-2026-3552][3], which affects `cryptography==49.0.0` and is fixed in 50.0.0. The current MLflow 3.15.1 release constrains `cryptography` to `<50`, so moving the repository to 50.0.0 causes resolver failure. The project retains the highest resolver-compatible pin and records the issue transparently. Clearing this finding requires either an upstream MLflow release that permits cryptography 50 or a reviewed architectural replacement/removal of the MLflow dependency; this repository does **not** bypass the resolver or ignore the advisory.

| Rule | Exact final Scorecard condition | Why it remains | Required next action | GitHub disposition |
|---|---|---|---|---|
| `VulnerabilitiesID` | One advisory: `PYSEC-2026-3552` | `cryptography` 50.0.0 is incompatible with MLflow 3.15.1's `<50` bound. | Monitor MLflow releases; re-resolve and upgrade immediately when the bound permits the fixed cryptography version, or formally redesign the dependency boundary. | Open upstream dependency constraint; no ignore rule. |

### Historical, governance, and external-program controls

Scorecard's remaining non-file advisories are correctly preserved because code changes cannot retroactively create review approvals, age the repository, backfill CI coverage, or enroll it in an external badge program. The controls remain operational: main is protected, CI and CodeQL run on pull requests, and no pull request is represented as human-reviewed when it was not.

| Rule | Exact final Scorecard condition | Code remediation status | Owner action required |
|---|---|---|---|
| `SASTID` | SAST ran on 21 of 26 commits. | CodeQL runs on current pull requests and main; historical commits cannot be retroactively changed. | Maintain the required CodeQL checks on every future change. |
| `CITestsID` | CI tested 16 of 19 merged pull requests. | Current protected-main CI is required; the score is historical. | Maintain required checks for every future pull request. |
| `CodeReviewID` | 0 of 15 approved changesets. | No review evidence was fabricated. | Configure a trusted second reviewer and require at least one approval for future changes. |
| `MaintainedID` | Repository is younger than 90 days. | Time-bound; no safe code change applies. | Re-evaluate after the 90-day age threshold. |
| `CIIBestPracticesID` | No OpenSSF Best Practices badge effort detected. | External program enrollment cannot be claimed by repository code. | Owner may enroll and complete the program separately. |

## Verification record

The current Scorecard run completed successfully. The complete hash-lock remediation pull request also passed the repository's protected-main quality, CodeQL Python, CodeQL Actions, rootless container-build, and critical-vulnerability scan checks before merge. Local validation for that pull request included development/runtime/fuzz Linux-Python 3.11 lock dry-run checks, 142 regression tests at 95.02% coverage, Ruff, mypy, Bandit, source governance, workflow YAML parsing, and whitespace checks. `pip-audit` remains unsuppressed; its residual cryptography and transitive diskcache findings are not treated as resolved by this document.

Future remediation should begin from a newly downloaded SARIF artifact rather than relying on this snapshot, because Scorecard scores and vulnerability databases change over time.

## References

[1] Current [OpenSSF Scorecard workflow run](https://github.com/tejaswin-amara/Fake-News-Detection-Using-NLP-LSTM-and-BERT-Transformer-Models/actions/runs/32641697857), accessed 2026-08-23. Registered as SRC-052.

[2] OpenSSF Scorecard [checks documentation](https://github.com/ossf/scorecard/blob/main/docs/checks.md), accessed 2026-08-22. Registered as SRC-052.

[3] OSV advisory [PYSEC-2026-3552](https://osv.dev/PYSEC-2026-3552), accessed 2026-08-22. Registered as SRC-052.
