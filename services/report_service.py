from db.connection import get_connection
import pandas as pd
from fpdf import FPDF
import os
from datetime import datetime, timedelta

class ReportService:
    
    @staticmethod
    def get_clinic_statistics():
        """Récupère toutes les statistiques de la clinique"""
        conn = get_connection()
        cursor = conn.cursor()
        
        stats = {}
       
        try:
            # 1. Nombre total de patients
            cursor.execute("SELECT COUNT(*) FROM patients")
            stats['total_patients'] = cursor.fetchone()[0]
            
            # 2. Nombre total de médecins
            cursor.execute("SELECT COUNT(*) FROM medecins")
            stats['total_medecins'] = cursor.fetchone()[0]
            
            # 3. Nombre total de rendez-vous VALIDES (avec patient et médecin existants)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM rendezvous r
                WHERE EXISTS (SELECT 1 FROM patients p WHERE p.id_patient = r.id_patient)
                AND EXISTS (SELECT 1 FROM medecins m WHERE m.id_medecin = r.id_medecin)
            """)
            stats['total_rendezvous'] = cursor.fetchone()[0]
            
            # 4. Spécialités les plus sollicitées (uniquement avec données valides)
            cursor.execute("""
                SELECT m.specialite, COUNT(r.id_rdv) as nb_rdv
                FROM medecins m
                JOIN rendezvous r ON m.id_medecin = r.id_medecin
                WHERE EXISTS (SELECT 1 FROM patients p WHERE p.id_patient = r.id_patient)
                GROUP BY m.specialite
                ORDER BY nb_rdv DESC
                LIMIT 5
            """)
            stats['specialites'] = cursor.fetchall()
            
            # 5. Derniers rendez-vous (pour l'historique) - uniquement valides
            cursor.execute("""
                SELECT 
                    p.nom || ' ' || p.prenom as patient, 
                    'Dr. ' || m.nom as medecin,
                    r.date_rdv, 
                    r.heure_rdv, 
                    r.motif
                FROM rendezvous r
                JOIN patients p ON r.id_patient = p.id_patient
                JOIN medecins m ON r.id_medecin = m.id_medecin
                ORDER BY r.date_rdv DESC, r.heure_rdv DESC
                LIMIT 10
            """)
            stats['derniers_rdv'] = cursor.fetchall()
            
            # 6. Statistiques par mois (uniquement rendez-vous valides)
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m', r.date_rdv) as mois, 
                    COUNT(*) as nb_rdv
                FROM rendezvous r
                WHERE EXISTS (SELECT 1 FROM patients p WHERE p.id_patient = r.id_patient)
                AND EXISTS (SELECT 1 FROM medecins m WHERE m.id_medecin = r.id_medecin)
                GROUP BY strftime('%Y-%m', r.date_rdv)
                ORDER BY mois DESC
                LIMIT 6
            """)
            stats['rdv_par_mois'] = cursor.fetchall()
            
            # 7. Nombre de rendez-vous orphelins (pour information)
            cursor.execute("""
                SELECT COUNT(*) as rdv_orphelins
                FROM rendezvous r
                WHERE NOT EXISTS (SELECT 1 FROM patients p WHERE p.id_patient = r.id_patient)
                OR NOT EXISTS (SELECT 1 FROM medecins m WHERE m.id_medecin = r.id_medecin)
            """)
            stats['rdv_orphelins'] = cursor.fetchone()[0]
            
            # 8. Pourcentage de rendez-vous valides
            cursor.execute("SELECT COUNT(*) FROM rendezvous")
            total_rdv_tous = cursor.fetchone()[0]
            if total_rdv_tous > 0:
                stats['pourcentage_valides'] = (stats['total_rendezvous'] / total_rdv_tous) * 100
            else:
                stats['pourcentage_valides'] = 100.0
                
            # 9. Prochains rendez-vous (5 prochains)
            stats['prochains_rdv'] = ReportService.get_prochains_rdv()
            
            # 10. Liste des médecins pour le filtre
            stats['liste_medecins'] = ReportService.get_all_medecins()
            
        except Exception as e:
            print(f"Erreur calcul statistiques: {e}")
            # Pour déboguer, afficher l'erreur complète
            import traceback
            print(traceback.format_exc())
            raise e
        finally:
            conn.close()
        
        return stats
    
    @staticmethod
    def get_prochains_rdv(limit=5):
        """Récupère les prochains rendez-vous"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Date d'aujourd'hui
            today = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute("""
                SELECT 
                    r.date_rdv,
                    r.heure_rdv,
                    'Dr. ' || m.nom as medecin,
                    p.nom || ' ' || p.prenom as patient,
                    r.motif
                FROM rendezvous r
                JOIN patients p ON r.id_patient = p.id_patient
                JOIN medecins m ON r.id_medecin = m.id_medecin
                WHERE r.date_rdv >= ?
                ORDER BY r.date_rdv ASC, r.heure_rdv ASC
                LIMIT ?
            """, (today, limit))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Erreur récupération prochains RDV: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_all_medecins():
        """Récupère tous les médecins"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id_medecin, nom, specialite FROM medecins ORDER BY nom")
            return cursor.fetchall()
        except Exception as e:
            print(f"Erreur récupération médecins: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_rdv_by_date_medecin(date_str, medecin_id=None):
        """Récupère les rendez-vous pour une date et un médecin spécifiques"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            if medecin_id:
                cursor.execute("""
                    SELECT 
                        r.date_rdv,
                        r.heure_rdv,
                        'Dr. ' || m.nom as medecin,
                        p.nom || ' ' || p.prenom as patient,
                        r.motif
                    FROM rendezvous r
                    JOIN patients p ON r.id_patient = p.id_patient
                    JOIN medecins m ON r.id_medecin = m.id_medecin
                    WHERE r.date_rdv = ? AND m.id_medecin = ?
                    ORDER BY r.heure_rdv ASC
                """, (date_str, medecin_id))
            else:
                cursor.execute("""
                    SELECT 
                        r.date_rdv,
                        r.heure_rdv,
                        'Dr. ' || m.nom as medecin,
                        p.nom || ' ' || p.prenom as patient,
                        r.motif
                    FROM rendezvous r
                    JOIN patients p ON r.id_patient = p.id_patient
                    JOIN medecins m ON r.id_medecin = m.id_medecin
                    WHERE r.date_rdv = ?
                    ORDER BY r.heure_rdv ASC
                """, (date_str,))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Erreur récupération RDV par date/médecin: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def nettoyer_rendezvous_orphelins():
        """Supprime les rendez-vous qui pointent vers des patients ou médecins inexistants"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Compter le nombre de rendez-vous orphelins avant nettoyage
            cursor.execute("""
                SELECT COUNT(*) as avant_nettoyage
                FROM rendezvous r
                WHERE NOT EXISTS (SELECT 1 FROM patients p WHERE p.id_patient = r.id_patient)
                OR NOT EXISTS (SELECT 1 FROM medecins m WHERE m.id_medecin = r.id_medecin)
            """)
            avant = cursor.fetchone()[0]
            
            if avant == 0:
                return {
                    'avant': 0,
                    'apres': 0,
                    'supprimes': 0,
                    'message': 'Aucun rendez-vous orphelin à nettoyer.'
                }
            
            # Supprimer les rendez-vous orphelins
            cursor.execute("""
                DELETE FROM rendezvous
                WHERE id_patient NOT IN (SELECT id_patient FROM patients)
                OR id_medecin NOT IN (SELECT id_medecin FROM medecins)
            """)
            
            # Compter après nettoyage
            cursor.execute("""
                SELECT COUNT(*) as apres_nettoyage
                FROM rendezvous r
                WHERE NOT EXISTS (SELECT 1 FROM patients p WHERE p.id_patient = r.id_patient)
                OR NOT EXISTS (SELECT 1 FROM medecins m WHERE m.id_medecin = r.id_medecin)
            """)
            apres = cursor.fetchone()[0]
            
            conn.commit()
            
            return {
                'avant': avant,
                'apres': apres,
                'supprimes': avant - apres,
                'message': f'{avant - apres} rendez-vous orphelins supprimés.'
            }
            
        except Exception as e:
            conn.rollback()
            print(f"Erreur nettoyage rendez-vous orphelins: {e}")
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def export_to_excel(stats, filename=None):
        """Exporte les statistiques en Excel"""
        try:
            if filename is None:
                # Créer un nom de fichier avec la date
                date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Créer les dossiers s'ils n'existent pas
                if not os.path.exists('excel_reports'):
                    os.makedirs('excel_reports')
                filename = f"excel_reports/rapport_clinique_{date_str}.xlsx"
            
            # Créer un writer Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 1. Feuille: Statistiques principales
                df_stats = pd.DataFrame([
                    ['Patients', stats['total_patients']],
                    ['Médecins', stats['total_medecins']],
                    ['Rendez-vous valides', stats['total_rendezvous']],
                    ['Rendez-vous orphelins', stats.get('rdv_orphelins', 0)],
                    ['Pourcentage valides', f"{stats.get('pourcentage_valides', 100):.1f}%"]
                ], columns=['Catégorie', 'Nombre'])
                
                df_stats.to_excel(writer, sheet_name='Statistiques', index=False)
                
                # 2. Feuille: Spécialités
                if stats['specialites']:
                    df_specialites = pd.DataFrame(
                        stats['specialites'], 
                        columns=['Spécialité', 'Nombre de rendez-vous']
                    )
                    df_specialites.to_excel(writer, sheet_name='Spécialités', index=False)
                
                # 3. Feuille: Derniers rendez-vous
                if stats['derniers_rdv']:
                    df_rdv = pd.DataFrame(
                        stats['derniers_rdv'],
                        columns=['Patient', 'Médecin', 'Date', 'Heure', 'Motif']
                    )
                    df_rdv.to_excel(writer, sheet_name='Derniers RDV', index=False)
                
                # 4. Feuille: RDV par mois
                if stats['rdv_par_mois']:
                    df_mois = pd.DataFrame(
                        stats['rdv_par_mois'],
                        columns=['Mois', 'Nombre de RDV']
                    )
                    df_mois.to_excel(writer, sheet_name='RDV par mois', index=False)
                
                # 5. Feuille: Prochains RDV
                if 'prochains_rdv' in stats and stats['prochains_rdv']:
                    df_prochains = pd.DataFrame(
                        stats['prochains_rdv'],
                        columns=['Date', 'Heure', 'Médecin', 'Patient', 'Motif']
                    )
                    df_prochains.to_excel(writer, sheet_name='Prochains RDV', index=False)
                
                # Ajuster la largeur des colonnes
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 30)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return filename
            
        except Exception as e:
            print(f"Erreur export Excel: {e}")
            raise e
    
    @staticmethod
    def export_to_pdf(stats, filename=None):
        """Exporte les statistiques en PDF"""
        try:
            if filename is None:
                date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Créer les dossiers s'ils n'existent pas
                if not os.path.exists('pdf_reports'):
                    os.makedirs('pdf_reports')
                filename = f"pdf_reports/rapport_clinique_{date_str}.pdf"
            
            # Créer le PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Titre
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Rapport Clinique Médicale', ln=True, align='C')
            pdf.ln(10)
            
            # Date
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 10, f'Généré le: {datetime.now().strftime("%d/%m/%Y %H:%M")}', ln=True)
            pdf.ln(10)
            
            # 1. Statistiques principales
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Statistiques Principales', ln=True)
            pdf.set_font('Arial', '', 12)
            
            pdf.cell(0, 10, f"Nombre total de patients: {stats['total_patients']}", ln=True)
            pdf.cell(0, 10, f"Nombre total de médecins: {stats['total_medecins']}", ln=True)
            pdf.cell(0, 10, f"Nombre total de rendez-vous valides: {stats['total_rendezvous']}", ln=True)
            
            # Ajouter information sur les rendez-vous orphelins si présents
            if stats.get('rdv_orphelins', 0) > 0:
                pdf.set_text_color(255, 0, 0)  # Rouge pour alerter
                pdf.cell(0, 10, f"⚠️  Rendez-vous orphelins: {stats['rdv_orphelins']} (à nettoyer)", ln=True)
                pdf.set_text_color(0, 0, 0)  # Revenir au noir
                pdf.cell(0, 10, f"Pourcentage de données valides: {stats.get('pourcentage_valides', 100):.1f}%", ln=True)
            
            pdf.ln(10)
            
            # 2. Spécialités les plus demandées
            if stats['specialites']:
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Spécialités les plus demandées:', ln=True)
                pdf.set_font('Arial', '', 12)
                
                for specialite, nb in stats['specialites']:
                    pdf.cell(0, 10, f"  • {specialite}: {nb} rendez-vous", ln=True)
                pdf.ln(10)
            
            # 3. Derniers rendez-vous
            if stats['derniers_rdv']:
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Derniers rendez-vous:', ln=True)
                pdf.set_font('Arial', '', 10)
                
                for rdv in stats['derniers_rdv']:
                    patient, medecin, date_rdv, heure, motif = rdv
                    # Gérer les erreurs de format de date
                    try:
                        date_fr = datetime.strptime(date_rdv, "%Y-%m-%d").strftime("%d/%m/%Y")
                    except:
                        date_fr = str(date_rdv)
                    pdf.cell(0, 8, f"  • {date_fr} {heure} - {patient} avec {medecin}: {motif}", ln=True)
                pdf.ln(5)
            
            # 4. Prochains rendez-vous
            if 'prochains_rdv' in stats and stats['prochains_rdv']:
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Prochains rendez-vous:', ln=True)
                pdf.set_font('Arial', '', 10)
                
                for rdv in stats['prochains_rdv']:
                    date_rdv, heure, medecin, patient, motif = rdv
                    try:
                        date_fr = datetime.strptime(date_rdv, "%Y-%m-%d").strftime("%d/%m/%Y")
                    except:
                        date_fr = str(date_rdv)
                    pdf.cell(0, 8, f"  • {date_fr} {heure} - {patient} avec {medecin}: {motif}", ln=True)
                pdf.ln(5)
            
            # 5. RDV par mois
            if stats['rdv_par_mois']:
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Rendez-vous par mois:', ln=True)
                pdf.set_font('Arial', '', 12)
                
                for mois, nb in stats['rdv_par_mois']:
                    # Convertir YYYY-MM en français
                    try:
                        annee, mois_num = mois.split('-')
                        mois_nom = {
                            '01': 'Janvier', '02': 'Février', '03': 'Mars',
                            '04': 'Avril', '05': 'Mai', '06': 'Juin',
                            '07': 'Juillet', '08': 'Août', '09': 'Septembre',
                            '10': 'Octobre', '11': 'Novembre', '12': 'Décembre'
                        }.get(mois_num, mois_num)
                        mois_str = f"{mois_nom} {annee}"
                    except:
                        mois_str = str(mois)
                    
                    pdf.cell(0, 10, f"  • {mois_str}: {nb} rendez-vous", ln=True)
            
            # Pied de page
            pdf.set_y(-15)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, 'Page %s' % pdf.page_no(), 0, 0, 'C')
            
            # Sauvegarder le PDF
            pdf.output(filename)
            return filename
            
        except Exception as e:
            print(f"Erreur export PDF: {e}")
            raise e
    
    @staticmethod
    def export_rdv_to_excel(rdv_list, date_str, medecin_nom=None):
        """Exporte une liste de rendez-vous en Excel"""
        try:
            # Créer un nom de fichier avec la date
            date_clean = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not os.path.exists('excel_reports'):
                os.makedirs('excel_reports')
            
            if medecin_nom:
                # Nettoyer le nom du médecin pour le nom de fichier
                medecin_clean = medecin_nom.replace(' ', '_').replace('.', '').replace('Dr_', '')
                filename = f"excel_reports/rdv_{date_str}_{medecin_clean}_{date_clean}.xlsx"
            else:
                filename = f"excel_reports/rdv_{date_str}_tous_{date_clean}.xlsx"
            
            # Créer un DataFrame
            df = pd.DataFrame(
                rdv_list,
                columns=['Date', 'Heure', 'Médecin', 'Patient', 'Motif']
            )
            
            # Convertir la date au format français
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')
            
            # Trier par heure
            if 'Heure' in df.columns:
                df = df.sort_values('Heure')
            
            # Exporter vers Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Feuille principale
                df.to_excel(writer, sheet_name='Rendez-vous', index=False)
                
                # Feuille de statistiques
                stats_data = [
                    ['Date', date_str],
                    ['Médecin', medecin_nom if medecin_nom else 'Tous les médecins'],
                    ['Nombre de RDV', len(rdv_list)]
                ]
                
                df_stats = pd.DataFrame(stats_data, columns=['Catégorie', 'Valeur'])
                df_stats.to_excel(writer, sheet_name='Statistiques', index=False)
                
                # Ajuster la largeur des colonnes
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 30)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return filename
            
        except Exception as e:
            print(f"Erreur export RDV Excel: {e}")
            raise e
    
    @staticmethod
    def export_rdv_to_pdf(rdv_list, date_str, medecin_nom=None):
        """Exporte une liste de rendez-vous en PDF"""
        try:
            # Créer un nom de fichier
            date_clean = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not os.path.exists('pdf_reports'):
                os.makedirs('pdf_reports')
            
            if medecin_nom:
                medecin_clean = medecin_nom.replace(' ', '_').replace('.', '').replace('Dr_', '')
                filename = f"pdf_reports/rdv_{date_str}_{medecin_clean}_{date_clean}.pdf"
            else:
                filename = f"pdf_reports/rdv_{date_str}_tous_{date_clean}.pdf"
            
            # Créer le PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Titre
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Liste des Rendez-vous', ln=True, align='C')
            pdf.ln(10)
            
            # Informations de filtrage
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Date : {date_str}", ln=True)
            
            if medecin_nom:
                pdf.cell(0, 10, f"Médecin : {medecin_nom}", ln=True)
            else:
                pdf.cell(0, 10, "Médecin : Tous les médecins", ln=True)
            
            pdf.cell(0, 10, f"Nombre de rendez-vous : {len(rdv_list)}", ln=True)
            pdf.ln(10)
            
            # Date de génération
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 10, f'Généré le: {datetime.now().strftime("%d/%m/%Y %H:%M")}', ln=True)
            pdf.ln(10)
            
            # Tableau des rendez-vous
            if rdv_list:
                # En-tête du tableau
                pdf.set_font('Arial', 'B', 12)
                col_widths = [40, 30, 60, 60]  # Date, Heure, Patient, Motif
                
                # En-têtes
                headers = ['Date', 'Heure', 'Patient', 'Motif']
                if not medecin_nom:
                    headers.insert(2, 'Médecin')
                    col_widths.insert(2, 40)
                
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, header, border=1, align='C')
                pdf.ln()
                
                # Contenu du tableau
                pdf.set_font('Arial', '', 10)
                for rdv in rdv_list:
                    date_rdv, heure, medecin, patient, motif = rdv
                    
                    # Convertir la date
                    try:
                        date_display = datetime.strptime(str(date_rdv), "%Y-%m-%d").strftime("%d/%m/%Y")
                    except:
                        date_display = str(date_rdv)
                    
                    # Ligne du tableau
                    row_data = [date_display, str(heure), str(patient)]
                    if not medecin_nom:
                        row_data.insert(2, str(medecin))
                    row_data.append(str(motif) if motif else "Non spécifié")
                    
                    for i, data in enumerate(row_data):
                        pdf.cell(col_widths[i], 10, data, border=1)
                    pdf.ln()
            
            else:
                pdf.set_font('Arial', 'I', 12)
                pdf.cell(0, 10, "Aucun rendez-vous trouvé", ln=True, align='C')
            
            # Pied de page
            pdf.set_y(-15)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, 'Page %s' % pdf.page_no(), 0, 0, 'C')
            
            # Sauvegarder
            pdf.output(filename)
            return filename
            
        except Exception as e:
            print(f"Erreur export RDV PDF: {e}")
            raise e

    # Méthode de débogage pour vérifier la structure
    @staticmethod
    def debug_table_structure():
        """Affiche la structure des tables pour débogage"""
        conn = get_connection()
        cursor = conn.cursor()
        
        print("=== STRUCTURE DE LA TABLE RENDEZVOUS ===")
        cursor.execute("PRAGMA table_info(rendezvous)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        print("\n=== STRUCTURE DE LA TABLE PATIENTS ===")
        cursor.execute("PRAGMA table_info(patients)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        print("\n=== STRUCTURE DE LA TABLE MEDECINS ===")
        cursor.execute("PRAGMA table_info(medecins)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        conn.close()