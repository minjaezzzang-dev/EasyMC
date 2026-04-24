"""Modrinth API client."""

import requests
from typing import List, Dict, Any, Optional
from pathlib import Path


MODRINTH_API = "https://api.modrinth.com/v2"

SERVER_PROJECT_IDS = {
    "paper": "PapMC",
    "purpur": "Purpur",
    "fabric": "fabric",
    "spigot": "Spigot",
    "folia": "Folia",
    "mohist": "Mohist",
    "velocitech": "velocitech",
}


class ModrinthClient:
    def __init__(self):
        self.session = requests.Session()

    def get_project_versions(self, project_id: str) -> List[Dict[str, Any]]:
        response = self.session.get(f"{MODRINTH_API}/project/{project_id}/version")
        response.raise_for_status()
        return response.json()

    def get_latest_version(self, project_id: str, mc_version: str = None) -> Optional[Dict[str, Any]]:
        versions = self.get_project_versions(project_id)
        if not versions:
            return None
        
        if mc_version:
            for v in versions:
                if mc_version in v.get("game_versions", []):
                    return v
        
        return versions[0]

    def get_download_url(self, project_id: str, mc_version: str = None) -> Optional[str]:
        latest = self.get_latest_version(project_id, mc_version)
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
        
        response = self.session.get(download_url, stream=True)
        response.raise_for_status()
        
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return str(file_path)

    def search_versions(self, query: str) -> List[Dict[str, Any]]:
        response = self.session.get(f"{MODRINTH_API}/project", params={"query": query})
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])