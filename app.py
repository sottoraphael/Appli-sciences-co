import streamlit as st
import google.generativeai as genai
import PyPDF2

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Ton tuteur de révision", page_icon="🦉", layout="centered")

# --- CUSTOM CSS (DESIGN MODERNE ET LISIBLE) ---
st.markdown("""
    <style>
    /* Fond de la page principale */
    .stApp {
        background-color: #FFFDF9;
    }
    
    /* Couleur de la barre latérale - Moderne et élégant (Gris-Bleu très clair) */
    [data-testid="stSidebar"] {
        background-color: #F0F4F8; 
        border-right: 1px solid #E2E8F0; /* Petite bordure propre */
    }
    
    /* Grossir les titres des options "Ton niveau" et "Ton objectif" */
    .stRadio > label {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #2D3748 !important;
        padding-bottom: 5px;
    }
    
    /* Grossir légèrement les choix (Novice, Avancé...) */
    .stRadio p {
        font-size: 1.05rem !important;
    }
    
    /* Style des boutons et éléments interactifs */
    .stButton>button {
        background-color: #5B9BD5;
        color: white;
        border-radius: 10px;
        border: none;
    }
    
    /* Titres plus doux */
    h1, h2, h3 {
        color: #2D3748;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Bulles de chat */
    [data-testid="stChatMessage"] {
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🦉 Ton tuteur de révision")
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
    st.header("🧭 Ton Cours")
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

# --- CONSTRUCTION DYNAMIQUE DU PROMPT ---
if texte_cours:
    prompt_systeme = f"""
    # RÔLE & OBJECTIF
    Tu es un expert en ingénierie pédagogique cognitive et un spécialiste technique EdTech.
    Ta mission est de transformer des contenus bruts en activités d'apprentissage en appliquant strictement les principes scientifiques ci-dessous.
    Base-toi exclusivement sur ce texte pour le fond : {texte_cours}
    # FORMAT ATTENDU : MODE INTERACTIF
    Pose une question à la fois. Attends la réponse. Analyse l'erreur. Donne le feedback.
    Ne donne jamais la solution directement avant que l'élève n'ait essayé. Guide-le.
    """

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
        
        # --- ÉCHAFAUDAGE SPÉCIFIQUE AU MODE A ---
        if niveau_eleve == "Novice":
            prompt_systeme += """
            # ÉCHAFAUDAGE (NOVICE)
            * Utilise exclusivement des questions à choix multiples (QCM) en appliquant strictement la stratégie des leurres ci-dessus pour faciliter la reconnaissance.
            """
        else:
            prompt_systeme += """
            # ÉCHAFAUDAGE (AVANCÉ)
            * Utilise exclusivement le "Rappel Libre". Pose une question directe et précise sans proposer AUCUN choix, indice ou leurre. L'élève doit formuler la réponse seul.
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

        # --- ÉCHAFAUDAGE SPÉCIFIQUE AU MODE B ---
        if niveau_eleve == "Novice":
            prompt_systeme += """
            # ÉCHAFAUDAGE (NOVICE)
            * Utilise le "Completion Problem Effect" (Schémas à compléter, Textes à trous, Tableaux partiels fournis par tes soins pour réduire la charge cognitive).
            """
        else:
            prompt_systeme += """
            # ÉCHAFAUDAGE (AVANCÉ)
            * Utilise des prompts ouverts ("Analysez...", "Critiquez...", "Crée un tableau comparatif complet"). Ne donne aucune structure de départ, laisse l'élève l'organiser.
            """

    prompt_systeme += """
    # GARDE-FOUS
    * Base-toi exclusivement sur le texte fourni pour le fond.
    * Applique la Constitution Pédagogique pour la forme.
    * PROPRETÉ : Ne laisse jamais de balises techniques type [cite] ou [source] dans le résultat final.
    """

    # --- GESTION DU MODELE ---
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=prompt_systeme
    )
    chat = model.start_chat(history=[])

    # --- AFFICHAGE DE L'HISTORIQUE ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # BOUCLE UNIQUE D'AFFICHAGE (Fini les doublons !)
    for msg in st.session_state.messages:
        # L'IA utilise le hibou, l'élève utilisera le sien plus tard (pour l'instant, c'est l'émoji par défaut)
        avatar_chat = "avatar_tuteur.png" if msg["role"] == "assistant" else "avatar_eleve.png"
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
        st.chat_message("user", avatar="avatar_eleve.png").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        prompt_enrichi = f"{prompt}\n\n[DIRECTIVE SYSTÈME STRICTE : L'élève est actuellement en {objectif_eleve} et niveau {niveau_eleve}. Tu DOIS impérativement changer ta façon de poser la prochaine question pour respecter la Constitution Pédagogique de ce mode, même si cela casse la dynamique de tes messages précédents.]"
        
        with st.chat_message("assistant", avatar="avatar_tuteur.png"):
            hist = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat.history = hist
            
            reponse = chat.send_message(prompt_enrichi)
            st.markdown(reponse.text)
            st.session_state.messages.append({"role": "assistant", "content": reponse.text})
else:
    st.info("👈 Charge un cours dans la barre latérale pour activer ton tuteur !")




