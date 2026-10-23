"""Repository invariants supplement, rather than replace, external scanners."""

import datetime
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def violations(root=ROOT):
    errors = []
    for path in (root / "deploy").rglob("kustomization.yaml"):
        config = yaml.safe_load(path.read_text())
        for resource in config.get("resources", []) + config.get("bases", []):
            if "://" in resource or resource.startswith(("git@", "/")):
                errors.append(f"{path.name}: external Kustomize resource forbidden")
    for path in (root / ".github/workflows").glob("*.y*ml"):
        content = path.read_text()
        for action in re.findall(r"uses:\s*([^\s#]+)", content):
            if not action.startswith("./") and not re.fullmatch(r"[^@]+@[a-f0-9]{40}", action):
                errors.append(f"{path.name}: action must use a full SHA: {action}")
        if "pull_request_target" in content:
            errors.append(f"{path.name}: privileged PR trigger forbidden")
        if "self-hosted" in content:
            errors.append(f"{path.name}: self-hosted runner forbidden")
    for path in (root / "deploy/base").glob("*.yaml"):
        for document in yaml.safe_load_all(path.read_text()):
            if not document or document.get("kind") not in {"Deployment", "StatefulSet"}:
                continue
            pod = document["spec"]["template"]["spec"]
            security = pod.get("securityContext", {})
            if not security.get("runAsNonRoot"):
                errors.append(f"{path.name}: non-root required")
            if pod.get("automountServiceAccountToken") is not False:
                errors.append(f"{path.name}: service account token must not mount")
            for container in pod["containers"]:
                context = container.get("securityContext", {})
                if (
                    context.get("privileged")
                    or context.get("allowPrivilegeEscalation") is not False
                ):
                    errors.append(f"{path.name}: privilege escalation forbidden")
                if context.get("readOnlyRootFilesystem") is not True:
                    errors.append(f"{path.name}: read-only root filesystem required")
                if "ALL" not in context.get("capabilities", {}).get("drop", []):
                    errors.append(f"{path.name}: drop all capabilities")
                if set(container.get("resources", {})) != {"requests", "limits"}:
                    errors.append(f"{path.name}: resource requests and limits required")
                if "readinessProbe" not in container or "livenessProbe" not in container:
                    errors.append(f"{path.name}: health probes required")
    today = datetime.date.today()
    for exception in json.loads((root / "security/exceptions.json").read_text()):
        required = {"id", "tool", "scope", "reason", "owner", "expires"}
        if not required.issubset(exception):
            errors.append("Exception missing required fields")
        elif datetime.date.fromisoformat(exception["expires"]) <= today:
            errors.append(f"Expired exception: {exception['id']}")
    return errors


if __name__ == "__main__":
    problems = violations()
    print("\n".join(problems) if problems else "Repository policy passed")
    raise SystemExit(bool(problems))
