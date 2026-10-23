"""Generate local secrets and provision the SELECT-only role; never print credentials."""

import argparse
import base64
import json
import secrets
import subprocess
from urllib.parse import urlparse

KUBECTL = ["sudo", "-n", "k3s", "kubectl", "-n", "secure-delivery"]


def kubectl(args, data=None):
    result = subprocess.run(KUBECTL + args, input=data, capture_output=True)  # noqa: S603
    if result.returncode:
        raise RuntimeError("Kubernetes operation failed; credentials omitted from diagnostics")
    return result.stdout


def ensure_secret(name, key, value):
    raw = kubectl(["get", "secret", name, "--ignore-not-found", "-o", "json"])
    existing = json.loads(raw or b"null")
    if existing:
        return base64.b64decode(existing["data"][key]).decode()
    document = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"name": name},
        "type": "Opaque",
        "stringData": {key: value},
    }
    kubectl(["apply", "-f", "-"], json.dumps(document).encode())
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provision", action="store_true")
    args = parser.parse_args()
    ensure_secret("database-admin", "password", secrets.token_urlsafe(40))
    url = ensure_secret(
        "app-database",
        "url",
        f"postgresql://app_reader:{secrets.token_urlsafe(40)}@database/postgres",
    )
    if args.provision:
        kubectl(["rollout", "status", "statefulset/database", "--timeout=180s"])
        password = urlparse(url).password
        if not password or not all(c.isalnum() or c in "_-" for c in password):
            raise RuntimeError("Unexpected generated credential format")
        sql = (
            "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='app_reader') "
            "THEN CREATE ROLE app_reader LOGIN; END IF; END $$; "
            f"ALTER ROLE app_reader PASSWORD '{password}'; "
            "GRANT CONNECT ON DATABASE postgres TO app_reader; "
            "GRANT USAGE ON SCHEMA public TO app_reader; GRANT SELECT ON releases TO app_reader;"
        )
        kubectl(
            ["exec", "-i", "database-0", "--", "psql", "-U", "postgres", "-v", "ON_ERROR_STOP=1"],
            sql.encode(),
        )
    print(
        "Database credentials prepared"
        + ("; SELECT-only role provisioned" if args.provision else "")
    )


if __name__ == "__main__":
    main()
