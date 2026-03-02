import streamlit as st
import google.generativeai as genai
import PyPDF2
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Ton tuteur de révision", page_icon="🦉", layout="centered")

# --- INITIALISATION DE L'HISTORIQUE ET DU CARNET ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "carnet_ia" not in st.session_state:
    st.session_state.carnet_ia = "On commence tout juste ! Réponds à quelques questions pour que je puisse faire un point sur tes acquis."

session_en_cours = len(st.session_state.messages) > 1

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
    
    /* --- TEXTE AGRANDI DANS LE CHAT --- */
    [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] li {
        font-size: 1.15rem !important;
        line-height: 1.6 !important;
    }

    /* --- ANTI-LATENCE VISUELLE --- */
    div[data-testid="stChatMessage"], 
    div[data-testid="stMarkdownContainer"], 
    div[data-testid="stChatInput"] { opacity: 1 !important; filter: none !important; transition: none !important; }
    div[data-testid="stMainBlockContainer"] { opacity: 1 !important; }
    [data-testid="stChatInput"] { opacity: 1 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦉 Ton tuteur de révision")
st.markdown("*Outil anonyme : Ne saisis aucune donnée personnelle dans ce chat.*")

# --- TUTORIEL D'ACCUEIL ---
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
        Choisis ton mode et ton niveau.<br>
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
    
# --- API KEY ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Clé API introuvable.")
    st.stop()

# --- LECTURE PDF EN CACHE ---
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
        if st.button("🔄 Nouvelle session", use_container_width=True):
            st.session_state.messages = []
            st.session_state.carnet_ia = "On commence tout juste ! Réponds à quelques questions pour que je puisse faire un point sur tes acquis."
            if "chat" in st.session_state:
                del st.session_state.chat # Reset de la mémoire de l'IA pour la nouvelle session
            st.rerun()

    # --- NOUVEAU : BILAN D'ÉTAPE DIRECT ---
    st.markdown("---")
    st.header("📈 Ton Bilan d'Étape")
    st.info(st.session_state.carnet_ia)

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

# --- CONSTRUCTION DYNAMIQUE DU PROMPT ---
if texte_cours:
    # 1. ON INITIALISE LE CHAT UNE SEULE FOIS DANS LA SESSION
    if "chat" not in st.session_state:
        prompt_systeme = f"""
        # RÔLE & OBJECTIF
        Tu es un tuteur expert en pédagogie. Ta mission est d'enseigner le cours suivant : {texte_cours}

        # 🧠 POSTURE DU COACH (RÈGLES ABSOLUES)
        1. Pose UNE SEULE question à la fois. Attends la réponse.
        2. Ne donne JAMAIS la réponse finale ou un long cours théorique s'il se trompe.
        3. RÈGLE ANTI-BAVARDAGE : Tes feedbacks doivent être ultra-concis (2 à 3 phrases MAXIMUM). Va droit au but.
        """

        if niveau_eleve == "Novice":
            prompt_systeme += """
            ## 🌳 ARBRE DE DÉCISION (PROFIL NOVICE)
            * N'utilise JAMAIS le feedback d'autorégulation ("Comment t'y es-tu pris ?").
            * Utilise le "Feedback de Processus" très directif et CONCIS :
               - Valide ce qui est juste (s'il y en a).
               - Pointe l'erreur factuellement SANS faire de cours magistral.
               - Pose une seule question facile pour l'aider à corriger son erreur pas à pas.
            """
        else:
            prompt_systeme += """
            ## 🌳 ARBRE DE DÉCISION (PROFIL AVANCÉ)
            * SI ERREUR DE MÉTHODE -> Feedback de Processus très concis (donne un indice stratégique).
            * SI ÉTOURDERIE OU ERREUR BÊTE -> Feedback d'Autorégulation :
               - Force-le à s'auto-évaluer (ex: "As-tu vérifié ton signe mathématique ?").
               - Ne corrige pas à sa place, oblige-le à relire son propre raisonnement.
            """

        prompt_systeme += """
        ## 🛑 ANTI-PROMPTS :
        - Pas de jugement sur la personne.
        - Pas de "C'est faux" sans petite explication.
        - Pas de longs paragraphes d'explication.
        """

        if "Mode A" in objectif_eleve:
            prompt_systeme += "* MODE MÉMORISATION : Teste un seul savoir atomique à la fois. "
            if niveau_eleve == "Novice":
                prompt_systeme += "Pose uniquement des QCM (A, B, C) avec des retours à la ligne."
            else:
                prompt_systeme += "Utilise le Rappel Libre pur (sans QCM)."
        else:
            prompt_systeme += "* MODE COMPRÉHENSION : Demande à l'élève d'expliquer, de comparer ou de transformer l'information. "

        model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=prompt_systeme)
        # On sauvegarde la session de chat. Elle gardera son propre historique automatiquement !
        st.session_state.chat = model.start_chat(history=[])

    # --- AFFICHAGE DE L'HISTORIQUE ---
    for msg in st.session_state.messages:
        avatar_chat = "avatar_tuteur.png" if msg["role"] == "assistant" else "avatar_eleve.png"
        with st.chat_message(msg["role"], avatar=avatar_chat):
            st.markdown(msg["content"])

    # --- PREMIER MESSAGE ---
    if not st.session_state.messages:
        with st.spinner("Analyse du cours en cours..."):
            res = st.session_state.chat.send_message("Présente-toi brièvement (1 phrase) et pose la première question.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.rerun()

    # --- GESTION DES MESSAGES UTILISATEUR ---
    if prompt := st.chat_input("Ta réponse..."):
        st.chat_message("user", avatar="avatar_eleve.png").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant", avatar="avatar_tuteur.png"):
            # PLUS BESOIN de manipuler l'historique manuellement, st.session_state.chat s'en charge !
            reponse = st.session_state.chat.send_message(prompt, stream=True)
            
            def generer_flux_rapide():
                for chunk in reponse:
                    yield chunk.text
                        
            texte_complet = st.write_stream(generer_flux_rapide())
            st.session_state.messages.append({"role": "assistant", "content": texte_complet})
            
            # MISE À JOUR DU BILAN (Tous les 3 échanges)
            nb_echanges = len(st.session_state.messages) // 2
            if nb_echanges % 3 == 0 and nb_echanges > 0:
                with st.spinner("Mise à jour du bilan..."):
                    prompt_notes = f"Tu es le tuteur. Bilan précédent : '{st.session_state.carnet_ia}'. Derniers échanges : {st.session_state.messages[-4:]}. Mets à jour ce bilan en t'adressant DIRECTEMENT à l'élève avec 'Tu'. Sois très factuel, précis et encourageant (2 phrases maximum)."
                    nouveau_carnet = genai.GenerativeModel("gemini-2.5-flash").generate_content(prompt_notes)
                    st.session_state.carnet_ia = nouveau_carnet.text
                    st.rerun() # On fait le rerun uniquement quand le bilan est prêt

else:
    st.info("👈 Charge un cours dans la barre latérale pour activer ton tuteur !")
