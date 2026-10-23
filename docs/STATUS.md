# Project status

Updated: 2026-10-23 (Africa/Tunis).

**State: initial project scope complete and verified. Application version 0.1.1 is healthy.
Repository changes use protected pull requests; ongoing maintenance remains tracked below.**

| Milestone | State | Completion evidence required |
|---|---|---|
| M0 — Inventory and architecture | Complete | SSH verified, 24 GiB host, Linux resources and existing workloads inspected |
| M1 — Application and database | Complete | Hosted container startup, PostgreSQL readiness and SELECT-only role verified |
| M2 — Security gates | Complete | Hosted run 39967961637 passed all gates, including real negative fixtures |
| M3 — k3s and Flux delivery | Complete | Dual-image rollout, admission/RBAC/network tests and durable GitOps rollback verified |
| M4 — Falco and Wazuh | Complete | Runtime and application events verified in Wazuh indexer over validated TLS |
| M5 — Portfolio release | Complete | Public repository, required verify check, admin-enforced protection, runbooks and sanitized evidence |

## Inventory

- Windows host: Git 2.55.0, Python 3.12.10, SSH and VMware Workstation available.
- Docker, kubectl, GitHub CLI and working WSL installation not found on PATH.
- Ubuntu VM: 2 virtual CPUs, 6 GiB memory, NAT networking; SSH verified with existing key.
- Linux kernel 6.8.0-147-generic, Docker 29.1.3 and active Wazuh agent verified.
- Existing n8n Docker workload is outside this project's scope; keep it running.
- Ubuntu disk has approximately 13 GiB free before cluster installation.
- Existing Wazuh VM and prior SOC lab documentation found; services not yet verified.
- GitHub connector identifies the account but lists no accessible repositories. Git credential
  manager provides working CLI authentication without exposing credentials.
- Local dependency tooling is installed under ignored `.tools/`.
- Eight local application/policy tests pass; lint passes; Kustomize renders successfully.
- Official checksums verified for local GitHub CLI, Gitleaks, Trivy and kubectl downloads.
- Public repository created; hosted gates execute and block releases on findings.
- k3s v1.37.1+k3s1 and both Flux v2.9.6 controllers are healthy.
- Wazuh manager, indexer and dashboard are active; manager reports 4.14.8.
- Falco 0.45.1 installed from its signed repository; modern eBPF and JSON output active.
- Controlled canary event verified in Wazuh: rule 112300, level 10, JSON decoder.
- Live Restricted admission and reconciler RBAC negative tests passed.
- Allowed pod-to-application access succeeded; equivalent unauthorized connection was rejected.
- PostgreSQL backup restored into a disposable database with the expected release inventory.
- Database-image scanning identified vulnerable unused gosu; a non-root derived image now
  removes that executable and is included in the same scan/test/promotion flow.
- Ten application/policy/promotion unit tests pass; all sixteen hosted gate stages passed.
- The deliberately insecure PR was rejected and closed without merging.
- GitOps rollback restored 0.1.0 from 0.1.1; restoring the current approved release returned 0.1.1.
- Main requires an up-to-date successful verify check and a pull request, including for admins;
  force pushes and deletion are disabled. No additional human approval is required in this solo lab.

## Ongoing maintenance

Review the open dependency update PR and the three exceptions before 2026-11-22.
Off-host backups, scheduled rescanning and signed-image admission are optional next enhancements,
not claims made by this version. The Wazuh and application VMs remain running for demonstration.

See [BACKLOG.md](BACKLOG.md), [DECISIONS.md](DECISIONS.md), and [VALIDATION.md](VALIDATION.md).
