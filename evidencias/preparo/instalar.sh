#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$HOME/.local/bin"
cd "${DIRETORIO_DOWNLOAD:?Defina um diretório de downloads fora do repo}"
curl -fsSLo kind https://github.com/kubernetes-sigs/kind/releases/download/v0.31.0/kind-linux-amd64
curl -fsSLo kind.sha256 https://github.com/kubernetes-sigs/kind/releases/download/v0.31.0/kind-linux-amd64.sha256sum
printf '%s  kind\n' "$(cut -d ' ' -f1 kind.sha256)" | sha256sum -c -
install -m755 kind "$HOME/.local/bin/kind"
curl -fsSLo kubectl https://dl.k8s.io/release/v1.35.0/bin/linux/amd64/kubectl
curl -fsSLo kubectl.sha256 https://dl.k8s.io/release/v1.35.0/bin/linux/amd64/kubectl.sha256
printf '%s  kubectl\n' "$(cat kubectl.sha256)" | sha256sum -c -
install -m755 kubectl "$HOME/.local/bin/kubectl"
curl -fsSLO https://github.com/aquasecurity/trivy/releases/download/v0.69.3/trivy_0.69.3_Linux-64bit.tar.gz
curl -fsSLo trivy_checksums.txt https://github.com/aquasecurity/trivy/releases/download/v0.69.3/trivy_0.69.3_checksums.txt
rg ' trivy_0.69.3_Linux-64bit.tar.gz$' trivy_checksums.txt | sha256sum -c -
tar -xzf trivy_0.69.3_Linux-64bit.tar.gz trivy
install -m755 trivy "$HOME/.local/bin/trivy"
kind version
kubectl version --client
trivy --version
