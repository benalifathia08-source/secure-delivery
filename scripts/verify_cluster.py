"""Exercise real admission, RBAC, networking and runtime detection in the local lab."""

import argparse
import datetime
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = json.loads((ROOT / "tools.lock.json").read_text())["images"]["probe"]["pinned"]
KUBECTL = ["sudo", "-n", "k3s", "kubectl"]
NAMES = ["demo-authorized", "demo-unauthorized"]


def command(args, data=None, check=True):
    result = subprocess.run(KUBECTL + args, input=data, capture_output=True)  # noqa: S603
    if check and result.returncode:
        raise RuntimeError("Cluster verification command failed: " + " ".join(args[:3]))
    return result


def apply(document, dry_run=False):
    args = ["-n", "secure-delivery", "apply", "-f", "-"]
    if dry_run:
        args.append("--dry-run=server")
    return command(args, json.dumps(document).encode(), check=not dry_run)


def pod(name, role):
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": name, "labels": {"role": role}},
        "spec": {
            "automountServiceAccountToken": False,
            "restartPolicy": "Never",
            "securityContext": {
                "runAsNonRoot": True,
                "runAsUser": 10001,
                "runAsGroup": 10001,
                "fsGroup": 10001,
                "seccompProfile": {"type": "RuntimeDefault"},
            },
            "containers": [
                {
                    "name": "probe",
                    "image": PROBE,
                    "command": ["sleep", "600"],
                    "securityContext": {
                        "allowPrivilegeEscalation": False,
                        "readOnlyRootFilesystem": True,
                        "capabilities": {"drop": ["ALL"]},
                    },
                    "resources": {
                        "requests": {"cpu": "10m", "memory": "16Mi"},
                        "limits": {"cpu": "100m", "memory": "64Mi"},
                    },
                    "volumeMounts": [{"name": "tmp", "mountPath": "/tmp"}],  # noqa: S108
                }
            ],
            "volumes": [{"name": "tmp", "emptyDir": {"sizeLimit": "8Mi"}}],
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-only", action="store_true")
    args = parser.parse_args()
    evidence = {"time": datetime.datetime.now(datetime.timezone.utc).isoformat(), "checks": {}}
    try:
        for name, role in zip(NAMES, ["authorized-client", "unauthorized-client"], strict=True):
            apply(pod(name, role))
            command(
                [
                    "-n",
                    "secure-delivery",
                    "wait",
                    "--for=condition=Ready",
                    "pod/" + name,
                    "--timeout=120s",
                ]
            )
        # Restricted admission must reject a privileged workload even with valid remaining fields.
        insecure = pod("admission-negative", "unauthorized-client")
        insecure["spec"]["containers"][0]["securityContext"]["privileged"] = True
        insecure["spec"]["containers"][0]["securityContext"]["allowPrivilegeEscalation"] = True
        denied = apply(insecure, dry_run=True)
        assert denied.returncode != 0 and b"PodSecurity" in denied.stderr
        evidence["checks"]["privileged_pod_rejected"] = True
        for verb, resource, namespace in [
            ("get", "secrets", "secure-delivery"),
            ("create", "deployments", "default"),
            ("create", "rolebindings", "secure-delivery"),
        ]:
            result = command(
                [
                    "auth",
                    "can-i",
                    verb,
                    resource,
                    "-n",
                    namespace,
                    "--as=system:serviceaccount:flux-system:app-reconciler",
                ],
                check=False,
            )
            assert result.stdout.strip() == b"no"
        evidence["checks"]["reconciler_privilege_boundaries"] = True
        if not args.runtime_only:
            apply(
                {
                    "apiVersion": "networking.k8s.io/v1",
                    "kind": "NetworkPolicy",
                    "metadata": {"name": "demo-client-egress"},
                    "spec": {
                        "podSelector": {
                            "matchExpressions": [
                                {
                                    "key": "role",
                                    "operator": "In",
                                    "values": ["authorized-client", "unauthorized-client"],
                                }
                            ]
                        },
                        "policyTypes": ["Egress"],
                        "egress": [
                            {
                                "to": [
                                    {"podSelector": {"matchLabels": {"app": "release-inventory"}}}
                                ],
                                "ports": [{"protocol": "TCP", "port": 8080}],
                            }
                        ],
                    },
                }
            )
            service = json.loads(
                command(["-n", "secure-delivery", "get", "service", "app", "-o", "json"]).stdout
            )
            url = "http://" + service["spec"]["clusterIP"] + ":8080/api/releases"
            time.sleep(3)
            allowed = command(
                ["-n", "secure-delivery", "exec", NAMES[0], "--", "wget", "-T", "5", "-qO-", url]
            )
            assert json.loads(allowed.stdout)["releases"]
            blocked = command(
                ["-n", "secure-delivery", "exec", NAMES[1], "--", "wget", "-T", "5", "-qO-", url],
                check=False,
            )
            network_error = any(
                message in blocked.stderr.lower()
                for message in [
                    b"timed out",
                    b"connection refused",
                    b"can't connect",
                    b"host is unreachable",
                    b"no route to host",
                ]
            )
            assert blocked.returncode != 0 and network_error
            evidence["checks"]["authorized_connection_succeeds"] = True
            evidence["checks"]["unauthorized_connection_blocked"] = True
        # The canary is harmless test data; this is a simulation, not a claim of exploitation.
        command(
            [
                "-n",
                "secure-delivery",
                "exec",
                NAMES[0],
                "--",
                "sh",
                "-c",
                "printf controlled-demo > /tmp/secure-delivery-runtime-canary; "
                "cat /tmp/secure-delivery-runtime-canary",
            ]
        )
        evidence["checks"]["runtime_canary_triggered"] = True
    finally:
        command(
            ["-n", "secure-delivery", "delete", "pod"] + NAMES + ["--ignore-not-found"], check=False
        )
        command(
            [
                "-n",
                "secure-delivery",
                "delete",
                "networkpolicy",
                "demo-client-egress",
                "--ignore-not-found",
            ],
            check=False,
        )
    output = ROOT / "reports/cluster-verification.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
