# Engineering decisions

## ADR-001 — GitHub-hosted CI and Flux deployment

Accepted 2026-10-23. Run untrusted pull-request work on disposable hosted runners. No public-repository self-hosted runner with lab access. Flux pulls approved deployment configuration; the Kubernetes API remains private. Promotion must depend on every security gate and reference the tested image digest. Flux is not itself a vulnerability gate.

## ADR-002 — Small read-only application

Accepted 2026-10-23. Use a Flask release inventory backed by PostgreSQL. Keep product behavior deliberately small so security controls are the focus. A SELECT-only database identity demonstrates least privilege. Credentials are generated locally and never committed. This is a local security lab, not an AWS/Azure production system.

## ADR-003 — Linux VM and k3s

Accepted 2026-10-23. Prefer an isolated Linux VM to installing a second virtualization stack on Windows. k3s provides network policy enforcement. Existing SOC workloads must not be modified until host identity and resource suitability are verified.

## ADR-004 — Complementary scanners

Accepted 2026-10-23. Gitleaks checks secrets; Trivy checks dependencies, images and configuration; Checkov checks a documented Kubernetes baseline; ZAP tests the running candidate; Falco detects runtime behavior. No blanket ignores or automatic suppression of unfixed vulnerabilities. Scanner infrastructure failure must block the release.

## ADR-005 — Host Falco and Wazuh collection

Accepted 2026-10-23. Prefer host-installed Falco writing JSON lines, collected by the existing Wazuh agent. This avoids weakening the application's Restricted namespace for a privileged sensor. Verify kernel compatibility and Wazuh field decoding before recording success.
