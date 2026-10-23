# Living backlog

Update this file and STATUS.md whenever a feature, milestone, decision, or blocker changes.

| ID | Priority | Work | State | Acceptance |
|---|---|---|---|---|
| B01 | P0 | Inventory tools and isolated Linux host | Complete | Reachable host and resource budget recorded |
| B02 | P0 | Read-only release inventory API and PostgreSQL | Complete | Failure handling and real database tests pass |
| B03 | P0 | Non-root immutable container build | Complete | Hosted build and read-only-root integration passed; image scan clean |
| B04 | P0 | Gitleaks, Trivy, Checkov gates and reports | Complete | Hosted gates passed with immutable pins and expiring scoped exceptions |
| B05 | P0 | ZAP against the candidate image | Complete | Active/passive scan and required endpoint checks passed |
| B06 | P0 | k3s isolation and enforcement | Complete | Restricted admission, RBAC boundaries and allow/deny network tests passed |
| B07 | P0 | Flux release promotion | Complete | Both tested image digests promoted; Flux and workload readiness True |
| B08 | P0 | Health and rollback procedures | Complete | 0.1.1 to 0.1.0 to 0.1.1 verified; database backup/restore passed |
| B09 | P1 | Falco JSON collection in Wazuh | Complete | Live canary detected by Falco and Wazuh rule 112300 level 10; sanitized evidence saved |
| B10 | P1 | Application security logs in Wazuh | Complete | Rule 112301 application events verified in Wazuh indexer |
| B11 | P0 | Publish complete GitHub repository | Complete | Public repository; main PR/check protection verified, including admins |
| B12 | P1 | Reproducible negative demonstrations | Complete | Scanner fixtures, rejected PR, denied connection, admission and runtime alert verified |
| B13 | P1 | Exceptions and maintenance | Complete | Three scoped expiring exceptions; Dependabot enabled; rendered manifests scanned |
| B14 | P1 | Portfolio documentation and evidence | Complete | Runbooks, decisions, threat model and sanitized observed results published |
| B15 | P0 | Scan and promote database image too | Complete | Derived database image scanned, tested and deployed by digest |

## Maintenance and optional next iteration

| ID | Work | State | Next action |
|---|---|---|---|
| O01 | Dependency updates | Ongoing | Review Dependabot PR #1; a newer major Gunicorn is not automatically merged |
| O02 | Exception review | Due before 2026-11-22 | Re-evaluate EX-001, EX-002 and EX-003; expired entries block new releases |
| O03 | Scheduled rescanning | Optional | Add periodic verification without unnecessary image promotion |
| O04 | Off-host backup retention | Optional | Encrypt backups and test recovery after loss of the whole VM |
| O05 | Image signing and admission verification | Optional | Add attestations and signature enforcement as a separate scoped milestone |
