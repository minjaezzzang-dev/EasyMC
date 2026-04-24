"""Main window for Minecraft Server Manager GUI."""

from typing import Optional
import threading
import webbrowser

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QListWidget, QListWidgetItem, QPushButton,
    QLabel, QComboBox, QSpinBox, QGroupBox, QMessageBox,
    QProgressDialog, QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from .types import ServerInfo
from .detector import JavaServerDetector
from .properties import ServerProperties
from .cli import generate_launch_script, generate_windows_script, save_script


SERVER_TYPES = {
    "Paper": "https://papermc.io/downloads",
    "Purpur": "https://purpurmc.org/downloads",
    "Fabric": "https://fabricmc.net/use/installer",
    "Spigot": "https://getbukkit.org/downloads/spigot",
    "Folia": "https://papermc.io/downloads?version=folia",
    "Mohist": "https://mohistmc.org/downloads",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.servers = []
        self.selected_server: Optional[ServerInfo] = None
        self.server_properties = ServerProperties()
        self.java_detector = JavaServerDetector()
        self.dark_mode = True
        
        self.init_ui()
        self.load_servers()
        self.apply_dark_mode()

    def init_ui(self):
        self.setWindowTitle("EasyMC")
        self.setGeometry(100, 100, 800, 650)

        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("EasyMC - Minecraft Server Manager")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        main_layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        self.servers_tab = self.create_servers_tab()
        self.settings_tab = self.create_settings_tab()
        
        self.tabs.addTab(self.servers_tab, "Servers")
        self.tabs.addTab(self.settings_tab, "Settings")
        
        main_layout.addWidget(self.tabs)

    def create_servers_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        install_layout = QHBoxLayout()
        install_layout.addWidget(QLabel("Server:"))
        
        self.server_combo = QComboBox()
        self.server_combo.addItems(list(SERVER_TYPES.keys()))
        install_layout.addWidget(self.server_combo)
        
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.download_server)
        install_layout.addWidget(self.download_btn)
        
        install_layout.addStretch()
        layout.addLayout(install_layout)

        self.server_list = QListWidget()
        self.server_list.itemClicked.connect(self.on_server_selected)
        layout.addWidget(self.server_list)

        action_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export Script")
        self.export_btn.clicked.connect(self.export_script)
        self.export_btn.setEnabled(False)
        action_layout.addWidget(self.export_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_servers)
        action_layout.addWidget(self.refresh_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)

        return widget

    def create_settings_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentTextChanged.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_combo)
        
        theme_layout.addStretch()
        layout.addLayout(theme_layout)

        props_group = QGroupBox("Server Properties")
        props_layout = QVBoxLayout(props_group)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Server Port:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(25565)
        self.port_spin.valueChanged.connect(self.on_port_changed)
        port_layout.addWidget(self.port_spin)
        port_layout.addStretch()
        props_layout.addLayout(port_layout)

        players_layout = QHBoxLayout()
        players_layout.addWidget(QLabel("Max Players:"))
        self.max_players_spin = QSpinBox()
        self.max_players_spin.setRange(1, 1000)
        self.max_players_spin.setValue(20)
        self.max_players_spin.valueChanged.connect(self.on_max_players_changed)
        players_layout.addWidget(self.max_players_spin)
        players_layout.addStretch()
        props_layout.addLayout(players_layout)

        gamemode_layout = QHBoxLayout()
        gamemode_layout.addWidget(QLabel("Gamemode:"))
        self.gamemode_combo = QComboBox()
        self.gamemode_combo.addItems(["survival", "creative", "adventure", "spectator"])
        self.gamemode_combo.currentTextChanged.connect(self.on_gamemode_changed)
        gamemode_layout.addWidget(self.gamemode_combo)
        gamemode_layout.addStretch()
        props_layout.addLayout(gamemode_layout)

        difficulty_layout = QHBoxLayout()
        difficulty_layout.addWidget(QLabel("Difficulty:"))
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["peaceful", "easy", "normal", "hard"])
        self.difficulty_combo.currentTextChanged.connect(self.on_difficulty_changed)
        difficulty_layout.addWidget(self.difficulty_combo)
        difficulty_layout.addStretch()
        props_layout.addLayout(difficulty_layout)

        layout.addWidget(props_group)
        layout.addStretch()

        self.load_properties()
        return widget

    def load_properties(self):
        self.port_spin.setValue(self.server_properties.get_port())
        self.max_players_spin.setValue(self.server_properties.get_max_players())
        self.gamemode_combo.setCurrentText(self.server_properties.get_gamemode())
        self.difficulty_combo.setCurrentText(self.server_properties.get_difficulty())

    def apply_dark_mode(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow { background-color: #1e1e1e; color: #ffffff; }
                QWidget { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #3a3a3a; color: #ffffff; border: 1px solid #555; padding: 8px 16px; border-radius: 4px; }
                QPushButton:hover { background-color: #4a4a4a; }
                QPushButton:pressed { background-color: #2a2a2a; }
                QListWidget { background-color: #252525; color: #ffffff; border: 1px solid #444; }
                QListWidget::item:selected { background-color: #0078d7; }
                QComboBox { background-color: #3a3a3a; color: #ffffff; border: 1px solid #555; padding: 4px; }
                QSpinBox { background-color: #3a3a3a; color: #ffffff; border: 1px solid #555; }
                QTabWidget::pane { border: 1px solid #444; }
                QTabBar::tab { background-color: #2a2a2a; color: #fff; padding: 8px 16px; }
                QTabBar::tab:selected { background-color: #0078d7; }
                QGroupBox { color: #fff; border: 1px solid #444; margin-top: 8px; padding-top: 8px; }
                QProgressDialog { background-color: #1e1e1e; }
            """)
        else:
            self.setStyleSheet("")

    def toggle_theme(self, theme):
        self.dark_mode = (theme == "Dark")
        self.apply_dark_mode()

    def on_port_changed(self, value):
        self.server_properties.set_port(value)

    def on_max_players_changed(self, value):
        self.server_properties.set_max_players(value)

    def on_gamemode_changed(self, text):
        self.server_properties.set_gamemode(text)

    def on_difficulty_changed(self, text):
        self.server_properties.set_difficulty(text)

    def on_tab_changed(self, index):
        if index == 0:
            self.load_servers()

    def load_servers(self):
        self.server_list.clear()
        try:
            servers = self.java_detector.discover_servers()
            for s in servers:
                item = QListWidgetItem(f"{s['name']} ({s['version']})")
                item.setData(Qt.ItemDataRole.UserRole, ServerInfo(
                    name=s['name'],
                    version=s['version'],
                    server_type=s['server_type'],
                    jar_path=s.get('jar_path')
                ))
                self.server_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load servers: {e}")

    def on_server_selected(self, item):
        self.selected_server = item.data(Qt.ItemDataRole.UserRole)
        self.export_btn.setEnabled(bool(self.selected_server))

    def download_server(self):
        server_type = self.server_combo.currentText()
        url = SERVER_TYPES.get(server_type)
        if url:
            webbrowser.open(url)

    def export_script(self):
        if not self.selected_server:
            QMessageBox.warning(self, "Error", "No server selected")
            return

        server = {
            "name": self.selected_server.name,
            "jar_path": self.selected_server.jar_path or f"./{self.selected_server.name}.jar"
        }

        import sys
        if sys.platform == "win32":
            script = generate_windows_script(server)
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Save Script", f"{self.selected_server.name}.bat", "Batch Files (*.bat)"
            )
        else:
            script = generate_launch_script(server)
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Save Script", f"{self.selected_server.name}.sh", "Shell Scripts (*.sh)"
            )

        if filepath:
            save_script(script, filepath)
            QMessageBox.information(self, "Success", f"Saved to {filepath}")