import sys
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QGroupBox, QGridLayout, QDateEdit, QTimeEdit, QComboBox,
    QCompleter  # ⭐ Ajouter QCompleter
)
from PySide6.QtCore import QDate, QTime, Qt, Signal, QStringListModel
from PySide6.QtGui import QFont, QIcon
from services.rendezvous_service import RendezVousService

class RendezVousUI(QWidget):
    # Signal pour notifier la fermeture
    closed = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Rendez-vous - Clinique Médicale")
        self.setGeometry(100, 100, 1200, 700)
        self.current_rdv_id = None
        self.selected_patient_id = None
        self.selected_medecin_id = None
        self.patients_dict = {}  # {nom_complet: id_patient}
        self.medecins_dict = {}  # {nom_complet: id_medecin}
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Titre principal
        title = QLabel("Gestion des Rendez-vous")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Groupe Formulaire
        form_group = QGroupBox("Nouveau Rendez-vous")
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # ⭐⭐ CHAMP PATIENT AVEC AUTO-COMPLÉTION ⭐⭐
        self.patient_input = QLineEdit()
        self.patient_input.setPlaceholderText("Écrivez le nom du patient...")
        self.patient_input.setMinimumHeight(40)
        
        # Créer un completer pour le patient
        self.patient_completer = QCompleter()
        self.patient_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.patient_completer.setFilterMode(Qt.MatchContains)
        self.patient_input.setCompleter(self.patient_completer)
        
        # ⭐⭐ CHAMP MÉDECIN AVEC AUTO-COMPLÉTION ⭐⭐
        self.medecin_input = QLineEdit()
        self.medecin_input.setPlaceholderText("Écrivez le nom du médecin...")
        self.medecin_input.setMinimumHeight(40)
        
        # Créer un completer pour le médecin
        self.medecin_completer = QCompleter()
        self.medecin_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.medecin_completer.setFilterMode(Qt.MatchContains)
        self.medecin_input.setCompleter(self.medecin_completer)

        # Date et heure
        self.date_edit = QDateEdit()
        self.time_edit = QTimeEdit()
        self.motif_input = QLineEdit()
        
        # Configuration des widgets
        self.load_patients()  # Charger les données pour auto-complétion
        self.load_medecins()  # Charger les données pour auto-complétion
        
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")
        
        self.motif_input.setPlaceholderText("Ex: Consultation générale")
        
        # Connecter les signaux
        self.patient_input.textChanged.connect(self.on_patient_text_changed)
        self.medecin_input.textChanged.connect(self.on_medecin_text_changed)
        
        # Labels et champs
        labels = ["Patient :", "Médecin :", "Date :", "Heure :", "Motif :"]
        fields = [self.patient_input, self.medecin_input, self.date_edit, self.time_edit, self.motif_input]

        for i, (label_text, field) in enumerate(zip(labels, fields)):
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 10))
            form_layout.addWidget(label, i, 0)
            form_layout.addWidget(field, i, 1)

        # Boutons formulaire
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.add_btn = QPushButton(" Prendre Rendez-vous")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_btn.setMinimumHeight(40)
        self.add_btn.clicked.connect(self.add_rendezvous)

        self.update_btn = QPushButton(" Modifier")
        self.update_btn.setIcon(QIcon.fromTheme("document-edit"))
        self.update_btn.setMinimumHeight(40)
        self.update_btn.clicked.connect(self.update_rendezvous)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton(" Supprimer")
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.clicked.connect(self.delete_rendezvous)
        self.delete_btn.setEnabled(False)

        self.clear_btn = QPushButton(" Annuler")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self.clear_form)

        # BOUTON FERMER
        self.close_btn = QPushButton(" Fermer")
        self.close_btn.setIcon(QIcon.fromTheme("window-close"))
        self.close_btn.setMinimumHeight(40)
        self.close_btn.clicked.connect(self.close_window)

        for btn in [self.add_btn, self.update_btn, self.delete_btn, self.clear_btn, self.close_btn]:
            btn.setCursor(Qt.PointingHandCursor)
            btn_layout.addWidget(btn)

        form_layout.addLayout(btn_layout, 5, 0, 1, 2)
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        # ===== BARRE DE RECHERCHE =====
        search_group = QGroupBox("Rechercher des Rendez-vous")
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        # Type de recherche
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["Recherche par patient", "Recherche par date", "Recherche avancée"])
        self.search_type_combo.setMinimumHeight(40)
        self.search_type_combo.currentIndexChanged.connect(self.on_search_type_changed)
        
        # Champ de recherche par patient
        self.search_patient_input = QLineEdit()
        self.search_patient_input.setPlaceholderText("Entrez le nom du patient")
        self.search_patient_input.setMinimumHeight(40)
        
        # Champ de recherche par date
        self.search_date_input = QDateEdit()
        self.search_date_input.setDate(QDate.currentDate())
        self.search_date_input.setCalendarPopup(True)
        self.search_date_input.setDisplayFormat("dd/MM/yyyy")
        self.search_date_input.setMinimumHeight(40)
        self.search_date_input.setVisible(False)
        
        # Champ de recherche avancée
        self.search_advanced_input = QLineEdit()
        self.search_advanced_input.setPlaceholderText("Rechercher dans motif, médecin, patient...")
        self.search_advanced_input.setMinimumHeight(40)
        self.search_advanced_input.setVisible(False)
        
        # Bouton Rechercher
        self.search_btn = QPushButton("🔍 Rechercher")
        self.search_btn.setMinimumHeight(40)
        self.search_btn.clicked.connect(self.search_rendezvous)
        
        # Bouton Réinitialiser
        self.reset_search_btn = QPushButton("🔄 Tout Afficher")
        self.reset_search_btn.setMinimumHeight(40)
        self.reset_search_btn.clicked.connect(self.reset_search)
        
        search_layout.addWidget(QLabel("Type :"))
        search_layout.addWidget(self.search_type_combo)
        search_layout.addWidget(self.search_patient_input)
        search_layout.addWidget(self.search_date_input)
        search_layout.addWidget(self.search_advanced_input)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.reset_search_btn)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)

        # Table des rendez-vous
        table_group = QGroupBox("Liste des Rendez-vous")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["N°", "Patient", "Médecin", "Date", "Heure", "Motif"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.on_table_cell_clicked)

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group, stretch=1)

        self.load_rendezvous()

    def load_patients(self):
        """Charger la liste des patients pour l'auto-complétion"""
        try:
            patients = RendezVousService.get_patients()
            patient_names = []
            self.patients_dict = {}
            
            for patient in patients:
                patient_id = patient[0]
                nom_complet = f"{patient[1]} {patient[2]}"  # nom + prénom
                patient_names.append(nom_complet)
                self.patients_dict[nom_complet] = patient_id
            
            # Configurer le completer avec la liste des noms
            model = QStringListModel(patient_names)
            self.patient_completer.setModel(model)
            
        except Exception as e:
            print(f"Erreur chargement patients: {e}")

    def load_medecins(self):
        """Charger la liste des médecins pour l'auto-complétion"""
        try:
            medecins = RendezVousService.get_medecins()
            medecin_names = []
            self.medecins_dict = {}
            
            for med in medecins:
                medecin_id = med[0]
                nom_complet = f"Dr. {med[1]} ({med[2]})"  # Dr. nom (spécialité)
                medecin_names.append(nom_complet)
                self.medecins_dict[nom_complet] = medecin_id
            
            # Configurer le completer avec la liste des noms
            model = QStringListModel(medecin_names)
            self.medecin_completer.setModel(model)
            
        except Exception as e:
            print(f"Erreur chargement médecins: {e}")

    def on_patient_text_changed(self, text):
        """Quand on écrit dans le champ patient"""
        # Chercher l'ID du patient correspondant au nom
        if text in self.patients_dict:
            self.selected_patient_id = self.patients_dict[text]
        else:
            self.selected_patient_id = None

    def on_medecin_text_changed(self, text):
        """Quand on écrit dans le champ médecin"""
        # Chercher l'ID du médecin correspondant au nom
        if text in self.medecins_dict:
            self.selected_medecin_id = self.medecins_dict[text]
        else:
            self.selected_medecin_id = None

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
        QLineEdit, QComboBox, QDateEdit, QTimeEdit {
            padding: 8px;
            border: 2px solid #cbd5e0;
            border-radius: 8px;
            font-size: 14px;
            background-color: white;
        }
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {
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

    def add_rendezvous(self):
        """Ajouter un nouveau rendez-vous"""
        patient_id = self.selected_patient_id
        medecin_id = self.selected_medecin_id
        date = self.date_edit.date().toString("yyyy-MM-dd")
        heure = self.time_edit.time().toString("HH:mm")
        motif = self.motif_input.text().strip()

        # Validation
        if not patient_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un patient valide!")
            self.patient_input.setFocus()
            return
        if not medecin_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un médecin valide!")
            self.medecin_input.setFocus()
            return
        if not motif:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir le motif!")
            self.motif_input.setFocus()
            return

        try:
            # Vérifier si le médecin est disponible
            if not RendezVousService.is_medecin_available(medecin_id, date, heure):
                QMessageBox.warning(self, "Erreur", "Le médecin a déjà un rendez-vous à cette heure!")
                return

            # Ajouter le rendez-vous
            RendezVousService.add(patient_id, medecin_id, date, heure, motif)
            
            QMessageBox.information(self, "Succès", "Rendez-vous enregistré avec succès!")
            self.load_rendezvous()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement: {e}")

    def load_rendezvous(self, rendezvous=None):
        """Charger les rendez-vous dans le tableau"""
        try:
            if rendezvous is None:
                rendezvous = RendezVousService.get_all()
            
            self.table.setRowCount(0)
            
            for index, rdv in enumerate(rendezvous, start=1):
                row_pos = self.table.rowCount()
                self.table.insertRow(row_pos)
                
                # Formater la date pour l'affichage
                date_str = QDate.fromString(rdv[3], "yyyy-MM-dd").toString("dd/MM/yyyy")
                
                # 1ère colonne : Numéro séquentiel (1, 2, 3, 4...)
                item_num = QTableWidgetItem(str(index))
                item_num.setTextAlignment(Qt.AlignCenter)
                item_num.setData(Qt.UserRole, rdv[0])  # Stocker l'ID réel du rendez-vous
                item_num.setData(Qt.UserRole + 1, rdv[1])  # id_patient
                item_num.setData(Qt.UserRole + 2, rdv[2])  # id_medecin
                self.table.setItem(row_pos, 0, item_num)
                
                # Autres colonnes
                self.table.setItem(row_pos, 1, QTableWidgetItem(rdv[6]))  # Patient
                self.table.setItem(row_pos, 2, QTableWidgetItem(f"Dr. {rdv[7]}"))  # Médecin
                self.table.setItem(row_pos, 3, QTableWidgetItem(date_str))  # Date
                self.table.setItem(row_pos, 4, QTableWidgetItem(rdv[4]))  # Heure
                self.table.setItem(row_pos, 5, QTableWidgetItem(rdv[5]))  # Motif
                
                # Rendre les cellules non éditables
                for col in range(6):
                    item = self.table.item(row_pos, col)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        except Exception as e:
            print(f"Erreur chargement rendez-vous: {e}")

    def on_search_type_changed(self, index):
        """Changer le type de champ de recherche"""
        # Masquer tous les champs d'abord
        self.search_patient_input.setVisible(False)
        self.search_date_input.setVisible(False)
        self.search_advanced_input.setVisible(False)
        
        if index == 0:  # Recherche par patient
            self.search_patient_input.setVisible(True)
            self.search_patient_input.setPlaceholderText("Entrez le nom du patient")
        elif index == 1:  # Recherche par date
            self.search_date_input.setVisible(True)
            self.search_date_input.setDate(QDate.currentDate())
        else:  # Recherche avancée
            self.search_advanced_input.setVisible(True)
            self.search_advanced_input.setPlaceholderText("Rechercher dans motif, médecin, patient...")

    def search_rendezvous(self):
        """Rechercher des rendez-vous"""
        search_type = self.search_type_combo.currentIndex()
        
        if search_type == 0:  # Recherche par patient
            keyword = self.search_patient_input.text().strip()
            if not keyword:
                QMessageBox.warning(self, "Recherche", "Veuillez entrer un nom de patient à rechercher!")
                return
            
            try:
                results = RendezVousService.search_by_name(keyword)
                self.display_search_results(results, keyword, "patient")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche: {e}")
                
        elif search_type == 1:  # Recherche par date
            search_date = self.search_date_input.date().toString("yyyy-MM-dd")
            
            try:
                results = RendezVousService.search_by_date(search_date)
                date_fr = self.search_date_input.date().toString("dd/MM/yyyy")
                self.display_search_results(results, date_fr, "date")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche: {e}")
                
        else:  # Recherche avancée
            keyword = self.search_advanced_input.text().strip()
            if not keyword:
                QMessageBox.warning(self, "Recherche", "Veuillez entrer un terme de recherche!")
                return
            
            try:
                results = RendezVousService.search_all(keyword)
                self.display_search_results(results, keyword, "tous les champs")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche: {e}")

    def display_search_results(self, results, search_term, search_type):
        """Afficher les résultats de recherche"""
        if results:
            self.load_rendezvous(results)
            QMessageBox.information(self, "Recherche", 
                                  f"{len(results)} rendez-vous trouvé(s) pour '{search_term}' ({search_type})")
        else:
            self.table.setRowCount(0)
            QMessageBox.information(self, "Recherche", 
                                  f"Aucun rendez-vous trouvé pour '{search_term}' ({search_type})")

    def reset_search(self):
        """Réinitialiser la recherche et afficher tous les rendez-vous"""
        self.search_patient_input.clear()
        self.search_advanced_input.clear()
        self.search_date_input.setDate(QDate.currentDate())
        self.load_rendezvous()
        QMessageBox.information(self, "Réinitialisation", "Affichage de tous les rendez-vous")

    def on_table_cell_clicked(self, row, col):
        """Lorsqu'on clique sur une ligne du tableau"""
        if row >= 0:
            # Activer les boutons modifier et supprimer
            self.update_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.add_btn.setEnabled(False)  # Désactiver le bouton ajouter
            
            # Récupérer l'ID du rendez-vous depuis les données de la première colonne
            item_num = self.table.item(row, 0)
            self.current_rdv_id = item_num.data(Qt.UserRole)
            
            # Récupérer les IDs patient et médecin
            patient_id = item_num.data(Qt.UserRole + 1)
            medecin_id = item_num.data(Qt.UserRole + 2)
            
            # Récupérer les autres données
            patient_name = self.table.item(row, 1).text()
            medecin_name = self.table.item(row, 2).text()
            date_str = self.table.item(row, 3).text()
            heure_str = self.table.item(row, 4).text()
            motif = self.table.item(row, 5).text()

            # Remplir le formulaire
            # Afficher le nom du patient
            self.patient_input.setText(patient_name)
            self.selected_patient_id = patient_id
            
            # Afficher le nom du médecin
            self.medecin_input.setText(medecin_name)
            self.selected_medecin_id = medecin_id

            # Date et heure
            qdate = QDate.fromString(date_str, "dd/MM/yyyy")
            qtime = QTime.fromString(heure_str, "HH:mm")
            self.date_edit.setDate(qdate)
            self.time_edit.setTime(qtime)
            self.motif_input.setText(motif)

    def update_rendezvous(self):
        """Mettre à jour un rendez-vous"""
        if not self.current_rdv_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un rendez-vous à modifier!")
            return

        patient_id = self.selected_patient_id
        medecin_id = self.selected_medecin_id
        date = self.date_edit.date().toString("yyyy-MM-dd")
        heure = self.time_edit.time().toString("HH:mm")
        motif = self.motif_input.text().strip()

        # Validation
        if not patient_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un patient valide!")
            return
        if not medecin_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un médecin valide!")
            return
        if not motif:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir le motif!")
            return

        try:
            # Vérifier la disponibilité (exclure le rendez-vous actuel)
            if not RendezVousService.is_medecin_available(medecin_id, date, heure, self.current_rdv_id):
                QMessageBox.warning(self, "Erreur", "Le médecin a déjà un rendez-vous à cette heure!")
                return

            # Confirmation
            reply = QMessageBox.question(
                self, "Confirmation",
                "Voulez-vous vraiment modifier ce rendez-vous?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Mettre à jour
                RendezVousService.update(self.current_rdv_id, patient_id, medecin_id, date, heure, motif)
                
                QMessageBox.information(self, "Succès", "Rendez-vous modifié avec succès!")
                self.load_rendezvous()
                self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification: {e}")

    def delete_rendezvous(self):
        """Supprimer un rendez-vous"""
        if not self.current_rdv_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un rendez-vous à supprimer!")
            return

        # Récupérer les infos du rendez-vous pour le message de confirmation
        selected_row = -1
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0).data(Qt.UserRole) == self.current_rdv_id:
                selected_row = i
                break
        
        if selected_row >= 0:
            patient = self.table.item(selected_row, 1).text()
            date = self.table.item(selected_row, 3).text()
            heure = self.table.item(selected_row, 4).text()

            # Confirmation
            reply = QMessageBox.question(
                self, "Confirmation",
                f"Voulez-vous vraiment supprimer le rendez-vous de {patient}\n"
                f"le {date} à {heure} ?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                try:
                    RendezVousService.delete(self.current_rdv_id)
                    QMessageBox.information(self, "Succès", "Rendez-vous supprimé avec succès!")
                    self.load_rendezvous()
                    self.clear_form()
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {e}")

    def clear_form(self):
        """Effacer le formulaire et réinitialiser les boutons"""
        self.patient_input.clear()
        self.medecin_input.clear()
        self.selected_patient_id = None
        self.selected_medecin_id = None
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        self.motif_input.clear()
        self.current_rdv_id = None
        
        # Réactiver ajouter, désactiver modifier/supprimer
        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def close_window(self):
        """Ferme la fenêtre et émet le signal"""
        self.closed.emit()
        self.close()

    def closeEvent(self, event):
        """Surcharge de la méthode de fermeture pour émettre le signal"""
        self.closed.emit()
        event.accept()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = RendezVousUI()
    window.show()
    sys.exit(app.exec())