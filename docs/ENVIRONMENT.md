# Verified lab environment

Private addresses and machine identifiers are deliberately omitted.

| System | Verified configuration |
|---|---|
| Windows host | Approximately 24 GiB RAM; VMware Workstation; Git 2.55.0; Python 3.12.10 |
| Application VM | Ubuntu 24.04, kernel 6.8.0-147-generic, 2 vCPU, 6 GiB RAM, NAT network |
| Kubernetes | k3s v1.37.1+k3s1; embedded NetworkPolicy controller enabled |
| Delivery | Flux v2.9.6; source and kustomize controllers only, pinned by digest |
| Runtime detection | Falco 0.45.1; modern eBPF; custom canary rule; package rule-following disabled |
| SIEM | Existing Wazuh 4.14.8 manager, indexer, dashboard and Filebeat verified active |
| Existing workload | n8n Docker container retained and verified running during cluster setup |

Application credentials were generated in the VM and stored as Kubernetes Secrets, with k3s
secrets encryption enabled. The application uses a SELECT-only database role. No enrollment
secret, private SSH key, kubeconfig, registry token, or database credential is stored in Git.

The Kubernetes API is reachable on the private VM network for cluster component routing.
There is no public ingress or router port forward configured by this project.

At final handoff, both lab guests were gracefully shut down and VMware reported zero
running VMs. The table records their last verified running configuration. Start Wazuh
and then Ubuntu using the resume procedure in OPERATIONS.md before a demonstration.
