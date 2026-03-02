import streamlit as st
import google.generativeai as genai
import tempfile
import os
from google.generativeai.types import HarmCategory, HarmBlockThreshold

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
    [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] li { font-size: 1.15rem !important; line-height: 1.6 !important; }
    div[data-testid="stChatMessage"], div[data-testid="stMarkdownContainer"], div[data-testid="stChatInput"] { opacity: 1 !important; filter: none !important; transition: none !important; }
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
        <span class="step-title">1. ⚙️ Règle ton tuteur</span> Choisis ton mode et ton niveau.<br>
        <span class="step-title">2. 🧭 Donne-lui ton cours</span> Charge ton PDF ou colle ton texte.<br>
        <span class="step-title">3. 💬 Discute</span> Réponds aux questions dans le chat, et demande ton bilan à la fin !
        </div><br>
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

# --- CONSTITUTION PÉDAGOGIQUE (LE CERVEAU) ---
# Je la place en haut pour qu'elle soit accessible par le tuteur ET par le bilan
def generer_prompt_systeme(niveau, objectif):
    prompt = """
    # RÔLE & OBJECTIF
    Tu es un expert en ingénierie pédagogique cognitive et un spécialiste technique EdTech. Ta mission est de transformer des contenus bruts en activités d'apprentissage.
    Base-toi exclusivement sur le cours fourni pour le fond.

    # 🧠 POSTURE DU COACH ET GESTION DU FEEDBACK
    Ton objectif absolu est de réduire la distance entre la compréhension actuelle de l'élève et la compréhension visée.
    1. Pose UNE SEULE question à la fois. Attends la réponse.
    2. Ne donne JAMAIS la solution directement avant que l'élève n'ait essayé. Fournis une information qui permet à l'élève de corriger sa propre trajectoire.
    3. RÈGLE ANTI-BAVARDAGE : Tes feedbacks doivent être ultra-concis (2 à 3 phrases MAXIMUM). Va droit au but.

    # 🛠️ STRUCTURE EXIGÉE POUR LE FEEDBACK DE PROCESSUS
    Lorsque tu dois faire un "Feedback de Processus", tu dois OBLIGATOIREMENT utiliser cette structure en 3 étapes :
    1. [Le Constat] : Décris ce qui est là, sans jugement (ex: "Ton résultat est faux...").
    2. [Le Diagnostic] : Pointe précisément la règle ou l'étape qui a posé problème (ex: "...car tu as confondu X et Y...").
    3. [Le Levier de guidage] : Donne la stratégie pour agir, SANS donner la réponse finale (ex: "...reprends ta définition de X avant de recommencer.").

    # 🪞 STRUCTURE EXIGÉE POUR LE FEEDBACK D'AUTORÉGULATION
    Lorsque tu dois faire un "Feedback d'Autorégulation" (pour les élèves avancés), utilise cette structure :
    1. [Le miroir] : Décris ce que tu vois factuellement (ex: "Je vois que tu as trouvé ce résultat direct...").
    2. [Activer le radar] : Interroge son système de détection (ex: "À quel moment as-tu vérifié la consigne ?").
    3. [La stratégie] : Pousse-le à la vérification (ex: "Quel outil peux-tu utiliser pour vérifier ce point ?").

    # 🛑 LES ANTI-PROMPTS (INTERDICTIONS STRICTES) :
    - Pas de jugement sur la personne.
    - Pas de "C'est faux" sans fournir d'explication selon la structure ci-dessus.
    - Pas de comparaison sociale ni de félicitations imméritées.
    """

    if niveau == "Novice":
        prompt += """
        ## 🌳 ARBRE DE DÉCISION DU FEEDBACK (PROFIL NOVICE)
        * INTERDICTION ABSOLUE : N'utilise JAMAIS le feedback d'autorégulation.
        * RÈGLE ACTIVE : Utilise EXCLUSIVEMENT le "Feedback de Processus" en respectant strictement sa structure en 3 étapes (Constat + Diagnostic + Levier de guidage).
        """
    else:
        prompt += """
        ## 🌳 ARBRE DE DÉCISION DU FEEDBACK (PROFIL AVANCÉ)
        * SI ERREUR DE MÉTHODE -> Active le "Feedback de Processus" avec sa structure stricte.
        * SI ÉTOURDERIE OU ERREUR BÊTE -> Active le "Feedback d'Autorégulation" avec sa structure stricte (Miroir + Radar + Stratégie).
        """

    if "Mode A" in objectif:
        prompt += """
        # MODE A : MÉMORISATION (Testing Effect)
        * Règle de l'Information Minimale : Une question = Un seul savoir atomique.
        * STRATÉGIE DES LEURRES : Confusion de Concepts, Erreur de "Bon Sens", Inversion de Causalité.
        """
        if niveau == "Novice":
            prompt += "* ÉCHAFAUDAGE (NOVICE) : QCM uniquement. Va à la ligne pour chaque proposition (A, B, C)."
        else:
            prompt += "* ÉCHAFAUDAGE (AVANCÉ) : Rappel Libre pur (sans QCM)."
    else:
        prompt += """
        # MODE B : COMPRÉHENSION (Apprentissage Génératif)
        * MENU GÉNÉRATIF : Transformation, Comparaison Structurée, Auto-explication, Cartographie, Contre-Exemple.
        """
        if niveau == "Novice":
            prompt += "* ÉCHAFAUDAGE (NOVICE) : Completion Problem Effect (Schémas à compléter, Textes à trous)."
        else:
            prompt += "* ÉCHAFAUDAGE (AVANCÉ) : Prompts ouverts purs."

    return prompt

# --- SÉCURITÉ IA ---
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- FONCTION DE BILAN (MÉTACOGNITION) ---
@st.dialog("📈 Ton Bilan de Révision")
def afficher_bilan():
    if len(st.session_state.messages) > 1:
        with st.spinner("L'IA analyse l'intégralité de tes réponses..."):
            # On recrée un historique complet EXCLUSIVEMENT pour le bilan
            historique_complet = []
            if "file_id" in st.session_state:
                f_obj = genai.get_file(st.session_state.file_id)
                historique_complet.append({"role": "user", "parts": [f_obj, "Voici mon document de cours."]})
            elif "texte_manuel" in st.session_state and st.session_state.texte_manuel:
                historique_complet.append({"role": "user", "parts": [f"Voici mon texte :\n{st.session_state.texte_manuel}"]})
            
            historique_complet.append({"role": "model", "parts": ["Compris."]})
            
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                historique_complet.append({"role": role, "parts": [msg["content"]]})
                
            model_bilan = genai.GenerativeModel("gemini-2.5-flash", system_instruction="Tu es un coach. Fais un bilan métacognitif factuel et encourageant de cette session. Adresse-toi à l'élève avec 'Tu'. Synthétise les acquis et les points à consolider. Ne pose plus de question.")
            chat_bilan = model_bilan.start_chat(history=historique_complet)
            
            try:
                reponse = chat_bilan.send_message("La session est terminée. Donne-moi mon bilan.")
                st.success(reponse.text)
            except Exception as e:
                st.error("Impossible de générer le bilan pour le moment.")
    else:
        st.warning("Il faut d'abord discuter un peu avec le tuteur !")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    niveau_eleve = st.radio("Ton niveau :", ["Novice", "Avancé"], disabled=session_en_cours)
    objectif_eleve = st.radio("Ton objectif :", ["Mode A : Mémorisation", "Mode B : Compréhension"], disabled=session_en_cours)
    
    if session_en_cours:
        st.info("🔒 Paramètres verrouillés pendant la révision.")
        if st.button("🏁 Terminer et voir mon bilan", use_container_width=True, type="primary"):
            afficher_bilan()
            
        st.markdown("---")
        if st.button("🔄 Changer de mode (Nouvelle session)", use_container_width=True):
            if "file_id" in st.session_state:
                try:
                    genai.delete_file(st.session_state.file_id)
                except Exception:
                    pass
                del st.session_state.file_id
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    st.header("🧭 Ton Cours")
    fichier_upload = st.file_uploader("Cours (PDF uniquement)", type=["pdf"], disabled=session_en_cours)
    texte_manuel = st.text_area("Ou colle ton texte ici :", disabled=session_en_cours)
    
    # On sauvegarde le texte manuel en session pour y accéder lors du bilan
    if texte_manuel and not session_en_cours:
        st.session_state.texte_manuel = texte_manuel

# --- GESTION DU DÉMARRAGE ET DU FICHIER ---
prompt_systeme = generer_prompt_systeme(niveau_eleve, objectif_eleve)

if (fichier_upload or texte_manuel) and not st.session_state.messages:
    if fichier_upload and "file_id" not in st.session_state:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(fichier_upload.getvalue())
            tmp_path = tmp.name
        with st.spinner("Envoi sécurisé du cours vers l'IA..."):
            fichier_ia = genai.upload_file(tmp_path)
            st.session_state.file_id = fichier_ia.name
        os.remove(tmp_path)
    
    # 1er message d'initialisation
    with st.spinner("Analyse du cours en cours..."):
        historique_init = []
        if "file_id" in st.session_state:
            historique_init.extend([
                {"role": "user", "parts": [genai.get_file(st.session_state.file_id), "Voici mon cours. Base-toi dessus."]},
                {"role": "model", "parts": ["C'est noté, je suis prêt."]}
            ])
        elif texte_manuel:
            historique_init.extend([
                {"role": "user", "parts": [f"Voici mon texte :\n{texte_manuel}\n\nBase-toi dessus."]},
                {"role": "model", "parts": ["C'est noté, je suis prêt."]}
            ])
            
        model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=prompt_systeme, safety_settings=safety_settings)
        chat = model.start_chat(history=historique_init)
        res = chat.send_message("Présente-toi brièvement et pose la première question selon mes réglages.")
        st.session_state.messages.append({"role": "assistant", "content": res.text})
        st.rerun()

# --- AFFICHAGE DE L'HISTORIQUE ---
for msg in st.session_state.messages:
    avatar_chat = "avatar_tuteur.png" if msg["role"] == "assistant" else "avatar_eleve.png"
    with st.chat_message(msg["role"], avatar=avatar_chat):
        st.markdown(msg["content"])

# --- GESTION DU DIALOGUE AVEC LA FENÊTRE GLISSANTE (LE SECRET DE LA VITESSE) ---
if session_en_cours:
    if prompt := st.chat_input("Ta réponse..."):
        st.chat_message("user", avatar="avatar_eleve.png").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant", avatar="avatar_tuteur.png"):
            # 1. On recrée un historique "propre" et LÉGER à chaque fois
            historique_dynamique = []
            
            # 2. On y met d'abord le fichier de base (déjà stocké chez Google)
            if "file_id" in st.session_state:
                historique_dynamique.extend([
                    {"role": "user", "parts": [genai.get_file(st.session_state.file_id), "Voici mon cours. Base-toi dessus."]},
                    {"role": "model", "parts": ["C'est noté, je suis prêt."]}
                ])
            elif "texte_manuel" in st.session_state:
                historique_dynamique.extend([
                    {"role": "user", "parts": [f"Voici mon texte :\n{st.session_state.texte_manuel}\n\nBase-toi dessus."]},
                    {"role": "model", "parts": ["C'est noté, je suis prêt."]}
                ])
            
            # 3. La Fenêtre Glissante : On ajoute SEULEMENT les 4 derniers messages !
            memoire_courte = st.session_state.messages[:-1][-4:]
            for msg in memoire_courte:
                role = "user" if msg["role"] == "user" else "model"
                historique_dynamique.append({"role": role, "parts": [msg["content"]]})
                
            # 4. On lance l'IA avec ce bagage allégé
            model_rapide = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=prompt_systeme, safety_settings=safety_settings)
            chat_rapide = model_rapide.start_chat(history=historique_dynamique)
            
            reponse = chat_rapide.send_message(prompt, stream=True)
            
            def generer_flux_rapide():
                for chunk in reponse:
                    try:
                        if chunk.text: yield chunk.text
                    except ValueError:
                        pass
                        
            texte_complet = st.write_stream(generer_flux_rapide())
            st.session_state.messages.append({"role": "assistant", "content": texte_complet})
            
            if len(st.session_state.messages) == 3:
                st.rerun()
