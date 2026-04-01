import subprocess
import tempfile
import os

def generer_pdf_latex_bytes(code_latex: str) -> bytes:
    """
    Compile un code source LaTeX en PDF via un sous-processus.
    
    Paramètres :
    - code_latex (str) : Le code source brut à compiler.
    
    Retourne :
    - bytes : Le flux binaire du fichier PDF généré.
    """
    # Utilisation d'un répertoire temporaire nettoyé automatiquement
    with tempfile.TemporaryDirectory() as tempdir:
        tex_file_path = os.path.join(tempdir, "document.tex")
        pdf_file_path = os.path.join(tempdir, "document.pdf")

        # Écriture du code généré par le LLM
        with open(tex_file_path, "w", encoding="utf-8") as f:
            f.write(code_latex)

        # Commande de compilation silencieuse et sans interaction
        commande = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-output-directory", tempdir,
            tex_file_path
        ]

        try:
            # Exécution avec un délai d'attente strict (15s) pour prévenir le blocage du thread
            subprocess.run(commande, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)

            # Lecture et extraction du flux binaire
            with open(pdf_file_path, "rb") as f:
                pdf_bytes = f.read()
                
            return pdf_bytes

        except subprocess.CalledProcessError as e:
            # Extraction des derniers logs d'erreur pour le débogage
            log_erreur = e.stdout.decode('utf-8', errors='ignore')
            raise RuntimeError(f"Échec de la compilation LaTeX. Log : {log_erreur[-500:]}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Délai d'attente dépassé : la compilation a pris plus de 15 secondes.")
        except FileNotFoundError:
            raise RuntimeError("Le compilateur 'pdflatex' n'est pas détecté sur le système hôte.")
