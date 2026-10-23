"""Restore a previously approved release tree through Git, preserving Flux reconciliation."""

import argparse
import base64
import json
import re

from scripts.promote import api


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Full lab-release commit SHA to restore")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}", args.target):
        raise ValueError("A full release commit SHA is required")
    current = api("git/ref/heads/lab-release")["object"]["sha"]
    comparison = api(f"compare/{args.target}...{current}")
    if comparison["status"] not in {"ahead", "identical"}:
        raise RuntimeError("Rollback target is not an ancestor of the current release")
    content = api("contents/release.json?ref=" + args.target)
    release = json.loads(base64.b64decode(content["content"]))
    workflow = api("actions/runs/" + release["run"])
    if workflow["conclusion"] != "success" or workflow["head_sha"] != release["source_commit"]:
        raise RuntimeError("Target release is not backed by a successful source workflow")
    target = api("git/commits/" + args.target)
    restored = api(
        "git/commits",
        {
            "message": "rollback: restore approved release " + args.target,
            "tree": target["tree"]["sha"],
            "parents": [current],
        },
    )
    api("git/refs/heads/lab-release", {"sha": restored["sha"], "force": False}, "PATCH")
    print(
        json.dumps(
            {
                "from_release": current,
                "restored_release": args.target,
                "rollback_commit": restored["sha"],
                "image": release["image"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
