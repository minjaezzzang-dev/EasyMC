"""API routes."""

from fastapi import APIRouter, HTTPException, Response
from typing import List, Dict, Any, Optional
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import from local src
src_path = Path(__file__).resolve().parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from models import Server, Version
from server.java import JavaServerDetector
from server.bedrock import BedrockServerDetector
from cli.generator import generate_launch_script, save_script
from server_properties import ServerProperties

router = APIRouter()
java_detector = JavaServerDetector()
bedrock_detector = BedrockServerDetector()
props = ServerProperties()

@router.get("/servers/java", response_model=List[Server])
async def list_java_servers():
    try:
        servers = java_detector.discover_servers()
        return servers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/servers/bedrock", response_model=List[Server])
async def list_bedrock_servers():
    try:
        servers = bedrock_detector.discover_bedrock_servers()
        return servers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/servers/search")
async def search_versions(query: str):
    try:
        from server.modrinth import ModrinthClient
        client = ModrinthClient()
        results = client.search_versions(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/servers/download")
async def download_script(server_type: str, version: str, name: str = "server"):
    try:
        server = {"server_type": server_type, "version": version, "name": name, "jar_path": f"./{name}.jar"}
        script_content = generate_launch_script(server)
        save_script(script_content, f"{name}.sh")
        return Response(content=script_content, media_type="text/plain", headers={"Content-Disposition": f'attachment; filename="{name}.sh"'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/servers/projects")
async def list_projects():
    try:
        from server.modrinth import SERVER_PROJECT_IDS
        return SERVER_PROJECT_IDS
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/servers/install")
async def install_server(server_type: str, mc_version: str = None, output_dir: str = "servers"):
    try:
        from server.modrinth import ModrinthClient, SERVER_PROJECT_IDS
        project_id = SERVER_PROJECT_IDS.get(server_type)
        if not project_id:
            return {"success": False, "error": f"Unknown server type: {server_type}"}
        client = ModrinthClient()
        file_path = client.download_version(project_id, output_dir, mc_version)
        if file_path:
            return {"success": True, "file_path": file_path}
        return {"success": False, "error": "Failed to download"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/properties")
async def get_properties():
    try:
        return props.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/properties/port")
async def get_port():
    return {"port": props.get_port()}

@router.post("/properties/port")
async def set_port(port: int):
    if props.set_port(port):
        return {"success": True, "port": port}
    return {"success": False, "error": "Failed to set port"}

@router.get("/properties/max-players")
async def get_max_players():
    return {"max_players": props.get_max_players()}

@router.post("/properties/max-players")
async def set_max_players(max_players: int):
    if props.set_max_players(max_players):
        return {"success": True, "max_players": max_players}
    return {"success": False, "error": "Failed to set max players"}

@router.get("/properties/motd")
async def get_motd():
    return {"motd": props.get_motd()}

@router.post("/properties/motd")
async def set_motd(motd: str):
    if props.set_motd(motd):
        return {"success": True, "motd": motd}
    return {"success": False, "error": "Failed to set MOTD"}

@router.get("/properties/gamemode")
async def get_gamemode():
    return {"gamemode": props.get_gamemode()}

@router.post("/properties/gamemode")
async def set_gamemode(gamemode: str):
    if props.set_gamemode(gamemode):
        return {"success": True, "gamemode": gamemode}
    return {"success": False, "error": "Invalid gamemode"}

@router.get("/properties/difficulty")
async def get_difficulty():
    return {"difficulty": props.get_difficulty()}

@router.post("/properties/difficulty")
async def set_difficulty(difficulty: str):
    if props.set_difficulty(difficulty):
        return {"success": True, "difficulty": difficulty}
    return {"success": False, "error": "Invalid difficulty"}