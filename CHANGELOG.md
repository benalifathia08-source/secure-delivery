# Changelog

## Maintenance — 2026-11-27

- New HIGH CVEs in Alpine packages (krb5-libs, libxml2, libxslt) blocked every candidate at the
  Trivy image gates. Both images now apply published Alpine fixes at build time (ADR-018).
- Reviewed EX-001, EX-002 and EX-003 after they expired and blocked releases; renewed to 2027-02-27.
- Consolidated project documentation and removed internal working notes.

## 0.1.1 maintenance — 2026-10-23

- Reviewed Gunicorn 26.2.0 update, full PR/main gates and live deployment verification.
- Repeated admission, RBAC, networking, runtime telemetry and backup/restore checks.
- Clarified the retained PostgreSQL identity exception and added a written demonstration.

## 0.1.1 — 2026-10-23

- Flask release inventory and PostgreSQL with a SELECT-only application identity.
- Sixteen fail-closed CI gate stages covering tests, repository policy, secrets, vulnerabilities,
  rendered configuration, real scanner negative fixtures, container integration and ZAP.
- Separate publication of the tested app/database image digests and scoped Flux reconciliation.
- Restricted k3s workloads, resource boundaries, default-deny networking and tested access controls.
- Falco modern-eBPF detection, selected application logs, and verified Wazuh indexing.
- Tested database backup/restore and durable GitOps rollback, with sanitized evidence.
- Protected main branch, expiring exceptions, operational runbooks and a backlog.
