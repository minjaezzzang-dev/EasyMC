"""Server properties file handling."""

from typing import Dict
from pathlib import Path


class ServerProperties:
    def __init__(self, file_path: str = "server.properties"):
        self.file_path = Path(file_path)
        self.props: Dict[str, str] = {}
        self.load()

    def load(self):
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.props[key.strip()] = value.strip()

    def save(self):
        with open(self.file_path, 'w') as f:
            for key, value in self.props.items():
                f.write(f"{key}={value}\n")

    def get(self, key: str, default: str = "") -> str:
        return self.props.get(key, default)

    def set(self, key: str, value: str):
        self.props[key] = value
        self.save()

    def get_port(self) -> int:
        return int(self.get("server-port", "25565"))

    def set_port(self, port: int):
        self.set("server-port", str(port))

    def get_max_players(self) -> int:
        return int(self.get("max-players", "20"))

    def set_max_players(self, max_players: int):
        self.set("max-players", str(max_players))

    def get_motd(self) -> str:
        return self.get("motd", "A Minecraft Server")

    def set_motd(self, motd: str):
        self.set("motd", motd)

    def get_gamemode(self) -> str:
        return self.get("gamemode", "survival")

    def set_gamemode(self, gamemode: str):
        self.set("gamemode", gamemode)

    def get_difficulty(self) -> str:
        return self.get("difficulty", "normal")

    def set_difficulty(self, difficulty: str):
        self.set("difficulty", difficulty)