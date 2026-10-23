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

## Live runtime and access-control evidence

On 2026-10-23 at 14:02 UTC, a disposable Restricted pod read the harmless canary path.
Falco emitted `Secure Delivery Canary Read`; Wazuh decoded the event as JSON and fired
rule 112300 at level 10. [Sanitized alert](../evidence/runtime-detection.json).
The same run verified rejection of a privileged pod by Pod Security Admission and denial
of reconciler access to Secrets, other namespaces, and RoleBindings.
[Cluster checks](../evidence/admission-rbac-runtime.json).

The fourth hosted run passed ZAP and scanner negative tests. It rejected the database's
unused vulnerable gosu binary and an unsupported Trivy CLI flag. The flag was removed;
the database image is being rebuilt without the vulnerable executable. Promotion remained blocked.

## Successful secure delivery and enforcement

[Run 39967961637](https://github.com/benalifathia08-source/secure-delivery/actions/runs/39967961637)
passed all gates and promoted both immutable image digests. Flux applied the release; application
and database are Ready. [CI summary](../evidence/ci-gates.json),
[scanner rejection tests](../evidence/scanner-negative-tests.json).

At 14:31 UTC the live cluster test verified authorized application access, denied unauthorized
access, Restricted admission, scoped reconciler permissions, and another runtime canary trigger.
[Network evidence](../evidence/network-isolation.json).

Wazuh indexer was queried with local admin certificate authentication and validated server TLS.
Both rules 112300 (runtime) and 112301 (application) were present.
[Sanitized indexed events](../evidence/indexed-alerts.json).

A PostgreSQL custom-format backup was stored locally with mode 0600 and restored into a uniquely
named disposable database. The restored inventory contained the expected data; the temporary
database was removed. [Restore evidence](../evidence/backup-restore.json).
