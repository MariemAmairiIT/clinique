import sys
import sqlite3
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QSpacerItem, QSizePolicy, QMessageBox,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QPixmap, QFont, QIcon, QColor
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer

from ui.patient_ui import PatientUI
from ui.medecin_ui import MedecinUI
from ui.rendezvous_ui import RendezVousUI
from ui.dossier_ui import DossierUI
from ui.reports_ui import ReportsUI  # NOUVEAU : Import de la page des rapports

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        print("HomePage loaded")
        self.setWindowTitle("Clinique Médicale")
        self.resize(1200, 700)

        # ================= DATABASE =================
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
            print("DB error:", e)
            self.patients_count = 0
            self.medecins_count = 0
            self.rendezvous_count = 0

        # ================= BACKGROUND =================
        self.bg = QLabel(self)
        self.bg.setScaledContents(True)
        self.bg.setPixmap(QPixmap("img/27f45db4a3041d1d9b60b58f9f8b7b7e.jpg"))

        # ================= MAIN LAYOUT =================
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(60, 40, 60, 40)

        # ================= LEFT TEXT =================
        left = QVBoxLayout()
        left.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # ----- Title -----
        title = QLabel("Système de Gestion Clinique")
        title_font = QFont("Segoe UI", 38, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: white;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 180))
        title.setGraphicsEffect(shadow)
        left.addWidget(title)

        # ----- Subtitle -----
        subtitle = QLabel("Interface professionnelle pour la gestion médicale")
        subtitle_font = QFont("Segoe UI", 16)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #dddddd;")
        sub_shadow = QGraphicsDropShadowEffect()
        sub_shadow.setBlurRadius(8)
        sub_shadow.setOffset(1, 1)
        sub_shadow.setColor(QColor(0, 0, 0, 150))
        subtitle.setGraphicsEffect(sub_shadow)
        left.addWidget(subtitle)

        # Space between texts and info
        left.addSpacing(50)
        left.addStretch()

        # ----- Info / Date -----
        info = QLabel(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
        info.setAlignment(Qt.AlignRight)
        info.setFont(QFont("Segoe UI", 12, QFont.Bold))
        left.addWidget(info)

        # ================= RIGHT PANEL =================
        self.panel = QWidget()
        self.panel.setFixedWidth(320)
        self.panel.setStyleSheet("background-color: transparent;")

        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setSpacing(18)
        panel_layout.setAlignment(Qt.AlignVCenter)

        self.buttons = []

        buttons = [
            ("👨‍⚕️ Patients", "#3498db", self.open_patients),
            ("👩‍⚕️ Médecins", "#1abc9c", self.open_medecins),
            ("📅 Rendez-vous", "#2ecc71", self.open_rendezvous),
            ("💊 Médicaments", "#9b59b6", self.open_dossiers),
            ("📊 Statistiques", "#e74c3c", self.open_reports),
            ("⚙️ Paramètres", "#95a5a6", self.placeholder),
        ]

        for text, color, action in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(55)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumWidth(280)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 14px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {color};
                    border: 2px solid {color};
                    font-weight: bold;
                }}
            """)
            btn.clicked.connect(action)
            panel_layout.addWidget(btn)
            self.buttons.append(btn)

        # ================= ADD TO MAIN LAYOUT =================
        main_layout.addLayout(left)
        main_layout.addWidget(self.panel, alignment=Qt.AlignRight)

        # ================= ANIMATION =================
        QTimer.singleShot(0, self.animate_panel)

    # ================= ANIMATION =================
    def animate_panel(self):
        opacity = QGraphicsOpacityEffect(self.panel)
        self.panel.setGraphicsEffect(opacity)
        fade = QPropertyAnimation(opacity, b"opacity")
        fade.setDuration(900)
        fade.setStartValue(0)
        fade.setEndValue(1)
        fade.start()
        self.fade_animation = fade

        for i, btn in enumerate(self.buttons):
            anim = QPropertyAnimation(btn, b"pos")
            anim.setDuration(700)
            anim.setStartValue(btn.pos() + QPoint(100, 0))
            anim.setEndValue(btn.pos())
            anim.setEasingCurve(QEasingCurve.OutBack)
            anim.start()
            setattr(self, f"anim_{i}", anim)

    # ================= RESIZE =================
    def resizeEvent(self, event):
        self.bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    # ================= ACTIONS =================
    def open_patients(self):
        try:
            self.patient_window = PatientUI()
            self.patient_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir les patients: {e}")

    def open_medecins(self):
        try:
            self.med_window = MedecinUI()
            self.med_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir les médecins: {e}")

    def open_rendezvous(self):
        try:
            self.rdv_window = RendezVousUI()
            self.rdv_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir les rendez-vous: {e}")

    def open_dossiers(self):
        try:
            self.dossier_window = DossierUI()
            self.dossier_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir les dossiers: {e}")

    def open_reports(self):
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
        self.reports_window = None

    def placeholder(self):
        print("Coming soon")

    def refresh_stats(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM patients")
            self.patients_count = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM medecins")
            self.medecins_count = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM rendezvous")
            self.rendezvous_count = self.cursor.fetchone()[0]
            
            print(f"Statistiques mises à jour: {self.patients_count} patients, "
                  f"{self.medecins_count} médecins, {self.rendezvous_count} RDV")
        except Exception as e:
            print(f"Erreur rafraîchissement stats: {e}")

    def closeEvent(self, event):
        if hasattr(self, "conn"):
            self.conn.close()
        event.accept()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_stats()


# ================= RUN =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = HomePage()
    w.show()
    sys.exit(app.exec())
