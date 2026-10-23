# Operations runbook

## Requirements

Use the authorized Ubuntu VM, private networking, SSH key authentication and sudo.
The verified environment has 2 CPUs and 6 GiB RAM. Keep adequate free disk space for
container images and database backups. The Windows host also runs a separate Wazuh VM.
Do not expose the Kubernetes API, Wazuh administration endpoints or database publicly.

## Fresh cluster bootstrap

Run from a checkout on the Linux VM after GitHub CI has produced a successful release.
The scripts use pinned releases and verify upstream download checksums or APT signatures.

```sh
git clone https://github.com/benalifathia08-source/secure-delivery.git
cd secure-delivery
bash scripts/bootstrap_k3s.sh
bash scripts/bootstrap_flux.sh
sudo k3s kubectl apply -f deploy/platform/namespace.yaml
sudo k3s kubectl apply -f deploy/platform/flux-rbac.yaml
python3 scripts/bootstrap_credentials.py
sudo k3s kubectl apply -f deploy/platform/flux-source.yaml
python3 scripts/bootstrap_credentials.py --provision
sudo k3s kubectl -n secure-delivery rollout status deployment/app --timeout=180s
sudo k3s kubectl -n flux-system get gitrepository,kustomization
```

The first app readiness check fails until database role provisioning finishes. Existing
Secrets are reused; the credential script does not silently rotate database passwords.
Do not delete the database PVC to fix a credential or rollout problem.

If adapting this repository to a different account, update the GitRepository URL and
package locations, and ensure the cluster can pull the published packages. Never put a
personal registry token in Git. No cluster kubeconfig is supplied to GitHub Actions.

## Inspect the application

```sh
sudo k3s kubectl -n secure-delivery port-forward service/app 8080:8080 --address=127.0.0.1
```

On that VM, open http://127.0.0.1:8080/ or /api/releases. For Windows access, use an SSH
local tunnel to the VM loopback port. Port forwarding is an administrator operation and
is not proof of NetworkPolicy enforcement; use the pod-based tests below for that.

## Delivery workflow

1. Open a feature pull request. Main requires the verify check and an up-to-date branch.
2. Inspect the gate summary and downloadable reports. A scanner execution failure blocks release.
3. Merge an approved clean change. The main workflow scans and tests both exact candidate images.
4. Successful publication records their GHCR manifest digests. A separate job promotes only
   application manifests and provenance to lab-release. Stale main runs cannot promote.
5. Flux fetches lab-release and reconciles using the namespace-scoped app-reconciler identity.
6. Verify readiness and compare the configured image digest with the runtime image ID.

Detailed reports expire after seven days. Preserve only reviewed, sanitized evidence in Git.
Gitleaks scans HEAD ancestry and the worktree; unrelated unmerged branches cannot poison main.

## Verify admission, RBAC, networking and detection

```sh
python3 scripts/verify_cluster.py
```

This creates two restricted, ready test pods with equivalent egress permissions. One has
the ingress-authorized role label and reaches the real application; the other is blocked.
The test also verifies Restricted admission, reconciler RBAC boundaries, and a harmless
runtime canary read. The script deletes only its named test resources afterward.
NetworkPolicy may reject traffic immediately or cause a timeout; both are valid enforcement.
Labels are not identity: RBAC must limit who can create or relabel pods.

The standalone scanner rejection tests run automatically in CI. To reproduce them on a
disposable Linux Docker host, install the locked development dependencies and run:

```sh
uv run --locked python scripts/negative_tests.py
```

The fixtures are generated in a temporary directory. No detector-matching fake credential
is committed to main. The intentionally failing demonstration PR is closed without merging.

## Falco and Wazuh

```sh
bash scripts/bootstrap_falco.sh
sudo python3 scripts/install_wazuh_agent.py
```

This installs modern-eBPF Falco, the controlled canary rule, rotating JSON output and the
selected application log collector. Existing Wazuh agent configuration is backed up locally;
logcollector configuration is tested before restarting the agent. Successful routine health
probes are excluded from forwarding to reduce noise. Request payloads and credentials are
never selected by the application collector.

On the Wazuh manager, first confirm rule IDs 112300-112302 are unused. Copy
observability/wazuh-rules.xml to /var/ossec/etc/rules/secure_delivery_rules.xml with owner/group
wazuh and mode 0640. Validate with /var/ossec/bin/wazuh-analysisd -t before restarting
wazuh-manager. If validation fails, remove the new project rule file or restore its previous
version before restarting. No existing ruleset files need to be edited.

Search Wazuh for rule.id:112300 (runtime simulation), rule.id:112301 (application access),
and rule.id:112302 (application 5xx). Validate both the manager alert and indexer ingestion.
The canary is a simulation, not an actual credential theft or successful exploit.

## Back up and verify database recovery

```sh
python3 scripts/backup_database.py
```

The custom-format dump stays in the VM user's private
~/.local/share/secure-delivery-backups directory. The script restores into a unique temporary
database, verifies the inventory and removes that temporary database. It never overwrites
live data. Backups contain application data and must not be committed. This lab script is
an on-demand recovery check; off-host retention and automated backup scheduling remain
optional future work.

## Durable GitOps rollback

Record the current release commit and choose a previously successful lab-release commit.
From a trusted administrator checkout with GitHub authentication available:

```sh
export GITHUB_REPOSITORY=benalifathia08-source/secure-delivery
export GH_TOKEN="$(gh auth token)"
uv run --locked python -m scripts.rollback --target FULL_PREVIOUS_RELEASE_COMMIT_SHA
unset GH_TOKEN
```

The script checks that the target is an ancestor and is backed by a successful source
workflow, then creates a new release-branch commit restoring the approved tree. It does not
force-push. Flux reconciles that commit automatically. For immediate reconciliation on the VM:

```sh
sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml flux reconcile kustomization secure-delivery --with-source
sudo k3s kubectl -n secure-delivery rollout status deployment/app --timeout=180s
```

Verify the API version, image digest, readiness and database contents. Restore a newer
approved release the same way when the rollback demonstration is finished.

An imperative kubectl rollout undo alone is not durable under Flux. If emergency direct
intervention is necessary, suspend the Kustomization, investigate, commit the corrected
desired state, and resume reconciliation.

Image rollback does not undo database migrations. This version initializes an empty
PostgreSQL 17 database and has no destructive migrations. Preserve the PVC and use tested
backup/restore plus a compatibility plan before introducing schema changes.

## Maintenance

Review Dependabot pull requests and all three expiring exceptions before 2026-11-22.
Run scripts/resolve_tools.py deliberately, inspect the upstream changes, and update affected
Dockerfiles/bootstrap pins together with tools.lock.json. Keep base Python at 3.12 and the
database on its intended major version; do not blindly follow a new major release.

Use .github/branch-protection.json as the declared main-branch protection policy.
No self-hosted Actions runner is installed in the lab. See THREAT_MODEL.md for limits.
