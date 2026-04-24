"""Main window for EasyMC - Minecraft Server Manager."""

from typing import Optional
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QListWidget, QListWidgetItem, QPushButton,
    QLabel, QComboBox, QSpinBox, QGroupBox, QMessageBox,
    QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .types import ServerInfo
from .worker import WorkerThread
from .detector import JavaServerDetector
from .properties import ServerProperties
from .cli import generate_launch_script, generate_windows_script, save_script
from .modrinth import ModrinthClient, SERVER_PROJECT_IDS


SERVER_TYPES = {
    "Java": {
        "Paper": "PapMC",
        "Purpur": "Purpur", 
        "Fabric": "fabric",
        "Spigot": "Spigot",
    },
    "Bedrock": {
        "LiteLoader": "liteloader",
        "Nukkit": "nukkit",
        "PocketMine": "pmmp",
    }
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_properties = ServerProperties()
        self.java_detector = JavaServerDetector()
        self.modrinth = ModrinthClient()
        self.dark_mode = True
        self.current_server_type = "Java"
        
        self.init_ui()
        self.load_servers()

    def init_ui(self):
        self.setWindowTitle("EasyMC")
        self.setGeometry(100, 100, 900, 700)

        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("EasyMC - Minecraft Server Manager")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        main_layout.addWidget(title)

        self.stack = QStackedWidget()
        
        self.home_page = self.create_home_page()
        self.manage_page = self.create_manage_page()
        self.create_page = self.create_create_page()
        
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.manage_page)
        self.stack.addWidget(self.create_page)
        
        main_layout.addWidget(self.stack)
        
        self.apply_dark_mode()

    def create_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        layout.addStretch()

        btn = QPushButton("Manage Server")
        btn.setFont(QFont("Arial", 16))
        btn.setMinimumHeight(60)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        layout.addWidget(btn)

        btn2 = QPushButton("Create Server")
        btn2.setFont(QFont("Arial", 16))
        btn2.setMinimumHeight(60)
        btn2.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        layout.addWidget(btn2)

        layout.addStretch()

        return page

    def create_manage_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        nav = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        nav.addWidget(back_btn)
        nav.addStretch()
        layout.addLayout(nav)

        layout.addWidget(QLabel("Your Servers"))
        
        self.server_list = QListWidget()
        self.server_list.itemClicked.connect(self.on_server_selected)
        layout.addWidget(self.server_list)

        actions = QHBoxLayout()
        self.edit_props_btn = QPushButton("Edit server.properties")
        self.edit_props_btn.setEnabled(False)
        self.edit_props_btn.clicked.connect(self.edit_properties)
        actions.addWidget(self.edit_props_btn)
        
        self.install_plugins_btn = QPushButton("Install Plugins")
        self.install_plugins_btn.setEnabled(False)
        self.install_plugins_btn.clicked.connect(self.install_plugins)
        actions.addWidget(self.install_plugins_btn)
        
        actions.addStretch()
        layout.addLayout(actions)

        return page

    def create_create_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        nav = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        nav.addWidget(back_btn)
        nav.addStretch()
        layout.addLayout(nav)

        layout.addWidget(QLabel("Select Server Type"))

        type_layout = QHBoxLayout()
        
        self.java_btn = QPushButton("Java Server")
        self.java_btn.setMinimumHeight(50)
        self.java_btn.clicked.connect(lambda: self.show_java_options())
        type_layout.addWidget(self.java_btn)
        
        self.bedrock_btn = QPushButton("Bedrock Server")
        self.bedrock_btn.setMinimumHeight(50)
        self.bedrock_btn.clicked.connect(lambda: self.show_bedrock_options())
        type_layout.addWidget(self.bedrock_btn)
        
        type_layout.addStretch()
        layout.addLayout(type_layout)

        self.java_group = QGroupBox("Java Server Options")
        java_layout = QVBoxLayout(self.java_group)
        
        self.java_combo = QComboBox()
        self.java_combo.addItems(list(SERVER_TYPES["Java"].keys()))
        java_layout.addWidget(QLabel("Server:"))
        java_layout.addWidget(self.java_combo)
        
        java_layout.addWidget(QLabel("Version:"))
        self.version_combo = QComboBox()
        self.version_combo.addItems(["1.21", "1.20.4", "1.20.2", "1.19.4", "1.18.2"])
        java_layout.addWidget(self.version_combo)
        
        java_btn = QPushButton("Download")
        java_btn.clicked.connect(self.download_java)
        java_layout.addWidget(java_btn)
        
        self.java_group.hide()
        layout.addWidget(self.java_group)

        self.bedrock_group = QGroupBox("Bedrock Server Options")
        bedrock_layout = QVBoxLayout(self.bedrock_group)
        
        self.bedrock_combo = QComboBox()
        self.bedrock_combo.addItems(list(SERVER_TYPES["Bedrock"].keys()))
        bedrock_layout.addWidget(QLabel("Server:"))
        bedrock_layout.addWidget(self.bedrock_combo)
        
        bedrock_btn = QPushButton("Download")
        bedrock_btn.clicked.connect(self.download_bedrock)
        bedrock_layout.addWidget(bedrock_btn)
        
        self.bedrock_group.hide()
        layout.addWidget(self.bedrock_group)

        eula_layout = QHBoxLayout()
        self.eula_check = QCheckBox("I accept Minecraft EULA")
        eula_layout.addWidget(self.eula_check)
        eula_layout.addStretch()
        layout.addLayout(eula_layout)

        layout.addStretch()

        return page

    def show_java_options(self):
        self.java_group.show()
        self.bedrock_group.hide()

    def show_bedrock_options(self):
        self.java_group.hide()
        self.bedrock_group.show()

    def download_java(self):
        server = self.java_combo.currentText()
        version = self.version_combo.currentText()
        project_id = SERVER_PROJECT_IDS.get(server)
        
        progress = QMessageBox(self)
        progress.setWindowTitle("Downloading")
        progress.setText(f"Downloading {server} {version}...")
        progress.setStandardButtons(QMessageBox.StandardButton.NoButton)
        progress.show()
        
        def do_download():
            return self.modrinth.download_version(project_id, "servers", version)
        
        self.worker = WorkerThread(do_download)
        self.worker.finished.connect(lambda r: self.on_download_finished(r, progress))
        self.worker.error.connect(lambda e: self.on_download_error(e, progress))
        self.worker.start()

    def on_download_finished(self, file_path, progress):
        progress.close()
        if file_path:
            QMessageBox.information(self, "Success", f"Downloaded to {file_path}")
            self.load_servers()
        else:
            QMessageBox.warning(self, "Error", "Download failed")

    def on_download_error(self, error, progress):
        progress.close()
        QMessageBox.warning(self, "Error", str(error))

    def download_bedrock(self):
        server = self.bedrock_combo.currentText()
        QMessageBox.information(self, "Coming Soon", f"Bedrock server download for {server} will be available soon.")

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
            pass

    def on_server_selected(self, item):
        self.edit_props_btn.setEnabled(True)
        self.install_plugins_btn.setEnabled(True)

    def edit_properties(self):
        QMessageBox.information(self, "Edit Properties", "Properties editor coming soon!")

    def install_plugins(self):
        QMessageBox.information(self, "Install Plugins", "Plugin installer coming soon!")

    def apply_dark_mode(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow { background-color: #1e1e1e; color: #ffffff; }
                QWidget { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #3a3a3a; color: #ffffff; border: 1px solid #555; padding: 10px 20px; border-radius: 6px; font-size: 14px; }
                QPushButton:hover { background-color: #505050; }
                QPushButton:pressed { background-color: #2a2a2a; }
                QListWidget { background-color: #252525; color: #ffffff; border: 1px solid #444; }
                QListWidget::item:selected { background-color: #0078d7; }
                QComboBox { background-color: #3a3a3a; color: #ffffff; border: 1px solid #555; padding: 6px; }
                QSpinBox { background-color: #3a3a3a; color: #ffffff; border: 1px solid #555; }
                QCheckBox { color: #ffffff; }
                QGroupBox { color: #ffffff; border: 1px solid #444; margin-top: 10px; padding-top: 10px; }
                QStackedWidget { border: 1px solid #444; }
            """)
        else:
            self.setStyleSheet("")