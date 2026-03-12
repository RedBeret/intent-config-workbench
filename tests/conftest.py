from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def copy_workspace(destination: Path) -> Path:
    for name in ["defaults", "inventory", "intent", "demo", "templates"]:
        shutil.copytree(REPO_ROOT / name, destination / name, dirs_exist_ok=True)
    for name in ["artifacts", "rendered", ".workbench"]:
        (destination / name).mkdir(parents=True, exist_ok=True)
    return destination


@pytest.fixture()
def workspace_copy(tmp_path: Path) -> Path:
    return copy_workspace(tmp_path / "workspace")
