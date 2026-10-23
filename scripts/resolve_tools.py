"""Resolve upstream references to immutable pins. Run deliberately; review the diff."""

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fetch(url, headers=None):
    if not url.startswith("https://"):
        raise ValueError("HTTPS required")
    request = urllib.request.Request(  # noqa: S310
        url, headers={"User-Agent": "secure-delivery", **(headers or {})}
    )
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        return json.load(response), response.headers


def image_pin(image):
    host, path = (
        image.split("/", 1) if image.startswith("ghcr.io/") else ("registry-1.docker.io", image)
    )
    repository, tag = path.rsplit(":", 1)
    if "/" not in repository:
        repository = "library/" + repository
    service = "ghcr.io" if host == "ghcr.io" else "registry.docker.io"
    auth_host = "ghcr.io/token" if host == "ghcr.io" else "auth.docker.io/token"
    token, _ = fetch(f"https://{auth_host}?service={service}&scope=repository:{repository}:pull")
    manifest, headers = fetch(
        f"https://{host}/v2/{repository}/manifests/{tag}",
        {
            "Authorization": "Bearer " + token["token"],
            "Accept": ", ".join(
                [
                    "application/vnd.oci.image.index.v1+json",
                    "application/vnd.docker.distribution.manifest.list.v2+json",
                    "application/vnd.oci.image.manifest.v1+json",
                    "application/vnd.docker.distribution.manifest.v2+json",
                ]
            ),
        },
    )
    digest = headers["Docker-Content-Digest"]
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
        raise ValueError("Invalid registry digest")
    return image.rsplit(":", 1)[0] + "@" + digest


def main():
    actions = {}
    for repository in ["actions/checkout", "actions/setup-python", "actions/upload-artifact"]:
        release, _ = fetch(f"https://api.github.com/repos/{repository}/releases/latest")
        tag = release["tag_name"]
        ref, _ = fetch(f"https://api.github.com/repos/{repository}/git/ref/tags/{tag}")
        obj = ref["object"]
        while obj["type"] == "tag":
            annotated, _ = fetch(obj["url"])
            obj = annotated["object"]
        if obj["type"] != "commit" or not re.fullmatch(r"[a-f0-9]{40}", obj["sha"]):
            raise ValueError("Invalid action pin")
        actions[repository] = {"tag": tag, "sha": obj["sha"]}
    images = {}
    for name, reference in {
        "python": "python:3.12-alpine",
        "postgres": "postgres:17-alpine",
        "probe": "alpine:3.22",
        "uv": "ghcr.io/astral-sh/uv:0.13.5",
        "trivy": "aquasec/trivy:latest",
        "gitleaks": "zricethezav/gitleaks:latest",
        "checkov": "bridgecrew/checkov:latest",
        "zap": "ghcr.io/zaproxy/zaproxy:stable",
    }.items():
        images[name] = {"source": reference, "pinned": image_pin(reference)}
        print("Resolved", name)
    (ROOT / "tools.lock.json").write_text(
        json.dumps({"actions": actions, "images": images}, indent=2) + "\n", encoding="utf-8"
    )
    # Record the resolver's upstream sources in the repository; no auth tokens are stored.


if __name__ == "__main__":
    main()
