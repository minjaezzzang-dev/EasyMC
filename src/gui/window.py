"""Main window for EasyMC - Minecraft Server Manager."""

from typing import Optional
import requests

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QListWidget, QListWidgetItem, QPushButton,
    QLabel, QComboBox, QSpinBox, QGroupBox, QMessageBox,
    QCheckBox, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .types import ServerInfo
from .worker import WorkerThread
from .detector import JavaServerDetector
from .properties import ServerProperties
from .cli import generate_launch_script, generate_windows_script, save_script
"""Main window for EasyMC - Minecraft Server Manager."""

from typing import Optional
import requests

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QListWidget, QListWidgetItem, QPushButton,
    QLabel, QComboBox, QSpinBox, QGroupBox, QMessageBox,
    QCheckBox, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .types import ServerInfo
from .worker import WorkerThread
from .detector import JavaServerDetector
from .properties import ServerProperties
from .cli import generate_launch_script, generate_windows_script, save_script
from .crawler import download_server as crawl_download


MODRINTH_API = "https://api.modrinth.com/v2"


MODRINTH_API = "https://api.modrinth.com/v2"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_properties = ServerProperties()
        self.java_detector = JavaServerDetector()
        self.dark_mode = True
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("EasyMC")
        self.setGeometry(100, 100, 900, 650)

        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("EasyMC")
        title.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        main_layout.addWidget(title)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_home_page())
        self.stack.addWidget(self.create_manage_page())
        self.stack.addWidget(self.create_download_page())
        
        main_layout.addWidget(self.stack)
        
        self.apply_dark_mode()

    def create_home_page(self) -> QWidget:
        page = QWidget()
        grid = QGridLayout(page)
        grid.setSpacing(15)

        btn1 = QPushButton("Manage Servers")
        btn1.setFont(QFont("Arial", 14))
        btn1.setMinimumSize(250, 100)
        btn1.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        grid.addWidget(btn1, 0, 0)

        btn2 = QPushButton("Download Server")
        btn2.setFont(QFont("Arial", 14))
        btn2.setMinimumSize(250, 100)
        btn2.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        grid.addWidget(btn2, 0, 1)

        return page

    def create_manage_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        back = QPushButton("← Home")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back)

        layout.addWidget(QLabel("Installed Servers:"))

        self.server_list = QListWidget()
        self.server_list.itemClicked.connect(self.on_server_selected)
        layout.addWidget(self.server_list)

        self.load_servers()
        return page

    def create_download_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        back = QPushButton("← Home")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back)

        layout.addWidget(QLabel("Server Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Java", "Bedrock"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("Server:"))
        self.server_combo = QComboBox()
        layout.addWidget(self.server_combo)

        layout.addWidget(QLabel("Version:"))
        self.version_combo = QComboBox()
        self.version_combo.currentTextChanged.connect(self.on_version_changed)
        layout.addWidget(self.version_combo)

        self.loading_label = QLabel("")
        layout.addWidget(self.loading_label)

        eula = QHBoxLayout()
        self.eula_check = QCheckBox("I accept Minecraft EULA")
        eula.addWidget(self.eula_check)
        eula.addStretch()
        layout.addLayout(eula)

        self.dl_btn = QPushButton("⬇ Download")
        self.dl_btn.clicked.connect(self.download_server)
        self.dl_btn.setMinimumHeight(45)
        layout.addWidget(self.dl_btn)

        layout.addStretch()

        self.on_type_changed("Java")
        return page

    def on_type_changed(self, t: str):
        self.server_combo.clear()
        self.version_combo.clear()
        self.version_combo.addItem("Loading...")
        self.loading_label.setText("Fetching versions...")
        
        if t == "Java":
            servers = ["Paper", "Purpur", "Fabric", "Spigot", "Folia", "Mohist"]
        else:
            servers = ["LiteLoader", "Nukkit", "PocketMine"]
        
        self.server_combo.addItems(servers)
        self.load_versions()

    def load_versions(self):
        server = self.server_combo.currentText()
        
        def fetch():
            try:
                if server == "Paper" or server == "Folia":
                    r = requests.get("https://api.papermc.io/v2/projects/paper", timeout=10)
                    return r.json().get("versions", [])[::-1][:20]
                elif server == "Purpur":
                    r = requests.get("https://api.purpurmc.org/v2/purpur", timeout=10)
                    return list(r.json().get("versions", {}).keys())[::-1][:20]
                elif server == "Fabric":
                    r = requests.get("https://meta.fabricmc.net/v2/versions/game", timeout=10)
                    return [x["version"] for x in r.json() if x.get("stable")][::-1][:20]
                elif server == "Mohist":
                    r = requests.get("https://mohistmc.com/api/v2/projects/mohist", timeout=10)
                    return list(r.json().keys())[::-1][:20]
                elif server == "Spigot":
                    return ["1.21", "1.20.6", "1.20.4", "1.20.2", "1.19.4"]
            except:
                return ["1.21", "1.20.4", "1.19.4"]
        
        def done(vers):
            self.version_combo.clear()
            self.version_combo.addItems(vers if vers else ["latest"])
            self.loading_label.setText("")
        
        self.worker = WorkerThread(fetch)
        self.worker.finished.connect(done)
        self.worker.start()

    def on_version_changed(self, v: str):
        pass

    def download_server(self):
        if not self.eula_check.isChecked():
            QMessageBox.warning(self, "EULA", "You must accept the EULA first")
            return

        server = self.server_combo.currentText()
        version = self.version_combo.currentText()
        project_id = SERVER_PROJECT_IDS.get(server)
        
        if not project_id:
        server = self.server_combo.currentText()
        version = self.version_combo.currentText()
        
        self.dl_btn.setEnabled(False)
        self.dl_btn.setText("Downloading...")

        def do_download():
            return crawl_download(server, version, "servers")

        self.worker = WorkerThread(do_download)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.error.connect(self.on_download_error)
        self.worker.start()

    def on_download_finished(self, file_path):
        self.dl_btn.setEnabled(True)
        self.dl_btn.setText("⬇ Download")
        if file_path:
            QMessageBox.information(self, "Done", f"Saved to {file_path}")
        else:
            QMessageBox.warning(self, "Error", "Download failed")

    def on_download_error(self, error):
        self.dl_btn.setEnabled(True)
        self.dl_btn.setText("⬇ Download")
        QMessageBox.warning(self, "Error", str(error))

    def load_servers(self):
        self.server_list.clear()
        try:
            for s in self.java_detector.discover_servers():
                item = QListWidgetItem(f"{s['name']} ({s['version']})")
                item.setData(Qt.ItemDataRole.UserRole, ServerInfo(
                    name=s['name'], version=s['version'],
                    server_type=s['server_type'], jar_path=s.get('jar_path')
                ))
                self.server_list.addItem(item)
        except:
            pass

    def on_server_selected(self, item):
        pass

    def apply_dark_mode(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; color: #d4d4d4; }
            QWidget { background-color: #1e1e1e; color: #d4d4d4; }
            QLabel { color: #d4d4d4; font-size: 13px; }
            QPushButton {
                background-color: #0e639c; color: #fff; border: none;
                padding: 10px 20px; border-radius: 4px; font-size: 13px;
            }
            QPushButton:hover { background-color: #1177bb; }
            QPushButton:pressed { background-color: #094771; }
            QListWidget { background-color: #252526; color: #d4d4d4; border: 1px solid #3c3c3c; font-size: 13px; }
            QListWidget::item:selected { background-color: #094771; }
            QComboBox { background-color: #3c3c3c; color: #d4d4d4; border: 1px solid #555; padding: 6px; font-size: 13px; }
            QSpinBox { background-color: #3c3c3c; color: #d4d4d4; border: 1px solid #555; font-size: 13px; }
            QCheckBox { color: #d4d4d4; font-size: 13px; }
            QStackedWidget { border: none; }
        """)