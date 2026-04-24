"""Modrinth API client for Minecraft servers."""

import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
import zipfile
import tarfile


MODRINTH_API = "https://api.modrinth.com/v2"

SERVER_PROJECT_IDS = {
    "Paper": "PapMC",
    "Purpur": "Purpur",
    "Fabric": "fabric",
    "Spigot": "Spigot",
    "Folia": "Folia",
    "Mohist": "Mohist",
}

CDN_URLS = {
    "Paper": "https://download.papermc.io/paper/{version}/{filename}",
    "Purpur": "https://purpurmc.org/({version}/{filename}",
    "Fabric": "https://maven.fabricmc.net/net/fabricmc/yarn/{version}/yarn-{version}-v2.jar",
    "Spigot": "https://cdn.getbukkit.org/spigot/spigot-{version}.jar",
}


class ModrinthClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "EasyMC/1.0"})

    def get_versions(self, project_id: str) -> List[Dict[str, Any]]:
        try:
            response = self.session.get(f"{MODRINTH_API}/project/{project_id}/version")
            response.raise_for_status()
            return response.json()
        except:
            return []

    def get_latest(self, project_id: str, minecraft_version: str = None) -> Optional[Dict[str, Any]]:
        versions = self.get_versions(project_id)
        if not versions:
            return None
        
        for v in versions:
            if minecraft_version and minecraft_version in v.get("game_versions", []):
                return v
        
        return versions[0] if versions else None

    def get_download_url(self, project_id: str, minecraft_version: str = None) -> Optional[str]:
        latest = self.get_latest(project_id, minecraft_version)
        if latest:
            files = latest.get("files", [])
            if files:
                return files[0].get("url")
        return None

    def download_version(self, project_id: str, output_dir: str = "servers", mc_version: str = None) -> Optional[str]:
        download_url = self.get_download_url(project_id, mc_version)
        if not download_url:
            return None
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = download_url.split("/")[-1]
        file_path = output_path / filename
        
        try:
            response = self.session.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(file_path)
        except Exception as e:
            print(f"Download error: {e}")
            return None