import streamlit as st
import google.generativeai as genai
import PyPDF2
import io
import time

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Ton tuteur de révision", page_icon="🦉", layout="centered")

# --- INITIALISATION DE L'HISTORIQUE ET DU CARNET ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "carnet_ia" not in st.session_state:
    st.session_state.carnet_ia = "Aucune information. L'élève vient de commencer."

# La session est considérée en cours dès que l'élève a envoyé son premier message (len > 1 car le message 1 est l'intro de l'IA)
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
    
# --- API KEY ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Clé API introuvable. Configurez 'GEMINI_API_KEY' dans les Secrets.")
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
        if st.button("🔄 Changer de mode (Nouvelle session)", use_container_width=True):
            st.session_state.messages = []
            st.session_state.carnet_ia = "Aucune information. L'élève vient de commencer."
            st.rerun()

    # --- AFFICHAGE DU CARNET DE BORD ---
    st.markdown("---")
    st.header("🧠 Profil de l'élève")
    st.markdown("*Notes internes de l'IA :*")
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
    prompt_systeme = f"""
    # RÔLE & OBJECTIF
    Tu es un expert en ingénierie pédagogique cognitive. Ta mission est de transformer des contenus bruts en activités d'apprentissage.
    Base-toi exclusivement sur ce texte pour le fond : {texte_cours}
    
    # 📋 CARNET DE BORD DE L'ÉLÈVE
    Voici ce que tu as déjà identifié sur cet élève au cours de la session :
    {st.session_state.carnet_ia}
    Utilise ces notes pour adapter ton niveau de vocabulaire et cibler ses faiblesses.

    # 🧠 POSTURE DU COACH COGNITIF
    Ton objectif absolu est de réduire la distance entre la compréhension actuelle de l'élève et la compréhension visée. Pose UNE SEULE question à la fois. Attends la réponse.
    RÈGLE D'OR : Tu ne dois JAMAIS donner la réponse finale directement. Fournis une information qui permet à l'élève de corriger sa propre trajectoire.
    """

    # --- ARBRE DE DÉCISION CSEN ---
    if niveau_eleve == "Novice":
        prompt_systeme += """
        ## 🌳 ARBRE DE DÉCISION DU FEEDBACK (PROFIL NOVICE)
        L'élève est NOVICE, bloqué ou potentiellement incertain. Il construit sa compétence.
        * INTERDICTION ABSOLUE : N'utilise JAMAIS le feedback d'autorégulation. Ne lui demande pas de s'auto-évaluer ou de juger sa méthode.
        * RÈGLE ACTIVE : Utilise EXCLUSIVEMENT le Modèle de l'Instruction et le "Feedback de Processus" très directif :
           1. Indices de correction : Pointe l'endroit précis de l'erreur ou donne la méthode de base étape par étape pour le rassurer.
           2. Sollicite l'amélioration : Aide-le à franchir le petit obstacle immédiat sans le noyer.
           3. Attributions causales : Explique de manière rassurante et explicite pourquoi une méthode marche ou ne marche pas.
        """
    else:
        prompt_systeme += """
        ## 🌳 ARBRE DE DÉCISION DU FEEDBACK (PROFIL AVANCÉ)
        L'élève est AVANCÉ. Il a déjà les bases et une confiance élevée, mais il peut faire des étourderies.
        * SI ERREUR DE MÉTHODE -> Active le "Feedback de Processus" (Donne des indices sur la stratégie, demande d'appliquer une méthode alternative).
        * SI ÉTOURDERIE OU ERREUR ALORS QU'IL SEMBLE SÛR DE LUI -> Active le "Feedback d'Autorégulation" pour créer un choc cognitif :
           1. Contrôle interne : Force-le à s'auto-évaluer pour qu'il devienne son propre contrôleur qualité (ex: "À ton avis, as-tu oublié une donnée ? Vérifie.").
           2. Monitoring : Questionne sa vigilance (ex: "As-tu pris le temps de vérifier ton calcul à cette étape ?").
           3. Dédramatisation : Rappelle que l'erreur est normale quand on va vite.
        """

    prompt_systeme += """
    ## 🛑 LES ANTI-PROMPTS (INTERDICTIONS STRICTES) :
    - INTERDICTION de juger la personne (Le "Soi"). Reste sur la tâche.
    - INTERDICTION du feedback stéréotypé isolé : Ne dis JAMAIS juste "C'est faux" ou "C'est juste" sans fournir d'explication.
    - INTERDICTION de comparaison sociale.
    - INTERDICTION des félicitations imméritées ou génériques. Explique toujours précisément POURQUOI c'est bien.
    """

    if "Mode A" in objectif_eleve:
        prompt_systeme += """
        # CONSTITUTION PÉDAGOGIQUE - MODE A : MÉMORISATION
        * Règle de l'Information Minimale : Une question = Un seul savoir atomique.
        * STRATÉGIE DES LEURRES : Confusion de Concepts, Erreur de "Bon Sens", Inversion de Causalité.
        """
        if niveau_eleve == "Novice":
            prompt_systeme += "* ÉCHAFAUDAGE (NOVICE) : Utilise exclusivement des QCM. Va à la ligne pour chaque proposition avec une ligne vide entre chaque choix."
        else:
            prompt_systeme += "* ÉCHAFAUDAGE (AVANCÉ) : Utilise exclusivement le Rappel Libre sans aucun choix."

    else:
        prompt_systeme += """
        # CONSTITUTION PÉDAGOGIQUE - MODE B : COMPRÉHENSION
        * MENU GÉNÉRATIF : Transformation, Comparaison Structurée, Auto-explication, Cartographie, ou Contre-Exemple.
        """
        if niveau_eleve == "Novice":
            prompt_systeme += "* ÉCHAFAUDAGE (NOVICE) : Utilise le Completion Problem Effect (Schémas à compléter, Textes à trous...)."
        else:
            prompt_systeme += "* ÉCHAFAUDAGE (AVANCÉ) : Prompts ouverts purs. Ne donne aucune structure de départ."

    prompt_systeme += """
    # GARDE-FOUS FINAUX
    * Base-toi exclusivement sur le texte. Ne laisse jamais de balises techniques dans le résultat.
    """

    # --- INITIALISATION DE L'IA ---
    model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=prompt_systeme)
    chat = model.start_chat(history=[])

    # --- AFFICHAGE DE L'HISTORIQUE ---
    for msg in st.session_state.messages:
        avatar_chat = "avatar_tuteur.png" if msg["role"] == "assistant" else "avatar_eleve.png"
        with st.chat_message(msg["role"], avatar=avatar_chat):
            st.markdown(msg["content"])

    # --- PREMIER MESSAGE DU TUTEUR ---
    if not st.session_state.messages:
        with st.spinner("Analyse du cours en cours..."):
            res = chat.send_message("Présente-toi brièvement et pose la première question selon mes réglages.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.rerun()

    # --- GESTION DES MESSAGES DE L'ÉLÈVE ---
    if prompt := st.chat_input("Ta réponse..."):
        st.chat_message("user", avatar="avatar_eleve.png").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant", avatar="avatar_tuteur.png"):
            
            # 1. OPTIMISATION : LA FENÊTRE GLISSANTE
            # On ne garde que les 4 derniers messages de l'historique pour une vitesse maximale constante
            memoire_courte = st.session_state.messages[:-1][-4:]
            hist = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in memoire_courte]
            chat.history = hist
            
            # 2. AFFICHAGE FLUIDE DE LA RÉPONSE
            reponse = chat.send_message(prompt, stream=True)
            
            def generer_flux_lisse():
                for chunk in reponse:
                    mots = chunk.text.split(" ")
                    for mot in mots:
                        yield mot + " "
                        time.sleep(0.03) 
                        
            texte_complet = st.write_stream(generer_flux_lisse())
            st.session_state.messages.append({"role": "assistant", "content": texte_complet})
            
            # 3. MISE À JOUR SILENCIEUSE DU CARNET DE BORD
            nb_echanges = len(st.session_state.messages) // 2
            # Tous les 3 échanges, l'IA prend des notes
            if nb_echanges % 3 == 0 and nb_echanges > 0:
                with st.spinner("L'IA met à jour ses notes pédagogiques..."):
                    prompt_notes = f"Tu es superviseur pédagogique. Profil actuel : '{st.session_state.carnet_ia}'. Derniers échanges : {st.session_state.messages[-4:]}. Mets à jour ce profil en 2 phrases maximum. Indique les acquis et les erreurs récurrentes. Parle à la 3ème personne (ex: L'élève a compris...)."
                    nouveau_carnet = genai.GenerativeModel("gemini-2.5-flash").generate_content(prompt_notes)
                    st.session_state.carnet_ia = nouveau_carnet.text
            
            # On force le rechargement pour figer les boutons au 1er message, ou pour afficher le nouveau carnet
            if len(st.session_state.messages) == 3 or (nb_echanges % 3 == 0):
                st.rerun()

else:
    st.info("👈 Charge un cours dans la barre latérale pour activer ton tuteur !")
