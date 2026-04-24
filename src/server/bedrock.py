"""
Bedrock server detection and Geyser integration.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BedrockServerDetector:
    """
    Detect Bedrock server installations (PocketMine, Nukkit, etc.)
    """

    TYPE_PATTERNS = {
        "pocketmine": ["PocketMine-MP.phar", "pocketmine.phar"],
        "nukkitx": ["nukkitx", "NukkitX"],
        "netherite": ["netherite", "Netherite"],
        "bedrockrock": ["bedrockrock", "BedrockRock"],
        "LiteBedrock": ["LiteBedrock", "litebedrock"],
        "gombedrock": ["go_mbedrock", "go-mbedrock"],
        "bds": ["bedrock_server", "bedrockserver"],
        "bdsx": ["bdsx", "BDSX"],
    }

    def __init__(self, base_dir: str = "servers"):
        self.base_dir = Path(base_dir)

    def discover_bedrock_servers(self) -> List[Dict[str, Any]]:
        """
        Scan for Bedrock server jars or phar files.
        """
        servers: List[Dict[str, Any]] = []
        for server_type, patterns in self.TYPE_PATTERNS.items():
            for pattern in patterns:
                matches = self.base_dir.glob(f"**/{pattern}")
                for path in matches:
                    version = self._extract_version_from_bedrock_file(path)
                    server = {
                        "name": path.stem,
                        "version": version,
                        "server_type": "bedrock",
                        "jar_path": str(path),
                    }
                    servers.append(server)
        return servers

    def _extract_version_from_bedrock_file(self, path: Path) -> str:
        """
        Heuristic to extract version from Bedrock file name or content.
        """
        name = path.stem.lower()
        match = re.search(r"\d+\.\d+", name)
        return match.group(0) if match else "unknown"
