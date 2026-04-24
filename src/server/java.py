"""
Java server detection and version compatibility logic.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JavaServerDetector:
    """
    Detect installed Java server jars (Paper, Purpur, Fabric, Veco).
    """

    TYPE_PATTERNS = {
        "paper": ["paper", "Paper"],
        "purpur": ["purpur", "Purpur"],
        "fabric": ["fabric", "Fabric"],
        "velocitech": ["velocitech", "Velocitech"],
        "spigot": ["spigot", "Spigot"],
        "craftbukkit": ["craftbukkit", "CraftBukkit"],
        "tuinity": ["tuinity", "Tuinity"],
        "airplane": ["airplane", "AirPlane"],
        "folia": ["folia", "Folia"],
        "mohist": ["mohist", "Mohist"],
        "catserver": ["catserver", "CatServer"],
    }

    def __init__(self, base_dir: str = "servers"):
        self.base_dir = Path(base_dir)

    def discover_servers(self) -> List[Dict[str, Any]]:
        """
        Scan base_dir for known server jars and return Server objects.
        """
        servers: List[Dict[str, Any]] = []
        for server_type in self.TYPE_PATTERNS.keys():
            pattern = self.TYPE_PATTERNS[server_type]
            for pattern_str in pattern:
                matches = self.base_dir.glob(f"**/{pattern_str}.jar")
                for jar_path in matches:
                    version = self._extract_version_from_jar(jar_path)
                    server = {
                        "name": jar_path.stem,
                        "version": version,
                        "server_type": server_type,
                        "jar_path": str(jar_path),
                    }
                    servers.append(server)
        return servers

    def _extract_version_from_jar(self, jar_path: Path) -> str:
        """
        Heuristic to extract version string from filename.
        """
        name = jar_path.stem.lower()
        match = re.search(r"(\d+\.\d+\.\d+)", name)
        return match.group(1) if match else "unknown"
