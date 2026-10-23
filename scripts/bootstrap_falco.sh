#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
workdir="$HOME/.local/share/secure-delivery-bootstrap/falco"
mkdir -p "$workdir"
curl -fsSL --proto '=https' https://falco.org/repo/falcosecurity-packages.asc -o "$workdir/key.asc"
fingerprint='478B2FBBC75F4237B731DA4365106822B35B1B1F'
gpg --show-keys --with-colons "$workdir/key.asc" | grep -q "$fingerprint"
gpg --dearmor --yes -o "$workdir/key.gpg" "$workdir/key.asc"
sudo install -m 0644 "$workdir/key.gpg" /usr/share/keyrings/falco-archive-keyring.gpg
echo 'deb [signed-by=/usr/share/keyrings/falco-archive-keyring.gpg] https://download.falco.org/packages/deb stable main' \
  | sudo tee /etc/apt/sources.list.d/falcosecurity.list >/dev/null
sudo apt-get update -qq
version='0.45.1'
sudo env DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=l FALCO_FRONTEND=noninteractive \
  FALCO_DRIVER_CHOICE=modern_ebpf FALCOCTL_ENABLED=no apt-get install -y "falco=$version"
sudo install -d -m 0750 /var/log/falco /var/log/secure-delivery /opt/secure-delivery
sudo install -m 0644 "$root/observability/falco-output.yaml" /etc/falco/config.d/secure-delivery.yaml
sudo install -m 0644 "$root/observability/falco-rules.yaml" /etc/falco/rules.d/secure-delivery.yaml
sudo install -m 0644 "$root/observability/logrotate.conf" /etc/logrotate.d/secure-delivery
sudo install -m 0644 "$root/scripts/collect_app_logs.py" /opt/secure-delivery/collect_app_logs.py
sudo install -m 0644 "$root/observability/application-logs.service" /etc/systemd/system/secure-delivery-logs.service
sudo touch /var/log/falco/secure-delivery.jsonl /var/log/secure-delivery/application.jsonl
sudo chmod 0640 /var/log/falco/secure-delivery.jsonl /var/log/secure-delivery/application.jsonl
sudo systemctl daemon-reload
sudo systemctl enable --now falco-modern-bpf.service secure-delivery-logs.service
sudo systemctl restart falco-modern-bpf.service
falco --version
sudo systemctl is-active falco-modern-bpf.service secure-delivery-logs.service
