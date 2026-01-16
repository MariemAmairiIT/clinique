# ui/medecin_ui.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from services.medecin_service import MedecinService


class MedecinUI(QWidget):
    # Signal pour notifier la fermeture
    closed = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Médecins - Clinique Médicale")
        self.setGeometry(100, 100, 1000, 600)
        self.selected_id = None
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Titre principal
        title = QLabel("Gestion des Médecins")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Groupe Formulaire
        form_group = QGroupBox("Informations du Médecin")
        form_group.setMinimumHeight(150)
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # Créer les champs d'entrée d'abord
        self.nom = QLineEdit()
        self.spec = QLineEdit()
        self.tel = QLineEdit()
        
        # Labels et champs
        labels = ["Nom complet :", "Spécialité :", "Téléphone :"]
        fields = [self.nom, self.spec, self.tel]

        for i, (label_text, field) in enumerate(zip(labels, fields)):
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 10))
            form_layout.addWidget(label, i, 0)
            form_layout.addWidget(field, i, 1)

        # Placeholders
        self.nom.setPlaceholderText("Ex: Dr. amine ")
        self.spec.setPlaceholderText("Ex: Cardiologue")
        self.tel.setPlaceholderText("Ex: +216 77 123 45 67")

        # Boutons formulaire
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.add_btn = QPushButton(" Ajouter")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_btn.setMinimumHeight(40)
        self.add_btn.clicked.connect(self.add)

        self.edit_btn = QPushButton(" Modifier")
        self.edit_btn.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_btn.setMinimumHeight(40)
        self.edit_btn.clicked.connect(self.update)

        self.delete_btn = QPushButton(" Supprimer")
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.clicked.connect(self.delete)

        self.clear_btn = QPushButton(" Annuler")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self.clear_form)

        # BOUTON FERMER AJOUTÉ ICI
        self.close_btn = QPushButton(" Fermer")
        self.close_btn.setIcon(QIcon.fromTheme("window-close"))
        self.close_btn.setMinimumHeight(40)
        self.close_btn.clicked.connect(self.close_window)

        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.clear_btn, self.close_btn]:
            btn.setCursor(Qt.PointingHandCursor)
            btn_layout.addWidget(btn)

        form_layout.addLayout(btn_layout, 3, 0, 1, 2)
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        # Barre de recherche
        search_group = QGroupBox("Rechercher un Médecin")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom, spécialité ou téléphone...")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.on_search_changed)
        
        self.search_btn = QPushButton(" Rechercher")
        self.search_btn.setIcon(QIcon.fromTheme("system-search"))
        self.search_btn.setMinimumHeight(40)
        self.search_btn.clicked.connect(self.search)
        
        self.reset_search_btn = QPushButton(" Réinitialiser")
        self.reset_search_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.reset_search_btn.setMinimumHeight(40)
        self.reset_search_btn.clicked.connect(self.reset_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.reset_search_btn)
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)

        # Table des médecins
        table_group = QGroupBox("Liste des Médecins")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["N°", "Nom complet", "Spécialité", "Téléphone"])  # Changé "ID" par "N°"
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.on_table_select)

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group, stretch=1)

        self.load_medecins()

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
        QLineEdit {
            padding: 10px;
            border: 2px solid #cbd5e0;
            border-radius: 8px;
            font-size: 14px;
            background-color: white;
        }
        QLineEdit:focus {
            border-color: #4299e1;
            background-color: #f0f8ff;
        }
        QPushButton {
            padding: 10px 20px;
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
        #close_btn {
            background-color: #718096;
            color: white;
        }
        #close_btn:hover {
            background-color: #4a5568;
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
        self.edit_btn.setObjectName("edit_btn")
        self.delete_btn.setObjectName("delete_btn")
        self.clear_btn.setObjectName("clear_btn")
        self.search_btn.setObjectName("search_btn")
        self.reset_search_btn.setObjectName("reset_search_btn")
        self.close_btn.setObjectName("close_btn")

    def load_medecins(self):
        self.table.setRowCount(0)
        medecins = MedecinService.get_all()
        self.display_medecins(medecins)

    def display_medecins(self, medecins):
        """Affiche la liste des médecins dans le tableau avec numérotation séquentielle"""
        self.table.setRowCount(0)
        
        # Stocker les médecins avec leurs vrais IDs pour référence
        self.medecin_data = []
        
        for index, med in enumerate(medecins, start=1):
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            
            # Stocker les données du médecin
            self.medecin_data.append({
                'row': row_pos,
                'id_medecin': med[0],  # ID réel dans la base de données
                'nom': med[1],
                'specialite': med[2],
                'telephone': med[3]
            })
            
            # 1ère colonne : Numéro séquentiel (1, 2, 3, 4...)
            item_num = QTableWidgetItem(str(index))
            item_num.setTextAlignment(Qt.AlignCenter)
            item_num.setData(Qt.UserRole, med[0])  # Stocker l'ID réel dans les données
            self.table.setItem(row_pos, 0, item_num)
            
            # 2ème colonne : Nom
            item_nom = QTableWidgetItem(str(med[1]))
            item_nom.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_pos, 1, item_nom)
            
            # 3ème colonne : Spécialité
            item_spec = QTableWidgetItem(str(med[2]))
            item_spec.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_pos, 2, item_spec)
            
            # 4ème colonne : Téléphone
            item_tel = QTableWidgetItem(str(med[3] if med[3] else ""))
            item_tel.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_pos, 3, item_tel)

    def add(self):
        if not self.nom.text().strip() or not self.spec.text().strip():
            QMessageBox.warning(self, "Champs requis", "Le nom et la spécialité sont obligatoires.")
            return
        MedecinService.add(self.nom.text().strip(), self.spec.text().strip(), self.tel.text().strip())
        self.load_medecins()
        self.clear_form()
        QMessageBox.information(self, "Succès", "Médecin ajouté avec succès.")

    def update(self):
        if not self.selected_id:
            QMessageBox.information(self, "Sélection", "Veuillez sélectionner un médecin à modifier.")
            return
        MedecinService.update(self.selected_id, self.nom.text().strip(), self.spec.text().strip(), self.tel.text().strip())
        self.load_medecins()
        self.clear_form()
        QMessageBox.information(self, "Succès", "Médecin modifié avec succès.")

    def delete(self):
        if not self.selected_id:
            QMessageBox.information(self, "Sélection", "Veuillez sélectionner un médecin à supprimer.")
            return
        
        # Trouver le numéro affiché du médecin
        selected_row = -1
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0).data(Qt.UserRole) == self.selected_id:
                selected_row = i
                break
        
        nom_medecin = self.table.item(selected_row, 1).text() if selected_row >= 0 else "ce médecin"
        
        reply = QMessageBox.question(
            self, 
            "Confirmation", 
            f"Êtes-vous sûr de vouloir supprimer {nom_medecin} ?\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            MedecinService.delete(self.selected_id)
            self.load_medecins()
            self.clear_form()
            QMessageBox.information(self, "Succès", "Médecin supprimé. Les numéros ont été réorganisés.")

    def on_table_select(self, row, column):
        # Récupérer l'ID réel depuis les données de la première colonne
        self.selected_id = self.table.item(row, 0).data(Qt.UserRole)
        self.nom.setText(self.table.item(row, 1).text())
        self.spec.setText(self.table.item(row, 2).text())
        self.tel.setText(self.table.item(row, 3).text())

    def clear_form(self):
        self.selected_id = None
        self.nom.clear()
        self.spec.clear()
        self.tel.clear()

    def search(self):
        """Effectue une recherche de médecins"""
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Recherche", "Veuillez entrer un terme de recherche.")
            return
        
        try:
            results = MedecinService.search(keyword)
            if results:
                self.display_medecins(results)
                self.search_input.setStyleSheet("border: 2px solid #48bb78;")
            else:
                self.table.setRowCount(0)
                QMessageBox.information(self, "Recherche", f"Aucun médecin trouvé pour '{keyword}'.")
                self.search_input.setStyleSheet("border: 2px solid #f56565;")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche: {str(e)}")

    def on_search_changed(self, text):
        """Recherche en temps réel (optionnel)"""
        if text.strip():
            try:
                results = MedecinService.search(text.strip())
                self.display_medecins(results)
                # Mettre en surbrillance les résultats
                if results:
                    self.search_input.setStyleSheet("border: 2px solid #48bb78;")
                else:
                    self.search_input.setStyleSheet("border: 2px solid #f56565;")
            except Exception as e:
                print(f"Erreur recherche temps réel: {e}")

    def reset_search(self):
        """Réinitialise la recherche et affiche tous les médecins"""
        self.search_input.clear()
        self.search_input.setStyleSheet("")  # Retirer le style de bordure
        self.load_medecins()

    def close_window(self):
        """Ferme la fenêtre et émet le signal"""
        self.closed.emit()  # Émet le signal avant de fermer
        self.close()

    def closeEvent(self, event):
        """Surcharge de la méthode de fermeture pour émettre le signal"""
        self.closed.emit()
        event.accept()