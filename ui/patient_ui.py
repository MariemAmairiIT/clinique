# ui/patient_ui.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from services.patient_service import ajouter_patient, get_all_patients, modifier_patient, supprimer_patient

class PatientUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Patients")
        self.setGeometry(200, 200, 900, 500)

        self.selected_patient_id = None

        # ===== Layout =====
        main_layout = QVBoxLayout(self)

        # Form
        form_layout = QVBoxLayout()
        self.entries = {}
        labels = ["Nom", "Prénom", "Âge", "Adresse", "Téléphone", "Antécédents"]
        for label in labels:
            h = QHBoxLayout()
            h.addWidget(QLabel(label))
            entry = QLineEdit()
            h.addWidget(entry)
            form_layout.addLayout(h)
            self.entries[label] = entry

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Ajouter")
        add_btn.clicked.connect(self.add_patient)
        edit_btn = QPushButton("Modifier")
        edit_btn.clicked.connect(self.edit_patient)
        delete_btn = QPushButton("Supprimer")
        delete_btn.clicked.connect(self.delete_patient)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        form_layout.addLayout(btn_layout)
        main_layout.addLayout(form_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(labels) + 1)  # ID + fields
        self.table.setHorizontalHeaderLabels(["ID"] + labels)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.on_table_select)
        main_layout.addWidget(self.table)

        self.load_patients()

    def load_patients(self):
        self.table.setRowCount(0)
        for patient in get_all_patients():
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            for col, value in enumerate(patient):
                self.table.setItem(row_pos, col, QTableWidgetItem(str(value)))

    def add_patient(self):
        data = [self.entries[label].text() for label in self.entries]
        if not all(data[:4]):
            QMessageBox.warning(self, "Erreur", "Nom, Prénom, Âge et Adresse sont obligatoires")
            return
        try:
            data[2] = int(data[2])
        except ValueError:
            QMessageBox.warning(self, "Erreur", "L'âge doit être un nombre")
            return
        ajouter_patient(*data)
        QMessageBox.information(self, "Succès", "Patient ajouté")
        self.load_patients()
        self.clear_entries()

    def edit_patient(self):
        if self.selected_patient_id is None:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un patient")
            return
        data = [self.entries[label].text() for label in self.entries]
        if not all(data[:4]):
            QMessageBox.warning(self, "Erreur", "Nom, Prénom, Âge et Adresse sont obligatoires")
            return
        try:
            data[2] = int(data[2])
        except ValueError:
            QMessageBox.warning(self, "Erreur", "L'âge doit être un nombre")
            return
        modifier_patient(self.selected_patient_id, *data)
        QMessageBox.information(self, "Succès", "Patient modifié")
        self.load_patients()
        self.clear_entries()

    def delete_patient(self):
        if self.selected_patient_id is None:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un patient")
            return
        reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment supprimer ce patient ?")
        if reply == QMessageBox.StandardButton.Yes:
            supprimer_patient(self.selected_patient_id)
            QMessageBox.information(self, "Succès", "Patient supprimé")
            self.load_patients()
            self.clear_entries()

    def on_table_select(self, row, column):
        self.selected_patient_id = int(self.table.item(row, 0).text())
        for i, label in enumerate(self.entries):
            self.entries[label].setText(self.table.item(row, i+1).text())

    def clear_entries(self):
        for entry in self.entries.values():
            entry.clear()
        self.selected_patient_id = None
