#!/usr/bin/env python3
"""
TS_Tool_Routier - Application complète
Éditeur de sauvegardes Transport Fever 2
"""

import sys
import os
import struct
import json
from pathlib import Path
from datetime import datetime

# PyQt6
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ============================================================================
# CONFIGURATION
# ============================================================================

VERSION = "1.0.0"
APP_NAME = "TS_Tool_Routier"
COMPANY = "TF2 Modding Community"

# Chemins
if hasattr(sys, '_MEIPASS'):
    # Mode exécutable PyInstaller
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Mode développement
    BASE_DIR = Path(__file__).parent

# ============================================================================
# CLASSES MÉTIER
# ============================================================================

class GameSave:
    """Représente une sauvegarde du jeu"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.data = None
        self.money = 0
        self.company_name = ""
        self.game_version = ""
        
        # Offsets connus (à adapter selon tes recherches)
        self.offsets = {
            'money': 1048600,      # Offset exemple - À MODIFIER
            'company_name': 1048500, # Offset exemple - À MODIFIER
            'game_version': 100     # Offset exemple - À MODIFIER
        }
    
    def load(self):
        """Charge le fichier de sauvegarde"""
        try:
            with open(self.filepath, 'rb') as f:
                self.data = bytearray(f.read())
            
            # Lire l'argent
            money_offset = self.offsets['money']
            if money_offset + 8 <= len(self.data):
                money_bytes = self.data[money_offset:money_offset+8]
                self.money = struct.unpack('<q', money_bytes)[0]
            
            # Lire le nom de la compagnie
            name_offset = self.offsets['company_name']
            if name_offset + 64 <= len(self.data):
                name_bytes = self.data[name_offset:name_offset+64]
                # Trouver le premier null byte
                end = name_bytes.find(b'\x00')
                if end != -1:
                    self.company_name = name_bytes[:end].decode('utf-8', errors='ignore')
            
            return True
            
        except Exception as e:
            print(f"Erreur chargement: {e}")
            return False
    
    def save(self, new_filepath=None):
        """Sauvegarde les modifications"""
        try:
            if new_filepath is None:
                new_filepath = self.filepath
            
            # Mettre à jour l'argent
            money_offset = self.offsets['money']
            if money_offset + 8 <= len(self.data):
                money_bytes = struct.pack('<q', self.money)
                self.data[money_offset:money_offset+8] = money_bytes
            
            # Écrire le fichier
            with open(new_filepath, 'wb') as f:
                f.write(self.data)
            
            return True
            
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            return False
    
    def set_money(self, amount):
        """Modifie l'argent"""
        self.money = amount

# ============================================================================
# INTERFACE UTILISATEUR
# ============================================================================

class SplashScreen(QSplashScreen):
    """Écran de démarrage"""
    
    def __init__(self):
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor(44, 62, 80))
        
        super().__init__(pixmap)
        
        # Style
        self.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        
        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Logo/Titre
        title = QLabel("🚚 TS_Tool_Routier")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #3498db;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Éditeur de sauvegardes Transport Fever 2")
        subtitle.setStyleSheet("font-size: 16px; color: #bdc3c7;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(50)
        
        # Barre de progression
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress)
        
        # Message
        self.message = QLabel("Initialisation...")
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message)
        
        layout.addStretch()
        
        # Version
        version_label = QLabel(f"Version {VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(version_label)

class MainWindow(QMainWindow):
    """Fenêtre principale"""
    
    def __init__(self):
        super().__init__()
        self.current_save = None
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        
        # Charger la configuration
        self.load_config()
        
        # Centre la fenêtre
        self.center_window()
    
    def setup_ui(self):
        """Configure l'interface"""
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setWindowIcon(QIcon(str(BASE_DIR / "resources" / "icon.ico")))
        self.resize(1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # ===== ZONE DE BIENVENUE =====
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                color: white;
            }
        """)
        
        welcome_layout = QVBoxLayout()
        
        # Titre
        title = QLabel("🎮 TS_Tool_Routier")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #3498db;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(title)
        
        # Description
        desc = QLabel("L'outil ultime pour modifier vos sauvegardes Transport Fever 2")
        desc.setStyleSheet("font-size: 14px; color: #bdc3c7;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(desc)
        
        welcome_frame.setLayout(welcome_layout)
        main_layout.addWidget(welcome_frame)
        
        # ===== ZONE PRINCIPALE =====
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Onglet 1: Éditeur principal
        editor_tab = QWidget()
        editor_layout = QVBoxLayout()
        
        # Informations fichier
        info_group = QGroupBox("📁 Informations de la sauvegarde")
        info_layout = QFormLayout()
        
        self.file_label = QLabel("Aucun fichier chargé")
        self.file_label.setStyleSheet("font-weight: bold;")
        
        self.money_label = QLabel("0 €")
        self.money_label.setStyleSheet("color: #27ae60; font-size: 16px; font-weight: bold;")
        
        self.company_label = QLabel("-")
        
        info_layout.addRow("Fichier:", self.file_label)
        info_layout.addRow("Argent:", self.money_label)
        info_layout.addRow("Compagnie:", self.company_label)
        
        info_group.setLayout(info_layout)
        editor_layout.addWidget(info_group)
        
        # Éditeur d'argent
        money_group = QGroupBox("💰 Éditeur d'argent")
        money_layout = QHBoxLayout()
        
        self.money_spin = QSpinBox()
        self.money_spin.setRange(-1000000000, 10000000000)
        self.money_spin.setSingleStep(1000)
        self.money_spin.setPrefix("€ ")
        self.money_spin.valueChanged.connect(self.on_money_changed)
        
        money_layout.addWidget(QLabel("Montant:"))
        money_layout.addWidget(self.money_spin)
        money_layout.addStretch()
        
        # Boutons présets
        presets = [("100K", 100000), ("500K", 500000), ("1M", 1000000), ("10M", 10000000)]
        for text, value in presets:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, v=value: self.set_money_preset(v))
            money_layout.addWidget(btn)
        
        money_group.setLayout(money_layout)
        editor_layout.addWidget(money_group)
        
        # Actions rapides
        actions_group = QGroupBox("⚡ Actions rapides")
        actions_layout = QGridLayout()
        
        buttons = [
            ("💾 Enregistrer", self.save_file, "Enregistre les modifications"),
            ("💾 Enregistrer sous", self.save_as, "Enregistre sous un nouveau nom"),
            ("🔄 Restaurer", self.restore_backup, "Restaurer une sauvegarde"),
            ("📊 Statistiques", self.show_stats, "Afficher les statistiques"),
            ("🔍 Rechercher offset", self.find_offset, "Trouver un offset"),
            ("📤 Exporter JSON", self.export_json, "Exporter en JSON"),
        ]
        
        row, col = 0, 0
        for text, slot, tooltip in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            btn.setToolTip(tooltip)
            btn.setMinimumHeight(40)
            actions_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        actions_group.setLayout(actions_layout)
        editor_layout.addWidget(actions_group)
        
        editor_layout.addStretch()
        editor_tab.setLayout(editor_layout)
        tab_widget.addTab(editor_tab, "Éditeur")
        
        # Onglet 2: Éditeur hexadécimal
        hex_tab = QWidget()
        hex_layout = QVBoxLayout()
        
        # Toolbar hex
        hex_toolbar = QHBoxLayout()
        
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("Offset (ex: 0x1234)")
        hex_toolbar.addWidget(self.hex_input)
        
        goto_btn = QPushButton("Aller à")
        goto_btn.clicked.connect(self.goto_offset)
        hex_toolbar.addWidget(goto_btn)
        
        hex_toolbar.addStretch()
        
        hex_layout.addLayout(hex_toolbar)
        
        # Zone d'affichage hex
        self.hex_display = QTextEdit()
        self.hex_display.setFont(QFont("Courier New", 10))
        self.hex_display.setReadOnly(True)
        hex_layout.addWidget(self.hex_display)
        
        hex_tab.setLayout(hex_layout)
        tab_widget.addTab(hex_tab, "🔧 Hexadécimal")
        
        # Onglet 3: À propos
        about_tab = QWidget()
        about_layout = QVBoxLayout()
        
        about_text = f"""
        <div style='text-align: center;'>
            <h1 style='color: #3498db;'>🚚 TS_Tool_Routier</h1>
            <h3>Version {VERSION}</h3>
            <p>L'éditeur de sauvegardes pour Transport Fever 2</p>
            
            <hr>
            
            <h3>📋 Fonctionnalités</h3>
            <ul style='text-align: left; margin: 20px;'>
                <li>Modification de l'argent du joueur</li>
                <li>Éditeur hexadécimal intégré</li>
                <li>Sauvegarde automatique des originaux</li>
                <li>Support des offsets personnalisés</li>
                <li>Export des données en JSON</li>
            </ul>
            
            <h3>⚠️ Important</h3>
            <p style='color: #e74c3c;'>
                Toujours faire des sauvegardes de vos fichiers originaux !
            </p>
            
            <hr>
            
            <p>Développé avec ❤️ pour la communauté TF2</p>
            <p>© 2024 {COMPANY}</p>
        </div>
        """
        
        about_label = QLabel(about_text)
        about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_label.setWordWrap(True)
        about_layout.addWidget(about_label)
        
        about_tab.setLayout(about_layout)
        tab_widget.addTab(about_tab, "ℹ️ À propos")
        
        # ===== BARRE DE STATUT =====
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt")
        
        # Indicateur de modification
        self.modified_label = QLabel()
        self.status_bar.addPermanentWidget(self.modified_label)
    
    def setup_menu(self):
        """Configure le menu"""
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
        file_menu.addAction(save_action)
        
        save_as_action = QAction("💾 Enregistrer sous...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as)
        save_as_action.setEnabled(False)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Quitter", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Édition
        edit_menu = menubar.addMenu("✏️ Édition")
        
        money_action = QAction("💰 Modifier l'argent...", self)
        money_action.triggered.connect(self.edit_money_dialog)
        edit_menu.addAction(money_action)
        
        # Menu Outils
        tools_menu = menubar.addMenu("🔧 Outils")
        
        hex_action = QAction("🔍 Éditeur hexadécimal", self)
        hex_action.triggered.connect(self.show_hex_editor)
        tools_menu.addAction(hex_action)
        
        config_action = QAction("⚙️ Configuration", self)
        config_action.triggered.connect(self.show_config)
        tools_menu.addAction(config_action)
        
        # Menu Aide
        help_menu = menubar.addMenu("❓ Aide")
        
        about_action = QAction("ℹ️ À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction("📚 Documentation", self)
        docs_action.triggered.connect(self.show_docs)
        help_menu.addAction(docs_action)
    
    def setup_toolbar(self):
        """Configure la barre d'outils"""
        toolbar = self.addToolBar("Outils")
        toolbar.setIconSize(QSize(32, 32))
        
        # Bouton Ouvrir
        open_btn = QAction(QIcon(str(BASE_DIR / "resources" / "open.png")), "Ouvrir", self)
        open_btn.triggered.connect(self.open_file)
        toolbar.addAction(open_btn)
        
        # Bouton Enregistrer
        self.save_btn = QAction(QIcon(str(BASE_DIR / "resources" / "save.png")), "Enregistrer", self)
        self.save_btn.triggered.connect(self.save_file)
        self.save_btn.setEnabled(False)
        toolbar.addAction(self.save_btn)
        
        toolbar.addSeparator()
        
        # Bouton Argent
        money_btn = QAction(QIcon(str(BASE_DIR / "resources" / "money.png")), "Argent", self)
        money_btn.triggered.connect(self.edit_money_dialog)
        toolbar.addAction(money_btn)
        
        # Bouton Hex
        hex_btn = QAction(QIcon(str(BASE_DIR / "resources" / "hex.png")), "Hex", self)
        hex_btn.triggered.connect(self.show_hex_editor)
        toolbar.addAction(hex_btn)
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def load_config(self):
        """Charge la configuration"""
        config_file = BASE_DIR / "config.ini"
        if config_file.exists():
            try:
                # À implémenter
                pass
            except:
                pass
    
    # ============================================================================
    # SLOTS (GESTION DES ÉVÉNEMENTS)
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
            self.load_save_file(filepath)
    
    def load_save_file(self, filepath):
        """Charge et affiche une sauvegarde"""
        self.current_save = GameSave(filepath)
        
        if self.current_save.load():
            # Mettre à jour l'interface
            self.file_label.setText(self.current_save.filename)
            self.money_label.setText(f"{self.current_save.money:,} €")
            self.company_label.setText(self.current_save.company_name)
            
            # Activer les contrôles
            self.money_spin.setValue(self.current_save.money)
            self.money_spin.setEnabled(True)
            self.save_btn.setEnabled(True)
            
            # Mettre à jour l'affichage hex
            self.update_hex_display()
            
            # Message de statut
            self.status_bar.showMessage(f"Chargé: {self.current_save.filename}")
            self.modified_label.setText("")
            
            QMessageBox.information(self, "Succès", 
                                  f"Sauvegarde chargée avec succès!\n\n"
                                  f"Fichier: {self.current_save.filename}\n"
                                  f"Argent: {self.current_save.money:,} €")
        else:
            QMessageBox.critical(self, "Erreur", 
                               "Impossible de charger le fichier de sauvegarde.")
            self.current_save = None
    
    def on_money_changed(self, value):
        """Quand l'argent est modifié"""
        if self.current_save:
            self.current_save.set_money(value)
            self.money_label.setText(f"{value:,} €")
            self.modified_label.setText("[MODIFIÉ]")
            self.modified_label.setStyleSheet("color: red; font-weight: bold;")
    
    def set_money_preset(self, amount):
        """Définit un montant prédéfini"""
        self.money_spin.setValue(amount)
    
    def save_file(self):
        """Enregistre le fichier courant"""
        if not self.current_save:
            return
        
        # Créer une sauvegarde
        backup_file = f"{self.current_save.filepath}.backup"
        import shutil
        shutil.copy2(self.current_save.filepath, backup_file)
        
        # Sauvegarder
        if self.current_save.save():
            self.modified_label.setText("")
            self.status_bar.showMessage("Fichier enregistré avec succès", 3000)
            QMessageBox.information(self, "Succès", 
                                  f"Fichier enregistré!\n\n"
                                  f"Backup créé: {os.path.basename(backup_file)}")
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")
    
    def save_as(self):
        """Enregistre sous un nouveau nom"""
        if not self.current_save:
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer sous",
            self.current_save.filepath,
            "Fichiers de sauvegarde (*.save);;Tous les fichiers (*.*)"
        )
        
        if filepath:
            if self.current_save.save(filepath):
                self.status_bar.showMessage(f"Enregistré sous: {os.path.basename(filepath)}", 3000)
                QMessageBox.information(self, "Succès", "Fichier enregistré avec succès.")
    
    def restore_backup(self):
        """Restaure une sauvegarde"""
        # À implémenter
        QMessageBox.information(self, "Info", "Fonction à venir...")
    
    def show_stats(self):
        """Affiche les statistiques"""
        if not self.current_save:
            QMessageBox.warning(self, "Erreur", "Aucun fichier chargé")
            return
        
        stats = f"""
        📊 Statistiques de la sauvegarde:
        
        Fichier: {self.current_save.filename}
        Taille: {len(self.current_save.data):,} octets
        Argent: {self.current_save.money:,} €
        Compagnie: {self.current_save.company_name}
        
        Offsets configurés:
        • Argent: 0x{self.current_save.offsets['money']:X}
        • Nom: 0x{self.current_save.offsets['company_name']:X}
        """
        
        QMessageBox.information(self, "Statistiques", stats)
    
    def find_offset(self):
        """Trouve un offset"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Recherche d'offset")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Cette fonctionnalité permet de trouver\n"
                              "les offsets en comparant deux sauvegardes."))
        
        layout.addStretch()
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def export_json(self):
        """Exporte en JSON"""
        if not self.current_save:
            QMessageBox.warning(self, "Erreur", "Aucun fichier chargé")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en JSON",
            f"{self.current_save.filename}.json",
            "Fichiers JSON (*.json);;Tous les fichiers (*.*)"
        )
        
        if filepath:
            data = {
                "filename": self.current_save.filename,
                "money": self.current_save.money,
                "company_name": self.current_save.company_name,
                "file_size": len(self.current_save.data),
                "export_date": datetime.now().isoformat()
            }
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Succès", f"Export JSON réussi:\n{filepath}")
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur d'export: {str(e)}")
    
    def edit_money_dialog(self):
        """Ouvre un dialogue pour modifier l'argent"""
        if not self.current_save:
            QMessageBox.warning(self, "Erreur", "Ouvrez d'abord une sauvegarde")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier l'argent")
        dialog.resize(300, 200)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(f"Argent actuel: {self.current_save.money:,} €"))
        layout.addSpacing(20)
        
        spinbox = QSpinBox()
        spinbox.setRange(-1000000000, 10000000000)
        spinbox.setValue(self.current_save.money)
        spinbox.setPrefix("€ ")
        layout.addWidget(spinbox)
        
        layout.addSpacing(20)
        
        btn_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_apply = QPushButton("Appliquer")
        btn_apply.clicked.connect(dialog.accept)
        btn_apply.setDefault(True)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_apply)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        
        if dialog.exec():
            self.money_spin.setValue(spinbox.value())
    
    def show_hex_editor(self):
        """Affiche l'onglet hexadécimal"""
        self.centralWidget().findChild(QTabWidget).setCurrentIndex(1)
    
    def update_hex_display(self):
        """Met à jour l'affichage hexadécimal"""
        if not self.current_save or not self.current_save.data:
            self.hex_display.setText("Aucune donnée à afficher")
            return
        
        # Afficher les premiers 1024 octets
        data = self.current_save.data[:1024]
        
        hex_text = ""
        ascii_text = ""
        
        for i in range(0, len(data), 16):
            # Offset
            hex_text += f"{i:08X}: "
            
            # Hex
            for j in range(16):
                if i + j < len(data):
                    hex_text += f"{data[i+j]:02X} "
                else:
                    hex_text += "   "
            
            hex_text += " "
            
            # ASCII
            for j in range(16):
                if i + j < len(data):
                    byte = data[i+j]
                    if 32 <= byte < 127:
                        hex_text += chr(byte)
                    else:
                        hex_text += "."
                else:
                    hex_text += " "
            
            hex_text += "\n"
        
        self.hex_display.setText(hex_text)
    
    def goto_offset(self):
        """Va à un offset spécifique"""
        offset_text = self.hex_input.text().strip()
        
        try:
            if offset_text.startswith('0x'):
                offset = int(offset_text, 16)
            else:
                offset = int(offset_text)
            
            QMessageBox.information(self, "Info", 
                                  f"Offset 0x{offset:X} sélectionné.\n\n"
                                  "Cette fonctionnalité sera implémentée\n"
                                  "dans une prochaine version.")
            
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Format d'offset invalide")
    
    def show_config(self):
        """Affiche la configuration"""
        QMessageBox.information(self, "Configuration", 
                              "Éditez le fichier config.ini\n"
                              "pour modifier les offsets et paramètres.")
    
    def show_about(self):
        """Affiche la boîte À propos"""
        QMessageBox.about(self, f"À propos de {APP_NAME}",
                         f"""
                         <h2>{APP_NAME} v{VERSION}</h2>
                         <p>Éditeur de sauvegardes pour Transport Fever 2</p>
                         
                         <p>Développé avec Python et PyQt6</p>
                         <p>© 2024 {COMPANY}</p>
                         
                         <hr>
                         <p><b>⚠️ Important:</b></p>
                         <p>Toujours faire des sauvegardes de vos fichiers originaux
                         avant de les modifier avec cet outil.</p>
                         """)
    
    def show_docs(self):
        """Affiche la documentation"""
        QMessageBox.information(self, "Documentation",
                              "Consultez le fichier README.txt\n"
                              "pour la documentation complète.")
    
    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        if self.modified_label.text():
            reply = QMessageBox.question(
                self, "Modifications non enregistrées",
                "Vous avez des modifications non enregistrées.\n"
                "Voulez-vous vraiment quitter ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        # Sauvegarder la configuration
        self.save_config()
        
        event.accept()
    
    def save_config(self):
        """Sauvegarde la configuration"""
        # À implémenter
        pass

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

def main():
    """Point d'entrée principal"""
    # Gestion des exceptions
    def excepthook(exc_type, exc_value, exc_traceback):
        """Capture toutes les exceptions"""
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Écrire dans un fichier log
        log_dir = BASE_DIR / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"crash_{datetime.now():%Y%m%d_%H%M%S}.log"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Crash {APP_NAME} v{VERSION}\n")
            f.write(f"Date: {datetime.now()}\n")
            f.write("\n" + "="*50 + "\n")
            f.write(error_msg)
        
        # Afficher un message d'erreur
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
        
        # Terminer l'application
        sys.exit(1)
    
    sys.excepthook = excepthook
    
    # Créer l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setOrganizationName(COMPANY)
    
    # Style
    app.setStyle("Fusion")
    
    # Palette de couleurs
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    # Écran de démarrage
    splash = SplashScreen()
    splash.show()
    
    # Simuler un chargement
    for i in range(1, 101):
        splash.progress.setValue(i)
        if i < 30:
            splash.message.setText("Initialisation...")
        elif i < 60:
            splash.message.setText("Chargement des modules...")
        elif i < 90:
            splash.message.setText("Préparation de l'interface...")
        else:
            splash.message.setText("Démarrage...")
        
        QApplication.processEvents()
        QThread.msleep(20)
    
    # Créer la fenêtre principale
    window = MainWindow()
    
    # Fermer le splash et afficher la fenêtre
    splash.finish(window)
    window.show()
    
    # Exécuter l'application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
