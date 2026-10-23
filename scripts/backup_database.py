"""Create a private PostgreSQL backup and prove restoration in a disposable database."""

import datetime
import json
import os
import subprocess
import uuid
from pathlib import Path

KUBECTL = [
    "sudo",
    "-n",
    "k3s",
    "kubectl",
    "-n",
    "secure-delivery",
    "exec",
    "-i",
    "database-0",
    "--",
]


def database(args, data=None):
    result = subprocess.run(KUBECTL + args, input=data, capture_output=True)  # noqa: S603
    if result.returncode:
        raise RuntimeError("Database backup/restore operation failed; output omitted")
    return result.stdout


def main():
    os.umask(0o077)
    folder = Path.home() / ".local/share/secure-delivery-backups"
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    data = database(["pg_dump", "-U", "postgres", "-d", "postgres", "-Fc"])
    (folder / (stamp + ".dump")).write_bytes(data)
    temporary = "restore_check_" + uuid.uuid4().hex[:12]
    database(["createdb", "-U", "postgres", temporary])
    try:
        database(["pg_restore", "-U", "postgres", "-d", temporary, "--exit-on-error"], data)
        rows = (
            database(
                ["psql", "-U", "postgres", "-d", temporary, "-Atc", "SELECT count(*) FROM releases"]
            )
            .decode()
            .strip()
        )
        if not rows.isdigit() or int(rows) < 1:
            raise RuntimeError("Restored release inventory was empty")
    finally:
        database(["dropdb", "-U", "postgres", temporary])
    print(
        json.dumps(
            {
                "time": stamp,
                "backup_bytes": len(data),
                "mode": "0600",
                "restore_verified": True,
                "restored_release_count": int(rows),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
