# Threat model

## Assets and trust boundaries

Protect repository integrity, CI tokens, the image-to-source relationship, database credentials,
the private Kubernetes API, and Wazuh telemetry. Treat pull requests and container processes
as potentially hostile. GitHub-hosted CI and the local lab are separate trust domains.

## Covered scenarios

- Accidental secret commits: worktree and Git-history scanning, redacted reports.
- Known vulnerable packages or images: Trivy release gates.
- Unsafe workload changes: Trivy, Checkov and repository policy; Restricted admission.
- Compromised ordinary app process: SELECT-only database identity, no API token,
  reduced Linux privileges, resource boundaries and network restrictions.
- Suspicious runtime activity: Falco rules and Wazuh collection, with detection tests.
- Mutable release tags: action SHA and container digest pinning.

## Important limits

- A malicious repository administrator can change workflows or disable protection.
- Namespace labels are not an authentication system. An identity allowed to create pods
  can spoof application labels; RBAC must restrict who can create or modify workloads.
- NetworkPolicy controls supported pod traffic, not every host-network or node path.
- Static scans cannot prove absence of vulnerabilities; ZAP coverage depends on exercised routes.
- Falco alerting is detection, not automatic containment. Sensor privileges are separate from
  the application namespace.
- Local PostgreSQL storage is single-node and not highly available. Image rollback does not
  reverse schema changes or restore data. Backups and restore tests are separate acceptance work.
- Flux is a reconciler, not a security scanner. The watched branch must receive only approved
  configuration, and its reconciliation identity must be namespace-scoped.
- The first version exposes no public ingress. Local demonstration access uses port forwarding.
