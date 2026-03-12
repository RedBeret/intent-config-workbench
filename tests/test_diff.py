from __future__ import annotations

from pathlib import Path

from intent_config_workbench.api import diff_workspace_api, render_workspace_api


def test_demo_overlay_changes_single_device(workspace_copy: Path) -> None:
    render_workspace_api(workspace_copy)
    summary = diff_workspace_api(
        workspace_copy,
        baseline_dir=workspace_copy / "rendered",
        intent_overlays=[workspace_copy / "demo" / "intent"],
        candidate_dir=workspace_copy / "artifacts" / "candidate",
    )

    assert summary["changed_devices"] == 1
    assert summary["unchanged_devices"] == 2
    changed = {device["hostname"] for device in summary["devices"] if device["changed"]}
    assert changed == {"edge-02"}
