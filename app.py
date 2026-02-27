import streamlit as st
import google.generativeai as genai
import PyPDF2

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Tuteur Socratique", page_icon="🧠", layout="centered")
st.title("🧠 Ton Tuteur de Révision Socratique")
st.markdown("*Outil anonyme : Ne saisis aucune donnée personnelle (nom, prénom) dans ce chat.*")

# --- INITIALISATION DE L'API GEMINI ---
# L'application va chercher la clé secrète que vous aurez configurée sur le serveur
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Clé API introuvable. Le professeur doit configurer les 'Secrets' de l'application.")
    st.stop()

# --- FONCTION POUR LIRE LES PDF ---
def extraire_texte_pdf(fichier):
    lecteur = PyPDF2.PdfReader(fichier)
    texte = ""
    for page in lecteur.pages:
        texte += page.extract_text() + "\n"
    return texte

# --- BARRE LATÉRALE (RÉGLAGES DE L'ÉLÈVE) ---
with st.sidebar:
    st.header("⚙️ Paramètres de révision")
    
    niveau_eleve = st.radio("Ton niveau sur ce chapitre :", ["Novice", "Avancé"])
    objectif_eleve = st.radio("Ton objectif :", ["Mode A : Mémorisation (Bases)", "Mode B : Compréhension (Profondeur)"])
    
    st.markdown("---")
    st.header("📚 Ton Cours")
    fichier_upload = st.file_uploader("Glisse ton cours ici (PDF ou TXT)", type=["pdf", "txt"])
    texte_manuel = st.text_area("...ou copie-colle ton texte ici :")

# --- PRÉPARATION DU TEXTE DU COURS ---
texte_cours = ""
if fichier_upload is not None:
    if fichier_upload.name.endswith('.pdf'):
        texte_cours = extraire_texte_pdf(fichier_upload)
    else:
        texte_cours = fichier_upload.read().decode("utf-8")
elif texte_manuel:
    texte_cours = texte_manuel

# --- LE CERVEAU PÉDAGOGIQUE (VOTRE PROMPT) ---
if texte_cours:
    # 1. Base commune & Rôle
    prompt_systeme = f"""
    # RÔLE & OBJECTIF
    Tu es un expert en ingénierie pédagogique cognitive et un spécialiste technique EdTech.
    Ta mission est de transformer des contenus bruts en activités d'apprentissage en appliquant strictement les principes scientifiques ci-dessous.
    
    Base-toi exclusivement sur ce texte pour le fond : {texte_cours}
    
    # FORMAT ATTENDU : MODE INTERACTIF
    Pose une question à la fois. Attends la réponse. Analyse l'erreur. Donne le feedback.
    Ne donne jamais la solution directement avant que l'élève n'ait essayé. Guide-le.
    """

    # 2. Injection de la Constitution Pédagogique selon l'objectif
    if "Mode A" in objectif_eleve:
        prompt_systeme += """
        # LA "CONSTITUTION" PÉDAGOGIQUE
        ## MODE A : ANCRAGE & MÉMORISATION (Testing Effect)
        * Principe : Se tester (récupération active) consolide la mémoire.
        * Règle de l'Information Minimale : Une question = Un seul savoir atomique.
        * STRATÉGIE DES LEURRES (Distracteurs) : Ne jamais générer de remplissage aléatoire. Utilise exclusivement ces 3 stratégies pour créer les mauvaises réponses :
           1. La Confusion de Concepts : Utilise un terme proche (champ lexical identique) mais de définition différente.
           2. L'Erreur de "Bon Sens" : La réponse intuitive mais fausse (celle que donnerait un novice complet).
           3. L'Inversion de Causalité : Inverse la cause et l'effet ou l'ordre des étapes.
        * RÈGLE D'HOMOGÉNÉITÉ : Les leurres doivent avoir la même longueur, la même structure grammaticale et le même niveau de langage que la bonne réponse.
        * Feedback : Explique toujours POURQUOI la réponse est juste ou fausse.
        """
    else:
        prompt_systeme += """
        # LA "CONSTITUTION" PÉDAGOGIQUE
        ## MODE B : COMPRÉHENSION & TRANSFERT (Apprentissage Génératif)
        * Principe : L'élève doit construire du sens (Processus SOI : Sélectionner, Organiser, Intégrer).
        * MENU GÉNÉRATIF (Choisis la stratégie la plus pertinente) :
           1. Transformation : Convertir un texte en schéma ou processus.
           2. Comparaison Structurée : Tableau (Ressemblances/Différences/Limites).
           3. Auto-explication : Verbaliser le pourquoi d'une étape.
           4. Cartographie : Hiérarchiser les concepts.
           5. Contre-Exemple : Identifier les limites de la règle.
        """

    # 3. Injection de l'Échafaudage selon le niveau
    if niveau_eleve == "Novice":
        prompt_systeme += """
        # ÉCHAFAUDAGE
        * Pour les NOVICES : Utilise le "Completion Problem Effect" (Schémas à compléter, Textes à trous, Tableaux partiels).
        """
    else:
        prompt_systeme += """
        # ÉCHAFAUDAGE
        * Pour les EXPERTS : Utilise des prompts ouverts ("Analysez...", "Critiquez...").
        """

    # 4. Garde-fous finaux
    prompt_systeme += """
    # GARDE-FOUS
    * Base-toi exclusivement sur le texte fourni pour le fond.
    * Applique la Constitution Pédagogique pour la forme.
    * PROPRETÉ : Ne laisse jamais de balises techniques type [cite] ou [source] dans le résultat final.
    """

# --- GESTION DU CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LANCEMENT DE L'IA ---
if texte_cours:
    # Création du modèle avec vos instructions
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        system_instruction=prompt_systeme
    )
    
    # Lancement de la session de chat IA
    chat = model.start_chat(history=[])
    
    # Message de démarrage automatique si le chat est vide
    if not st.session_state.messages:
        with st.spinner("Le tuteur lit ton cours..."):
            reponse_initiale = chat.send_message("Bonjour, j'ai fourni mon cours. Peux-tu te présenter et me poser la première question selon mes paramètres ?")
            st.session_state.messages.append({"role": "assistant", "content": reponse_initiale.text})
            st.rerun()

    # Zone de saisie pour l'élève
    if prompt := st.chat_input("Ta réponse..."):
        # 1. On affiche le message normal pour l'élève
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 2. INJECTION INVISIBLE : On force l'IA à changer de cap
        prompt_enrichi = f"{prompt}\n\n[DIRECTIVE SYSTÈME STRICTE : L'élève est actuellement en {objectif_eleve} et niveau {niveau_eleve}. Tu DOIS impérativement changer ta façon de poser la prochaine question pour respecter la Constitution Pédagogique de ce mode, même si cela casse la dynamique de tes messages précédents.]"
        
        with st.chat_message("assistant"):
            # On recrée l'historique
            hist = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat.history = hist
            
            # 3. L'IA génère sa réponse
            reponse = chat.send_message(prompt_enrichi)
            
            # 4. On affiche et on sauvegarde
            st.markdown(reponse.text)
            st.session_state.messages.append({"role": "assistant", "content": reponse.text})
        
        # Obtenir et afficher la réponse de l'IA
        with st.chat_message("assistant"):
            with st.spinner("Le tuteur réfléchit..."):
                # On recrée l'historique pour l'API Gemini à partir de notre session
                historique_gemini = []
                for msg in st.session_state.messages[:-1]: # Tout sauf le dernier message de l'user
                    role = "user" if msg["role"] == "user" else "model"
                    historique_gemini.append({"role": role, "parts": [msg["content"]]})
                
                chat.history = historique_gemini
                reponse = chat.send_message(prompt_eleve)
                st.markdown(reponse.text)
                
        st.session_state.messages.append({"role": "assistant", "content": reponse.text})
else:

    st.info("👈 Commence par sélectionner ton niveau, ton objectif, et charge un cours dans la barre latérale gauche pour activer le tuteur !")








