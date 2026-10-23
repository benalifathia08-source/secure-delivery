# Project completion report

Date: 2026-10-23. Scope: a cloud-native application security lab on local hardware.

## Delivered

| Area | Completed work and evidence |
|---|---|
| Application | Containerized Flask release inventory API, PostgreSQL, SELECT-only application identity and separate readiness/liveness checks |
| CI security | Sixteen fail-closed gate stages: tests, repository policy, Gitleaks worktree/history, Trivy dependencies/configuration/both images, Checkov, real negative fixtures, integration and ZAP |
| Delivery | Public GitHub repository, protected main, full-SHA actions, immutable image digests, tested dual-image publication and a minimal provenance-bearing Flux release branch |
| Kubernetes | k3s, Restricted admission, scoped reconciler RBAC, non-root read-only workloads, resource limits, default-deny networking and verified allow/deny connectivity |
| Runtime visibility | Host Falco modern eBPF, controlled canary detection and selected application logs forwarded into the existing Wazuh lab; both event types verified in the indexer |
| Recovery | Private PostgreSQL backup restored into a disposable database; durable approved-release GitOps rollback from 0.1.1 to 0.1.0 and back |
| Portfolio | Architecture, decisions, threat model, exception ledger, living backlog, operational runbooks, written demonstration and sanitized evidence |

The intentionally insecure [demonstration PR #2](https://github.com/benalifathia08-source/secure-delivery/pull/2)
failed secret and deployment-configuration gates and was closed without merging.
The running approved application remained separate from that failed candidate.

## Final cleanup

- Reconciled historical progress notes with the later successful validation.
- Reviewed and merged [Dependabot PR #1](https://github.com/benalifathia08-source/secure-delivery/pull/1)
  for Gunicorn 26.2.0 after refreshing it against main and passing the complete gate suite.
  Existing server settings remain; cleartext HTTP/2 was not enabled.
- Clarified why the derived PostgreSQL image retains upstream UID 70. The existing
  narrow exception and its expiry remain unchanged; no CVE suppression was introduced.
- Added [DEMO.md](DEMO.md), startup checks, graceful shutdown instructions and this handoff report.
- Local checks after the dependency update: ten tests passed, Ruff passed, repository policy
  passed, and Gitleaks found no secrets in the worktree or full candidate ancestry.

## Final verification and power state

The updated main [run 39981257611](https://github.com/benalifathia08-source/secure-delivery/actions/runs/39981257611)
passed all sixteen gates and promoted the candidate. The last live source commit was
`7b8f4b7c8f5f58257a54fb17520adb54fc9aa97c`; Flux applied release revision
`35002860fee06aff4d06285ed087e7ec52289726`.

At 15:53 UTC, application 0.1.1 ran Gunicorn 26.2.0 with readiness 200; both configured
image digests matched their runtime IDs and Flux was Ready. Repeated admission, RBAC,
authorized/unauthorized network and runtime-canary checks passed. Fresh Falco and application
events reached the Wazuh indexer. The final private 3,052-byte backup restored one inventory
row successfully. No test pods, test policy or temporary restore databases remained.
See the [final evidence](../evidence/README.md) and [validation ledger](VALIDATION.md).

Both lab VMs were shut down using their guest operating systems. At **15:54:49 UTC**,
VMware reported **zero running VMs**. No forced power-off was used. The shared Ubuntu n8n
workload is paused with that VM; VM disks, the database PVC and private backups were preserved.
[Power-state evidence](../evidence/final-power-state.json).

The final handoff commit updates documentation, sanitized evidence and exception rationale;
it does not change application code or deployment manifests. Its hosted workflow runs after
VM shutdown. Any newer approved release published by that workflow will reconcile on the
next startup; the live image evidence above belongs to the explicitly recorded pre-shutdown
release. This report does not claim that an off VM applied a later promotion.

## Operating the completed lab

Start Wazuh-Server, then Ubuntu in VMware and follow the resume checks in
[OPERATIONS.md](OPERATIONS.md). The database PVC, credentials and private on-VM backups
persist across shutdown. Flux catches up with approved releases published while the VM
was off. Use the [demonstration guide](DEMO.md) for an interview or later recording.

No user-supplied account, download, password or API key is required to complete this handoff.
The lab uses the existing authorized local access and no paid cloud account.

## Maintenance and honest limits

The original project scope is complete. Continuing operation still requires reviewing
future dependency updates and EX-001, EX-002 and EX-003 **before 2026-11-22**; expired
exceptions block subsequent releases. Scanner results describe the recorded scan date,
not a permanent guarantee of vulnerability absence.

A clean-OS VM rebuild and full shutdown/start recovery drill have not been performed.
Automatic startup configuration was inspected; bootstrap and restart procedures are documented.
A walkthrough video has not been recorded. Scheduled rescanning, encrypted off-host backups
and image signing/admission are optional enhancements in the backlog.

This is a single-node local lab with no public ingress or high availability. Backups remain
on the application VM and do not protect against loss of that whole VM. Falco demonstrations
use a harmless controlled canary; they do not claim an actual successful exploit or automatic
containment. This project does not claim an AWS/Azure production deployment.
