from fpdf import FPDF
import datetime
import re

class PDFBilan(FPDF):
    def header(self):
        # En-tête épuré et institutionnel
        self.set_font('helvetica', 'B', 18)
        self.set_text_color(30, 64, 175) # Bleu institutionnel
        self.cell(0, 12, 'Bilan Métacognitif', border=0, ln=1, align='L')
        # Ligne de séparation élégante
        self.set_draw_color(200, 200, 200)
        self.line(10, 22, 200, 22)
        self.ln(5)

    def footer(self):
        # Pied de page avec horodatage
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        date_g = datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")
        self.cell(0, 10, f'Généré le {date_g} - Tuteur Cognitif (GIPTIC)', 0, 0, 'C')


def nettoyer_texte(texte):
    """
    Nettoie les résidus Markdown, LaTeX et caractères incompatibles avec l'encodage PDF.
    """
    # 1. Nettoyage mathématique (LaTeX -> Texte lisible)
    texte = texte.replace('$', '')
    texte = texte.replace('\\times', 'x')
    texte = texte.replace('\\frac', '/')
    texte = texte.replace('\\', '')
    
    # 2. Suppression des astérisques Markdown
    texte = texte.replace('**', '')
    texte = texte.replace('*', '')
    
    # 3. Suppression des numérotations initiales générées par l'IA (ex: "1. Tes acquis")
    texte = re.sub(r'^\d+\.\s*', '', texte)
    
    # 4. Encodage de sécurité Latin-1 (Purge des emojis)
    texte = texte.encode('latin-1', 'ignore').decode('latin-1')
    return texte.strip()


def generer_pdf_bytes(texte_bilan, matiere, niveau, objectif):
    """
    Parse la réponse de l'IA ligne par ligne et génère un PDF formaté et hiérarchisé.
    """
    pdf = PDFBilan()
    pdf.add_page()
    
    # ---------------------------------------------------------
    # BLOC 1 : MÉTA-INFORMATIONS DE LA SESSION
    # ---------------------------------------------------------
    pdf.set_fill_color(245, 247, 250) # Fond gris très clair
    pdf.set_font("helvetica", '', 10)
    pdf.set_text_color(80, 80, 80)
    
    # Protection des caractères accentués pour le header
    matiere_p = matiere.encode('latin-1', 'ignore').decode('latin-1')
    objectif_p = objectif.encode('latin-1', 'ignore').decode('latin-1')
    
    pdf.cell(0, 8, f" Matière : {matiere_p}  |  Classe : {niveau}", border=0, ln=1, fill=True)
    pdf.cell(0, 8, f" Objectif travaillé : {objectif_p}", border=0, ln=1, fill=True)
    pdf.ln(10)
    
    # ---------------------------------------------------------
    # BLOC 2 : TITRE DU RAPPORT
    # ---------------------------------------------------------
    pdf.set_font("helvetica", 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Analyse de ta session d'apprentissage :", ln=1)
    pdf.ln(2)

    # ---------------------------------------------------------
    # BLOC 3 : PARSING INTELLIGENT DU CONTENU
    # ---------------------------------------------------------
    lignes = texte_bilan.split('\n')
    
    for ligne in lignes:
        ligne = nettoyer_texte(ligne)
        
        # Ignorer les lignes vides
        if not ligne:
            continue
            
        # A. Détection : Acquis
        if "acquis" in ligne.lower() and ":" in ligne:
            pdf.set_font("helvetica", 'B', 12)
            pdf.set_text_color(34, 139, 34) # Vert forêt
            pdf.cell(0, 8, "Tes acquis :", ln=1)
            
            pdf.set_font("helvetica", '', 11)
            pdf.set_text_color(50, 50, 50)
            contenu = ligne.split(":", 1)[1].strip()
            pdf.multi_cell(0, 6, txt=f"  • {contenu}")
            pdf.ln(4)
            
        # B. Détection : Erreurs
        elif "erreur" in ligne.lower() and ":" in ligne:
            pdf.set_font("helvetica", 'B', 12)
            pdf.set_text_color(220, 20, 60) # Rouge cramoisi
            pdf.cell(0, 8, "Tes erreurs (et comment les corriger) :", ln=1)
            
            pdf.set_font("helvetica", '', 11)
            pdf.set_text_color(50, 50, 50)
            contenu = ligne.split(":", 1)[1].strip()
            pdf.multi_cell(0, 6, txt=f"  • {contenu}")
            pdf.ln(4)
            
        # C. Détection : Le Piège
        elif ("relecture" in ligne.lower() or "correction" in ligne.lower() or "piège" in ligne.lower()) and ":" in ligne:
            pdf.set_font("helvetica", 'B', 12)
            pdf.set_text_color(255, 140, 0) # Orange
            pdf.cell(0, 8, "Le piège cognitif :", ln=1)
            
            pdf.set_font("helvetica", '', 11)
            pdf.set_text_color(50, 50, 50)
            contenu = ligne.split(":", 1)[1].strip()
            pdf.multi_cell(0, 6, txt=f"  • {contenu}")
            pdf.ln(4)
            
        # D. Détection : Prochaine Étape
        elif ("étape" in ligne.lower() or "prochaine" in ligne.lower()) and ":" in ligne:
            pdf.set_font("helvetica", 'B', 12)
            pdf.set_text_color(30, 64, 175) # Bleu foncé
            pdf.cell(0, 8, "Prochaine étape :", ln=1)
            
            pdf.set_font("helvetica", '', 11)
            pdf.set_text_color(50, 50, 50)
            contenu = ligne.split(":", 1)[1].strip()
            pdf.multi_cell(0, 6, txt=f"  • {contenu}")
            pdf.ln(4)
            
        # E. Autre texte générique
        else:
            # S'il y a un texte d'introduction type "Voici ton bilan :"
            if "voici" in ligne.lower():
                continue # On l'ignore pour alléger le PDF
            pdf.set_font("helvetica", '', 11)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 6, txt=ligne)
            pdf.ln(2)
            
    return pdf.output()

**Qu'est-ce qui va changer à l'écran pour l'élève ?**
* Au lieu d'un gros bloc de texte, le PDF génèrera des sections distinctes avec des titres en gras, colorés et aérés (Les acquis en vert, les erreurs en rouge, les pièges en orange).
* La syntaxe `$\$f(x)=ax\$.$` se transformera automatiquement en `f(x)=ax`.
* Les tirets brouillons seront remplacés par des puces `•` avec indentation.

Mettez simplement à jour ce fichier `generateur_pdf.py` sur GitHub et la mise en forme s'appliquera instantanément à vos prochains téléchargements !
