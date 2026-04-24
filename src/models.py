"""Data models for Minecraft Server Manager."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Server:
    """Information about a Minecraft server."""
    name: str
    version: str
    server_type: str
    jar_path: Optional[str] = None
    modrinth_id: Optional[str] = None

@dataclass
class Version:
    """Modrinth version info."""
    project_id: str
    version_name: str
    file_name: str
    description: str
    download_url: str
    timestamp: datetime

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Version":
        """Create Version from API response."""
        return cls(
            project_id=data.get("project_id", ""),
            version_name=data.get("version_number", ""),
            file_name=data.get("file_name", ""),
            description=data.get("description", ""),
            download_url=data.get("download_url", ""),
            timestamp=datetime.now(),
        )

@dataclass
class PlayerStat:
    """Player statistics for dashboard."""
    player_name: str
    health: float
    online_players: int
    max_players: int
    latency: str
