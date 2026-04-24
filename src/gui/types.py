"""Data models for GUI."""

from typing import Optional
from dataclasses import dataclass


@dataclass
class ServerInfo:
    name: str
    version: str
    server_type: str
    jar_path: Optional[str] = None