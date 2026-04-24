"""Download server jars by scraping official sites using BeautifulSoup."""

import requests
from bs4 import BeautifulSoup
from typing import Optional
from pathlib import Path


def download_paper(version: str, output_dir: str) -> Optional[str]:
    project = "paper"
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    try:
        r = requests.get("https://api.papermc.io/v2/projects/paper", timeout=15)
        r.raise_for_status()
        data = r.json()
        
        if version and version in data["versions"]:
            v = version
        else:
            v = data["versions"][-1]
        
        r2 = requests.get(f"https://api.papermc.io/v2/projects/paper/versions/{v}/builds", timeout=15)
        r2.raise_for_status()
        builds = r2.json()["builds"]
        latest = builds[-1]["build"]
        name = builds[-1]["downloads"]["application"]["name"]
        
        url = f"https://api.papermc.io/v2/projects/paper/versions/{v}/builds/{latest}/downloads/{name}"
        r3 = requests.get(url, stream=True, timeout=120)
        r3.raise_for_status()
        
        fpath = out / f"paper-{v}-{latest}.jar"
        with open(fpath, "wb") as f:
            for chunk in r3.iter_content(65536):
                if chunk: f.write(chunk)
        return str(fpath)
    except Exception as e:
        print(f"Paper download failed: {e}")
        return None


def download_purpur(version: str, output_dir: str) -> Optional[str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    try:
        r = requests.get("https://api.purpurmc.org/v2/purpur", timeout=15)
        r.raise_for_status()
        data = r.json()
        
        if version and version in data["versions"]:
            v = version
        else:
            v = list(data["versions"].keys())[-1]
        
        builds = data["versions"][v]
        if isinstance(builds, list):
            latest = builds[-1]
        else:
            latest = builds
        
        url = f"https://api.purpurmc.org/v2/purpur/{v}/{latest}/download"
        r3 = requests.get(url, stream=True, timeout=120)
        r3.raise_for_status()
        
        fpath = out / f"purpur-{v}-{latest}.jar"
        with open(fpath, "wb") as f:
            for chunk in r3.iter_content(65536):
                if chunk: f.write(chunk)
        return str(fpath)
    except Exception as e:
        print(f"Purpur download failed: {e}")
        return None


def download_mohist(version: str, output_dir: str) -> Optional[str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    try:
        r = requests.get("https://mohistmc.com/api/v2/projects/mohist", timeout=15)
        r.raise_for_status()
        data = r.json()
        
        if version:
            v = version
        else:
            v = list(data.keys())[-1]
        
        builds = data[v]
        latest = builds[-1]
        url = f"https://mohistmc.com/api/v2/projects/mohist/{v}/{latest}/download"
        
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()
        
        fpath = out / f"mohist-{v}-{latest}.jar"
        with open(fpath, "wb") as f:
            for chunk in resp.iter_content(65536):
                if chunk: f.write(chunk)
        return str(fpath)
    except Exception as e:
        print(f"Mohist download failed: {e}")
        return None


def download_fabric(version: str, output_dir: str) -> Optional[str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    try:
        r = requests.get("https://meta.fabricmc.net/v2/versions/loader", timeout=15)
        r.raise_for_status()
        loaders = r.json()
        
        if version:
            v = version
        else:
            rv = requests.get("https://meta.fabricmc.net/v2/versions/game", timeout=15)
            v = rv.json()[-1]["version"]
        
        loader = loaders[0]["loader"]["version"]
        installer = loaders[0].get("installer", {}).get("version", "1.0.0")
        
        url = f"https://meta.fabricmc.net/v2/versions/loader/{v}/{loader}/{installer}/server/jar"
        
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()
        
        fpath = out / f"fabric-server-{v}.jar"
        with open(fpath, "wb") as f:
            for chunk in resp.iter_content(65536):
                if chunk: f.write(chunk)
        return str(fpath)
    except Exception as e:
        print(f"Fabric download failed: {e}")
        return None


def download_spigot(version: str, output_dir: str) -> Optional[str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    try:
        url = f"https://download.getbukkit.org/spigot/spigot-{version}.jar"
        resp = requests.get(url, stream=True, timeout=120)
        
        if resp.status_code != 200:
            url = "https://download.getbukkit.org/spigot/spigot-1.20.4.jar"
            resp = requests.get(url, stream=True, timeout=120)
            resp.raise_for_status()
        
        fpath = out / url.split("/")[-1]
        with open(fpath, "wb") as f:
            for chunk in resp.iter_content(65536):
                if chunk: f.write(chunk)
        return str(fpath)
    except Exception as e:
        print(f"Spigot download failed: {e}")
        return None


def download_server(server_type: str, version: str, output_dir: str = "servers") -> Optional[str]:
    funcs = {
        "Paper": download_paper,
        "Purpur": download_purpur,
        "Fabric": download_fabric,
        "Spigot": download_spigot,
        "Folia": download_paper,
        "Mohist": download_mohist,
    }
    
    fn = funcs.get(server_type)
    if not fn:
        return None
    
    if server_type == "Folia":
        return download_paper(version, output_dir)
    
    return fn(version, output_dir)