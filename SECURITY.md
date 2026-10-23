# Security policy

## Release gates

| Gate | Blocking policy |
|---|---|
| Gitleaks | Any unapproved secret finding in worktree or Git history |
| Trivy dependencies / image | HIGH or CRITICAL vulnerabilities, including unfixed findings |
| Trivy configuration | HIGH or CRITICAL misconfigurations |
| Checkov | Any failure in the explicitly selected Kubernetes baseline |
| ZAP | Medium or High alerts; execution errors or required endpoint failures |
| Application | Unit tests, readiness, real database read-only identity |
| Repository policy | Mutable action references, privilege escalation, missing restrictions |

Low ZAP findings remain visible in reports. Checkov is intentionally a selected baseline,
not a claim of passing every policy. See `.checkov.yaml` for exact policy IDs.

The one current exception permits PostgreSQL's official non-root UID 70 for CKV_K8S_40;
it is scoped to that StatefulSet and expires 2026-11-22. `security/exceptions.json` is the review ledger,
not an automatic suppression mechanism. A future exception must identify its tool, finding,
scope, reason, owner and expiry, and be applied explicitly in the relevant scanner configuration.
Expired exceptions fail repository policy. Never use broad blanket suppressions.

Reports are retained as workflow artifacts for seven days. Gitleaks output is redacted.
Do not upload real credentials or unsanitized lab logs as evidence.

## Disclosure

For a real credential exposure, revoke the credential before attempting history cleanup.
Do not include credentials in public issues. Use GitHub private vulnerability reporting if
enabled. This is a learning lab; there is no production service or SLA.
