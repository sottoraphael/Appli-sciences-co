import streamlit as st
import google.generativeai as genai
import PyPDF2
import io
import time

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Ton tuteur de révision", page_icon="🦉", layout="centered")

# --- INITIALISATION DE L'HISTORIQUE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

session_en_cours = len(st.session_state.messages) > 0

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFDF9; }
    [data-testid="stSidebar"] { background-color: #F0F4F8; border-right: 1px solid #E2E8F0; }
    .stRadio > label { font-size: 1.25rem !important; font-weight: 600 !important; color: #2D3748 !important; padding-bottom: 5px; }
    .stRadio p { font-size: 1.05rem !important; }
    .stButton>button { background-color: #5B9BD5; color: white; border-radius: 10px; border: none; }
    h1, h2, h3 { color: #2D3748; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    [data-testid="stChatMessage"] { border-radius: 15px; }
    
    [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] li {
        font-size: 1.15rem !important;
        line-height: 1.6 !important;
    }

    div[data-testid="stChatMessage"], 
    div[data-testid="stMarkdownContainer"], 
    div[data-testid="stChatInput"] { opacity: 1 !important; filter: none !important; transition: none !important; }
    div[data-testid="stMainBlockContainer"] { opacity: 1 !important; }
    [data-testid="stChatInput"] { opacity: 1 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦉 Ton tuteur de révision")
st.markdown("*Outil anonyme : Ne saisis aucune donnée personnelle dans ce chat.*")

# --- TUTORIEL ---
@st.dialog("👋 Bienvenue sur ton tuteur de révision")
def afficher_tutoriel():
    st.markdown("""
        <style>
        .big-font { font-size: 1.25rem !important; line-height: 1.7 !important; color: #2D3748; }
        .step-title { font-weight: bold; color: #5B9BD5; font-size: 1.35rem; display: block; margin-top: 15px; }
        .mode-box { background-color: #F0F4F8; padding: 15px; border-radius: 12px; margin: 15px 0; border-left: 6px solid #5B9BD5; }
        </style>
        <div class="big-font">
        Ce tuteur utilise les <b>sciences cognitives</b> pour t'aider à réviser sans stress.<br>
        <div class="mode-box">
        <b>💡 Quel mode choisir ?</b><br><br>
        • <b>Mémorisation :</b> Pour retenir les définitions et les concepts "par cœur".<br><br>
        • <b>Compréhension :</b> Pour maîtriser ton cours en profondeur en l'expliquant avec tes propres mots.
        </div>
        <b>Comment l'utiliser en 3 étapes :</b><br>
        <span class="step-title">1. ⚙️ Règle ton tuteur</span>
        Choisis ton mode et ton niveau dans la barre à gauche.<br>
        <span class="step-title">2. 🧭 Donne-lui ton cours</span>
        Charge ton PDF ou colle ton texte.<br>
        <span class="step-title">3. 💬 Discute</span>
        Réponds aux questions dans le chat !
        </div>
        <br>
    """, unsafe_allow_html=True)
    if st.button("🚀 J'ai compris, c'est parti !", use_container_width=True):
        st.session_state.tutoriel_vu = True
        st.rerun()

if "tutoriel_vu" not in st.session_state:
    afficher_tutoriel()
    
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Clé API introuvable. Configurez 'GEMINI_API_KEY' dans les Secrets.")
    st.stop()

@st.cache_data
def obtenir_texte_cours(fichier_bytes, type_fichier):
    if type_fichier == "pdf":
        lecteur = PyPDF2.PdfReader(io.BytesIO(fichier_bytes))
        texte = ""
        for page in lecteur.pages:
            texte += page.extract_text() + "\n"
        return texte
    else:
        return fichier_bytes.decode("utf-8")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    niveau_eleve = st.radio("Ton niveau :", ["Novice", "Avancé"], disabled=session_en_cours)
    objectif_eleve = st.radio("Ton objectif :", ["Mode A : Mémorisation", "Mode B : Compréhension"], disabled=session_en_cours)
    
    if session_en_cours:
        st.info("🔒 Paramètres verrouillés pendant la révision.")
        if st.button("🔄 Changer de mode (Nouvelle session)", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    st.header("🧭 Ton Cours")
    fichier_upload = st.file_uploader("Cours (PDF/TXT)", type=["pdf", "txt"])
    texte_manuel = st.text_area("Ou colle ton texte ici :")

texte_cours = ""
if fichier_upload:
    bytes_data = fichier_upload.getvalue()
    type_f = "pdf" if fichier_upload.name.endswith('.pdf') else "txt"
    texte_cours = obtenir_texte_cours(bytes_data, type_f)
elif texte_manuel:
    texte_cours = texte_manuel

# --- CONSTRUCTION DYNAMIQUE DU PROMPT (AVEC LE NOUVEAU MOTEUR DE FEEDBACK) ---
if texte_cours:
    prompt_systeme = f"""
    # RÔLE & OBJECTIF
    Tu es un expert en ingénierie pédagogique cognitive et un spécialiste technique EdTech.
    Ta mission est de transformer des contenus bruts en activités d'apprentissage.
    Base-toi exclusivement sur ce texte pour le fond : {texte_cours}
    
    # 🧠 POSTURE ET GESTION DU FEEDBACK (COACH COGNITIF)
    Ton objectif absolu est de réduire la distance entre la compréhension actuelle de l'élève et la compréhension visée. Pose UNE SEULE question à la fois. Attends la réponse.
    RÈGLE D'OR : Tu ne dois JAMAIS donner la réponse finale directement. Fournis une information qui permet à l'élève de corriger sa propre trajectoire.

    ## ARBRE DE DÉCISION DU FEEDBACK (À appliquer à chaque réponse de l'élève) :
    1. SI ERREUR DE MÉTHODE OU BLOCAGE -> Active le "Feedback de Processus" :
       - Indices de correction : Pointe l'endroit de l'erreur ou suggère une piste sans donner la solution (ex: "As-tu pensé à utiliser tous les éléments ?").
       - Sollicite l'amélioration : Ne clos pas l'échange (ex: "Deux éléments sur trois sont corrects. Cherche le troisième.").
       - Attributions causales : Relie la réussite ou l'échec aux stratégies (ex: "Tu as réussi car tu es bien passé par les différentes étapes" ou "C'est faux car il te manque cette étape").

    2. SI ÉTOURDERIE, BONNE MÉTHODE MAIS ERREUR, OU DOUTE -> Active le "Feedback d'Autorégulation" :
       - Contrôle interne : Demande à l'élève de s'auto-évaluer (ex: "À ton avis, ta réponse est-elle correcte ? Vérifie-la.").
       - Monitoring : Questionne le suivi de la tâche (ex: "Comment t'y es-tu pris pour trouver ce résultat ?").
       - Dédramatisation : Présente toujours les erreurs comme des étapes normales et indispensables de l'apprentissage.

    ## 🛑 LES ANTI-PROMPTS (INTERDICTIONS STRICTES) :
    - INTERDICTION de juger la personne (Le "Soi") : Ne dis JAMAIS "Tu es nul", "Tu es brillant" ou "Tu es doué". Reste sur la tâche.
    - INTERDICTION du feedback stéréotypé isolé : Ne dis JAMAIS juste "C'est faux" ou "C'est juste" sans fournir d'explication sur le processus.
    - INTERDICTION de comparaison sociale : Ne compare JAMAIS l'élève aux autres ou à une moyenne.
    - INTERDICTION des félicitations imméritées ou génériques : Évite les "Bravo !" vagues. Explique toujours précisément POURQUOI c'est bien, car un succès immérité accroît l'incertitude.
    """

    # La suite reste identique pour les Niveaux et les Modes (Constitution Pédagogique)
    if "Mode A" in objectif_eleve:
        prompt_systeme += """
        # CONSTITUTION PÉDAGOGIQUE - MODE A : MÉMORISATION (Testing Effect)
        * Règle de l'Information Minimale : Une question = Un seul savoir atomique.
        * STRATÉGIE DES LEURRES : Utilise exclusivement ces 3 stratégies pour les mauvaises réponses : Confusion de Concepts, Erreur de "Bon Sens", Inversion de Causalité.
        * RÈGLE D'HOMOGÉNÉITÉ : Les leurres doivent avoir la même longueur et structure grammaticale que la bonne réponse.
        """
        if niveau_eleve == "Novice":
            prompt_systeme += """
            * ÉCHAFAUDAGE (NOVICE) : Utilise exclusivement des QCM. 
            * FORMATAGE VISUEL STRICT : Va à la ligne pour chaque proposition. Laisse une ligne vide entre chaque choix. (A) ... B) ... C) ...).
            """
        else:
            prompt_systeme += "* ÉCHAFAUDAGE (AVANCÉ) : Utilise exclusivement le Rappel Libre sans aucun choix."

    else:
        prompt_systeme += """
        # CONSTITUTION PÉDAGOGIQUE - MODE B : COMPRÉHENSION (Apprentissage Génératif)
        * MENU GÉNÉRATIF : Choisis parmi Transformation, Comparaison Structurée, Auto-explication, Cartographie, ou Contre-Exemple.
        """
        if niveau_eleve == "Novice":
            prompt_systeme += "* ÉCHAFAUDAGE (NOVICE) : Utilise le Completion Problem Effect (Schémas à compléter, Textes à trous...)."
        else:
            prompt_systeme += "* ÉCHAFAUDAGE (AVANCÉ) : Prompts ouverts purs. Ne donne aucune structure de départ."

    prompt_systeme += """
    # GARDE-FOUS FINAUX
    * Base-toi exclusivement sur le texte.
    * Ne laisse jamais de balises techniques type [cite] dans le résultat.
    """

    model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=prompt_systeme)
    chat = model.start_chat(history=[])

    for msg in st.session_state.messages:
        avatar_chat = "avatar_tuteur.png" if msg["role"] == "assistant" else "avatar_eleve.png"
        with st.chat_message(msg["role"], avatar=avatar_chat):
            st.markdown(msg["content"])

    if not st.session_state.messages:
        with st.spinner("Analyse du cours en cours..."):
            res = chat.send_message("Présente-toi brièvement et pose la première question selon mes réglages.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.rerun()

    if prompt := st.chat_input("Ta réponse..."):
        st.chat_message("user", avatar="avatar_eleve.png").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant", avatar="avatar_tuteur.png"):
            hist = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat.history = hist
            
            reponse = chat.send_message(prompt, stream=True)
            
            def generer_flux_lisse():
                for chunk in reponse:
                    mots = chunk.text.split(" ")
                    for mot in mots:
                        yield mot + " "
                        time.sleep(0.03) 
                        
            texte_complet = st.write_stream(generer_flux_lisse())
            st.session_state.messages.append({"role": "assistant", "content": texte_complet})
            
            if len(st.session_state.messages) == 2:
                st.rerun()
else:
    st.info("👈 Charge un cours dans la barre latérale pour activer ton tuteur !")
