# Validation ledger

Record date, exact scope, observed result and limitations. A configuration file is not proof of enforcement.

| Date | Check | Observed result |
|---|---|---|
| 2026-10-23 | Windows tool inventory | Git, Python, SSH, VMware present; Docker/kubectl/gh absent; WSL not installed |
| 2026-10-23 | GitHub connector | Authenticated identity available; repository listing empty |
| 2026-10-23 | Ubuntu VM definition | 2 vCPU / 6 GiB / NAT; guest runtime unverified |

| 2026-10-23 | Application and policy tests | 8 passed, including database outage and rejection of privilege escalation/mutable action |
| 2026-10-23 | Ruff | Passed after targeted CI tooling annotations |
| 2026-10-23 | Gitleaks worktree | Passed; downloaded third-party tool examples excluded by directory scope |
| 2026-10-23 | Trivy configuration HIGH/CRITICAL | Passed: 5 configuration files detected |
| 2026-10-23 | Kustomize | Lab overlay rendered successfully |
| 2026-10-23 | Linux inspection | SSH verified; kernel 6.8, Docker 29.1.3, Wazuh agent active; existing n8n preserved |

Pending: real database, container build, image/dependency scans, Checkov, ZAP, Actions,
k3s, Flux, network enforcement, rollback, Falco, Wazuh alert ingestion.
