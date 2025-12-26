# ui/medecin_ui.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QGroupBox
)
from services.medecin_service import MedecinService

class MedecinUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Médecins")
        self.setGeometry(200, 200, 900, 500)
        self.selected_id = None

        main_layout = QVBoxLayout(self)

        # Form
        form_group = QGroupBox("Médecin")
        form_layout = QHBoxLayout()
        form_group.setLayout(form_layout)

        self.nom = QLineEdit()
        self.spec = QLineEdit()
        self.tel = QLineEdit()
        form_layout.addWidget(QLabel("Nom"))
        form_layout.addWidget(self.nom)
        form_layout.addWidget(QLabel("Spécialité"))
        form_layout.addWidget(self.spec)
        form_layout.addWidget(QLabel("Téléphone"))
        form_layout.addWidget(self.tel)

        add_btn = QPushButton("💾 Ajouter")
        add_btn.clicked.connect(self.add)
        edit_btn = QPushButton("✏️ Modifier")
        edit_btn.clicked.connect(self.update)
        delete_btn = QPushButton("🗑 Supprimer")
        delete_btn.clicked.connect(self.delete)

        form_layout.addWidget(add_btn)
        form_layout.addWidget(edit_btn)
        form_layout.addWidget(delete_btn)

        main_layout.addWidget(form_group)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Spécialité", "Téléphone"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.on_table_select)
        main_layout.addWidget(self.table)

        self.load_medecins()

    def load_medecins(self):
        self.table.setRowCount(0)
        for med in MedecinService.get_all():
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            for col, value in enumerate(med):
                self.table.setItem(row_pos, col, QTableWidgetItem(str(value)))

    def add(self):
        if not self.nom.text() or not self.spec.text():
            QMessageBox.warning(self, "Erreur", "Nom et spécialité obligatoires")
            return
        MedecinService.add(self.nom.text(), self.spec.text(), self.tel.text())
        self.load_medecins()
        self.clear_form()

    def update(self):
        if not self.selected_id:
            return
        MedecinService.update(self.selected_id, self.nom.text(), self.spec.text(), self.tel.text())
        self.load_medecins()
        self.clear_form()

    def delete(self):
        if not self.selected_id:
            return
        reply = QMessageBox.question(self, "Confirmation", "Supprimer ce médecin ?")
        if reply == QMessageBox.StandardButton.Yes:
            MedecinService.delete(self.selected_id)
            self.load_medecins()
            self.clear_form()

    def on_table_select(self, row, column):
        self.selected_id = int(self.table.item(row, 0).text())
        self.nom.setText(self.table.item(row, 1).text())
        self.spec.setText(self.table.item(row, 2).text())
        self.tel.setText(self.table.item(row, 3).text())

    def clear_form(self):
        self.selected_id = None
        self.nom.clear()
        self.spec.clear()
        self.tel.clear()
