# Living backlog

Update this file and STATUS.md whenever a feature, milestone, decision, or blocker changes.

| ID | Priority | Work | State | Acceptance |
|---|---|---|---|---|
| B01 | P0 | Inventory tools and isolated Linux host | Complete | Reachable host and resource budget recorded |
| B02 | P0 | Read-only release inventory API and PostgreSQL | Complete | Failure handling and real database tests pass |
| B03 | P0 | Non-root immutable container build | Complete | Hosted build and read-only-root integration passed; image scan clean |
| B04 | P0 | Gitleaks, Trivy, Checkov gates and reports | In progress | Local source secret/config scans pass; hosted gates pending |
| B05 | P0 | ZAP against the candidate image | In progress | Completed scan found CI HTTP-only; narrowly scoped EX-002 added |
| B06 | P0 | k3s isolation and enforcement | In progress | Cluster healthy; application policy enforcement tests pending |
| B07 | P0 | Flux release promotion | Planned | Only tested digest enters watched release configuration |
| B08 | P0 | Health and rollback procedures | Planned | Git rollback demonstrated; database limitations documented |
| B09 | P1 | Falco JSON collection in Wazuh | In progress | Sensor active; collection/rules being enabled; live trigger pending |
| B10 | P1 | Application security logs in Wazuh | In progress | Whitelisted JSON collector implemented; live ingestion pending |
| B11 | P0 | Publish complete GitHub repository | In progress | Authentication recovered; initial publication next |
| B12 | P1 | Reproducible negative demonstrations | In progress | Real scanner fixtures implemented; hosted execution pending |
| B13 | P1 | Exceptions and maintenance | In progress | Three scoped expiring exceptions; Dependabot enabled; rendered manifests now scanned |
| B14 | P1 | Portfolio documentation and evidence | In progress | No unexecuted claims; sanitized evidence accompanies results |
