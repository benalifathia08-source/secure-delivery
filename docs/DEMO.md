# Demonstration guide

Allow roughly ten minutes after both lab VMs have started. Use a trusted Linux lab
checkout and the restart checks in [OPERATIONS.md](OPERATIONS.md). Keep credentials,
kubeconfigs, addresses and raw Wazuh events off screen when recording.

## 1. Explain the delivery boundary

Show the README architecture and protected main branch. Pull requests run on disposable
GitHub-hosted runners. Gitleaks, Trivy, Checkov and ZAP must pass before a main build can
publish its tested images and promote their digests. Flux pulls the approved release;
GitHub Actions has no network path or kubeconfig into the lab.

## 2. Show the rejected change

Open [closed PR #2](https://github.com/benalifathia08-source/secure-delivery/pull/2) and
its failed security run. It introduced a deliberately nonfunctional credential and
privileged deployment. Show the failing secret/configuration stages and skipped
promotion. The PR was closed without merging, leaving the approved main branch clean.
Do not weaken the gate or merge the demonstration branch to reproduce the result.

The normal workflow also runs real generated negative scanner fixtures on every candidate.
Detailed Actions artifacts expire after seven days; sanitized summaries in evidence/ persist.

## 3. Show a successful release

Open the latest successful main security run, gate summary and lab-release provenance.
On the Ubuntu VM:

```sh
sudo k3s kubectl -n flux-system get gitrepository,kustomization
sudo k3s kubectl -n secure-delivery get pods
sudo k3s kubectl -n secure-delivery get deployment app -o jsonpath='{.spec.template.spec.containers[0].image}'
```

Use the loopback port-forward described in OPERATIONS.md to inspect `/`, `/api/releases`
and `/health/ready`. Explain the intentionally small read-only application and SELECT-only
database identity. Port forwarding is an administrator path, not a NetworkPolicy test.

## 4. Prove enforcement and runtime detection

```sh
python3 scripts/verify_cluster.py
```

Read the resulting checks: privileged pod rejected, reconciler privilege boundaries,
authorized connection succeeds, unauthorized connection blocked, runtime canary triggered.
The two network clients have equivalent egress permissions; their ingress role labels differ.
The script cleans its named resources afterward. A denied connection can fail immediately
or time out. Labels rely on RBAC limits on who can create and relabel workloads.

Search Wazuh for rule IDs 112300 and 112301. Confirm the fresh canary timestamp reached
the indexer and explain the level-10 controlled file-read simulation. Falco detects;
NetworkPolicy and Pod Security enforce. This is not a claim of successful exploitation.

## 5. Explain recovery and exceptions

Show the saved 0.1.1 → 0.1.0 → 0.1.1 rollback evidence and the runbook's approved-release
rollback command. The GitOps rollback creates a new commit, so reconciliation preserves it.
It does not reverse database migrations. The backup script tests recovery in a disposable
database without overwriting live data.

Explain all three narrowly scoped exceptions and their 2026-11-22 expiry. No CVE is
suppressed. Finish with the project's limits: one local cluster, no public ingress,
no high availability, no off-host disaster recovery, and no clean-OS rebuild verification.
The repository supplies a written walkthrough; a video has not been recorded.
