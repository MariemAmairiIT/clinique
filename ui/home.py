import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QSpacerItem, QSizePolicy, QMessageBox
)
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtCore import Qt

# Import your other UIs
from ui.patient_ui import PatientUI
from ui.medecin_ui import MedecinUI
from ui.rendezvous_ui import RendezVousUI
from .dossier_ui import DossierUI
from .reports_ui import ReportsUI  # NOUVEAU : Import de la page des rapports

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clinique Médicale")
        self.setGeometry(100, 100, 1000, 600)

        # ===== Database connection =====
        try:
            self.conn = sqlite3.connect("clinique.db")
            self.cursor = self.conn.cursor()
            
            # Récupérer plusieurs statistiques
            self.cursor.execute("SELECT COUNT(*) FROM patients")
            self.patients_count = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM medecins")
            self.medecins_count = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM rendezvous")
            self.rendezvous_count = self.cursor.fetchone()[0]
            
        except Exception as e:
            print(f"Database error: {e}")
            self.patients_count = 0
            self.medecins_count = 0
            self.rendezvous_count = 0

        # ===== Background Image =====
        self.bg_label = QLabel(self)
        pixmap = QPixmap("img/27f45db4a3041d1d9b60b58f9f8b7b7e.jpg")  # Put bg.png in the same folder
        if pixmap.isNull():
            print("Background image not found!")
        else:
            pixmap = pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding
            )
            self.bg_label.setPixmap(pixmap)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())

        # ===== Overlay =====
        self.overlay = QWidget(self)
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);")

        # ===== Layout =====
        layout = QVBoxLayout(self.overlay)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ===== Hero Title =====
        title = QLabel("Bienvenue dans le système de gestion clinique")
        title.setStyleSheet("color: white;")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # ===== Sous-titre =====
        subtitle = QLabel("Gestion complète de votre clinique médicale")
        subtitle.setStyleSheet("color: #95a5a6;")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # ===== Spacer =====
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ===== Statistiques rapides =====
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setSpacing(20)
        
        # Patients
        patients_card = self.create_stat_card("👥 Patients", str(self.patients_count), "#3498db")
        # Médecins
        medecins_card = self.create_stat_card("👨‍⚕️ Médecins", str(self.medecins_count), "#1abc9c")
        # Rendez-vous
        rdv_card = self.create_stat_card("📅 Rendez-vous", str(self.rendezvous_count), "#2ecc71")
        
        stats_layout.addWidget(patients_card)
        stats_layout.addWidget(medecins_card)
        stats_layout.addWidget(rdv_card)
        
        layout.addWidget(stats_widget)
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ===== Buttons =====
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        buttons_info = [
            ("👨‍⚕️ Patients", "#3498db", self.open_patients),
            ("👩‍⚕️ Médecins", "#1abc9c", self.open_medecins),
            ("📅 Rendez-vous", "#2ecc71", self.open_rendezvous), 
            ("📁 Dossiers", "#9b59b6", self.open_dossiers),
            ("📊 Rapports", "#f39c12", self.open_reports),  # CHANGÉ : Rapports au lieu de Statistiques
            ("⚙️ Paramètres", "#95a5a6", self.placeholder)
        ]

        for text, color, func in buttons_info:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.setMinimumWidth(140)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    border: 2px solid transparent;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {color};
                    border: 2px solid {color};
                    font-weight: bold;
                }}
            """)
            btn.clicked.connect(func)
            buttons_layout.addWidget(btn)

        layout.addLayout(buttons_layout)

        # ===== Spacer =====
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ===== Info Label =====
        info_text = f"""
        <div style='color: white; text-align: center;'>
            <p style='font-size: 14px;'><b>Système de Gestion Clinique</b></p>
            <p style='font-size: 12px; color: #bdc3c7;'>
                {self.patients_count} Patients • {self.medecins_count} Médecins • {self.rendezvous_count} RDV
            </p>
            <p style='font-size: 11px; color: #95a5a6;'>
                © {datetime.now().year} Clinique Médicale • Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </p>
        </div>
        """
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

    def create_stat_card(self, title, value, color):
        """Crée une carte de statistique"""
        card = QWidget()
        card.setMinimumWidth(150)
        card.setMaximumWidth(200)
        card.setMinimumHeight(100)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                border-left: 5px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title_label)
        
        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Valeur
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            color: {color}; 
            font-size: 24px; 
            font-weight: bold;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
            padding: 5px;
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        return card

    # ===== Button functions =====
    def open_patients(self):
        """Ouvre la gestion des patients"""
        try:
            self.patient_window = PatientUI()
            self.patient_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir les patients: {e}")

    def open_medecins(self):
        """Ouvre la gestion des médecins"""
        try:
            self.med_window = MedecinUI()
            self.med_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir les médecins: {e}")

    def open_rendezvous(self):
        """Ouvre la gestion des rendez-vous"""
        try:
            self.rdv_window = RendezVousUI()
            self.rdv_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir les rendez-vous: {e}")

    def open_dossiers(self):
        """Ouvre la gestion des dossiers"""
        try:
            self.dossier_window = DossierUI()
            self.dossier_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir les dossiers: {e}")

    def open_reports(self):
        """Ouvre les rapports statistiques"""
        try:
            self.reports_window = ReportsUI()
            self.reports_window.closed.connect(self.on_reports_closed)
            self.reports_window.show()
        except ImportError as e:
            QMessageBox.warning(self, "Fonctionnalité indisponible", 
                              "La fonctionnalité Rapports n'est pas encore implémentée.\n"
                              "Assurez-vous que le module reports_ui.py existe.")
            print(f"Erreur d'import: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir les rapports: {e}")

    def on_reports_closed(self):
        """Quand la fenêtre des rapports se ferme"""
        self.reports_window = None

    def placeholder(self):
        """Fonction placeholder pour les boutons non implémentés"""
        QMessageBox.information(self, "Information", 
                              "Cette fonctionnalité sera disponible dans une prochaine version!")

    def refresh_stats(self):
        """Rafraîchit les statistiques affichées"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM patients")
            self.patients_count = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM medecins")
            self.medecins_count = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM rendezvous")
            self.rendezvous_count = self.cursor.fetchone()[0]
            
            # Mettre à jour l'affichage (vous devrez stocker les labels pour les mettre à jour)
            # Cette partie nécessite de garder des références aux labels créés
            print(f"Statistiques mises à jour: {self.patients_count} patients, "
                  f"{self.medecins_count} médecins, {self.rendezvous_count} RDV")
                  
        except Exception as e:
            print(f"Erreur rafraîchissement stats: {e}")

    def resizeEvent(self, event):
        """Redimensionne l'image de fond quand la fenêtre change de taille"""
        super().resizeEvent(event)
        if not self.bg_label.pixmap().isNull():
            pixmap = self.bg_label.pixmap()
            pixmap = pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding
            )
            self.bg_label.setPixmap(pixmap)
            self.bg_label.setGeometry(0, 0, self.width(), self.height())
            self.overlay.setGeometry(0, 0, self.width(), self.height())

    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        if hasattr(self, 'conn'):
            self.conn.close()
        event.accept()

    def showEvent(self, event):
        """Quand la fenêtre s'affiche"""
        super().showEvent(event)
        # Rafraîchir les stats à l'ouverture
        self.refresh_stats()


# ===== Run Application =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Style global
    app.setStyleSheet("""
        QMessageBox {
            background-color: #f8f9fa;
            font-family: Arial;
        }
        QMessageBox QLabel {
            color: #2c3e50;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            background-color: #3498db;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #2980b9;
        }
    """)
    
    window = HomePage()
    window.show()
    sys.exit(app.exec())