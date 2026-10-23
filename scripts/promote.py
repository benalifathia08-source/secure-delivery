"""Promote only the tested image digest to a separate Flux-watched Git branch."""

import json
import os
import re
import urllib.error
import urllib.request


def api(path, payload=None, method=None):
    url = "https://api.github.com/repos/" + os.environ["GITHUB_REPOSITORY"] + "/" + path
    request = urllib.request.Request(  # noqa: S310
        url,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": "Bearer " + os.environ["GH_TOKEN"],
            "Accept": "application/vnd.github+json",
            "User-Agent": "secure-delivery",
        },
        method=method,
    )
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
        return json.load(response)


def main():
    source = os.environ["SOURCE_SHA"]
    image = os.environ["RELEASE_IMAGE"]
    database_image = os.environ["DATABASE_IMAGE"]
    if not re.fullmatch(r"ghcr\.io/[a-z0-9_./-]+@sha256:[a-f0-9]{64}", image):
        raise ValueError("Promotion requires a GHCR image digest")
    if not re.fullmatch(r"ghcr\.io/[a-z0-9_./-]+@sha256:[a-f0-9]{64}", database_image):
        raise ValueError("Promotion requires a GHCR database digest")
    if api("git/ref/heads/main")["object"]["sha"] != source:
        raise RuntimeError("Refusing stale promotion: main has moved")
    source_commit = api("git/commits/" + source)
    try:
        previous = api("git/ref/heads/lab-release")["object"]["sha"]
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        previous = None
    config = (
        "apiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\n"
        "resources:\n  - ../../base\nimages:\n  - name: secure-delivery-candidate\n"
        f"    newName: {image.split('@')[0]}\n    digest: {image.split('@')[1]}\n"
        "  - name: secure-delivery-database\n"
        f"    newName: {database_image.split('@')[0]}\n"
        f"    digest: {database_image.split('@')[1]}\n"
    )
    provenance = (
        json.dumps(
            {
                "source_commit": source,
                "image": image,
                "database_image": database_image,
                "run": os.environ["GITHUB_RUN_ID"],
            },
            indent=2,
        )
        + "\n"
    )
    tree = api(
        "git/trees",
        {
            "base_tree": source_commit["tree"]["sha"],
            "tree": [
                {
                    "path": "deploy/overlays/lab/kustomization.yaml",
                    "mode": "100644",
                    "type": "blob",
                    "content": config,
                },
                {"path": "release.json", "mode": "100644", "type": "blob", "content": provenance},
            ],
        },
    )
    commit = api(
        "git/commits",
        {
            "message": f"release: promote tested source {source[:12]}",
            "tree": tree["sha"],
            "parents": [previous or source],
        },
    )
    if previous:
        api("git/refs/heads/lab-release", {"sha": commit["sha"], "force": False}, "PATCH")
    else:
        api("git/refs", {"ref": "refs/heads/lab-release", "sha": commit["sha"]})
    print("Promoted", image, "from", source)


if __name__ == "__main__":
    main()
