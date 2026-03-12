from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml
from pydantic import ValidationError

from .models import (
    DeviceConfig,
    DeviceIntent,
    GlobalDefaults,
    InventoryDevice,
    WorkspaceBundle,
    pydantic_error_to_issues,
)
from .utils import deep_merge, sorted_yaml_files


@dataclass
class WorkspaceValidationError(Exception):
    issues: list[dict[str, str]]

    def __str__(self) -> str:
        details = ", ".join(f"{issue['source']}:{issue['field']}: {issue['message']}" for issue in self.issues)
        return f"Workspace validation failed: {details}"


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a mapping in {path}")
    return payload


def _load_defaults(path: Path) -> GlobalDefaults:
    try:
        return GlobalDefaults.model_validate(_load_yaml_mapping(path))
    except ValidationError as error:
        raise WorkspaceValidationError(pydantic_error_to_issues(str(path), error)) from error


def _load_inventory(path: Path) -> dict[str, InventoryDevice]:
    payload = _load_yaml_mapping(path)
    devices = payload.get("devices")
    if not isinstance(devices, list):
        raise ValueError(f"{path} must contain a 'devices' list")
    results: dict[str, InventoryDevice] = {}
    issues: list[dict[str, str]] = []
    for index, item in enumerate(devices):
        try:
            device = InventoryDevice.model_validate(item)
        except ValidationError as error:
            issues.extend(pydantic_error_to_issues(f"{path}#{index}", error))
            continue
        if device.hostname in results:
            issues.append(
                {
                    "source": str(path),
                    "field": f"devices[{index}].hostname",
                    "message": f"duplicate hostname '{device.hostname}'",
                }
            )
            continue
        results[device.hostname] = device
    if issues:
        raise WorkspaceValidationError(issues)
    return results


def _load_intents(intent_dirs: Iterable[Path]) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for directory in intent_dirs:
        if not directory.exists():
            raise FileNotFoundError(f"Missing required directory: {directory}")
        for path in sorted_yaml_files(directory):
            payload = _load_yaml_mapping(path)
            hostname = payload.get("hostname", path.stem)
            if hostname != path.stem:
                raise ValueError(f"Intent file name {path.name} must match hostname {hostname}")
            existing = merged.get(hostname, {"hostname": hostname})
            merged[hostname] = deep_merge(existing, payload)
    return merged


def load_workspace(workspace: Path, intent_overlays: list[Path] | None = None) -> WorkspaceBundle:
    workspace = workspace.resolve()
    defaults = _load_defaults(workspace / "defaults" / "global.yaml")
    inventory = _load_inventory(workspace / "inventory" / "devices.yaml")
    intent_dirs = [workspace / "intent"]
    if intent_overlays:
        intent_dirs.extend(path.resolve() for path in intent_overlays)
    raw_intents = _load_intents(intent_dirs)

    devices: list[DeviceConfig] = []
    issues: list[dict[str, str]] = []

    missing_intent = sorted(set(inventory) - set(raw_intents))
    unknown_intent = sorted(set(raw_intents) - set(inventory))
    for hostname in missing_intent:
        issues.append({"source": hostname, "field": "hostname", "message": "missing intent file"})
    for hostname in unknown_intent:
        issues.append({"source": hostname, "field": "hostname", "message": "inventory entry not found"})

    for hostname in sorted(set(inventory).intersection(raw_intents)):
        inventory_device = inventory[hostname]
        try:
            intent_device = DeviceIntent.model_validate(raw_intents[hostname])
            merged = inventory_device.model_dump() | intent_device.model_dump(exclude={"hostname"})
            device = DeviceConfig.model_validate({"hostname": hostname, **merged})
        except ValidationError as error:
            issues.extend(pydantic_error_to_issues(hostname, error))
            continue
        devices.append(device)

    if issues:
        raise WorkspaceValidationError(issues)

    return WorkspaceBundle(defaults=defaults, devices=devices).ordered()
