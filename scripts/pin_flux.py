"""Pin generated Flux manifests and disable remote bases / cross-namespace references."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    lock = json.loads((ROOT / "tools.lock.json").read_text())
    manifest = sys.stdin.read()
    for name in ["flux-source", "flux-kustomize"]:
        record = lock["images"][name]
        if record["source"] not in manifest:
            raise RuntimeError("Flux release and controller lock disagree")
        manifest = manifest.replace(record["source"], record["pinned"])
    documents = manifest.split("\n---\n")
    for index, document in enumerate(documents):
        if "kind: Deployment" in document and "name: kustomize-controller" in document:
            document = re.sub(
                r"(?m)^([ ]*)args:$",
                lambda match: (
                    match[0]
                    + "\n"
                    + match[1]
                    + "- --no-remote-bases=true\n"
                    + match[1]
                    + "- --no-cross-namespace-refs=true"
                ),
                document,
                count=1,
            )
            documents[index] = document
    print("\n---\n".join(documents))


if __name__ == "__main__":
    main()
