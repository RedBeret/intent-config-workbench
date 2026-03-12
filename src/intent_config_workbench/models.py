from __future__ import annotations

import ipaddress
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

RFC5737_NETWORKS = (
    ipaddress.IPv4Network("192.0.2.0/24"),
    ipaddress.IPv4Network("198.51.100.0/24"),
    ipaddress.IPv4Network("203.0.113.0/24"),
)

HOSTNAME_RE = re.compile(r"^[a-z][a-z0-9-]{0,30}$")
USERNAME_RE = re.compile(r"^[a-z][a-z0-9_]{1,20}$")
INTERFACE_RE = re.compile(r"^(Mgmt0|Ethernet[0-9]{1,3})$")
SERIAL_RE = re.compile(r"^SYN-[A-Z]+-[0-9]{4}$")
SECRET_TOKEN_RE = re.compile(r"^SYNTHETIC-[A-Z0-9-]+$")


def _is_rfc5737_ipv4(value: ipaddress.IPv4Address) -> bool:
    return any(value in network for network in RFC5737_NETWORKS)


def _normalize_ipv4_interface(value: str) -> str:
    interface = ipaddress.IPv4Interface(value)
    if not _is_rfc5737_ipv4(interface.ip):
        raise ValueError("must use an RFC5737 example address")
    return str(interface)


def _normalize_ipv4_address(value: str) -> str:
    address = ipaddress.IPv4Address(value)
    if not _is_rfc5737_ipv4(address):
        raise ValueError("must use an RFC5737 example address")
    return str(address)


class GlobalDefaults(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain_name: str = Field(pattern=r"^[a-z0-9.-]+\.invalid$")
    banner: str
    ntp_servers: list[str] = Field(default_factory=list)
    dns_servers: list[str] = Field(default_factory=list)
    render_timeout_seconds: float = Field(default=5, gt=0, le=30)
    retry_attempts: int = Field(default=3, ge=1, le=10)
    retry_backoff_seconds: float = Field(default=0.2, gt=0, le=5)
    database_path: str = ".workbench/workbench.db"

    @field_validator("ntp_servers", "dns_servers")
    @classmethod
    def validate_ipv4_lists(cls, value: list[str]) -> list[str]:
        return [_normalize_ipv4_address(entry) for entry in value]


class ManagementSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interface_name: str = "Mgmt0"
    ipv4: str
    gateway: str
    dns_servers: list[str] = Field(default_factory=list)

    @field_validator("interface_name")
    @classmethod
    def validate_interface_name(cls, value: str) -> str:
        if not INTERFACE_RE.match(value):
            raise ValueError("must be Mgmt0 or Ethernet<number>")
        return value

    @field_validator("ipv4")
    @classmethod
    def validate_ipv4(cls, value: str) -> str:
        return _normalize_ipv4_interface(value)

    @field_validator("gateway")
    @classmethod
    def validate_gateway(cls, value: str) -> str:
        return _normalize_ipv4_address(value)

    @field_validator("dns_servers")
    @classmethod
    def validate_dns_servers(cls, value: list[str]) -> list[str]:
        return [_normalize_ipv4_address(entry) for entry in value]


class InventoryDevice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hostname: str
    serial: str
    role: Literal["access", "distribution"]
    platform: str = Field(pattern=r"^[a-z0-9-]+$")
    location: str = Field(pattern=r"^[a-z0-9-]+$")
    mgmt: ManagementSettings

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, value: str) -> str:
        if not HOSTNAME_RE.match(value):
            raise ValueError("must be lowercase letters, digits, and hyphens")
        return value

    @field_validator("serial")
    @classmethod
    def validate_serial(cls, value: str) -> str:
        if not SERIAL_RE.match(value):
            raise ValueError("must be a synthetic serial in the form SYN-ROLE-0000")
        return value


class UserAccount(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    role: Literal["netops", "read-only"]
    secret_token: str
    ssh_key: str = Field(pattern=r"^ssh-ed25519\s+\S+\s+\S+$")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not USERNAME_RE.match(value):
            raise ValueError("must use a synthetic lowercase username")
        return value

    @field_validator("secret_token")
    @classmethod
    def validate_secret_token(cls, value: str) -> str:
        if not SECRET_TOKEN_RE.match(value):
            raise ValueError("must be a synthetic token starting with SYNTHETIC-")
        return value


class InterfaceIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = Field(min_length=3, max_length=80)
    enabled: bool = True
    mtu: int = Field(default=1500, ge=576, le=9216)
    mode: Literal["access", "trunk", "routed"]
    access_vlan: int | None = Field(default=None, ge=1, le=4094)
    native_vlan: int | None = Field(default=None, ge=1, le=4094)
    allowed_vlans: list[int] = Field(default_factory=list)
    ipv4_address: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not INTERFACE_RE.match(value):
            raise ValueError("must be Mgmt0 or Ethernet<number>")
        return value

    @field_validator("allowed_vlans")
    @classmethod
    def validate_allowed_vlans(cls, value: list[int]) -> list[int]:
        return sorted(set(value))

    @field_validator("ipv4_address")
    @classmethod
    def validate_ipv4_address(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _normalize_ipv4_interface(value)

    @model_validator(mode="after")
    def validate_mode_specific_fields(self) -> "InterfaceIntent":
        if self.mode == "access" and self.access_vlan is None:
            raise ValueError("access mode requires access_vlan")
        if self.mode == "trunk" and not self.allowed_vlans:
            raise ValueError("trunk mode requires allowed_vlans")
        if self.mode == "routed" and self.ipv4_address is None:
            raise ValueError("routed mode requires ipv4_address")
        if self.mode != "access" and self.access_vlan is not None:
            raise ValueError("access_vlan is only valid for access mode")
        if self.mode != "trunk" and self.native_vlan is not None:
            raise ValueError("native_vlan is only valid for trunk mode")
        if self.mode != "trunk" and self.allowed_vlans:
            raise ValueError("allowed_vlans are only valid for trunk mode")
        if self.mode != "routed" and self.ipv4_address is not None:
            raise ValueError("ipv4_address is only valid for routed mode")
        return self


class VlanIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(ge=1, le=4094)
    name: str = Field(pattern=r"^[A-Z0-9_]+$")


class StaticRoutePlaceholder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prefix: str
    next_hop: str
    description: str = Field(min_length=3, max_length=60)

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, value: str) -> str:
        network = ipaddress.IPv4Network(value, strict=False)
        if not _is_rfc5737_ipv4(network.network_address):
            raise ValueError("must use an RFC5737 example network")
        return str(network)

    @field_validator("next_hop")
    @classmethod
    def validate_next_hop(cls, value: str) -> str:
        return _normalize_ipv4_address(value)


class RoutingIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    router_id: str
    static_routes: list[StaticRoutePlaceholder] = Field(default_factory=list)

    @field_validator("router_id")
    @classmethod
    def validate_router_id(cls, value: str) -> str:
        return _normalize_ipv4_address(value)


class DeviceIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hostname: str
    users: list[UserAccount]
    interfaces: list[InterfaceIntent]
    vlans: list[VlanIntent]
    routing: RoutingIntent

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, value: str) -> str:
        if not HOSTNAME_RE.match(value):
            raise ValueError("must be lowercase letters, digits, and hyphens")
        return value


class DeviceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hostname: str
    serial: str
    role: Literal["access", "distribution"]
    platform: str
    location: str
    mgmt: ManagementSettings
    users: list[UserAccount]
    interfaces: list[InterfaceIntent]
    vlans: list[VlanIntent]
    routing: RoutingIntent

    def ordered(self) -> "DeviceConfig":
        return self.model_copy(
            update={
                "users": sorted(self.users, key=lambda item: item.username),
                "interfaces": sorted(self.interfaces, key=lambda item: item.name),
                "vlans": sorted(self.vlans, key=lambda item: item.id),
                "routing": self.routing.model_copy(
                    update={
                        "static_routes": sorted(
                            self.routing.static_routes,
                            key=lambda item: (item.prefix, item.next_hop, item.description),
                        )
                    }
                ),
            }
        )


class WorkspaceBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    defaults: GlobalDefaults
    devices: list[DeviceConfig]

    def ordered(self) -> "WorkspaceBundle":
        return self.model_copy(
            update={
                "devices": [device.ordered() for device in sorted(self.devices, key=lambda item: item.hostname)]
            }
        )


def pydantic_error_to_issues(label: str, error: ValidationError) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for entry in error.errors():
        loc = ".".join(str(part) for part in entry["loc"])
        issues.append({"source": label, "field": loc, "message": entry["msg"]})
    return issues
