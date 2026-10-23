"""Append project log sources, validate, and restore the original configuration on failure."""

import datetime
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = Path("/var/ossec/etc/ossec.conf")


def main():
    original = CONFIG.read_text()
    fragment = (ROOT / "observability/wazuh-agent.xml").read_text()
    if "/var/log/falco/secure-delivery.jsonl" in original:
        print("Project Wazuh log sources already configured")
        return
    ET.fromstring("<root>" + original + fragment + "</root>")  # noqa: S314 - trusted local files
    backup = CONFIG.with_name(
        "ossec.conf.secure-delivery-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    )
    shutil.copy2(CONFIG, backup)
    backup.chmod(0o600)
    CONFIG.write_text(original + "\n" + fragment)
    try:
        subprocess.run(["/var/ossec/bin/wazuh-logcollector", "-t"], check=True)
        subprocess.run(["/usr/bin/systemctl", "restart", "wazuh-agent"], check=True)
    except subprocess.CalledProcessError:
        shutil.copy2(backup, CONFIG)
        raise
    print("Project log collection validated and enabled; original configuration backed up locally")


if __name__ == "__main__":
    main()
