#!/usr/bin/env python3
"""
TS_Tool_Routier - Éditeur Transport Fever 2
Développé par ROUTIER87
"""

import sys
import os
import struct
import json
import traceback
import shutil
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ============================================================================
# CONFIGURATION
# ============================================================================

VERSION = "1.0.0"
APP_NAME = "TS_Tool_Routier"
AUTHOR = "ROUTIER87"

# ============================================================================
# CLASSE PRINCIPALE
# ============================================================================

class TS_Tool_Routier(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Variables
        self.current_file = None
        self.file_data = None
        self.money_offset = 1048600  # À CHANGER APRÈS TES TESTS !
        self.modified = False
        
        # Setup
        self.setup_ui()
        self.setWindowTitle(f"{APP_NAME} v{VERSION} - par {AUTHOR}")
        self.resize(900, 700)
        self.center()
        
        # Style
        self.apply_style()
        
        # Créer le dossier logs
        Path("logs").mkdir(exist_ok=True)
        
        # Journal
        self.log("Application démarrée")
    
    def center(self):
        """Centre la fenêtre"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2,
                 (screen.height() - size.height()) // 2)
    
    def apply_style(self):
        """Applique le style à l'interface"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
            QPushButton#moneyBtn {
                background-color: #27ae60;
            }
            QPushButton#moneyBtn:hover {
                background-color: #219653;
            }
            QPushButton#hexBtn {
                background-color: #e74c3c;
            }
            QPushButton#hexBtn:hover {
                background-color: #c0392b;
            }
            QSpinBox {
                padding: 5px;
                font-size: 14px;
                background-color: white;
                border-radius: 3px;
                min-width: 150px;
            }
            QGroupBox {
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid #555;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #34495e;
            }
            QTabBar::tab {
                background-color: #2c3e50;
                color: white;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
            }
            QStatusBar {
                background-color: #34495e;
                color: white;
            }
            QMenuBar {
                background-color: #34495e;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
            }
            QMenu {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
        """)
    
    def log(self, message):
        """Écrit un message dans le journal"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        
        # Afficher dans la barre de statut
        self.status_bar.showMessage(message, 3000)
        
        # Écrire dans le fichier log
        log_file = Path("logs") / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + "\n")
    
    def setup_ui(self):
        """Configure l'interface"""
        # Créer la barre de menu
        self.create_menu_bar()
        
        # Widget central avec onglets
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # ===== ONGLET 1 : ÉDITEUR =====
        editor_tab = QWidget()
        editor_layout = QVBoxLayout(editor_tab)
        
        # Titre
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #34495e; border-radius: 10px;")
        title_layout = QVBoxLayout(title_frame)
        
        title = QLabel(f"🚚 {APP_NAME}")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #3498db;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title)
        
        subtitle = QLabel(f"Éditeur de sauvegardes Transport Fever 2 - par {AUTHOR}")
        subtitle.setStyleSheet("font-size: 14px; color: #bdc3c7;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)
        
        editor_layout.addWidget(title_frame)
        
        # Boutons principaux
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        
        self.btn_open = QPushButton("📂 Ouvrir une sauvegarde")
        self.btn_open.clicked.connect(self.open_file)
        self.btn_open.setToolTip("Ouvrir un fichier .save")
        btn_layout.addWidget(self.btn_open)
        
        self.btn_save = QPushButton("💾 Enregistrer")
        self.btn_save.clicked.connect(self.save_file)
        self.btn_save.setEnabled(False)
        self.btn_save.setToolTip("Enregistrer les modifications")
        btn_layout.addWidget(self.btn_save)
        
        self.btn_save_as = QPushButton("💾 Enregistrer sous")
        self.btn_save_as.clicked.connect(self.save_as)
        self.btn_save_as.setEnabled(False)
        self.btn_save_as.setToolTip("Enregistrer sous un nouveau nom")
        btn_layout.addWidget(self.btn_save_as)
        
        editor_layout.addWidget(btn_frame)
        
        # Informations fichier
        info_group = QGroupBox("📁 Informations du fichier")
        info_layout = QGridLayout()
        
        self.lbl_filename = QLabel("Aucun fichier chargé")
        self.lbl_filename.setStyleSheet("font-weight: bold; color: #3498db;")
        
        self.lbl_filesize = QLabel("Taille: -")
        self.lbl_money = QLabel("Argent: 0 €")
        self.lbl_money.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        self.lbl_offset = QLabel("Offset argent: 0x000000")
        
        info_layout.addWidget(QLabel("Fichier:"), 0, 0)
        info_layout.addWidget(self.lbl_filename, 0, 1)
        info_layout.addWidget(QLabel("Taille:"), 1, 0)
        info_layout.addWidget(self.lbl_filesize, 1, 1)
        info_layout.addWidget(QLabel("Argent:"), 2, 0)
        info_layout.addWidget(self.lbl_money, 2, 1)
        info_layout.addWidget(QLabel("Offset:"), 3, 0)
        info_layout.addWidget(self.lbl_offset, 3, 1)
        
        info_group.setLayout(info_layout)
        editor_layout.addWidget(info_group)
        
        # Éditeur d'argent
        money_group = QGroupBox("💰 Éditeur d'argent")
        money_layout = QVBoxLayout()
        
        # Contrôle d'argent
        money_control_layout = QHBoxLayout()
        money_control_layout.addWidget(QLabel("Montant:"))
        
        self.money_spinbox = QSpinBox()
        self.money_spinbox.setRange(-1000000000, 10000000000)
        self.money_spinbox.setValue(0)
        self.money_spinbox.setSingleStep(1000)
        self.money_spinbox.setPrefix("€ ")
        self.money_spinbox.valueChanged.connect(self.on_money_changed)
        self.money_spinbox.setEnabled(False)
        money_control_layout.addWidget(self.money_spinbox)
        
        money_control_layout.addStretch()
        money_layout.addLayout(money_control_layout)
        
        # Boutons présets
        presets_layout = QHBoxLayout()
        presets = [
            ("100K", 100000),
            ("500K", 500000),
            ("1M", 1000000),
            ("5M", 5000000),
            ("10M", 10000000),
            ("MAX", 999999999)
        ]
        
        for text, value in presets:
            btn = QPushButton(text)
            btn.setObjectName("moneyBtn")
            btn.clicked.connect(lambda checked, v=value: self.set_money_preset(v))
            presets_layout.addWidget(btn)
        
        money_layout.addLayout(presets_layout)
        money_group.setLayout(money_layout)
        editor_layout.addWidget(money_group)
        
        # Zone hexadécimale
        hex_group = QGroupBox("🔧 Aperçu hexadécimal (premiers 512 octets)")
        hex_layout = QVBoxLayout()
        
        self.hex_preview = QTextEdit()
        self.hex_preview.setReadOnly(True)
        self.hex_preview.setMaximumHeight(150)
        hex_layout.addWidget(self.hex_preview)
        
        hex_group.setLayout(hex_layout)
        editor_layout.addWidget(hex_group)
        
        editor_layout.addStretch()
        
        # ===== ONGLET 2 : HEXADÉCIMAL =====
        hex_tab = QWidget()
        hex_layout_main = QVBoxLayout(hex_tab)
        
        # Toolbar hex
        hex_toolbar = QHBoxLayout()
        
        hex_toolbar.addWidget(QLabel("Offset:"))
        self.hex_offset_input = QLineEdit()
        self.hex_offset_input.setPlaceholderText("0x00000000")
        self.hex_offset_input.setMaximumWidth(150)
        hex_toolbar.addWidget(self.hex_offset_input)
        
        self.btn_goto = QPushButton("Aller à")
        self.btn_goto.clicked.connect(self.goto_hex_offset)
        self.btn_goto.setEnabled(False)
        hex_toolbar.addWidget(self.btn_goto)
        
        hex_toolbar.addStretch()
        
        hex_toolbar.addWidget(QLabel("Rechercher:"))
        self.hex_search_input = QLineEdit()
        self.hex_search_input.setPlaceholderText("Texte ou hex")
        self.hex_search_input.setMaximumWidth(200)
        hex_toolbar.addWidget(self.hex_search_input)
        
        self.btn_search = QPushButton("🔍")
        self.btn_search.clicked.connect(self.search_hex)
        self.btn_search.setEnabled(False)
        hex_toolbar.addWidget(self.btn_search)
        
        hex_layout_main.addLayout(hex_toolbar)
        
        # Affichage hex principal
        self.hex_display = QTextEdit()
        self.hex_display.setReadOnly(True)
        hex_layout_main.addWidget(self.hex_display)
        
        # Info hex
        hex_info_layout = QHBoxLayout()
        
        self.lbl_hex_pos = QLabel("Position: 0x00000000")
        self.lbl_hex_value = QLabel("Valeur: 0x00")
        self.lbl_hex_size = QLabel("Taille: 0 octets")
        
        hex_info_layout.addWidget(self.lbl_hex_pos)
        hex_info_layout.addWidget(self.lbl_hex_value)
        hex_info_layout.addWidget(self.lbl_hex_size)
        hex_info_layout.addStretch()
        
        hex_layout_main.addLayout(hex_info_layout)
        
        # ===== ONGLET 3 : OUTILS =====
        tools_tab = QWidget()
        tools_layout = QVBoxLayout(tools_tab)
        
        # Configuration offsets
        offset_group = QGroupBox("⚙️ Configuration des offsets")
        offset_layout = QFormLayout()
        
        self.offset_money_input = QLineEdit("1048600")
        self.offset_money_input.setPlaceholderText("Offset de l'argent")
        offset_layout.addRow("Offset argent:", self.offset_money_input)
        
        self.btn_save_offset = QPushButton("💾 Sauvegarder offset")
        self.btn_save_offset.clicked.connect(self.save_offset_config)
        offset_layout.addRow(self.btn_save_offset)
        
        offset_group.setLayout(offset_layout)
        tools_layout.addWidget(offset_group)
        
        # Outils avancés
        tools_group = QGroupBox("🛠️ Outils avancés")
        tools_btn_layout = QGridLayout()
        
        tools_buttons = [
            ("📊 Analyser fichier", self.analyze_file),
            ("🔍 Comparer sauvegardes", self.compare_saves),
            ("📤 Exporter JSON", self.export_json),
            ("🔄 Restaurer backup", self.restore_backup),
            ("🧹 Nettoyer logs", self.clean_logs),
            ("ℹ️  Infos système", self.system_info)
        ]
        
        row, col = 0, 0
        for text, slot in tools_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            btn.setMinimumHeight(40)
            tools_btn_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        tools_group.setLayout(tools_btn_layout)
        tools_layout.addWidget(tools_group)
        
        tools_layout.addStretch()
        
        # ===== ONGLET 4 : À PROPOS =====
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        
        about_text = f"""
        <div style='text-align: center; padding: 20px;'>
            <h1 style='color: #3498db;'>🚚 {APP_NAME}</h1>
            <h3>Version {VERSION}</h3>
            <p>Éditeur de sauvegardes Transport Fever 2</p>
            
            <hr style='border: 1px solid #555; margin: 20px;'>
            
            <h3>👨‍💻 Développeur</h3>
            <p style='font-size: 16px; color: #2ecc71;'>{AUTHOR}</p>
            
            <h3>🎯 Fonctionnalités</h3>
            <ul style='text-align: left; margin: 20px;'>
                <li>Modification de l'argent du joueur</li>
                <li>Éditeur hexadécimal intégré</li>
                <li>Sauvegarde automatique des fichiers</li>
                <li>Configuration des offsets</li>
                <li>Export des données en JSON</li>
                <li>Système de logging complet</li>
            </ul>
            
            <h3>⚠️ Important</h3>
            <p style='color: #e74c3c; font-weight: bold;'>
                ⚠️ Toujours faire des sauvegardes de vos fichiers originaux !
            </p>
            
            <hr style='border: 1px solid #555; margin: 20px;'>
            
            <p>Développé avec Python 3 et PyQt6</p>
            <p>© 2024 {AUTHOR} - Tous droits réservés</p>
        </div>
        """
        
        about_label = QLabel(about_text)
        about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_label.setWordWrap(True)
        about_layout.addWidget(about_label)
        
        about_layout.addStretch()
        
        # Ajouter les onglets
        self.tab_widget.addTab(editor_tab, "🏠 Éditeur")
        self.tab_widget.addTab(hex_tab, "🔧 Hexadécimal")
        self.tab_widget.addTab(tools_tab, "🛠️ Outils")
        self.tab_widget.addTab(about_tab, "ℹ️ À propos")
        
        # Barre de statut
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt")
        
        # Indicateur de modification
        self.modified_label = QLabel()
        self.status_bar.addPermanentWidget(self.modified_label)
    
    def create_menu_bar(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("📁 Fichier")
        
        open_action = QAction("📂 Ouvrir...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("💾 Enregistrer", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        save_action.setEnabled(False)
        self.save_action = save_action
        file_menu.addAction(save_action)
        
        save_as_action = QAction("💾 Enregistrer sous...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as)
        save_as_action.setEnabled(False)
        self.save_as_action = save_as_action
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Quitter", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Édition
        edit_menu = menubar.addMenu("✏️ Édition")
        
        money_action = QAction("💰 Éditeur d'argent...", self)
        money_action.triggered.connect(self.show_money_editor)
        edit_menu.addAction(money_action)
        
        offset_action = QAction("⚙️ Configurer offsets...", self)
        offset_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        edit_menu.addAction(offset_action)
        
        # Menu Outils
        tools_menu = menubar.addMenu("🔧 Outils")
        
        hex_action = QAction("🔍 Éditeur hexadécimal", self)
        hex_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        tools_menu.addAction(hex_action)
        
        analyze_action = QAction("📊 Analyser fichier", self)
        analyze_action.triggered.connect(self.analyze_file)
        tools_menu.addAction(analyze_action)
        
        tools_menu.addSeparator()
        
        backup_action = QAction("🔄 Gérer backups", self)
        backup_action.triggered.connect(self.manage_backups)
        tools_menu.addAction(backup_action)
        
        # Menu Aide
        help_menu = menubar.addMenu("❓ Aide")
        
        about_action = QAction("ℹ️ À propos", self)
        about_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        help_menu.addAction(about_action)
        
        docs_action = QAction("📚 Documentation", self)
        docs_action.triggered.connect(self.show_docs)
        help_menu.addAction(docs_action)
    
    # ============================================================================
    # FONCTIONS DE GESTION DE FICHIERS
    # ============================================================================
    
    def open_file(self):
        """Ouvre un fichier de sauvegarde"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir une sauvegarde Transport Fever 2",
            str(Path.home() / "Documents" / "Transport Fever 2" / "save"),
            "Fichiers de sauvegarde (*.save);;Tous les fichiers (*.*)"
        )
        
        if filepath:
            self.load_file(filepath)
    
    def load_file(self, filepath):
        """Charge un fichier de sauvegarde"""
        try:
            # Lire le fichier
            with open(filepath, 'rb') as f:
                self.file_data = bytearray(f.read())
            
            self.current_file = filepath
            self.modified = False
            
            # Mettre à jour les infos
            filename = os.path.basename(filepath)
            filesize = len(self.file_data)
            
            self.lbl_filename.setText(filename)
            self.lbl_filesize.setText(f"Taille: {filesize:,} octets")
            self.lbl_offset.setText(f"Offset argent: 0x{self.money_offset:X}")
            
            # Lire l'argent
            self.read_money()
            
            # Activer les contrôles
            self.money_spinbox.setEnabled(True)
            self.btn_save.setEnabled(True)
            self.btn_save_as.setEnabled(True)
            self.save_action.setEnabled(True)
            self.save_as_action.setEnabled(True)
            self.btn_goto.setEnabled(True)
            self.btn_search.setEnabled(True)
            
            # Mettre à jour l'affichage hex
            self.update_hex_preview()
            self.update_hex_display()
            
            # Journal
            self.log(f"Fichier chargé: {filename} ({filesize:,} octets)")
            
            QMessageBox.information(self, "Succès", 
                                  f"Fichier chargé avec succès !\n\n"
                                  f"📁 {filename}\n"
                                  f"📊 {filesize:,} octets\n"
                                  f"💰 {self.money_spinbox.value():,} €")
            
        except Exception as e:
            self.log(f"Erreur chargement: {str(e)}")
            QMessageBox.critical(self, "Erreur", 
                               f"Impossible de charger le fichier:\n{str(e)}")
    
    def read_money(self):
        """Lit la valeur de l'argent depuis le fichier"""
        try:
            if self.file_data and self.money_offset + 8 <= len(self.file_data):
                money_bytes = self.file_data[self.money_offset:self.money_offset+8]
                money = struct.unpack('<q', money_bytes)[0]
                
                self.money_spinbox.setValue(money)
                self.lbl_money.setText(f"Argent: {money:,} €")
                
                return money
        except Exception as e:
            self.log(f"Erreur lecture argent: {str(e)}")
        
        return 0
    
    def save_file(self):
        """Enregistre le fichier courant"""
        if not self.current_file or not self.file_data:
            return
        
        # Créer un backup
        backup_file = f"{self.current_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2(self.current_file, backup_file)
            self.log(f"Backup créé: {backup_file}")
        except Exception as e:
            self.log(f"Erreur création backup: {str(e)}")
        
        # Mettre à jour l'argent
        money = self.money_spinbox.value()
        money_bytes = struct.pack('<q', money)
        
        if self.money_offset + 8 <= len(self.file_data):
            self.file_data[self.money_offset:self.money_offset+8] = money_bytes
        
        # Écrire le fichier
        try:
            with open(self.current_file, 'wb') as f:
                f.write(self.file_data)
            
            self.modified = False
            self.modified_label.setText("")
            
            self.log(f"Fichier enregistré: {self.current_file}")
            
            QMessageBox.information(self, "Succès",
                                  f"✅ Fichier enregistré avec succès !\n\n"
                                  f"💰 Nouvel argent: {money:,} €\n"
                                  f"💾 Backup: {os.path.basename(backup_file)}")
            
        except Exception as e:
            self.log(f"Erreur sauvegarde: {str(e)}")
            QMessageBox.critical(self, "Erreur",
                               f"Erreur lors de l'enregistrement:\n{str(e)}")
    
    def save_as(self):
        """Enregistre sous un nouveau nom"""
        if not self.current_file:
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer sous",
            self.current_file,
            "Fichiers de sauvegarde (*.save);;Tous les fichiers (*.*)"
        )
        
        if filepath:
            # Mettre à jour l'argent avant sauvegarde
            money = self.money_spinbox.value()
            money_bytes = struct.pack('<q', money)
            
            if self.money_offset + 8 <= len(self.file_data):
                self.file_data[self.money_offset:self.money_offset+8] = money_bytes
            
            # Écrire le nouveau fichier
            try:
                with open(filepath, 'wb') as f:
                    f.write(self.file_data)
                
                self.log(f"Fichier enregistré sous: {filepath}")
                
                QMessageBox.information(self, "Succès",
                                      f"✅ Fichier enregistré sous:\n{filepath}\n\n"
                                      f"💰 Argent: {money:,} €")
                
            except Exception as e:
                self.log(f"Erreur sauvegarde sous: {str(e)}")
                QMessageBox.critical(self, "Erreur",
                                   f"Erreur lors de l'enregistrement:\n{str(e)}")
    
    # ============================================================================
    # FONCTIONS DE L'INTERFACE
    # ============================================================================
    
    def on_money_changed(self, value):
        """Quand l'argent est modifié"""
        self.lbl_money.setText(f"Argent: {value:,} €")
        self.modified = True
        self.modified_label.setText("[MODIFIÉ]")
        self.modified_label.setStyleSheet("color: red; font-weight: bold;")
    
    def set_money_preset(self, amount):
        """Définit un montant prédéfini"""
        self.money_spinbox.setValue(amount)
    
    def show_money_editor(self):
        """Affiche l'éditeur d'argent"""
        if not self.current_file:
            QMessageBox.warning(self, "Attention", "Ouvrez d'abord un fichier")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Éditeur d'argent avancé")
        dialog.resize(300, 200)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(f"Argent actuel: {self.money_spinbox.value():,} €"))
        
        spinbox = QSpinBox()
        spinbox.setRange(-1000000000, 10000000000)
        spinbox.setValue(self.money_spinbox.value())
        spinbox.setPrefix("€ ")
        layout.addWidget(spinbox)
        
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_apply = QPushButton("Appliquer")
        btn_apply.clicked.connect(dialog.accept)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_apply)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        
        if dialog.exec():
            self.money_spinbox.setValue(spinbox.value())
    
    def update_hex_preview(self):
        """Met à jour l'aperçu hexadécimal"""
        if not self.file_data:
            self.hex_preview.setText("Aucune donnée")
            return
        
        # Afficher les premiers 512 octets
        preview_size = min(512, len(self.file_data))
        preview_data = self.file_data[:preview_size]
        
        hex_text = ""
        for i in range(0, preview_size, 16):
            hex_text += f"{i:08X}: "
            
            for j in range(16):
                if i + j < preview_size:
                    hex_text += f"{preview_data[i+j]:02X} "
                else:
                    hex_text += "   "
            
            hex_text += " "
            
            for j in range(16):
                if i + j < preview_size:
                    byte = preview_data[i+j]
                    if 32 <= byte < 127:
                        hex_text += chr(byte)
                    else:
                        hex_text += "."
                else:
                    hex_text += " "
            
            hex_text += "\n"
        
        self.hex_preview.setText(hex_text)
    
    def update_hex_display(self):
        """Met à jour l'affichage hexadécimal complet"""
        if not self.file_data:
            self.hex_display.setText("Aucun fichier chargé")
            return
        
        hex_text = ""
        for i in range(0, len(self.file_data), 16):
            hex_text += f"{i:08X}: "
            
            for j in range(16):
                if i + j < len(self.file_data):
                    hex_text += f"{self.file_data[i+j]:02X} "
                else:
                    hex_text += "   "
            
            hex_text += " "
            
            for j in range(16):
                if i + j < len(self.file_data):
                    byte = self.file_data[i+j]
                    if 32 <= byte < 127:
                        hex_text += chr(byte)
                    else:
                        hex_text += "."
                else:
                    hex_text += " "
            
            hex_text += "\n"
        
        self.hex_display.setText(hex_text)
        self.lbl_hex_size.setText(f"Taille: {len(self.file_data):,} octets")
    
    def goto_hex_offset(self):
        """Va à un offset spécifique dans l'affichage hex"""
        offset_text = self.hex_offset_input.text().strip()
        
        try:
            if offset_text.startswith('0x'):
                offset = int(offset_text, 16)
            else:
                offset = int(offset_text)
            
            # Mettre à jour la position
            self.lbl_hex_pos.setText(f"Position: 0x{offset:X}")
            
            # Afficher la valeur à cet offset
            if offset < len(self.file_data):
                value = self.file_data[offset]
                self.lbl_hex_value.setText(f"Valeur: 0x{value:02X} ({value})")
            
            # Faire défiler vers la position
            cursor = self.hex_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            
            # Calculer la ligne (16 octets par ligne)
            line = offset // 16
            
            for _ in range(line):
                cursor.movePosition(QTextCursor.MoveOperation.Down)
            
            self.hex_display.setTextCursor(cursor)
            self.hex_display.ensureCursorVisible()
            
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Offset invalide")
    
    def search_hex(self):
        """Recherche dans les données hex"""
        search_text = self.hex_search_input.text().strip()
        if not search_text or not self.file_data:
            return
        
        # Essayer comme hex d'abord
        try:
            search_bytes = bytes.fromhex(search_text.replace(' ', ''))
        except:
            # Sinon comme texte
            search_bytes = search_text.encode('utf-8')
        
        # Rechercher
        try:
            index = self.file_data.find(search_bytes)
            if index != -1:
                self.hex_offset_input.setText(f"0x{index:X}")
                self.goto_hex_offset()
                QMessageBox.information(self, "Recherche", 
                                      f"Trouvé à l'offset 0x{index:X}")
            else:
                QMessageBox.information(self, "Recherche", "Non trouvé")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur recherche: {str(e)}")
    
    def save_offset_config(self):
        """Sauvegarde la configuration des offsets"""
        try:
            self.money_offset = int(self.offset_money_input.text())
            self.lbl_offset.setText(f"Offset argent: 0x{self.money_offset:X}")
            
            # Si un fichier est chargé, mettre à jour l'affichage
            if self.current_file:
                self.read_money()
            
            self.log(f"Offset argent mis à jour: 0x{self.money_offset:X}")
            
            QMessageBox.information(self, "Succès", 
                                  f"Offset argent mis à jour:\n0x{self.money_offset:X}")
            
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Offset invalide")
    
    # ============================================================================
    # FONCTIONS DES OUTILS
    # ============================================================================
    
    def analyze_file(self):
        """Analyse le fichier"""
        if not self.current_file:
            QMessageBox.warning(self, "Attention", "Ouvrez d'abord un fichier")
            return
        
        try:
            filesize = len(self.file_data)
            money = self.money_spinbox.value()
            
            # Compter les zéros (peut indiquer des zones vides)
            zeros = self.file_data.count(0)
            zero_percent = (zeros / filesize) * 100
            
            # Chercher des patterns communs
            patterns = {
                "FF FF FF FF": self.file_data.count(b'\xFF\xFF\xFF\xFF'),
                "00 00 00 00": self.file_data.count(b'\x00\x00\x00\x00'),
                "SAVE": self.file_data.find(b'SAVE'),
                "GAME": self.file_data.find(b'GAME'),
            }
            
            analysis = f"""
            📊 Analyse du fichier :
            
            📁 Fichier: {os.path.basename(self.current_file)}
            📏 Taille: {filesize:,} octets
            💰 Argent: {money:,} €
            
            📈 Statistiques :
            • Octets nuls: {zeros:,} ({zero_percent:.1f}%)
            • Offset argent: 0x{self.money_offset:X}
            
            🔍 Patterns trouvés :
            """
            
            for pattern, count in patterns.items():
                if count > 0:
                    analysis += f"• '{pattern}': {count} occurrences\n"
            
            QMessageBox.information(self, "Analyse", analysis)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur analyse: {str(e)}")
    
    def compare_saves(self):
        """Compare deux sauvegardes"""
        QMessageBox.information(self, "Info", 
                              "Pour trouver le vrai offset de l'argent:\n\n"
                              "1. Créez deux sauvegardes identiques\n"
                              "2. Modifiez l'argent dans le jeu\n"
                              "3. Comparez les fichiers avec un éditeur hexa\n"
                              "4. Modifiez l'offset dans la configuration")
    
    def export_json(self):
        """Exporte les données en JSON"""
        if not self.current_file:
            QMessageBox.warning(self, "Attention", "Ouvrez d'abord un fichier")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en JSON",
            f"{os.path.basename(self.current_file)}.json",
            "Fichiers JSON (*.json);;Tous les fichiers (*.*)"
        )
        
        if filepath:
            try:
                data = {
                    "filename": os.path.basename(self.current_file),
                    "filepath": self.current_file,
                    "filesize": len(self.file_data),
                    "money": self.money_spinbox.value(),
                    "money_offset": self.money_offset,
                    "export_date": datetime.now().isoformat(),
                    "author": AUTHOR,
                    "version": VERSION
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                self.log(f"Export JSON: {filepath}")
                
                QMessageBox.information(self, "Succès",
                                      f"✅ Export JSON réussi !\n\n"
                                      f"📁 Fichier: {filepath}")
                
            except Exception as e:
                self.log(f"Erreur export JSON: {str(e)}")
                QMessageBox.critical(self, "Erreur",
                                   f"Erreur export JSON:\n{str(e)}")
    
    def restore_backup(self):
        """Restaure une sauvegarde"""
        QMessageBox.information(self, "Info",
                              "Les backups sont automatiquement créés\n"
                              "quand vous enregistrez un fichier.\n\n"
                              "Cherchez les fichiers avec l'extension\n"
                              ".backup_YYYYMMDD_HHMMSS")
    
    def clean_logs(self):
        """Nettoie les logs"""
        try:
            log_dir = Path("logs")
            if log_dir.exists():
                # Compter les fichiers
                log_files = list(log_dir.glob("*.log"))
                
                if not log_files:
                    QMessageBox.information(self, "Info", "Aucun fichier log à nettoyer")
                    return
                
                # Demander confirmation
                reply = QMessageBox.question(
                    self, "Confirmation",
                    f"Supprimer {len(log_files)} fichier(s) log ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    for log_file in log_files:
                        log_file.unlink()
                    
                    self.log("Logs nettoyés")
                    QMessageBox.information(self, "Succès", "Logs nettoyés avec succès")
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur nettoyage logs: {str(e)}")
    
    def system_info(self):
        """Affiche les informations système"""
        import platform
        
        info = f"""
        🖥️ Informations système :
        
        Application: {APP_NAME} v{VERSION}
        Développeur: {AUTHOR}
        
        Système: {platform.system()} {platform.release()}
        Processeur: {platform.processor()}
        Python: {platform.python_version()}
        
        📁 Dossiers :
        • Application: {os.getcwd()}
        • Logs: {os.path.join(os.getcwd(), 'logs')}
        
        💾 Fichier courant :
        • {self.current_file if self.current_file else 'Aucun'}
        """
        
        QMessageBox.information(self, "Informations système", info)
    
    def manage_backups(self):
        """Gère les backups"""
        QMessageBox.information(self, "Gestion des backups",
                              "Fonctionnalité à venir dans la prochaine version!")
    
    def show_docs(self):
        """Affiche la documentation"""
        docs = f"""
        📚 Documentation {APP_NAME}
        
        1. 🎮 UTILISATION :
           • Ouvrir une sauvegarde (.save)
           • Modifier l'argent avec le contrôle numérique
           • Enregistrer (Ctrl+S)
        
        2. ⚙️ CONFIGURATION :
           • Modifiez l'offset argent dans l'onglet Outils
           • Pour trouver le vrai offset :
             1. Créez 2 sauvegardes avec argent différent
             2. Comparez avec un éditeur hexa
             3. Trouvez l'octet qui change
             4. Entrez l'offset dans la configuration
        
        3. ⚠️ IMPORTANT :
           • Toujours faire des sauvegardes manuelles !
           • L'application crée un backup automatique
           • Les modifications sont permanentes
        
        4. 🔧 SUPPORT :
           • Logs dans le dossier 'logs/'
           • Développeur: {AUTHOR}
           • Version: {VERSION}
        """
        
        QMessageBox.information(self, "Documentation", docs)
    
    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        if self.modified:
            reply = QMessageBox.question(
                self, "Modifications non enregistrées",
                "Vous avez des modifications non enregistrées.\nVoulez-vous vraiment quitter ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        self.log("Application fermée")
        event.accept()

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

def main():
    """Point d'entrée principal"""
    # Gestion des exceptions
    def excepthook(exc_type, exc_value, exc_traceback):
        """Capture toutes les exceptions"""
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Écrire dans le log
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Crash {APP_NAME} v{VERSION}\n")
            f.write(f"Date: {datetime.now()}\n")
            f.write(f"Développeur: {AUTHOR}\n")
            f.write("\n" + "="*50 + "\n")
            f.write(error_msg)
        
        # Afficher message
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Erreur critique")
        msg_box.setText(f"Une erreur s'est produite dans {APP_NAME}")
        msg_box.setInformativeText(
            f"L'erreur a été enregistrée dans:\n{log_file}\n\n"
            f"Veuillez envoyer ce fichier pour support."
        )
        msg_box.setDetailedText(error_msg)
        msg_box.exec()
        
        sys.exit(1)
    
    sys.excepthook = excepthook
    
    # Créer l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    
    # Créer et afficher la fenêtre principale
    window = TS_Tool_Routier()
    window.show()
    
    # Exécuter
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
