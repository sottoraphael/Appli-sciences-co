import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Ton tuteur de révision", page_icon="🦉", layout="centered")

# --- INITIALISATION DE LA SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# La session est en cours si le tuteur a posé sa première question
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
        Réponds aux questions dans le chat, et demande ton bilan à la fin !
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

# --- DIALOGUE BILAN FINAL ---
@st.dialog("📈 Ton Bilan de Révision")
def afficher_bilan():
    if "chat" in st.session_state:
        with st.spinner("L'IA analyse tes réponses et rédige ton bilan..."):
            prompt_bilan = "La session est terminée. Fais un bilan métacognitif factuel et encourageant de cette révision. Adresse-toi directement à l'élève avec 'Tu'. Synthétise ce qu'il a bien maîtrisé, et les points (méthode ou connaissances) qu'il doit encore consolider. Ne pose plus de question."
            reponse = st.session_state.chat.send_message(prompt_bilan)
            st.success(reponse.text)
    else:
        st.warning("Aucune session en cours à analyser.")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    niveau_eleve = st.radio("Ton niveau :", ["Novice", "Avancé"], disabled=session_en_cours)
    objectif_eleve = st.radio("Ton objectif :", ["Mode A : Mémorisation", "Mode B : Compréhension"], disabled=session_en_cours)
    
    if session_en_cours:
        st.info("🔒 Paramètres verrouillés pendant la révision.")
        
        # Le fameux bouton Bilan Différé
        if st.button("🏁 Terminer et voir mon bilan", use_container_width=True, type="primary"):
            afficher_bilan()
            
        st.markdown("---")
        if st.button("🔄 Nouvelle session", use_container_width=True):
            # Nettoyage de la mémoire et des fichiers chez Google
            if "file_id" in st.session_state:
                try:
                    genai.delete_file(st.session_state.file_id)
                except Exception:
                    pass
                del st.session_state.file_id
            if "chat" in st.session_state:
                del st.session_state.chat
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    st.header("🧭 Ton Cours")
    fichier_upload = st.file_uploader("Cours (PDF)", type=["pdf"])
    texte_manuel = st.text_area("Ou colle ton texte ici :")

# --- CONSTRUCTION DE LA CONSTITUTION PÉDAGOGIQUE (LE CERVEAU) ---
prompt_systeme = """
# RÔLE & OBJECTIF
Tu es un tuteur expert en pédagogie et sciences cognitives. Ta mission est d'enseigner le cours fourni.

# 🧠 POSTURE DU COACH (RÈGLES ABSOLUES)
1. Pose UNE SEULE question à la fois. Attends la réponse.
2. Ne donne JAMAIS la réponse finale ou un long cours théorique s'il se trompe.
3. RÈGLE ANTI-BAVARDAGE : Tes feedbacks doivent être ultra-concis (2 à 3 phrases MAXIMUM). Va droit au but.
"""

if niveau_eleve == "Novice":
    prompt_systeme += """
    ## 🌳 ARBRE DE DÉCISION (PROFIL NOVICE)
    L'élève construit sa compétence. 
    * N'utilise JAMAIS le feedback d'autorégulation ("Comment t'y es-tu pris ?").
    * Utilise EXCLUSIVEMENT le "Feedback de Processus" très directif et CONCIS :
       - Pointe l'erreur factuellement SANS faire de cours magistral.
       - Pose une question de guidage pas-à-pas.
    """
else:
    prompt_systeme += """
    ## 🌳 ARBRE DE DÉCISION (PROFIL AVANCÉ)
    L'élève a déjà les bases.
    * SI ERREUR DE MÉTHODE -> Feedback de Processus très concis (donne un indice stratégique).
    * SI ÉTOURDERIE OU ERREUR ALORS QU'IL SEMBLE SÛR DE LUI -> Feedback d'Autorégulation :
       - Force-le à s'auto-évaluer (ex: "As-tu vérifié ton signe ?").
       - Oblige-le à relire son propre raisonnement pour créer un choc cognitif.
    """

prompt_systeme += """
## 🛑 ANTI-PROMPTS :
- Pas de jugement sur la personne ("Tu es nul", "Tu es doué").
- Pas de "C'est faux" sans petite explication.
- Pas de comparaison aux autres.
"""

if "Mode A" in objectif_eleve:
    prompt_systeme += """
    # MODE MÉMORISATION (Testing Effect)
    * Teste un seul savoir atomique à la fois.
    * Stratégie des leurres : Confusion de concepts, Erreur de bon sens, Inversion de causalité.
    """
    if niveau_eleve == "Novice":
        prompt_systeme += "* Utilise exclusivement des QCM (A, B, C) avec retours à la ligne."
    else:
        prompt_systeme += "* Utilise exclusivement le Rappel Libre pur (sans QCM ni indices)."
else:
    prompt_systeme += """
    # MODE COMPRÉHENSION (Apprentissage Génératif)
    * Demande à l'élève d'expliquer, de comparer ou de transformer l'information.
    """
    if niveau_eleve == "Novice":
        prompt_systeme += "* Utilise le Completion Problem Effect (Textes à trous, schémas partiels)."
    else:
        prompt_systeme += "* Prompts ouverts purs. Laisse l'élève structurer sa réponse."

# --- LOGIQUE DE DÉMARRAGE ET GESTION FICHIER (API FILE) ---
if (fichier_upload or texte_manuel) and "chat" not in st.session_state:
    
    # 1. GESTION DU DOCUMENT (Vitesse maximisée)
    historique_initial = []
    
    if fichier_upload and "file_id" not in st.session_state:
        # Création d'un fichier temporaire propre
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(fichier_upload.getvalue())
            tmp_path = tmp.name
            
        with st.spinner("Envoi sécurisé du cours vers l'IA..."):
            # Upload via l'API File : Le PDF n'est lu qu'UNE SEULE FOIS !
            fichier_ia = genai.upload_file(tmp_path)
            st.session_state.file_id = fichier_ia.name
        os.remove(tmp_path)
        
        # On injecte le fichier de l'API dans le contexte initial
        f_obj = genai.get_file(st.session_state.file_id)
        historique_initial = [
            {"role": "user", "parts": [f_obj, "Voici mon document de cours. Base-toi exclusivement dessus."]},
            {"role": "model", "parts": ["C'est bien noté. Je me baserai exclusivement sur ce document. Je suis prêt."]}
        ]
        
    elif texte_manuel:
        # Cas du texte collé
        historique_initial = [
            {"role": "user", "parts": [f"Voici mon texte de cours :\n{texte_manuel}\n\nBase-toi exclusivement dessus."]},
            {"role": "model", "parts": ["C'est bien noté. Je suis prêt."]}
        ]

    # 2. INITIALISATION DU CERVEAU DE L'IA DANS LA SESSION
    model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=prompt_systeme)
    st.session_state.chat = model.start_chat(history=historique_initial)

    # 3. PREMIÈRE QUESTION AUTOMATIQUE
    with st.spinner("Analyse du cours..."):
        res = st.session_state.chat.send_message("Présente-toi brièvement (1 phrase) et pose la première question.")
        st.session_state.messages.append({"role": "assistant", "content": res.text})
        st.rerun()

# --- AFFICHAGE DE L'HISTORIQUE VISUEL ---
for msg in st.session_state.messages:
    avatar_chat = "avatar_tuteur.png" if msg["role"] == "assistant" else "avatar_eleve.png"
    with st.chat_message(msg["role"], avatar=avatar_chat):
        st.markdown(msg["content"])

# --- GESTION DU DIALOGUE (LA VITESSE PURE) ---
if "chat" in st.session_state:
    if prompt := st.chat_input("Ta réponse..."):
        # Affichage du message de l'élève
        st.chat_message("user", avatar="avatar_eleve.png").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Appel direct à l'IA sans tout recharger !
        with st.chat_message("assistant", avatar="avatar_tuteur.png"):
            reponse = st.session_state.chat.send_message(prompt, stream=True)
            
            def generer_flux_rapide():
                for chunk in reponse:
                    yield chunk.text
                        
            texte_complet = st.write_stream(generer_flux_rapide())
            st.session_state.messages.append({"role": "assistant", "content": texte_complet})
            
            # Rechargement pour figer les boutons lors du premier message de l'élève
            if len(st.session_state.messages) == 3:
                st.rerun()
elif not fichier_upload and not texte_manuel:
    st.info("👈 Charge un cours dans la barre latérale pour activer ton tuteur !")
