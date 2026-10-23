# Engineering decisions

## ADR-001 — GitHub-hosted CI and Flux deployment

Accepted 2026-10-23. Run untrusted pull-request work on disposable hosted runners. No public-repository self-hosted runner with lab access. Flux pulls approved deployment configuration; the Kubernetes API remains private. Promotion must depend on every security gate and reference the tested image digest. Flux is not itself a vulnerability gate.

## ADR-002 — Small read-only application

Accepted 2026-10-23. Use a Flask release inventory backed by PostgreSQL. Keep product behavior deliberately small so security controls are the focus. A SELECT-only database identity demonstrates least privilege. Credentials are generated locally and never committed. This is a local security lab, not an AWS/Azure production system.

## ADR-003 — Linux VM and k3s

Accepted 2026-10-23. Prefer an isolated Linux VM to installing a second virtualization stack on Windows. k3s provides network policy enforcement. Existing SOC workloads must not be modified until host identity and resource suitability are verified.

## ADR-004 — Complementary scanners

Accepted 2026-10-23. Gitleaks checks secrets; Trivy checks dependencies, images and configuration; Checkov checks a documented Kubernetes baseline; ZAP tests the running candidate; Falco detects runtime behavior. No blanket ignores or automatic suppression of unfixed vulnerabilities. Scanner infrastructure failure must block the release.

## ADR-005 — Host Falco and Wazuh collection

Accepted 2026-10-23. Prefer host-installed Falco writing JSON lines, collected by the existing Wazuh agent. This avoids weakening the application's Restricted namespace for a privileged sensor. Verify kernel compatibility and Wazuh field decoding before recording success.

## ADR-006 — Replace Debian application base after actual scan findings

Accepted 2026-10-23. The initial Debian bookworm base produced numerous unfixed HIGH/CRITICAL
OS findings. Keep the blocking policy and test the smaller official Alpine Python base.
The application has no dependency on glibc; psycopg distributes musllinux wheels.
Align the builder and runtime virtual-environment paths so executable shebangs remain valid.

## ADR-007 — Scoped PostgreSQL identity exception

Accepted 2026-10-23. Official PostgreSQL Alpine uses UID 70. Retain the vendor non-root identity
and all other restrictions instead of maintaining a custom database image just to change its UID.
Record EX-001 for CKV_K8S_40 only, expiring 2026-11-22. This does not waive root or privileged execution.

## ADR-008 — Private VM network, cluster-reachable API

Accepted 2026-10-23. A loopback-only API binding broke Kubernetes Service routing and k3s
agent connections. Use the default binding on the isolated NAT VM, without a router port forward
or public ingress. Kubernetes components need API reachability; loopback-only binding is not
a valid isolation mechanism for this cluster. kubeconfig remains mode 0600.

## ADR-009 — Isolated CI transport exception

Accepted 2026-10-23. ZAP's only finding in the second run was rule 10106, HTTP Only Site.
Retain it as informational for exactly http://app:8080 in the ephemeral Docker test context,
with no published ports or durable credentials. EX-002 expires 2026-11-22. Other targets
remain subject to the normal threshold; a future public ingress must use TLS.

## ADR-010 — Separate platform bootstrap from application reconciliation

Accepted 2026-10-23. A platform administrator creates the Restricted namespace and Flux
RBAC. Flux applies application resources using an impersonated namespace-scoped identity
that cannot read secrets, alter RBAC, create namespaces, or deploy outside the namespace.

## ADR-011 — Review necessary networking reconciliation privilege

Accepted 2026-10-23. Trivy KSV-0056 correctly identifies that Flux can change Services and
NetworkPolicies. This is required for delivery but limited to the application namespace.
EX-003 expires 2026-11-22 and applies only to this Role file. Scan both platform manifests
and final rendered application manifests so overlays cannot bypass configuration checks.

## ADR-012 — Selected application log forwarding

Accepted 2026-10-23. A host collector reads recent application pod logs, selects only known
HTTP event fields, deduplicates request IDs in bounded memory, and writes JSON for the Wazuh
agent. It does not forward arbitrary pod output, request data, or database credentials.
This lab collector polls every 15 seconds and is not a lossless production logging system.
