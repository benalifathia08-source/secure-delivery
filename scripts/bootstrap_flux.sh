#!/usr/bin/env bash
set -euo pipefail
version='v2.9.6'
workdir="$HOME/.local/share/secure-delivery-bootstrap/flux"
mkdir -p "$workdir"
cd "$workdir"
base="https://github.com/fluxcd/flux2/releases/download/$version"
archive="flux_${version#v}_linux_amd64.tar.gz"
curl --fail --location --proto '=https' --tlsv1.2 "$base/$archive" -o "$archive"
curl --fail --location --proto '=https' --tlsv1.2 \
  "$base/flux_${version#v}_checksums.txt" -o checksums.txt
awk -v file="$archive" '$2 == file { print }' checksums.txt > archive.sha256
test -s archive.sha256
sha256sum --check archive.sha256
tar -xzf "$archive" flux
sudo install -m 0755 flux /usr/local/bin/flux
sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml flux install --components=source-controller,kustomize-controller \
  --watch-all-namespaces=false --network-policy=true
sudo k3s kubectl -n flux-system rollout status deployment/source-controller --timeout=180s
sudo k3s kubectl -n flux-system rollout status deployment/kustomize-controller --timeout=180s
