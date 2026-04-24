"""Java server detection."""

import re
from pathlib import Path
from typing import List, Dict, Any


class JavaServerDetector:
    TYPE_PATTERNS = {
        "paper": ["paper", "Paper"],
        "purpur": ["purpur", "Purpur"],
        "fabric": ["fabric", "Fabric"],
        "velocitech": ["velocitech", "Velocitech"],
        "spigot": ["spigot", "Spigot"],
        "folia": ["folia", "Folia"],
        "mohist": ["mohist", "Mohist"],
    }

    def __init__(self, base_dir: str = "servers"):
        self.base_dir = Path(base_dir)

    def discover_servers(self) -> List[Dict[str, Any]]:
        servers = []
        for server_type in self.TYPE_PATTERNS.keys():
            for pattern_str in self.TYPE_PATTERNS[server_type]:
                if not self.base_dir.exists():
                    continue
                for jar_path in self.base_dir.glob(f"**/{pattern_str}.jar"):
                    version = self._extract_version(jar_path)
                    servers.append({
                        "name": jar_path.stem,
                        "version": version,
                        "server_type": server_type,
                        "jar_path": str(jar_path),
                    })
        return servers

    def _extract_version(self, jar_path: Path) -> str:
        name = jar_path.stem.lower()
        match = re.search(r"(\d+\.\d+\.\d+)", name)
        return match.group(1) if match else "unknown"