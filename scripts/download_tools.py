"""Download official release binaries and verify their upstream SHA-256 checksums."""

import hashlib
import json
import re
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".tools"


def download(url):
    if not url.startswith("https://"):
        raise ValueError("HTTPS required")
    request = urllib.request.Request(url, headers={"User-Agent": "secure-delivery"})  # noqa: S310
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
        return response.read()


def main():
    for name, repository, pattern in [
        ("gh", "cli/cli", r"gh_.*_windows_amd64.zip$"),
        ("gitleaks", "gitleaks/gitleaks", r"gitleaks_.*_windows_x64.zip$"),
        ("trivy", "aquasecurity/trivy", r"trivy_.*_windows-64bit.zip$"),
    ]:
        release = json.loads(download(f"https://api.github.com/repos/{repository}/releases/latest"))
        assets = release["assets"]
        binary = next(a for a in assets if re.match(pattern, a["name"], re.IGNORECASE))
        checksums = next(a for a in assets if re.search(r"checksums\.txt$", a["name"]))
        checksums_text = download(checksums["browser_download_url"]).decode()
        line = next(line for line in checksums_text.splitlines() if line.endswith(binary["name"]))
        expected = line.split()[0]
        data = download(binary["browser_download_url"])
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Checksum mismatch: {name}")
        folder = ROOT / name
        folder.mkdir(parents=True, exist_ok=True)
        archive = folder / binary["name"]
        archive.write_bytes(data)
        with zipfile.ZipFile(archive) as zipped:
            for member in zipped.infolist():
                if not (folder / member.filename).resolve().is_relative_to(folder.resolve()):
                    raise ValueError("Unsafe archive member")
            zipped.extractall(folder)
        print(name, release["tag_name"], "checksum verified")


if __name__ == "__main__":
    main()
