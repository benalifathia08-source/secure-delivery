# Evidence index

All files in this directory contain actual observed results, with private addresses, agent
identities, credentials, full raw events and kubeconfigs excluded.

| File | What it proves |
|---|---|
| ci-gates.json | All hosted security gates passed for the recorded source commit |
| scanner-negative-tests.json | Real scanners rejected generated secret and insecure workload fixtures |
| admission-rbac-runtime.json | Restricted admission and deployment identity limits were enforced |
| network-isolation.json | Equivalent ready clients had allowed versus denied application connectivity |
| runtime-detection.json | A controlled container canary read produced a level-10 Wazuh alert |
| indexed-alerts.json | Runtime and selected application alerts reached the Wazuh indexer |
| backup-restore.json | A private backup restored successfully into a disposable database |
| rejected-demo.json | The intentionally insecure PR failed secret and configuration gates |
| release-before-rollback.json | Version 0.1.1 ran with the configured immutable image digest |
| rollback-action.json | A new Git commit restored a previously approved release without force push |
| release-after-rollback.json | Version 0.1.0 became healthy with the expected runtime digest |
| release-restored-current.json | Version 0.1.1 was restored after the recovery test |

The runtime canary is a controlled simulation, not a claim of a successful exploit.
Workflow artifacts contain detailed scanner reports and expire after seven days; these
sanitized summaries preserve essential results. See [validation](../docs/VALIDATION.md) for run links and limitations.
