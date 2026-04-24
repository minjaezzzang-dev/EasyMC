"""Main window for Minecraft Server Manager GUI."""

from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QListWidget, QListWidgetItem, QPushButton, QLineEdit,
    QLabel, QComboBox, QSpinBox, QGroupBox, QMessageBox,
    QProgressDialog, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .types import ServerInfo
from .worker import WorkerThread
from .modrinth import ModrinthClient, SERVER_PROJECT_IDS
from .detector import JavaServerDetector
from .properties import ServerProperties
from .cli import generate_launch_script, generate_windows_script, save_script


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.servers = []
        self.search_results = []
        self.selected_server: Optional[ServerInfo] = None
        self.modrinth_client = ModrinthClient()
        self.server_properties = ServerProperties()
        self.java_detector = JavaServerDetector()
        self.current_tab = "java"
        
        self.init_ui()
        self.load_servers()

    def init_ui(self):
        self.setWindowTitle("Minecraft Server Manager")
        self.setGeometry(100, 100, 900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Minecraft Server Manager")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        main_layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        self.java_tab = self.create_server_tab()
        self.search_tab = self.create_search_tab()
        
        self.tabs.addTab(self.java_tab, "Java Servers")
        self.tabs.addTab(self.search_tab, "Search")
        
        main_layout.addWidget(self.tabs)

        props_group = self.create_properties_group()
        main_layout.addWidget(props_group)

    def create_server_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        install_layout = QHBoxLayout()
        install_layout.addWidget(QLabel("Server Type:"))
        
        self.server_type_combo = QComboBox()
        self.server_type_combo.addItems(["paper", "purpur", "fabric", "spigot", "folia", "mohist"])
        install_layout.addWidget(self.server_type_combo)
        
        install_layout.addWidget(QLabel("Version:"))
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("e.g., 1.20.4")
        self.version_input.setFixedWidth(100)
        install_layout.addWidget(self.version_input)
        
        self.install_btn = QPushButton("Install")
        self.install_btn.clicked.connect(self.install_server)
        install_layout.addWidget(self.install_btn)
        
install_layout.addStretch()
        layout.addLayout(install_layout)

        self.server_list = QListWidget()
        self.server_list.itemClicked.connect(self.on_server_selected)
        layout.addWidget(self.server_list)

        export_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export Start Script")
        self.export_btn.clicked.connect(self.export_script)
        self.export_btn.setEnabled(False)
        export_layout.addWidget(self.export_btn)
        export_layout.addStretch()
        layout.addLayout(export_layout)

        return widget

    def create_search_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Modrinth...")
        self.search_input.returnPressed.connect(self.do_search)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.do_search)
        search_layout.addWidget(self.search_btn)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)

        self.search_results_list = QListWidget()
        self.search_results_list.itemClicked.connect(self.on_search_result_selected)
        layout.addWidget(self.search_results_list)

        return widget

    def create_properties_group(self) -> QGroupBox:
        group = QGroupBox("Server Properties")
        layout = QHBoxLayout(group)

        layout.addWidget(QLabel("Port:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(25565)
        self.port_spin.valueChanged.connect(self.on_port_changed)
        layout.addWidget(self.port_spin)

        layout.addWidget(QLabel("Max Players:"))
        self.max_players_spin = QSpinBox()
        self.max_players_spin.setRange(1, 1000)
        self.max_players_spin.setValue(20)
        self.max_players_spin.valueChanged.connect(self.on_max_players_changed)
        layout.addWidget(self.max_players_spin)

        layout.addWidget(QLabel("Gamemode:"))
        self.gamemode_combo = QComboBox()
        self.gamemode_combo.addItems(["survival", "creative", "adventure", "spectator"])
        self.gamemode_combo.currentTextChanged.connect(self.on_gamemode_changed)
        layout.addWidget(self.gamemode_combo)

        layout.addWidget(QLabel("Difficulty:"))
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["peaceful", "easy", "normal", "hard"])
        self.difficulty_combo.currentTextChanged.connect(self.on_difficulty_changed)
        layout.addWidget(self.difficulty_combo)

        layout.addWidget(QLabel("MOTD:"))
        self.motd_input = QLineEdit()
        self.motd_input.setPlaceholderText("A Minecraft Server")
        self.motd_input.textChanged.connect(self.on_motd_changed)
        layout.addWidget(self.motd_input)

        layout.addStretch()
        self.load_properties()
        return group

    def load_properties(self):
        self.port_spin.setValue(self.server_properties.get_port())
        self.max_players_spin.setValue(self.server_properties.get_max_players())
        self.gamemode_combo.setCurrentText(self.server_properties.get_gamemode())
        self.difficulty_combo.setCurrentText(self.server_properties.get_difficulty())
        self.motd_input.setText(self.server_properties.get_motd())

    def on_port_changed(self, value):
        self.server_properties.set_port(value)

    def on_max_players_changed(self, value):
        self.server_properties.set_max_players(value)

    def on_gamemode_changed(self, text):
        self.server_properties.set_gamemode(text)

    def on_difficulty_changed(self, text):
        self.server_properties.set_difficulty(text)

    def on_motd_changed(self, text):
        self.server_properties.set_motd(text)

    def on_tab_changed(self, index):
        if index == 0:
            self.current_tab = "java"
            self.load_servers()
        elif index == 1:
            self.current_tab = "search"

    def load_servers(self):
        self.server_list.clear()
        try:
            servers = self.java_detector.discover_servers()
            for s in servers:
                item = QListWidgetItem(f"{s['name']} ({s['version']}) - {s['server_type']}")
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

    def on_search_result_selected(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        self.selected_server = ServerInfo(
            name=data.get('title', data.get('slug', 'unknown')),
            version=data.get('latest_version', ''),
            server_type='java'
        )

    def install_server(self):
        server_type = self.server_type_combo.currentText()
        version = self.version_input.text() or None

        progress = QProgressDialog("Installing server...", "Cancel", 0, 0, self)
        progress.setWindowTitle("Installing")
        progress.setModal(True)
        progress.show()

        def do_install():
            project_id = SERVER_PROJECT_IDS.get(server_type)
            if not project_id:
                raise ValueError(f"Unknown server type: {server_type}")
            return self.modrinth_client.download_version(project_id, "servers", version)

        self.worker = WorkerThread(do_install)
        self.worker.finished.connect(lambda r: self.on_install_finished(progress, r))
        self.worker.error.connect(lambda e: self.on_install_error(progress, e))
        self.worker.start()

    def on_install_finished(self, progress, file_path):
        progress.close()
        if file_path:
            QMessageBox.information(self, "Success", f"Installed to {file_path}")
            self.load_servers()
        else:
            QMessageBox.warning(self, "Error", "Failed to download")

    def on_install_error(self, progress, error):
        progress.close()
        QMessageBox.warning(self, "Error", error)

    def do_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        self.search_btn.setEnabled(False)
        
        def do_search_api():
            return self.modrinth_client.search_versions(query)

        self.worker = WorkerThread(do_search_api)
        self.worker.finished.connect(self.on_search_finished)
        self.worker.error.connect(self.on_search_error)
        self.worker.start()

    def on_search_finished(self, results):
        self.search_btn.setEnabled(True)
        self.search_results_list.clear()
        
        for r in results:
            item = QListWidgetItem(f"{r.get('title', 'unknown')} - {r.get('latest_version', '')}")
            item.setData(Qt.ItemDataRole.UserRole, r)
            self.search_results_list.addItem(item)

    def on_search_error(self, error):
        self.search_btn.setEnabled(True)
        QMessageBox.warning(self, "Error", error)

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