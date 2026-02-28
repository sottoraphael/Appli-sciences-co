import streamlit as st
import google.generativeai as genai
import PyPDF2

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Tuteur Socratique", page_icon="🧠", layout="centered")
st.title("🧠 Ton Tuteur de Révision Socratique")
st.markdown("*Outil anonyme : Ne saisis aucune donnée personnelle dans ce chat.*")

# --- INITIALISATION DE L'API GEMINI ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Clé API introuvable. Configurez 'GEMINI_API_KEY' dans les Secrets.")
    st.stop()

# --- FONCTION POUR LIRE LES PDF ---
def extraire_texte_pdf(fichier):
    lecteur = PyPDF2.PdfReader(fichier)
    texte = ""
    for page in lecteur.pages:
        texte += page.extract_text() + "\n"
    return texte

# --- BARRE LATÉRALE (RÉGLAGES) ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    niveau_eleve = st.radio("Ton niveau :", ["Novice", "Avancé"])
    objectif_eleve = st.radio("Ton objectif :", ["Mode A : Mémorisation", "Mode B : Compréhension"])
    
    st.markdown("---")
    st.header("📚 Ton Cours")
    fichier_upload = st.file_uploader("Cours (PDF/TXT)", type=["pdf", "txt"])
    texte_manuel = st.text_area("Ou colle ton texte ici :")

# --- EXTRACTION DU CONTENU ---
texte_cours = ""
if fichier_upload:
    if fichier_upload.name.endswith('.pdf'):
        texte_cours = extraire_texte_pdf(fichier_upload)
    else:
        texte_cours = fichier_upload.read().decode("utf-8")
elif texte_manuel:
    texte_cours = texte_manuel

# --- CONSTRUCTION DYNAMIQUE DU PROMPT (VERSION INTÉGRALE) ---
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

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Configuration du modèle
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash"
        system_instruction=prompt_systeme
    )
    chat = model.start_chat(history=[])

    # --- AFFICHAGE DE L'HISTORIQUE ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        # On définit l'avatar selon le rôle
        avatar_chat = "avatar_tuteur.png" if msg["role"] == "assistant" else None # Remplacez None par "avatar_eleve.png" quand vous l'aurez
        with st.chat_message(msg["role"], avatar=avatar_chat):
            st.markdown(msg["content"])

    # --- GESTION DU PREMIER MESSAGE ---
    if not st.session_state.messages:
        with st.spinner("Analyse du cours..."):
            res = chat.send_message("Présente-toi brièvement et pose la première question selon mes réglages.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.rerun()

    # --- SAISIE ET ENVOI DE LA RÉPONSE DE L'ÉLÈVE ---
    if prompt := st.chat_input("Ta réponse..."):
        # On affiche le message normal pour l'élève
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # INJECTION INVISIBLE : On force l'IA à changer de cap
        prompt_enrichi = f"{prompt}\n\n[DIRECTIVE SYSTÈME STRICTE : L'élève est actuellement en {objectif_eleve} et niveau {niveau_eleve}. Tu DOIS impérativement changer ta façon de poser la prochaine question pour respecter la Constitution Pédagogique de ce mode, même si cela casse la dynamique de tes messages précédents.]"
        
        with st.chat_message("assistant", avatar="avatar_tuteur.png"):
            # On recrée l'historique
            hist = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat.history = hist
            
            # L'IA génère sa réponse
            reponse = chat.send_message(prompt_enrichi)
            
            # On affiche et on sauvegarde
            st.markdown(reponse.text)
            st.session_state.messages.append({"role": "assistant", "content": reponse.text})
else:
    st.info("👈 Charge un cours dans la barre latérale pour activer ton tuteur !")



