import sys
import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QGroupBox, QGridLayout, QTabWidget, QDateEdit, QComboBox,
    QFrame, QScrollArea, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QPainter, QColor
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QBarSeries, QBarSet, QBarCategoryAxis
from services.report_service import ReportService
from datetime import datetime, timedelta

class ReportsUI(QWidget):
    # Signal pour notifier la fermeture
    closed = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rapports Statistiques - Clinique Médicale")
        self.setGeometry(100, 100, 1200, 800)
        self.stats = None
        self.selected_date = None
        self.selected_medecin_id = None
        self.filtered_rdv_list = []
        self.init_ui()
        self.apply_styles()
        self.load_statistics()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Titre principal
        title = QLabel("📊 Rapports Statistiques de la Clinique")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Créer un système d'onglets
        self.tab_widget = QTabWidget()
        
        # Onglet 1: Vue d'ensemble avec graphiques
        overview_tab = QWidget()
        self.setup_overview_tab(overview_tab)
        self.tab_widget.addTab(overview_tab, "📈 Vue d'ensemble")
        
        # Onglet 2: Tableaux détaillés
        tables_tab = QWidget()
        self.setup_tables_tab(tables_tab)
        self.tab_widget.addTab(tables_tab, "📋 Détails")
        
        # Onglet 3: Graphiques avancés
        charts_tab = QWidget()
        self.setup_charts_tab(charts_tab)
        self.tab_widget.addTab(charts_tab, "📊 Graphiques")
        
        main_layout.addWidget(self.tab_widget)

        # Boutons d'action en bas
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # Bouton Actualiser
        self.refresh_btn = QPushButton("🔄 Actualiser les statistiques")
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.clicked.connect(self.load_statistics)
        
        # Bouton Nettoyer BD
        self.clean_btn = QPushButton("🧹 Nettoyer données")
        self.clean_btn.setMinimumHeight(40)
        self.clean_btn.clicked.connect(self.nettoyer_donnees)
        
        # Bouton Export PDF
        self.pdf_btn = QPushButton("📄 Exporter en PDF")
        self.pdf_btn.setMinimumHeight(40)
        self.pdf_btn.clicked.connect(self.export_pdf)
        
        # Bouton Export Excel
        self.excel_btn = QPushButton("📊 Exporter en Excel")
        self.excel_btn.setMinimumHeight(40)
        self.excel_btn.clicked.connect(self.export_excel)
        
        # Bouton Fermer
        self.close_btn = QPushButton("✖ Fermer")
        self.close_btn.setMinimumHeight(40)
        self.close_btn.clicked.connect(self.close_window)
        
        # Ajouter les boutons
        for btn in [self.refresh_btn, self.clean_btn, self.pdf_btn, self.excel_btn, self.close_btn]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumWidth(180)
            buttons_layout.addWidget(btn)
        
        main_layout.addLayout(buttons_layout)

    def setup_overview_tab(self, tab):
        """Configure l'onglet Vue d'ensemble avec graphiques et filtres"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Statistiques principales
        stats_group = QGroupBox("Statistiques Globales")
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        self.patients_label = QLabel("Patients: Chargement...")
        self.medecins_label = QLabel("Médecins: Chargement...")
        self.rdv_label = QLabel("Rendez-vous: Chargement...")
        self.prochains_rdv_label = QLabel("Prochains RDV: Chargement...")
        
        for label in [self.patients_label, self.medecins_label, self.rdv_label, self.prochains_rdv_label]:
            label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            label.setStyleSheet("color: #2c3e50; padding: 10px; background-color: #f0f9ff; border-radius: 8px;")
        
        stats_layout.addWidget(self.patients_label, 0, 0)
        stats_layout.addWidget(self.medecins_label, 0, 1)
        stats_layout.addWidget(self.rdv_label, 1, 0)
        stats_layout.addWidget(self.prochains_rdv_label, 1, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Section de filtrage par date et médecin
        filter_group = QGroupBox("🔍 Filtrer les rendez-vous par date et médecin")
        filter_layout = QGridLayout()
        
        # Date selection
        date_label = QLabel("Date :")
        date_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("dd/MM/yyyy")
        self.date_picker.setMinimumHeight(35)
        self.date_picker.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 2px solid #cbd5e0;
                border-radius: 8px;
                font-size: 14px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: #cbd5e0;
                border-left-style: solid;
            }
        """)
        
        # Médecin selection
        medecin_label = QLabel("Médecin :")
        medecin_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        self.medecin_combo = QComboBox()
        self.medecin_combo.setMinimumHeight(35)
        self.medecin_combo.addItem("Tous les médecins", None)
        self.medecin_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #cbd5e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #4a5568;
            }
        """)
        
        # Bouton de recherche
        self.search_btn = QPushButton("🔎 Chercher les RDV")
        self.search_btn.setMinimumHeight(35)
        self.search_btn.clicked.connect(self.search_rdv_by_filter)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4299e1;
                color: white;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #3182ce;
            }
        """)
        
        # Bouton réinitialiser
        self.reset_filter_btn = QPushButton("🔄 Réinitialiser")
        self.reset_filter_btn.setMinimumHeight(35)
        self.reset_filter_btn.clicked.connect(self.reset_filter)
        self.reset_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #a0aec0;
                color: white;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #90a0b8;
            }
        """)
        
        # Label pour afficher le nombre de résultats
        self.results_count_label = QLabel("0 résultats")
        self.results_count_label.setAlignment(Qt.AlignCenter)
        self.results_count_label.setMinimumWidth(120)
        self.results_count_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #2c5282;
                background-color: #bee3f8;
                padding: 5px 15px;
                border-radius: 10px;
                border: 1px solid #4299e1;
            }
        """)
        self.results_count_label.setVisible(False)
        
        filter_layout.addWidget(date_label, 0, 0)
        filter_layout.addWidget(self.date_picker, 0, 1)
        filter_layout.addWidget(medecin_label, 0, 2)
        filter_layout.addWidget(self.medecin_combo, 0, 3)
        filter_layout.addWidget(self.search_btn, 0, 4)
        filter_layout.addWidget(self.reset_filter_btn, 0, 5)
        filter_layout.addWidget(self.results_count_label, 0, 6)
        
        # Boutons d'export pour les résultats filtrés
        self.export_excel_filter_btn = QPushButton("💾 Excel (résultats)")
        self.export_excel_filter_btn.setMinimumHeight(35)
        self.export_excel_filter_btn.clicked.connect(self.export_filtered_excel)
        self.export_excel_filter_btn.setToolTip("Exporter les résultats actuels en Excel")
        self.export_excel_filter_btn.setEnabled(False)
        
        self.export_pdf_filter_btn = QPushButton("📄 PDF (résultats)")
        self.export_pdf_filter_btn.setMinimumHeight(35)
        self.export_pdf_filter_btn.clicked.connect(self.export_filtered_pdf)
        self.export_pdf_filter_btn.setToolTip("Exporter les résultats actuels en PDF")
        self.export_pdf_filter_btn.setEnabled(False)
        
        # Styles pour les boutons d'export
        btn_style = """
            QPushButton {
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:enabled {
                background-color: #48bb78;
                color: white;
            }
            QPushButton:enabled:hover {
                background-color: #38a169;
            }
            QPushButton:disabled {
                background-color: #cbd5e0;
                color: #a0aec0;
            }
        """
        
        self.export_excel_filter_btn.setStyleSheet(btn_style)
        self.export_pdf_filter_btn.setStyleSheet(btn_style)
        
        filter_layout.addWidget(self.export_excel_filter_btn, 1, 0, 1, 2)
        filter_layout.addWidget(self.export_pdf_filter_btn, 1, 2, 1, 2)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Résultats de la recherche
        self.results_group = QGroupBox("📋 Rendez-vous trouvés")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Date", "Heure", "Patient", "Médecin", "Motif"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setMaximumHeight(200)
        
        results_layout.addWidget(self.results_table)
        self.results_group.setLayout(results_layout)
        self.results_group.setVisible(False)  # Caché par défaut
        layout.addWidget(self.results_group)
        
        # Graphiques
        charts_layout = QHBoxLayout()
        
        # Graphique 1: Évolution des rendez-vous
        self.chart1_group = QGroupBox("📈 Évolution des rendez-vous (6 derniers mois)")
        chart1_layout = QVBoxLayout()
        self.chart_view1 = QChartView()
        self.chart_view1.setRenderHint(QPainter.Antialiasing)
        self.chart_view1.setMinimumHeight(300)
        chart1_layout.addWidget(self.chart_view1)
        self.chart1_group.setLayout(chart1_layout)
        
        # Graphique 2: Répartition par spécialité
        self.chart2_group = QGroupBox("📊 Répartition par spécialité")
        chart2_layout = QVBoxLayout()
        self.chart_view2 = QChartView()
        self.chart_view2.setRenderHint(QPainter.Antialiasing)
        self.chart_view2.setMinimumHeight(300)
        chart2_layout.addWidget(self.chart_view2)
        self.chart2_group.setLayout(chart2_layout)
        
        charts_layout.addWidget(self.chart1_group)
        charts_layout.addWidget(self.chart2_group)
        
        layout.addLayout(charts_layout)

    def setup_tables_tab(self, tab):
        """Configure l'onglet avec les tableaux détaillés"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Table des spécialités
        specialites_group = QGroupBox("Spécialités les plus demandées")
        specialites_layout = QVBoxLayout()
        
        self.specialites_table = QTableWidget()
        self.specialites_table.setColumnCount(3)
        self.specialites_table.setHorizontalHeaderLabels(["Rang", "Spécialité", "Nombre de RDV"])
        self.specialites_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.specialites_table.setMaximumHeight(200)
        
        specialites_layout.addWidget(self.specialites_table)
        specialites_group.setLayout(specialites_layout)
        layout.addWidget(specialites_group)
        
        # Table des derniers rendez-vous
        rdv_group = QGroupBox("Derniers rendez-vous")
        rdv_layout = QVBoxLayout()
        
        self.rdv_table = QTableWidget()
        self.rdv_table.setColumnCount(5)
        self.rdv_table.setHorizontalHeaderLabels(["Patient", "Médecin", "Date", "Heure", "Motif"])
        self.rdv_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        rdv_layout.addWidget(self.rdv_table)
        rdv_group.setLayout(rdv_layout)
        layout.addWidget(rdv_group)

    def setup_charts_tab(self, tab):
        """Configure l'onglet avec graphiques avancés"""
        layout = QVBoxLayout(tab)
        
        # Graphique des tendances
        trends_group = QGroupBox("📈 Tendances hebdomadaires")
        trends_layout = QVBoxLayout()
        self.trends_chart_view = QChartView()
        self.trends_chart_view.setRenderHint(QPainter.Antialiasing)
        self.trends_chart_view.setMinimumHeight(350)
        trends_layout.addWidget(self.trends_chart_view)
        trends_group.setLayout(trends_layout)
        layout.addWidget(trends_group)
        
        # Graphique comparatif
        compare_group = QGroupBox("📊 Comparatif médecins")
        compare_layout = QVBoxLayout()
        self.compare_chart_view = QChartView()
        self.compare_chart_view.setRenderHint(QPainter.Antialiasing)
        self.compare_chart_view.setMinimumHeight(350)
        compare_layout.addWidget(self.compare_chart_view)
        compare_group.setLayout(compare_layout)
        layout.addWidget(compare_group)

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
        QPushButton {
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            border: none;
        }
        QPushButton:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        QTabWidget::pane {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #e2e8f0;
            padding: 10px 20px;
            margin-right: 2px;
            border-radius: 8px 8px 0 0;
        }
        QTabBar::tab:selected {
            background-color: #4299e1;
            color: white;
        }
        QTabBar::tab:hover:!selected {
            background-color: #cbd5e0;
        }
        #refresh_btn {
            background-color: #4299e1;
            color: white;
        }
        #refresh_btn:hover {
            background-color: #3182ce;
        }
        #clean_btn {
            background-color: #ed8936;
            color: white;
        }
        #clean_btn:hover {
            background-color: #dd6b20;
        }
        #pdf_btn {
            background-color: #f56565;
            color: white;
        }
        #pdf_btn:hover {
            background-color: #e53e3e;
        }
        #excel_btn {
            background-color: #48bb78;
            color: white;
        }
        #excel_btn:hover {
            background-color: #38a169;
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
        """
        self.setStyleSheet(stylesheet)
        
        # Ajouter des IDs aux boutons
        self.refresh_btn.setObjectName("refresh_btn")
        self.clean_btn.setObjectName("clean_btn")
        self.pdf_btn.setObjectName("pdf_btn")
        self.excel_btn.setObjectName("excel_btn")
        self.close_btn.setObjectName("close_btn")

    def load_statistics(self):
        """Charge et affiche les statistiques avec graphiques et filtres"""
        try:
            # Désactiver les boutons pendant le chargement
            self.refresh_btn.setEnabled(False)
            self.clean_btn.setEnabled(False)
            self.pdf_btn.setEnabled(False)
            self.excel_btn.setEnabled(False)
            self.search_btn.setEnabled(False)
            
            # Afficher un message de chargement
            self.patients_label.setText("Patients: Chargement...")
            self.medecins_label.setText("Médecins: Chargement...")
            self.rdv_label.setText("Rendez-vous: Chargement...")
            self.prochains_rdv_label.setText("Prochains RDV: Chargement...")
            
            # Charger les statistiques
            self.stats = ReportService.get_clinic_statistics()
            
            # Mettre à jour les labels
            self.patients_label.setText(f"👥 Patients: {self.stats['total_patients']}")
            self.medecins_label.setText(f"👨‍⚕️ Médecins: {self.stats['total_medecins']}")
            self.rdv_label.setText(f"📅 Rendez-vous: {self.stats['total_rendezvous']}")
            
            # Mettre à jour le label des prochains RDV
            if 'prochains_rdv' in self.stats:
                upcoming_count = len(self.stats['prochains_rdv'])
                self.prochains_rdv_label.setText(f"🔜 {upcoming_count} RDV à venir")
            
            # Mettre à jour la liste des médecins dans le ComboBox
            self.update_medecin_combo()
            
            # Avertissement si rendez-vous orphelins
            if 'rdv_orphelins' in self.stats and self.stats['rdv_orphelins'] > 0:
                self.prochains_rdv_label.setText(f"⚠️ {self.stats['rdv_orphelins']} RDV orphelins!")
                self.prochains_rdv_label.setStyleSheet(
                    "color: #c53030; padding: 10px; background-color: #fed7d7; border-radius: 8px; font-weight: bold;"
                )
                # Activer le bouton de nettoyage
                self.clean_btn.setEnabled(True)
            else:
                self.prochains_rdv_label.setStyleSheet(
                    "color: #2c3e50; padding: 10px; background-color: #f0f9ff; border-radius: 8px;"
                )
                # Désactiver le bouton de nettoyage si pas d'orphelins
                self.clean_btn.setEnabled(False)
            
            # Mettre à jour les tableaux
            self.update_specialites_table()
            self.update_rdv_table()
            
            # Mettre à jour les graphiques
            self.update_charts()
            
            # Réactiver les boutons
            self.refresh_btn.setEnabled(True)
            self.pdf_btn.setEnabled(True)
            self.excel_btn.setEnabled(True)
            self.search_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des statistiques:\n{str(e)}")
            # Réactiver le bouton refresh en cas d'erreur
            self.refresh_btn.setEnabled(True)
            self.clean_btn.setEnabled(False)
            self.pdf_btn.setEnabled(False)
            self.excel_btn.setEnabled(False)
            self.search_btn.setEnabled(False)

    def update_medecin_combo(self):
        """Met à jour la liste des médecins dans le ComboBox"""
        if not self.stats or 'liste_medecins' not in self.stats:
            return
        
        # Sauvegarder la sélection actuelle
        current_data = self.medecin_combo.currentData()
        
        # Vider le ComboBox
        self.medecin_combo.clear()
        self.medecin_combo.addItem("Tous les médecins", None)
        
        # Ajouter les médecins
        for medecin in self.stats['liste_medecins']:
            medecin_id, nom, specialite = medecin
            display_text = f"{nom} ({specialite})"
            self.medecin_combo.addItem(display_text, medecin_id)
        
        # Restaurer la sélection précédente si possible
        if current_data:
            index = self.medecin_combo.findData(current_data)
            if index >= 0:
                self.medecin_combo.setCurrentIndex(index)

    def search_rdv_by_filter(self):
        """Recherche les rendez-vous selon les filtres date/médecin"""
        try:
            # Récupérer la date sélectionnée
            selected_date = self.date_picker.date()
            date_str = selected_date.toString("yyyy-MM-dd")
            
            # Récupérer le médecin sélectionné
            medecin_id = self.medecin_combo.currentData()
            
            # Récupérer les rendez-vous
            rdv_list = ReportService.get_rdv_by_date_medecin(date_str, medecin_id)
            
            # Afficher les résultats
            self.display_filter_results(rdv_list, date_str, medecin_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche:\n{str(e)}")

    def display_filter_results(self, rdv_list, date_str, medecin_id):
        """Affiche les résultats de la recherche filtrée"""
        # Stocker les résultats pour l'export
        self.filtered_rdv_list = rdv_list
        
        if not rdv_list:
            self.results_group.setVisible(True)
            self.results_table.setRowCount(0)
            
            # Désactiver les boutons d'export
            self.export_excel_filter_btn.setEnabled(False)
            self.export_pdf_filter_btn.setEnabled(False)
            self.results_count_label.setVisible(False)
            
            QMessageBox.information(self, "Résultats", 
                                  f"Aucun rendez-vous trouvé pour la date {date_str}" + 
                                  ("" if medecin_id is None else f" et le médecin sélectionné"))
            return
        
        # Formater la date en français
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            mois = ["janvier", "février", "mars", "avril", "mai", "juin", 
                   "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
            
            jour_semaine = jours_semaine[date_obj.weekday()]
            jour = date_obj.day
            mois_nom = mois[date_obj.month - 1]
            annee = date_obj.year
            
            date_formatted = f"{jour_semaine} {jour} {mois_nom} {annee}"
        except:
            date_formatted = date_str
        
        # Récupérer le nom du médecin si sélectionné
        medecin_name = ""
        if medecin_id:
            for medecin in self.stats['liste_medecins']:
                if medecin[0] == medecin_id:
                    medecin_name = medecin[1]
                    break
        
        # Mettre à jour le titre du groupe
        title = f"📋 Rendez-vous du {date_formatted}"
        if medecin_name:
            title += f" - Dr. {medecin_name}"
        self.results_group.setTitle(title)
        
        # Mettre à jour le label du nombre de résultats
        self.results_count_label.setText(f"{len(rdv_list)} résultats")
        self.results_count_label.setVisible(True)
        
        # Remplir le tableau
        self.results_table.setRowCount(len(rdv_list))
        
        for row, rdv in enumerate(rdv_list):
            date_rdv, heure, medecin, patient, motif = rdv
            
            # Formater la date pour l'affichage
            try:
                date_display = datetime.strptime(date_rdv, "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                date_display = date_rdv
            
            items = [
                QTableWidgetItem(date_display),
                QTableWidgetItem(str(heure)),
                QTableWidgetItem(str(patient)),
                QTableWidgetItem(str(medecin)),
                QTableWidgetItem(str(motif) if motif else "Non spécifié")
            ]
            
            for col, item in enumerate(items):
                self.results_table.setItem(row, col, item)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        
        self.results_group.setVisible(True)
        
        # Activer les boutons d'export
        self.export_excel_filter_btn.setEnabled(True)
        self.export_pdf_filter_btn.setEnabled(True)
        
        # Message d'information
        message = f"{len(rdv_list)} rendez-vous trouvés pour le {date_formatted}"
        if medecin_name:
            message += f" avec Dr. {medecin_name}"
        QMessageBox.information(self, "Résultats", message)

    def reset_filter(self):
        """Réinitialise les filtres"""
        self.date_picker.setDate(QDate.currentDate())
        self.medecin_combo.setCurrentIndex(0)  # "Tous les médecins"
        self.results_group.setVisible(False)
        self.results_count_label.setVisible(False)
        
        # Désactiver les boutons d'export
        self.export_excel_filter_btn.setEnabled(False)
        self.export_pdf_filter_btn.setEnabled(False)
        
        # Effacer les résultats stockés
        self.filtered_rdv_list = []

    def update_specialites_table(self):
        """Met à jour la table des spécialités"""
        self.specialites_table.setRowCount(0)
        
        if self.stats and 'specialites' in self.stats and self.stats['specialites']:
            for row, (specialite, nb) in enumerate(self.stats['specialites']):
                self.specialites_table.insertRow(row)
                
                # Rang
                item_rank = QTableWidgetItem(str(row + 1))
                item_rank.setTextAlignment(Qt.AlignCenter)
                
                # Spécialité
                item_specialite = QTableWidgetItem(str(specialite))
                
                # Nombre
                item_nb = QTableWidgetItem(str(nb))
                item_nb.setTextAlignment(Qt.AlignCenter)
                
                self.specialites_table.setItem(row, 0, item_rank)
                self.specialites_table.setItem(row, 1, item_specialite)
                self.specialites_table.setItem(row, 2, item_nb)
                
                # Rendre non éditable
                for item in [item_rank, item_specialite, item_nb]:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def update_rdv_table(self):
        """Met à jour la table des rendez-vous"""
        self.rdv_table.setRowCount(0)
        
        if self.stats and 'derniers_rdv' in self.stats and self.stats['derniers_rdv']:
            for row, rdv in enumerate(self.stats['derniers_rdv']):
                try:
                    # Extraire les données du rendez-vous
                    if len(rdv) >= 5:
                        patient, medecin, date_rdv, heure, motif = rdv[:5]
                    else:
                        patient = rdv[0] if len(rdv) > 0 else "Inconnu"
                        medecin = rdv[1] if len(rdv) > 1 else "Inconnu"
                        date_rdv = rdv[2] if len(rdv) > 2 else ""
                        heure = rdv[3] if len(rdv) > 3 else ""
                        motif = rdv[4] if len(rdv) > 4 else "Non spécifié"
                    
                    # Convertir la date au format français
                    date_fr = ""
                    if date_rdv:
                        try:
                            date_fr = datetime.strptime(str(date_rdv), "%Y-%m-%d").strftime("%d/%m/%Y")
                        except:
                            try:
                                date_fr = datetime.strptime(str(date_rdv), "%d/%m/%Y").strftime("%d/%m/%Y")
                            except:
                                date_fr = str(date_rdv)
                    
                    self.rdv_table.insertRow(row)
                    
                    items = [
                        QTableWidgetItem(str(patient)),
                        QTableWidgetItem(str(medecin)),
                        QTableWidgetItem(date_fr),
                        QTableWidgetItem(str(heure) if heure else ""),
                        QTableWidgetItem(str(motif) if motif else "Non spécifié")
                    ]
                    
                    for col, item in enumerate(items):
                        self.rdv_table.setItem(row, col, item)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        
                except Exception as e:
                    print(f"Erreur lors de l'ajout du rendez-vous {row}: {e}")
                    continue

    def update_charts(self):
        """Met à jour tous les graphiques"""
        try:
            # 1. Graphique d'évolution des rendez-vous (ligne)
            self.create_evolution_chart()
            
            # 2. Graphique de répartition par spécialité (barres)
            self.create_specialties_chart()
            
            # 3. Graphique des tendances hebdomadaires
            self.create_weekly_trends_chart()
            
            # 4. Graphique comparatif médecins
            self.create_doctors_comparison_chart()
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour des graphiques: {e}")

    def create_evolution_chart(self):
        """Crée le graphique d'évolution des rendez-vous"""
        if not self.stats or 'rdv_par_mois' not in self.stats or not self.stats['rdv_par_mois']:
            return
        
        chart = QChart()
        chart.setTitle("Évolution des rendez-vous")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        series = QLineSeries()
        series.setName("Rendez-vous")
        series.setColor(QColor("#4299e1"))
        
        # Ajouter les données
        months = []
        for mois, nb_rdv in reversed(self.stats['rdv_par_mois']):  # Inverser pour ordre chronologique
            try:
                # Convertir YYYY-MM en nom de mois
                annee, mois_num = mois.split('-')
                mois_nom = {
                    '01': 'Jan', '02': 'Fév', '03': 'Mar',
                    '04': 'Avr', '05': 'Mai', '06': 'Jun',
                    '07': 'Jul', '08': 'Aoû', '09': 'Sep',
                    '10': 'Oct', '11': 'Nov', '12': 'Déc'
                }.get(mois_num, mois_num)
                label = f"{mois_nom} {annee[2:]}"
                months.append(label)
                series.append(len(months) - 1, nb_rdv)
            except:
                continue
        
        chart.addSeries(series)
        
        # Axe X
        axis_x = QBarCategoryAxis()
        axis_x.append(months)
        axis_x.setTitleText("Mois")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Axe Y
        axis_y = QValueAxis()
        axis_y.setTitleText("Nombre de RDV")
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        self.chart_view1.setChart(chart)

    def create_specialties_chart(self):
        """Crée le graphique de répartition par spécialité"""
        if not self.stats or 'specialites' not in self.stats or not self.stats['specialites']:
            return
        
        chart = QChart()
        chart.setTitle("Répartition par spécialité")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        series = QBarSeries()
        series.setLabelsVisible(True)
        series.setLabelsFormat("@value RDV")
        
        # Couleurs pour les barres
        colors = ["#4299e1", "#48bb78", "#ed8936", "#9f7aea", "#f56565"]
        
        specialties = []
        for i, (specialite, nb_rdv) in enumerate(self.stats['specialites']):
            bar_set = QBarSet(str(specialite))
            bar_set.append(nb_rdv)
            bar_set.setColor(QColor(colors[i % len(colors)]))
            bar_set.setLabelColor(QColor("#2d3748"))
            series.append(bar_set)
            specialties.append(str(specialite))
        
        chart.addSeries(series)
        
        # Axe X
        axis_x = QBarCategoryAxis()
        axis_x.append(specialties)
        axis_x.setTitleText("Spécialités")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Axe Y
        axis_y = QValueAxis()
        axis_y.setTitleText("Nombre de RDV")
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        self.chart_view2.setChart(chart)

    def create_weekly_trends_chart(self):
        """Crée le graphique des tendances hebdomadaires"""
        # Pour cet exemple, on génère des données simulées
        # Dans une vraie application, vous récupéreriez ces données de la base
        chart = QChart()
        chart.setTitle("Tendances hebdomadaires")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        series = QLineSeries()
        series.setName("Rendez-vous cette semaine")
        series.setColor(QColor("#9f7aea"))
        
        # Données simulées pour une semaine
        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        rendezvous = [12, 18, 15, 20, 22, 10, 5]  # Données simulées
        
        for i, (jour, nb) in enumerate(zip(jours, rendezvous)):
            series.append(i, nb)
        
        chart.addSeries(series)
        
        # Axe X
        axis_x = QBarCategoryAxis()
        axis_x.append(jours)
        axis_x.setTitleText("Jour")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Axe Y
        axis_y = QValueAxis()
        axis_y.setTitleText("Nombre de RDV")
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        self.trends_chart_view.setChart(chart)

    def create_doctors_comparison_chart(self):
        """Crée le graphique comparatif des médecins"""
        # Données simulées - dans une vraie app, récupérez de la base
        chart = QChart()
        chart.setTitle("Activité des médecins (top 5)")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        series = QBarSeries()
        series.setLabelsVisible(True)
        series.setLabelsFormat("@value RDV")
        
        # Données simulées
        medecins = ["Dr. Martin", "Dr. Dubois", "Dr. Leroy", "Dr. Petit", "Dr. Robert"]
        consultations = [45, 38, 32, 28, 25]
        colors = ["#4299e1", "#48bb78", "#ed8936", "#9f7aea", "#f56565"]
        
        for i, (medecin, nb_cons) in enumerate(zip(medecins, consultations)):
            bar_set = QBarSet(medecin)
            bar_set.append(nb_cons)
            bar_set.setColor(QColor(colors[i % len(colors)]))
            bar_set.setLabelColor(QColor("#2d3748"))
            series.append(bar_set)
        
        chart.addSeries(series)
        
        # Axe X
        axis_x = QBarCategoryAxis()
        axis_x.append(medecins)
        axis_x.setTitleText("Médecins")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Axe Y
        axis_y = QValueAxis()
        axis_y.setTitleText("Nombre de consultations")
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        self.compare_chart_view.setChart(chart)

    def export_filtered_excel(self):
        """Exporte les résultats filtrés en Excel"""
        if not hasattr(self, 'filtered_rdv_list') or not self.filtered_rdv_list:
            QMessageBox.warning(self, "Attention", "Aucun rendez-vous à exporter!")
            return
        
        try:
            # Récupérer les informations de filtrage
            selected_date = self.date_picker.date()
            date_str = selected_date.toString("yyyy-MM-dd")
            
            # Récupérer le nom du médecin
            medecin_nom = None
            medecin_id = self.medecin_combo.currentData()
            if medecin_id:
                for medecin in self.stats['liste_medecins']:
                    if medecin[0] == medecin_id:
                        medecin_nom = f"Dr. {medecin[1]}"
                        break
            
            # Exporter
            filename = ReportService.export_rdv_to_excel(
                self.filtered_rdv_list, 
                date_str, 
                medecin_nom
            )
            
            QMessageBox.information(
                self, 
                "Export réussi", 
                f"Les rendez-vous ont été exportés avec succès!\n\n"
                f"Fichier: {filename}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export:\n{str(e)}")

    def export_filtered_pdf(self):
        """Exporte les résultats filtrés en PDF"""
        if not hasattr(self, 'filtered_rdv_list') or not self.filtered_rdv_list:
            QMessageBox.warning(self, "Attention", "Aucun rendez-vous à exporter!")
            return
        
        try:
            # Récupérer les informations de filtrage
            selected_date = self.date_picker.date()
            date_str = selected_date.toString("yyyy-MM-dd")
            
            # Récupérer le nom du médecin
            medecin_nom = None
            medecin_id = self.medecin_combo.currentData()
            if medecin_id:
                for medecin in self.stats['liste_medecins']:
                    if medecin[0] == medecin_id:
                        medecin_nom = f"Dr. {medecin[1]}"
                        break
            
            # Exporter
            filename = ReportService.export_rdv_to_pdf(
                self.filtered_rdv_list, 
                date_str, 
                medecin_nom
            )
            
            QMessageBox.information(
                self, 
                "Export réussi", 
                f"Les rendez-vous ont été exportés avec succès!\n\n"
                f"Fichier: {filename}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export:\n{str(e)}")

    def nettoyer_donnees(self):
        """Nettoie les données orphelines"""
        reply = QMessageBox.question(
            self, 'Confirmation',
            'Voulez-vous nettoyer les rendez-vous orphelins?\n'
            '(Ceux dont le patient ou le médecin a été supprimé)\n\n'
            'Cette action est irréversible.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = ReportService.nettoyer_rendezvous_orphelins()
                
                if result['supprimes'] > 0:
                    QMessageBox.information(
                        self, 'Nettoyage terminé',
                        f"Nettoyage terminé avec succès!\n\n"
                        f"Rendez-vous orphelins avant: {result['avant']}\n"
                        f"Rendez-vous orphelins après: {result['apres']}\n"
                        f"Nombre supprimé: {result['supprimes']}\n\n"
                        f"{result['message']}"
                    )
                else:
                    QMessageBox.information(
                        self, 'Nettoyage',
                        result['message']
                    )
                
                # Recharger les statistiques après nettoyage
                self.load_statistics()
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du nettoyage:\n{str(e)}")

    def export_pdf(self):
        """Exporte les statistiques en PDF"""
        if not self.stats:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger les statistiques!")
            return
        
        try:
            filename = ReportService.export_to_pdf(self.stats)
            QMessageBox.information(self, "Succès", 
                                  f"Rapport PDF généré avec succès!\n\nFichier: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export PDF:\n{str(e)}")

    def export_excel(self):
        """Exporte les statistiques en Excel"""
        if not self.stats:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger les statistiques!")
            return
        
        try:
            filename = ReportService.export_to_excel(self.stats)
            QMessageBox.information(self, "Succès", 
                                  f"Rapport Excel généré avec succès!\n\nFichier: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export Excel:\n{str(e)}")

    def close_window(self):
        """Ferme la fenêtre"""
        self.closed.emit()
        self.close()

    def closeEvent(self, event):
        """Gère la fermeture"""
        self.closed.emit()
        event.accept()

    def showEvent(self, event):
        """Gère l'affichage de la fenêtre"""
        super().showEvent(event)
        # Charger les statistiques automatiquement quand la fenêtre s'ouvre
        self.load_statistics()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ReportsUI()
    window.show()
    sys.exit(app.exec())