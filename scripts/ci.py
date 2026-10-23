"""Run fail-closed security gates on a disposable Linux Docker host."""

import json
import os
import secrets
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
LOCK = json.loads((ROOT / "tools.lock.json").read_text())
RESULTS = []


def run(args, **kwargs):
    return subprocess.run(args, check=True, cwd=ROOT, **kwargs)  # noqa: S603


def image(name):
    return LOCK["images"][name]["pinned"]


def scanner(name, args, mounts=None):
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{ROOT}:/src:ro",
        "-v",
        f"{REPORTS}:/reports",
        "-w",
        "/src",
    ]
    if name == "gitleaks":
        command += [
            "-e",
            "GIT_CONFIG_COUNT=1",
            "-e",
            "GIT_CONFIG_KEY_0=safe.directory",
            "-e",
            "GIT_CONFIG_VALUE_0=/src",
        ]
    for mount in mounts or []:
        command += ["-v", mount]
    return run(command + [image(name)] + args)


def gate(name, action):
    started = time.monotonic()
    try:
        action()
    except (subprocess.CalledProcessError, OSError, RuntimeError) as error:
        RESULTS.append(
            {
                "gate": name,
                "passed": False,
                "error": type(error).__name__,
                "seconds": round(time.monotonic() - started, 2),
            }
        )
        return False
    RESULTS.append({"gate": name, "passed": True, "seconds": round(time.monotonic() - started, 2)})
    return True


def integration(candidate):
    network = "secure-delivery-ci"
    admin_password = secrets.token_urlsafe(32)
    reader_password = secrets.token_urlsafe(32)
    run(["docker", "network", "create", network])
    try:
        env = {**os.environ, "POSTGRES_PASSWORD": admin_password}
        run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "database",
                "--network",
                network,
                "-e",
                "POSTGRES_PASSWORD",
                "-v",
                f"{ROOT / 'deploy/base/init.sql'}:/docker-entrypoint-initdb.d/init.sql:ro",
                image("postgres"),
            ],
            env=env,
        )
        for _attempt in range(60):
            ready = subprocess.run(  # noqa: S603
                ["docker", "exec", "database", "pg_isready", "-U", "postgres"],
                capture_output=True,
            )
            if ready.returncode == 0:
                # pg_isready can succeed during entrypoint initialization; require the schema.
                schema = subprocess.run(  # noqa: S603
                    [
                        "docker",
                        "exec",
                        "database",
                        "psql",
                        "-U",
                        "postgres",
                        "-Atc",
                        "SELECT count(*) FROM releases",
                    ],
                    capture_output=True,
                )
                if schema.returncode == 0:
                    break
            time.sleep(1)
        else:
            raise RuntimeError("Database did not become ready")
        sql = (
            f"CREATE ROLE app_reader LOGIN PASSWORD '{reader_password}'; "
            "GRANT CONNECT ON DATABASE postgres TO app_reader; "
            "GRANT USAGE ON SCHEMA public TO app_reader; "
            "GRANT SELECT ON releases TO app_reader;"
        )
        run(
            ["docker", "exec", "-i", "database", "psql", "-U", "postgres", "-v", "ON_ERROR_STOP=1"],
            input=sql.encode(),
            stdout=subprocess.DEVNULL,
        )
        env = {
            **os.environ,
            "DATABASE_URL": f"postgresql://app_reader:{reader_password}@database/postgres",
        }
        run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "app",
                "--network",
                network,
                "--read-only",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges:true",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=32m,uid=10001,gid=10001",
                "--memory=256m",
                "--cpus=0.5",
                "-e",
                "DATABASE_URL",
                candidate,
            ],
            env=env,
        )
        for _attempt in range(60):
            health = subprocess.run(  # noqa: S603
                [
                    "docker",
                    "exec",
                    "app",
                    "python",
                    "-c",
                    "import urllib.request; "
                    "urllib.request.urlopen('http://localhost:8080/health/ready', timeout=3)",
                ],
                capture_output=True,
            )
            if health.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("Application did not become ready")
        # Real database least-privilege test: writes must fail, reads must succeed.
        reader_env = {**os.environ, "PGPASSWORD": reader_password}
        write = subprocess.run(  # noqa: S603
            [
                "docker",
                "exec",
                "-e",
                "PGPASSWORD",
                "database",
                "psql",
                "-h",
                "127.0.0.1",
                "-U",
                "app_reader",
                "-d",
                "postgres",
                "-v",
                "ON_ERROR_STOP=1",
                "-c",
                "INSERT INTO releases(version,description) VALUES ('bad','must fail')",
            ],
            env=reader_env,
            capture_output=True,
        )
        if write.returncode == 0 or b"permission denied" not in write.stderr:
            raise RuntimeError("Read-only database role verification failed")
        run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                network,
                "-v",
                f"{ROOT / 'security/zap.yaml'}:/zap/wrk/zap.yaml:ro",
                "-v",
                f"{REPORTS}:/zap/wrk/reports:rw",
                image("zap"),
                "zap.sh",
                "-cmd",
                "-autorun",
                "/zap/wrk/zap.yaml",
            ]
        )
        if not (REPORTS / "zap-report.json").is_file():
            raise RuntimeError("ZAP report missing")
    finally:
        for container in ["app", "database"]:
            subprocess.run(["docker", "rm", "-f", "-v", container], capture_output=True)  # noqa: S603
        subprocess.run(["docker", "network", "rm", network], capture_output=True)  # noqa: S603


def main():
    REPORTS.mkdir(exist_ok=True)
    REPORTS.chmod(0o777)  # ZAP uses a non-root identity in a disposable runner. noqa: S103
    candidate = "secure-delivery:ci"
    gate("application-tests", lambda: run(["uv", "run", "--locked", "pytest", "-q"]))
    gate("lint", lambda: run(["uv", "run", "--locked", "ruff", "check", "."]))
    gate("repository-policy", lambda: run(["uv", "run", "--locked", "python", "scripts/policy.py"]))
    gate(
        "gitleaks-history",
        lambda: scanner(
            "gitleaks",
            [
                "git",
                "/src",
                "--redact",
                "--report-format",
                "json",
                "--report-path",
                "/reports/gitleaks.json",
                "--log-opts=--all",
            ],
        ),
    )
    gate(
        "gitleaks-worktree",
        lambda: scanner(
            "gitleaks",
            [
                "dir",
                "/src",
                "--redact",
                "--report-format",
                "json",
                "--report-path",
                "/reports/gitleaks-worktree.json",
            ],
        ),
    )
    gate(
        "trivy-dependencies",
        lambda: scanner(
            "trivy",
            [
                "fs",
                "--scanners",
                "vuln",
                "--severity",
                "HIGH,CRITICAL",
                "--exit-code",
                "1",
                "--skip-dirs",
                ".tools,.venv,.git,reports",
                "--format",
                "json",
                "--output",
                "/reports/trivy-dependencies.json",
                "/src",
            ],
        ),
    )
    gate(
        "trivy-config",
        lambda: scanner(
            "trivy",
            [
                "config",
                "--severity",
                "HIGH,CRITICAL",
                "--exit-code",
                "1",
                "--format",
                "json",
                "--output",
                "/reports/trivy-config.json",
                "/src/deploy",
            ],
        ),
    )
    gate(
        "checkov",
        lambda: scanner(
            "checkov",
            [
                "-d",
                "/src/deploy",
                "--config-file",
                "/src/.checkov.yaml",
                "--compact",
                "-o",
                "json",
                "--output-file-path",
                "/reports",
            ],
        ),
    )
    built = gate(
        "container-build",
        lambda: run(
            ["docker", "build", "--pull", "--iidfile", "reports/candidate.id", "-t", candidate, "."]
        ),
    )
    if built:
        gate(
            "trivy-image",
            lambda: scanner(
                "trivy",
                [
                    "image",
                    "--scanners",
                    "vuln",
                    "--severity",
                    "HIGH,CRITICAL",
                    "--exit-code",
                    "1",
                    "--format",
                    "json",
                    "--output",
                    "/reports/trivy-image.json",
                    candidate,
                ],
                ["/var/run/docker.sock:/var/run/docker.sock"],
            ),
        )
        gate("integration-and-zap", lambda: integration(candidate))
    summary = {
        "source_commit": os.environ.get("GITHUB_SHA", "local"),
        "gates": RESULTS,
        "passed": bool(RESULTS) and all(result["passed"] for result in RESULTS),
    }
    (REPORTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    rows = ["# Security gate results", "", "| Gate | Result |", "|---|---|"]
    rows += [f"| {r['gate']} | {'PASS' if r['passed'] else 'FAIL'} |" for r in RESULTS]
    (REPORTS / "summary.md").write_text("\n".join(rows) + "\n")
    print("\n".join(rows))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
