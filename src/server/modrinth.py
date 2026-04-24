"""
Modrinth API client for Minecraft server versions.
"""

import requests
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODRINTH_API = "https://api.modrinth.com/v2"

SERVER_PROJECT_IDS = {
    "paper": "PapMC",
    "purpur": "Purpur",
    "fabric": "fabric",
    "spigot": "Spigot",
    "tuinity": "Tuinity",
    "airplane": "Airplane",
    "folia": "Folia",
    "mohist": "Mohist",
    "catserver": "CatServer",
    "velocitech": "velocitech",
    "paperspigot": "PaperSpigot",
}

class ModrinthClient:
    def __init__(self):
        self.session = requests.Session()

    def get_project_versions(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all versions for a specific project."""
        response = self.session.get(f"{MODRINTH_API}/project/{project_id}/version")
        response.raise_for_status()
        return response.json()

    def get_latest_version(self, project_id: str, minecraft_version: str = None) -> Optional[Dict[str, Any]]:
        """Get the latest version for a project, optionally filtered by Minecraft version."""
        versions = self.get_project_versions(project_id)
        if not versions:
            return None
        
        if minecraft_version:
            for v in versions:
                game_versions = v.get("game_versions", [])
                if minecraft_version in game_versions:
                    return v
        
        return versions[0]

    def get_download_url(self, project_id: str, version: str = None, mc_version: str = None) -> Optional[str]:
        """Get download URL for a project version."""
        if version:
            versions = self.get_project_versions(project_id)
            for v in versions:
                if v.get("version_number") == version:
                    files = v.get("files", [])
                    if files:
                        return files[0].get("url")
        else:
            latest = self.get_latest_version(project_id, mc_version)
            if latest:
                files = latest.get("files", [])
                if files:
                    return files[0].get("url")
        return None

    def download_version(self, project_id: str, output_dir: str = "servers", mc_version: str = None) -> Optional[str]:
        """Download the latest server JAR to output directory."""
        download_url = self.get_download_url(project_id, mc_version=mc_version)
        if not download_url:
            return None
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = download_url.split("/")[-1]
        file_path = output_path / filename
        
        logger.info("Downloading %s to %s", download_url, file_path)
        
        response = self.session.get(download_url, stream=True)
        response.raise_for_status()
        
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info("Downloaded %s", file_path)
        return str(file_path)

    def search_versions(self, query: str, project_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for versions matching query.
        """
        if project_id:
            response = self.session.get(f"{MODRINTH_API}/project/{project_id}/version", params={"query": query})
        else:
            response = self.session.get(f"{MODRINTH_API}/project", params={"query": query})
        response.raise_for_status()
        data = response.json()

        if project_id:
            version_list = data.get("versions", [])
        else:
            version_list = data.get("results", [])

        logger.info("Found %d versions via Modrinth", len(version_list))
        return version_list
