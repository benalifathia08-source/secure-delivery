import shutil

from scripts.policy import ROOT, violations


def test_repository_baseline():
    assert violations() == []


def test_privileged_manifest_rejected(tmp_path):
    for folder in ["deploy", ".github", "security"]:
        shutil.copytree(ROOT / folder, tmp_path / folder)
    manifest = tmp_path / "deploy/base/app.yaml"
    manifest.write_text(
        manifest.read_text().replace(
            "allowPrivilegeEscalation: false", "allowPrivilegeEscalation: true"
        )
    )
    assert any("privilege escalation" in error for error in violations(tmp_path))


def test_mutable_action_rejected(tmp_path):
    for folder in ["deploy", ".github", "security"]:
        shutil.copytree(ROOT / folder, tmp_path / folder)
    workflow = tmp_path / ".github/workflows/bad.yaml"
    workflow.write_text("jobs:\n  bad:\n    steps:\n      - uses: actions/checkout@main\n")
    assert any("full SHA" in error for error in violations(tmp_path))
