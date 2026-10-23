# Operations runbook

## Prerequisites and boundaries

Use an isolated Linux VM with a compatible eBPF kernel, 2+ CPUs, 6+ GiB memory and sufficient
disk space for images. Keep the Kubernetes API private. Do not change existing SOC services,
Docker workloads, Wazuh rules, or SSH policy as part of cluster bootstrap.

The host-installed Falco sensor needs elevated privileges. The application does not.
Use a separate namespace and service accounts for the application and Flux reconciliation.

## Delivery

1. Make changes on a feature branch and open a pull request.
2. Inspect all security gates and their readable report artifact.
3. Merge to protected main only after required checks pass.
4. The main workflow builds, scans and tests the candidate; successful runs publish the exact
   tested image and promote its digest to `lab-release`.
5. Flux watches `deploy/overlays/lab` on `lab-release` and waits for workload health.
6. Verify the running image digest, application readiness, and database permissions.

Initial bootstrap and credential creation scripts will be added and verified during M3.
Do not apply main's sentinel image or put real database secrets in Git.

## Rollback

For Flux-managed deployment, revert the release configuration in Git to the last known-good
digest. Record the source and destination digest and the reason. Wait for Flux reconciliation,
then verify readiness, `/api/releases`, and the running image reference.

An imperative `kubectl rollout undo` alone is not durable: Flux will restore Git's desired
state. During an emergency, suspend the relevant Flux Kustomization first, investigate, then
commit the corrected desired state and resume it.

Application rollback does not reverse database migrations. This version only initializes an
empty database and makes no subsequent schema changes. Never delete the PVC as a rollback.
Before future migrations, implement a tested backup/restore and compatibility strategy.

## Demonstration acceptance

- Generate a synthetic secret in a temporary test directory; Gitleaks must reject it.
- Generate a privileged workload in a temporary directory; Trivy and Checkov must reject it.
- Remove those temporary failures and prove that the valid candidate passes.
- Deploy only the promoted digest.
- Show an authorized connection succeeds and an otherwise equivalent unauthorized connection
  fails after both source pods are Ready. Do not treat an image-pull failure as network evidence.
- Trigger a controlled Falco rule in a disposable test pod and locate the corresponding Wazuh
  event. Capture a sanitized event with rule, timestamp, process and container identifiers.
- Revert to a known-good application digest and verify restored readiness.

## Evidence hygiene

Raw reports, kubeconfigs and credentials stay outside Git. Publish small sanitized excerpts
with command purpose, expected result, observed result, date and limitations. Never claim
these demonstrations passed until execution is recorded in VALIDATION.md.
