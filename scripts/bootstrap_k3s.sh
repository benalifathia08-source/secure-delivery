#!/usr/bin/env bash
set -euo pipefail
# Run on the authorized single-node Linux lab host. No public ingress is installed.
version='v1.37.1+k3s1'
if command -v k3s >/dev/null 2>&1; then
  k3s --version
  echo 'Existing k3s detected; refusing to overwrite its configuration.'
  exit 0
fi
workdir="$HOME/.local/share/secure-delivery-bootstrap"
mkdir -p "$workdir"
cd "$workdir"
base="https://github.com/k3s-io/k3s/releases/download/$version"
curl --fail --location --proto '=https' --tlsv1.2 "$base/k3s" -o k3s
curl --fail --location --proto '=https' --tlsv1.2 "$base/sha256sum-amd64.txt" -o checksums.txt
awk '$2 == "k3s" { print }' checksums.txt > k3s.sha256
test -s k3s.sha256
sha256sum --check k3s.sha256
curl --fail --location --proto '=https' --tlsv1.2 \
  "https://raw.githubusercontent.com/k3s-io/k3s/$version/install.sh" -o install.sh
sudo install -m 0755 k3s /usr/local/bin/k3s
sudo env INSTALL_K3S_SKIP_DOWNLOAD=true INSTALL_K3S_VERSION="$version" \
  sh install.sh server --disable=traefik --disable=servicelb \
  --secrets-encryption --write-kubeconfig-mode=600
sudo k3s kubectl wait --for=condition=Ready node --all --timeout=180s
sudo k3s kubectl get nodes
