import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt

# Import your other UIs
from ui.patient_ui import PatientUI
from ui.medecin_ui import MedecinUI

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clinique Médicale")
        self.setGeometry(100, 100, 1000, 600)

        # ===== Database connection =====
        try:
            self.conn = sqlite3.connect("clinique.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT COUNT(*) FROM patients")
            self.patients_count = self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Database error: {e}")
            self.patients_count = 0

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

        # ===== Spacer =====
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ===== Buttons =====
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        buttons_info = [
            ("👨‍⚕️ Patients", "#3498db", self.open_patients),
            ("👩‍⚕️ Médecins", "#1abc9c", self.open_medecins),
            ("📅 Rendez-vous", "#2ecc71", self.placeholder),
            ("💊 Médicaments", "#9b59b6", self.placeholder),
            ("📊 Statistiques", "#e74c3c", self.placeholder),
            ("⚙️ Paramètres", "#95a5a6", self.placeholder)
        ]

        for text, color, func in buttons_info:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 15px 25px;
                    border-radius: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {color};
                }}
            """)
            btn.clicked.connect(func)
            buttons_layout.addWidget(btn)

        layout.addLayout(buttons_layout)

        # ===== Spacer =====
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ===== Info Label =====
        info_label = QLabel(f"Patients: {self.patients_count} | Date: {datetime.now().strftime('%d/%m/%Y')}")
        info_label.setStyleSheet("color: white;")
        info_label.setFont(QFont("Arial", 12))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

    # ===== Button functions =====
    def open_patients(self):
        self.patient_window = PatientUI()
        self.patient_window.show()

    def open_medecins(self):
        self.med_window = MedecinUI()
        self.med_window.show()

    def placeholder(self):
        print("Button clicked!")

    def closeEvent(self, event):
        if hasattr(self, 'conn'):
            self.conn.close()
        event.accept()


# ===== Run Application =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec())
