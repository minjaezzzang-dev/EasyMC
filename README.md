# Minecraft Server Manager

Minecraft server management tool with PyQt6 GUI.

## Structure

```
EasyMC/
├── src/gui/           # PyQt6 GUI
│   ├── window.py     # Main window
│   ├── modrinth.py  # Modrinth API
│   ├── detector.py # Server detection
│   ├── properties.py
│   ├── cli.py      # Launch script generator
│   └── worker.py   # Async worker
├── main.py          # Entry point
├── requirements.txt
├── build.py         # Nuitka build
└── .github/workflows/build.yml
```

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Build

```bash
pip install nuitka
python build.py
```

## Features

- Install servers from Modrinth (Paper, Purpur, Fabric, Spigot, Folia, Mohist)
- Server detection (discovers JARs in servers/ folder)
- Edit server.properties (port, max players, gamemode, difficulty, MOTD)
- Export launch scripts (.bat / .sh)