# Minecraft Server Manager

Modern Minecraft server management tool with FastAPI backend.

## Project Structure

```
MinecraftServerManager/
├── src/                    # Python source code
│   ├── api/               # FastAPI routes
│   │   └── routes.py
│   ├── cli/              # Script generators
│   │   ├── generator.py
│   │   └── __init__.py
│   ├── server/           # Server detection
│   │   ├── bedrock.py
│   │   ├── java.py
│   │   ├── modrinth.py
│   │   ├── __init__.py
│   │   └── __pycache__/
│   ├── core.py          # FastAPI app
│   └── models.py        # Data models
├── src/ui/               # Next.js frontend
│   ├── components/
│   ├── contexts/
│   ├── pages/
│   ├── styles/
│   ├── package.json
│   └── tsconfig.json
├── build/                # Build scripts
│   ├── build.py
│   ├── build.ps1
│   ├── build.sh
│   ├── build.bat
│   ├── build_win.py
│   └── MinecraftServerManager.iss
├── .github/workflows/      # CI/CD
│   └── build.yml
├── dist/                 # Built executables
│   ├── main.exe
│   └── MinecraftServerManager-Setup-1.0.0.exe
├── tests/                # Tests
├── main.py              # Entry point
├── run.py              # Run both API + UI
├── requirements.txt    # Python deps
└── README.md
```

## Quick Start

### Run
```bash
python main.py
```

### Build
```bash
# Windows
py -3.11 -m PyInstaller main.py --onefile --windowed --add-data "src;src" --hidden-import miniupnpc --clean

# Or use build script
python build/build.py
```

### Install
```cmd
ISCC.exe build\MinecraftServerManager.iss
```

## Features

- Java Server Detection (Paper, Purpur, Fabric, Spigot, etc.)
- Bedrock Server Detection (PocketMine, Nukkit, BDS, etc.)
- Modrinth Integration
- Auto Port Forwarding (UPnP)
- Launch Script Generator
- Modern Web UI