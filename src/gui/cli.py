"""CLI utilities for launch script generation."""

from typing import Dict, Any


def generate_launch_script(server: Dict[str, Any], memory: int = 2048) -> str:
    """Generate a launch script for the server."""
    jar_path = server.get("jar_path", "./server.jar")
    name = server.get("name", "server")
    
    script = f"""#!/bin/bash
# {name} startup script

MEMORY={memory}

java -Xms${{MEMORY}}M -Xmx${{MEMORY}}M -jar {jar_path} nogui
"""
    return script


def generate_windows_script(server: Dict[str, Any], memory: int = 2048) -> str:
    """Generate a Windows batch script for the server."""
    jar_path = server.get("jar_path", "./server.jar")
    
    script = f"""@echo off
REM Server startup script

set MEMORY={memory}

java -Xms%MEMORY%M -Xmx%MEMORY%M -jar {jar_path} nogui
"""
    return script


def save_script(content: str, filename: str) -> str:
    """Save script to file."""
    with open(filename, 'w') as f:
        f.write(content)
    return filename