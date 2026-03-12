from __future__ import annotations

from pathlib import Path

import pytest

from intent_config_workbench.api import WorkspaceValidationError, validate_workspace

FIXTURES = Path(__file__).parent / "fixtures"


def test_validate_reports_field_level_errors(workspace_copy: Path) -> None:
    invalid_source = FIXTURES / "invalid" / "edge-01.yaml"
    (workspace_copy / "intent" / "edge-01.yaml").write_text(invalid_source.read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(WorkspaceValidationError) as error_info:
        validate_workspace(workspace_copy)

    issues = error_info.value.issues
    assert any(issue["source"] == "edge-01" for issue in issues)
    assert any(issue["field"].startswith("users.0.username") for issue in issues)
