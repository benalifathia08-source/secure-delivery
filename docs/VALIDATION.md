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

## First hosted run — release rejected

[Run 39961617144](https://github.com/benalifathia08-source/secure-delivery/actions/runs/39961617144)
passed unit tests, lint, repository policy, both secret scans, dependency scanning and Trivy
configuration scanning. Checkov flagged PostgreSQL UID 70, Trivy rejected the Debian image's
unfixed HIGH/CRITICAL OS findings, and integration exposed a copied virtual-environment path
error. Publication and promotion did not run. These findings drive fixes; the gate thresholds
remain unchanged.

## k3s bootstrap

Checksum-verified k3s v1.37.1+k3s1 installed on the approved Ubuntu VM. Node is Ready;
CoreDNS, metrics-server and local-path-provisioner are Running after correcting API binding.
Existing n8n container remained running. Secrets encryption enabled; kubeconfig mode 0600.
Traefik and ServiceLB disabled. Application and Flux are not yet deployed.

## Second hosted run

[Run 39962842540](https://github.com/benalifathia08-source/secure-delivery/actions/runs/39962842540)
passed all static gates, container build and Trivy image scan. The candidate ran as non-root
with a read-only root, reached PostgreSQL, and its database role was denied INSERT.
ZAP completed active/passive scans and produced HTML/JSON reports; HTTP-only on the isolated
test address was the sole Medium finding. Release remained blocked pending scoped EX-002.

## Runtime sensor and collection preparation

Falco 0.45.1 was installed through its signed APT repository after verifying the current
signing-key fingerprint. Modern eBPF is active on kernel 6.8; the canary rule and JSON output
configuration validate. Automatic rule-following is disabled for reproducibility.
The package manager briefly restarted the existing Sysmon service; its configuration was
not changed. Subsequent bootstrap runs request list-only handling of unrelated service restarts.
Application log collector is active. End-to-end Wazuh events are not yet verified.

The third hosted run completed ZAP successfully but rejected platform networking reconciliation
permissions. EX-003 documents that required, namespace-scoped controller privilege.
