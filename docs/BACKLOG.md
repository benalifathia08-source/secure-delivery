# Living backlog

Update this file and STATUS.md whenever a feature, milestone, decision, or blocker changes.

| ID | Priority | Work | State | Acceptance |
|---|---|---|---|---|
| B01 | P0 | Inventory tools and isolated Linux host | Complete | Reachable host and resource budget recorded |
| B02 | P0 | Read-only release inventory API and PostgreSQL | In progress | Failure handling and real database tests pass |
| B03 | P0 | Non-root immutable container build | Planned | Digest recorded; read-only root filesystem works |
| B04 | P0 | Gitleaks, Trivy, Checkov gates and reports | In progress | Local source secret/config scans pass; hosted gates pending |
| B05 | P0 | ZAP against the candidate image | Planned | Scan completes; selected findings block promotion |
| B06 | P0 | k3s isolation and enforcement | Planned | Restricted namespace, RBAC, limits, allow/deny network tests |
| B07 | P0 | Flux release promotion | Planned | Only tested digest enters watched release configuration |
| B08 | P0 | Health and rollback procedures | Planned | Git rollback demonstrated; database limitations documented |
| B09 | P1 | Falco JSON collection in Wazuh | Planned | Controlled runtime alert searchable in Wazuh |
| B10 | P1 | Application security logs in Wazuh | Planned | Sanitized HTTP event searchable in Wazuh |
| B11 | P0 | Publish complete GitHub repository | In progress | Authentication recovered; initial publication next |
| B12 | P1 | Reproducible negative demonstrations | Planned | Fake secret, insecure config, denied connection, alert |
| B13 | P1 | Exceptions and maintenance | Planned | Narrow exceptions expire; pinned dependencies updated |
| B14 | P1 | Portfolio documentation and evidence | In progress | No unexecuted claims; sanitized evidence accompanies results |
