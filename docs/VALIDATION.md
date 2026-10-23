# Validation ledger

Record date, exact scope, observed result and limitations. A configuration file is not proof of enforcement.

This ledger is chronological. Early failures and pending work describe those stages;
the later successful checks supersede them. See STATUS.md for the current handoff state.

## Initial inventory and local checks (historical)

| Date | Check | Observed result |
|---|---|---|
| 2026-10-23 | Windows tool inventory | Git, Python, SSH, VMware present; Docker/kubectl/gh absent; WSL not installed |
| 2026-10-23 | GitHub connector | Authenticated identity available; repository listing empty |
| 2026-10-23 | Ubuntu VM definition | 2 vCPU / 6 GiB / NAT; guest runtime unverified at initial inventory |
| 2026-10-23 | Application and policy tests | 8 passed, including database outage and rejection of privilege escalation/mutable action |
| 2026-10-23 | Ruff | Passed after targeted CI tooling annotations |
| 2026-10-23 | Gitleaks worktree | Passed; downloaded third-party tool examples excluded by directory scope |
| 2026-10-23 | Trivy configuration HIGH/CRITICAL | Passed: 5 configuration files detected |
| 2026-10-23 | Kustomize | Lab overlay rendered successfully |
| 2026-10-23 | Linux inspection | SSH verified; kernel 6.8, Docker 29.1.3, Wazuh agent active; existing n8n preserved |

At this initial stage, the real database, containers, full scans, cluster enforcement,
rollback and Wazuh ingestion were pending. Their subsequent results are recorded below.

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
Traefik and ServiceLB disabled. Application and Flux deployment followed in later stages.

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
Application log collector was active; Wazuh ingestion was verified in the later live checks.

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
the database image was subsequently rebuilt without the vulnerable executable. Promotion
remained blocked until that rebuilt image passed scanning and integration.

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

## Rejected change and recovery demonstration

[PR #2](https://github.com/benalifathia08-source/secure-delivery/pull/2) introduced a deliberately
synthetic, nonfunctional credential and a privileged workload change. Its
[run 39972343014](https://github.com/benalifathia08-source/secure-delivery/actions/runs/39972343014)
failed the expected secret/configuration gates; promotion was skipped. The PR was closed
without merging. [Sanitized gate results](../evidence/rejected-demo.json).

[Run 39972006316](https://github.com/benalifathia08-source/secure-delivery/actions/runs/39972006316)
published version 0.1.1. Its configured digest matched the runtime image ID. The rollback
script restored a previously approved release through a new Git commit, and Flux returned
the application to 0.1.0 with matching runtime digest. Restoring the current approved release
returned the application to 0.1.1. See [before](../evidence/release-before-rollback.json),
[rollback action](../evidence/rollback-action.json), [after](../evidence/release-after-rollback.json),
and [restored current](../evidence/release-restored-current.json).

Main branch protection was applied through GitHub's API and read back: verify is bound to
the GitHub Actions app, strict up-to-date checks and pull requests are required, admin
enforcement is enabled, and force pushes/deletion are disabled. Solo-lab approval count is zero.
Dependency vulnerability alerts are enabled. No public self-hosted runner or paid service was used.

## Final dependency review and repeat verification

[Dependabot PR #1](https://github.com/benalifathia08-source/secure-delivery/pull/1) was
reviewed, updated against protected main, passed [run 39980590984](https://github.com/benalifathia08-source/secure-delivery/actions/runs/39980590984)
and merged. The new main [run 39981257611](https://github.com/benalifathia08-source/secure-delivery/actions/runs/39981257611)
passed all sixteen gates and promoted both images. [Gate evidence](../evidence/dependency-update-ci.json).

At 15:53 UTC on 2026-10-23, the final lab checks verified application 0.1.1 with Gunicorn
26.2.0 and HTTP readiness 200; both configured image digests matched the running images.
Both Flux resources were Ready at revision 35002860fee06aff4d06285ed087e7ec52289726.
All five application-VM services were active, the existing n8n container was running,
and no demonstration resources or temporary restore databases remained.
[Health evidence](../evidence/final-live-check.json).

The repeated [cluster checks](../evidence/final-cluster-verification.json) passed Restricted
admission, reconciler boundaries, authorized access, unauthorized access denial and the runtime
canary trigger. Fresh rule 112300 and 112301 timestamps were verified in the Wazuh indexer
after that test started, using validated TLS and local certificate authentication.
[Indexed evidence](../evidence/final-indexed-alerts.json).

The final PostgreSQL backup was 3,052 bytes, mode 0600, and restored one inventory row into
a disposable database that was subsequently removed. [Backup evidence](../evidence/final-backup-restore.json).
Main protection was re-read and still requires the strict Actions verify check and a PR,
including administrators. [Protection evidence](../evidence/final-branch-protection.json).

Local checks after updating the lockfile: ten tests passed, Ruff and repository policy passed,
and Gitleaks found no secrets in HEAD ancestry or the worktree. Relative documentation links
were also checked. These local checks supplement the hosted container and scanner evidence.

Both guest operating systems were then instructed to shut down gracefully. At 15:54:49 UTC,
VMware listed zero running VMs; no forced power-off was used. The shared n8n workload is
paused with Ubuntu. Disks, the PVC and private on-VM backups were retained.
[Shutdown evidence](../evidence/final-power-state.json).
Final documentation/evidence publication follows shutdown; later approved promotions wait
for the next VM startup and are not represented as already verified live here.
