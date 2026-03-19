from fpdf import FPDF
import datetime
import re

class PDFBilan(FPDF):
    def header(self):
        # Configuration de l'en-tête institutionnel
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(30, 64, 175) # Bleu foncé institutionnel
        self.cell(0, 10, 'Bilan Métacognitif - Tuteur Cognitif', border=0, ln=1, align='C')
        self.ln(10)

    def footer(self):
        # Configuration du pied de page avec horodatage
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        date_generation = datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")
        self.cell(0, 10, f'Document généré le {date_generation} - Ingénierie de la Preuve', border=0, align='C')

def nettoyer_markdown(texte):
    """
    Supprime les balises Markdown générées par l'IA pour un rendu PDF propre en texte brut.
    (fpdf2 gère mal le markdown complexe par défaut sans polices spécifiques)
    """
    # Supprime les astérisques du gras et de l'italique
    texte = re.sub(r'\*\*(.*?)\*\*', r'\1', texte)
    texte = re.sub(r'\*(.*?)\*', r'\1', texte)
    # Uniformise les puces
    texte = texte.replace('- ', '• ')
    return texte

def generer_pdf_bytes(texte_bilan, matiere, niveau, objectif):
    """
    Génère le PDF en mémoire vive et retourne les bytes pour le téléchargement Streamlit.
    """
    pdf = PDFBilan()
    pdf.add_page()
    
    # Corps du document
    pdf.set_font("helvetica", size=11)
    pdf.set_text_color(50, 50, 50)
    
    # Bloc d'information de la session
    pdf.set_fill_color(240, 244, 248) # Fond gris-bleu clair
    pdf.cell(0, 10, f" Matière : {matiere} | Classe : {niveau} ", border=0, ln=1, fill=True)
    pdf.cell(0, 10, f" Objectif travaillé : {objectif}", border=0, ln=1, fill=True)
    pdf.ln(10)
    
    # Titre du contenu
    pdf.set_font("helvetica", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Analyse de ta session d'apprentissage :", border=0, ln=1)
    pdf.ln(5)
    
    # Ajout du texte de l'IA nettoyé
    pdf.set_font("helvetica", size=11)
    texte_propre = nettoyer_markdown(texte_bilan)
    
    # multi_cell permet de gérer les retours à la ligne automatiques
    pdf.multi_cell(0, 7, txt=texte_propre)
    
    # Renvoi du fichier sous forme d'octets (bytes)
    return pdf.output()
