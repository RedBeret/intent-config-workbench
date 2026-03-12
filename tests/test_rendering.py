from __future__ import annotations

from pathlib import Path

from intent_config_workbench.api import render_workspace_api

GOLDEN_DIR = Path(__file__).parent / "golden"


def test_render_matches_golden_files(workspace_copy: Path) -> None:
    summary = render_workspace_api(workspace_copy)

    assert summary["devices"] == 3
    for hostname in ["dist-01", "edge-01", "edge-02"]:
        rendered = (workspace_copy / "rendered" / f"{hostname}.cfg").read_text(encoding="utf-8")
        golden = (GOLDEN_DIR / f"{hostname}.cfg").read_text(encoding="utf-8")
        assert rendered == golden


def test_rerender_is_deterministic_and_idempotent(workspace_copy: Path) -> None:
    first = render_workspace_api(workspace_copy)
    second = render_workspace_api(workspace_copy)

    assert first["devices"] == second["devices"] == 3
    assert first["changed"] == 3
    assert second["changed"] == 0
    for hostname in ["dist-01", "edge-01", "edge-02"]:
        rendered = (workspace_copy / "rendered" / f"{hostname}.cfg").read_text(encoding="utf-8")
        golden = (GOLDEN_DIR / f"{hostname}.cfg").read_text(encoding="utf-8")
        assert rendered == golden
