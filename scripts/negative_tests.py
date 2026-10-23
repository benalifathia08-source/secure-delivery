"""Prove scanners reject synthetic inputs without contaminating Git history."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "tools.lock.json").read_text())


def reject(tool, folder, args):
    result = subprocess.run(  # noqa: S603
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{folder}:/fixture:ro",
            "-v",
            f"{ROOT}:/src:ro",
            LOCK["images"][tool]["pinned"],
        ]
        + args,
        capture_output=True,
    )
    if result.returncode != 1:
        raise RuntimeError(f"{tool} negative test did not return finding exit code 1")
    return {"tool": tool, "expected": "reject", "exit_code": result.returncode}


def main():
    with tempfile.TemporaryDirectory(prefix="secure-delivery-negative-") as folder:
        fixture = Path(folder)
        (fixture / "secret.txt").write_text("LAB_FAKE_" + "CREDENTIAL_" + "A1" * 12)
        (fixture / "pod.yaml").write_text(
            "apiVersion: v1\nkind: Pod\nmetadata:\n  name: insecure-demo\nspec:\n"
            "  containers:\n    - name: bad\n      image: alpine:latest\n"
            "      securityContext:\n        privileged: true\n"
            "        allowPrivilegeEscalation: true\n"
        )
        results = [
            reject(
                "gitleaks",
                fixture,
                ["dir", "/fixture", "--config", "/src/.gitleaks.toml", "--redact", "--no-banner"],
            ),
            reject(
                "trivy",
                fixture,
                ["config", "/fixture", "--severity", "HIGH,CRITICAL", "--exit-code", "1"],
            ),
            reject(
                "checkov",
                fixture,
                [
                    "-d",
                    "/fixture",
                    "--framework",
                    "kubernetes",
                    "--check",
                    "CKV_K8S_20",
                    "--compact",
                ],
            ),
        ]
        output = ROOT / "reports/negative-tests.json"
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps(results, indent=2) + "\n")
        print("Gitleaks, Trivy and Checkov rejected synthetic insecure inputs")


if __name__ == "__main__":
    main()
