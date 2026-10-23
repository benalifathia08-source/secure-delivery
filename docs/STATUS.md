# Project status

Updated: 2026-10-23 (Africa/Tunis).

**State: application and pipeline implementation ready for first hosted CI run. Not yet deployed.**

| Milestone | State | Completion evidence required |
|---|---|---|
| M0 — Inventory and architecture | Complete | SSH verified, 24 GiB host, Linux resources and existing workloads inspected |
| M1 — Application and database | Complete | Hosted container startup, PostgreSQL readiness and SELECT-only role verified |
| M2 — Security gates | In progress | Local Gitleaks and Trivy configuration pass; hosted integration pending |
| M3 — k3s and Flux delivery | In progress | k3s healthy; Flux installation and first approved promotion pending |
| M4 — Falco and Wazuh | In progress | Falco 0.45.1 active with modern eBPF; Wazuh rules and collection being configured |
| M5 — Portfolio release | Planned | Published GitHub repository, protected branch, complete evidence |

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
- Database-image scanning identified vulnerable unused gosu; a non-root derived image now
  removes that executable and is included in the same scan/test/promotion flow.

See [BACKLOG.md](BACKLOG.md), [DECISIONS.md](DECISIONS.md), and [VALIDATION.md](VALIDATION.md).
