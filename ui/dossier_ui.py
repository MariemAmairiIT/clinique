import sys
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QGroupBox, QGridLayout, QDateEdit, QComboBox, QTextEdit,
    QCompleter  # QCompleter importé depuis QtWidgets
)
from PySide6.QtCore import QDate, Qt, Signal, QStringListModel
from PySide6.QtGui import QFont, QIcon
from services.dossier_service import DossierService
from services.patient_service import PatientService

class DossierUI(QWidget):
    # Signal pour notifier la fermeture
    closed = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dossiers Médicaux - Clinique Médicale")
        self.setGeometry(100, 100, 1200, 700)
        self.current_dossier_id = None
        self.selected_patient_id = None
        self.patient_names = []  # Stocker les noms des patients
        self.patients_dict = {}  # Dictionnaire {nom_complet: id_patient}
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Titre principal
        title = QLabel("Gestion des Dossiers Médicaux")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Groupe Formulaire - Nouvelle entrée de dossier
        form_group = QGroupBox("Nouvelle Entrée de Dossier")
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # ⭐⭐ SOLUTION : Champ texte + Auto-complétion ⭐⭐
        self.patient_input = QLineEdit()
        self.patient_input.setPlaceholderText("Écrivez le nom du patient...")
        self.patient_input.setMinimumHeight(40)
        
        # Créer un completer pour l'auto-complétion
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)  # Insensible à la casse
        self.completer.setFilterMode(Qt.MatchContains)  # Recherche dans tout le texte
        
        # Connecter le completer au champ
        self.patient_input.setCompleter(self.completer)
        
        # Charger les patients
        self.load_patients()
        
        # Quand on écrit dans le champ
        self.patient_input.textChanged.connect(self.on_patient_text_changed)
        
        form_layout.addWidget(QLabel("Patient :"), 0, 0)
        form_layout.addWidget(self.patient_input, 0, 1)

        # Date de la visite
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addWidget(QLabel("Date de visite :"), 1, 0)
        form_layout.addWidget(self.date_edit, 1, 1)

        # Observations (champ texte plus grand)
        self.observations_input = QTextEdit()
        self.observations_input.setPlaceholderText("Observations médicales, symptômes, diagnostic...")
        self.observations_input.setMaximumHeight(100)
        form_layout.addWidget(QLabel("Observations :"), 2, 0)
        form_layout.addWidget(self.observations_input, 2, 1)

        # Traitement
        self.traitement_input = QTextEdit()
        self.traitement_input.setPlaceholderText("Traitement prescrit, médicaments, posologie...")
        self.traitement_input.setMaximumHeight(100)
        form_layout.addWidget(QLabel("Traitement :"), 3, 0)
        form_layout.addWidget(self.traitement_input, 3, 1)

        # Boutons formulaire
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.add_btn = QPushButton("➕ Ajouter")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_btn.setMinimumHeight(40)
        self.add_btn.clicked.connect(self.add_dossier)

        self.update_btn = QPushButton("✏️ Modifier")
        self.update_btn.setIcon(QIcon.fromTheme("document-edit"))
        self.update_btn.setMinimumHeight(40)
        self.update_btn.clicked.connect(self.update_dossier)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("🗑️ Supprimer")
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.clicked.connect(self.delete_dossier)
        self.delete_btn.setEnabled(False)

        self.clear_btn = QPushButton("🧹 Effacer")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self.clear_form)

        # BOUTON FERMER
        self.close_btn = QPushButton("✖ Fermer")
        self.close_btn.setIcon(QIcon.fromTheme("window-close"))
        self.close_btn.setMinimumHeight(40)
        self.close_btn.clicked.connect(self.close_window)

        for btn in [self.add_btn, self.update_btn, self.delete_btn, self.clear_btn, self.close_btn]:
            btn.setCursor(Qt.PointingHandCursor)
            btn_layout.addWidget(btn)

        form_layout.addLayout(btn_layout, 4, 0, 1, 2)
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        # ===== BARRE DE RECHERCHE =====
        search_group = QGroupBox("Rechercher un Dossier")
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom de patient...")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.on_search_changed)
        
        self.search_btn = QPushButton("🔍 Rechercher")
        self.search_btn.setMinimumHeight(40)
        self.search_btn.clicked.connect(self.search_dossiers)
        
        self.reset_search_btn = QPushButton("🔄 Tout Afficher")
        self.reset_search_btn.setMinimumHeight(40)
        self.reset_search_btn.clicked.connect(self.reset_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.reset_search_btn)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)

        # Table des dossiers
        table_group = QGroupBox("Historique des Dossiers")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["N°", "Patient", "Date", "Observations", "Traitement"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.on_table_cell_clicked)

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group, stretch=1)

        self.load_dossiers()

    def load_patients(self):
        """Charger la liste des patients pour l'auto-complétion"""
        try:
            patients = PatientService.get_all()
            self.patient_names = []
            self.patients_dict = {}
            
            for patient in patients:
                patient_id = patient[0]
                nom_complet = f"{patient[1]} {patient[2]}"  # nom + prénom
                self.patient_names.append(nom_complet)
                self.patients_dict[nom_complet] = patient_id
            
            # Configurer le completer avec la liste des noms
            model = QStringListModel(self.patient_names)
            self.completer.setModel(model)
            
        except Exception as e:
            print(f"Erreur chargement patients: {e}")

    def on_patient_text_changed(self, text):
        """Quand on écrit dans le champ patient"""
        # Chercher l'ID du patient correspondant au nom
        if text in self.patients_dict:
            self.selected_patient_id = self.patients_dict[text]
        else:
            self.selected_patient_id = None

    def apply_styles(self):
        stylesheet = """
        QWidget {
            background-color: #f8fafc;
            font-family: Segoe UI, Arial;
        }
        QGroupBox {
            font-weight: bold;
            font-size: 14px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: white;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px 0 10px;
            color: #2d3748;
        }
        QLabel {
            color: #2d3748;
        }
        QLineEdit, QComboBox, QDateEdit, QTextEdit {
            padding: 8px;
            border: 2px solid #cbd5e0;
            border-radius: 8px;
            font-size: 14px;
            background-color: white;
        }
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
            border-color: #4299e1;
            background-color: #f0f8ff;
        }
        QPushButton {
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            min-width: 120px;
        }
        QPushButton:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        #add_btn {
            background-color: #48bb78;
            color: white;
        }
        #add_btn:hover {
            background-color: #38a169;
        }
        #edit_btn {
            background-color: #4299e1;
            color: white;
        }
        #edit_btn:hover {
            background-color: #3182ce;
        }
        #delete_btn {
            background-color: #f56565;
            color: white;
        }
        #delete_btn:hover {
            background-color: #e53e3e;
        }
        #clear_btn {
            background-color: #a0aec0;
            color: white;
        }
        #clear_btn:hover {
            background-color: #90a0b8;
        }
        #close_btn {
            background-color: #718096;
            color: white;
        }
        #close_btn:hover {
            background-color: #4a5568;
        }
        #search_btn {
            background-color: #805ad5;
            color: white;
        }
        #search_btn:hover {
            background-color: #6b46c1;
        }
        #reset_search_btn {
            background-color: #ed8936;
            color: white;
        }
        #reset_search_btn:hover {
            background-color: #dd6b20;
        }
        QTableWidget {
            gridline-color: #e2e8f0;
            background-color: white;
            alternate-background-color: #f7fafc;
            selection-background-color: #bee3f8;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
        }
        QHeaderView::section {
            background-color: #4299e1;
            color: white;
            padding: 10px;
            font-weight: bold;
            border: none;
        }
        QMessageBox {
            background-color: white;
        }
        """
        self.setStyleSheet(stylesheet)
        
        # Ajouter des IDs aux boutons pour le style
        self.add_btn.setObjectName("add_btn")
        self.update_btn.setObjectName("edit_btn")
        self.delete_btn.setObjectName("delete_btn")
        self.clear_btn.setObjectName("clear_btn")
        self.close_btn.setObjectName("close_btn")
        self.search_btn.setObjectName("search_btn")
        self.reset_search_btn.setObjectName("reset_search_btn")

    def add_dossier(self):
        """Ajouter une nouvelle entrée de dossier"""
        patient_id = self.selected_patient_id
        date = self.date_edit.date().toString("yyyy-MM-dd")
        observations = self.observations_input.toPlainText().strip()
        traitement = self.traitement_input.toPlainText().strip()

        # Validation
        if not patient_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un patient valide!")
            self.patient_input.setFocus()
            return
        if not observations:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir des observations!")
            self.observations_input.setFocus()
            return

        try:
            DossierService.add(patient_id, observations, traitement, date)
            QMessageBox.information(self, "Succès", "Entrée de dossier ajoutée avec succès!")
            self.load_dossiers()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout: {e}")

    def load_dossiers(self, dossiers=None):
        """Charger les dossiers dans le tableau"""
        try:
            if dossiers is None:
                dossiers = DossierService.get_all()
            
            self.table.setRowCount(0)
            
            for index, dossier in enumerate(dossiers, start=1):
                row_pos = self.table.rowCount()
                self.table.insertRow(row_pos)
                
                # 1ère colonne : Numéro
                item_num = QTableWidgetItem(str(index))
                item_num.setTextAlignment(Qt.AlignCenter)
                item_num.setData(Qt.UserRole, dossier[0])  # ID dossier
                item_num.setData(Qt.UserRole + 1, dossier[1])  # ID patient
                self.table.setItem(row_pos, 0, item_num)
                
                # Autres colonnes
                self.table.setItem(row_pos, 1, QTableWidgetItem(dossier[5]))  # Patient
                
                # Formater la date
                date_str = QDate.fromString(dossier[4], "yyyy-MM-dd").toString("dd/MM/yyyy")
                self.table.setItem(row_pos, 2, QTableWidgetItem(date_str))  # Date
                
                # Observations (tronquer si trop long)
                obs = dossier[2] if dossier[2] else ""
                if len(obs) > 50:
                    obs = obs[:47] + "..."
                self.table.setItem(row_pos, 3, QTableWidgetItem(obs))
                
                # Traitement (tronquer si trop long)
                traitement = dossier[3] if dossier[3] else ""
                if len(traitement) > 50:
                    traitement = traitement[:47] + "..."
                self.table.setItem(row_pos, 4, QTableWidgetItem(traitement))
                
                # Rendre les cellules non éditables
                for col in range(5):
                    item = self.table.item(row_pos, col)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        except Exception as e:
            print(f"Erreur chargement dossiers: {e}")

    def on_search_changed(self, text):
        """Recherche en temps réel"""
        if text.strip():
            try:
                results = DossierService.search_patients(text.strip())
                # Convertir en format compatible avec load_dossiers
                formatted_results = []
                for patient in results:
                    # Récupérer les dossiers du patient
                    dossiers = DossierService.get_by_patient(patient[0])
                    formatted_results.extend(dossiers)
                self.load_dossiers(formatted_results)
            except Exception as e:
                print(f"Erreur recherche: {e}")

    def search_dossiers(self):
        """Recherche des dossiers"""
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Recherche", "Veuillez entrer un terme de recherche!")
            return
        
        try:
            results = DossierService.search_patients(keyword)
            if results:
                # Convertir en format compatible
                formatted_results = []
                for patient in results:
                    dossiers = DossierService.get_by_patient(patient[0])
                    formatted_results.extend(dossiers)
                
                if formatted_results:
                    self.load_dossiers(formatted_results)
                    QMessageBox.information(self, "Recherche", 
                                          f"{len(formatted_results)} entrée(s) trouvée(s) pour '{keyword}'")
                else:
                    self.table.setRowCount(0)
                    QMessageBox.information(self, "Recherche", 
                                          f"Aucun dossier trouvé pour '{keyword}'")
            else:
                self.table.setRowCount(0)
                QMessageBox.information(self, "Recherche", 
                                      f"Aucun dossier trouvé pour '{keyword}'")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche: {e}")

    def reset_search(self):
        """Réinitialiser la recherche"""
        self.search_input.clear()
        self.load_dossiers()

    def on_table_cell_clicked(self, row, col):
        """Lorsqu'on clique sur une ligne du tableau"""
        if row >= 0:
            # Activer les boutons modifier et supprimer
            self.update_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.add_btn.setEnabled(False)
            
            # Récupérer l'ID du dossier et du patient
            item_num = self.table.item(row, 0)
            self.current_dossier_id = item_num.data(Qt.UserRole)
            patient_id = item_num.data(Qt.UserRole + 1)
            
            # Récupérer les données complètes du dossier
            try:
                # Charger tous les dossiers pour trouver celui-ci
                dossiers = DossierService.get_all()
                for dossier in dossiers:
                    if dossier[0] == self.current_dossier_id:
                        # Remplir le formulaire
                        # Afficher le nom du patient dans le champ
                        patient_name = dossier[5]  # nom complet du patient
                        self.patient_input.setText(patient_name)
                        self.selected_patient_id = patient_id
                        
                        # Date
                        qdate = QDate.fromString(dossier[4], "yyyy-MM-dd")
                        self.date_edit.setDate(qdate)
                        
                        # Observations
                        self.observations_input.setText(dossier[2] if dossier[2] else "")
                        
                        # Traitement
                        self.traitement_input.setText(dossier[3] if dossier[3] else "")
                        break
            except Exception as e:
                print(f"Erreur chargement dossier: {e}")

    def update_dossier(self):
        """Mettre à jour une entrée de dossier"""
        if not self.current_dossier_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une entrée à modifier!")
            return

        patient_id = self.selected_patient_id
        date = self.date_edit.date().toString("yyyy-MM-dd")
        observations = self.observations_input.toPlainText().strip()
        traitement = self.traitement_input.toPlainText().strip()

        # Validation
        if not patient_id:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir un patient valide!")
            return
        if not observations:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir des observations!")
            return

        try:
            DossierService.update(self.current_dossier_id, observations, traitement)
            QMessageBox.information(self, "Succès", "Dossier modifié avec succès!")
            self.load_dossiers()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification: {e}")

    def delete_dossier(self):
        """Supprimer une entrée de dossier"""
        if not self.current_dossier_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une entrée à supprimer!")
            return

        # Récupérer les infos pour le message de confirmation
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            patient = self.table.item(selected_row, 1).text()
            date = self.table.item(selected_row, 2).text()

            # Confirmation
            reply = QMessageBox.question(
                self, "Confirmation",
                f"Voulez-vous vraiment supprimer l'entrée du dossier de {patient}\n"
                f"du {date} ?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                try:
                    DossierService.delete(self.current_dossier_id)
                    QMessageBox.information(self, "Succès", "Entrée de dossier supprimée avec succès!")
                    self.load_dossiers()
                    self.clear_form()
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {e}")

    def clear_form(self):
        """Effacer le formulaire"""
        self.patient_input.clear()
        self.selected_patient_id = None
        self.date_edit.setDate(QDate.currentDate())
        self.observations_input.clear()
        self.traitement_input.clear()
        self.current_dossier_id = None
        
        # Réactiver ajouter, désactiver modifier/supprimer
        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def close_window(self):
        """Fermer la fenêtre"""
        self.closed.emit()
        self.close()

    def closeEvent(self, event):
        """Gestion de la fermeture"""
        self.closed.emit()
        event.accept()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = DossierUI()
    window.show()
    sys.exit(app.exec())