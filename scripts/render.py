"""Render the final Kustomize overlay using a checksum-pinned kubectl binary."""

import hashlib
import json
import platform
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    pin = json.loads((ROOT / "tools.lock.json").read_text())["kubectl"]
    system = "windows" if platform.system() == "Windows" else "linux"
    binary = ROOT / ".tools/kubectl" / ("kubectl.exe" if system == "windows" else "kubectl")
    binary.parent.mkdir(parents=True, exist_ok=True)
    expected = pin[f"{system}_amd64_sha256"]
    if not binary.exists() or hashlib.sha256(binary.read_bytes()).hexdigest() != expected:
        url = f"https://dl.k8s.io/release/{pin['version']}/bin/{system}/amd64/{binary.name}"
        with urllib.request.urlopen(url, timeout=120) as response:  # noqa: S310
            data = response.read()
        if hashlib.sha256(data).hexdigest() != expected:
            raise RuntimeError("kubectl checksum mismatch")
        binary.write_bytes(data)
        binary.chmod(0o755)
    output = ROOT / "reports/rendered.yaml"
    output.parent.mkdir(exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        subprocess.run(  # noqa: S603 - checksum verified executable, fixed arguments
            [str(binary), "kustomize", "deploy/overlays/lab"],
            cwd=ROOT,
            stdout=stream,
            check=True,
        )
    print("Rendered deployment overlay using verified kubectl", pin["version"])


if __name__ == "__main__":
    main()
