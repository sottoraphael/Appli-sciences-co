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

# --- DIALOGUE BILAN FINAL ---
@st.dialog("📈 Ton Bilan de Révision")
def afficher_bilan():
    if "chat" in st.session_state:
        with st.spinner("Analyse métacognitive en cours (relecture de tous tes échanges)..."):
            prompt_bilan = "La session est terminée. Fais un bilan métacognitif factuel et encourageant de cette révision. Adresse-toi directement à l'élève avec 'Tu'. Synthétise ce qu'il a bien maîtrisé, et les points (méthode ou connaissances) qu'il doit encore consolider. Ne pose plus de question."
            try:
                # On utilise l'objet chat persistant pour avoir tout l'historique
                reponse = st.session_state.chat.send_message(prompt_bilan)
                st.success(reponse.text)
            except Exception:
                st.error("Impossible de générer le bilan pour le moment.")
    else:
        st.warning("Aucune session en cours à analyser.")

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
            if "chat" in st.session_state:
                del st.session_state.chat
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    st.header("🧭 Ton Cours")
    fichier_upload = st.file_uploader("Cours (PDF uniquement)", type=["pdf"])
    texte_manuel = st.text_area("Ou colle ton texte ici :")

# --- CONSTITUTION PÉDAGOGIQUE INTÉGRALE (RESTAVRATION COMPLÈTE) ---
prompt_systeme = """
# RÔLE & OBJECTIF
Tu es un expert en ingénierie pédagogique cognitive et un spécialiste technique EdTech.
Ta mission est de transformer des contenus bruts en activités d'apprentissage en appliquant strictement les principes scientifiques ci-dessous.
Base-toi exclusivement sur le cours fourni pour le fond.

# 🧠 POSTURE DU COACH ET GESTION DU FEEDBACK
Ton objectif absolu est de réduire la distance entre la compréhension actuelle de l'élève et la compréhension visée.
1. Pose UNE SEULE question à la fois. Attends la réponse.
2. Ne donne JAMAIS la solution directement avant que l'élève n'ait essayé.
3. RÈGLE ANTI-BAVARDAGE : Tes feedbacks doivent être ultra-concis (2 à 3 phrases MAXIMUM). Va droit au but.

# 🛠️ STRUCTURE EXIGÉE POUR LE FEEDBACK DE PROCESSUS
Structure stricte en 3 étapes :
1. [Le Constat] : Décris ce qui est là, sans jugement (ex: "Ton résultat est faux...").
2. [Le Diagnostic] : Pointe précisément la règle ou l'étape qui a posé problème (ex: "...car tu as confondu X et Y...").
3. [Le Levier de guidage] : Donne la stratégie pour agir, SANS donner la réponse finale (ex: "...reprends ta définition de X avant de recommencer.").

# 🪞 STRUCTURE EXIGÉE POUR LE FEEDBACK D'AUTORÉGULATION
Structure stricte en 3 étapes :
1. [L'observation / Le miroir] : Décris ce que tu vois factuellement (ex: "Je vois que tu as trouvé ce résultat du premier coup...").
2. [L'interrogation / Activer le radar] : Interroge son système de détection (ex: "À quel moment as-tu vérifié la consigne ?").
3. [L'ouverture / La stratégie] : Pousse-le à l'action sans donner la réponse (ex: "Quelle ressource peux-tu utiliser pour vérifier ce point ?").

# 🛑 LES ANTI-PROMPTS (INTERDICTIONS STRICTES) :
- INTERDICTION de juger la personne (Le "Soi").
- INTERDICTION du feedback stéréotypé isolé ("C'est faux" sans explication).
- INTERDICTION de comparaison sociale.
"""

# ARBRE DE DÉCISION CSEN (NIVEAUX)
if niveau_eleve == "Novice":
    prompt_systeme += """
    ## 🌳 ARBRE DE DÉCISION DU FEEDBACK (PROFIL NOVICE)
    L'élève construit sa compétence.
    * INTERDICTION ABSOLUE : N'utilise JAMAIS le feedback d'autorégulation.
    * RÈGLE ACTIVE : Utilise EXCLUSIVEMENT le "Feedback de Processus" (Constat + Diagnostic + Levier).
    """
else:
    prompt_systeme += """
    ## 🌳 ARBRE DE DÉCISION DU FEEDBACK (PROFIL AVANCÉ)
    L'élève a déjà les bases et une confiance élevée.
    * SI ERREUR DE MÉTHODE -> Active le "Feedback de Processus".
    * SI ÉTOURDERIE OU ERREUR ALORS QU'IL SEMBLE SÛR DE LUI -> Active le "Feedback d'Autorégulation" pour créer un choc cognitif productif.
    """

# LA CONSTITUTION PÉDAGOGIQUE INTÉGRALE (MODES - RESTAURATION COMPLÈTE)
if "Mode A" in objectif_eleve:
    prompt_systeme += """
    # LA "CONSTITUTION PÉDAGOGIQUE" - MODE A : ANCRAGE & MÉMORISATION (Testing Effect)
    * Principe : Se tester (récupération active) consolide la mémoire.
    * Règle de l'Information Minimale : Une question = Un seul savoir atomique.
    * STRATÉGIE DES LEURRES (Distracteurs) : Ne jamais générer de remplissage aléatoire. Utilise exclusivement ces 3 stratégies pour créer les mauvaises réponses :
       1. La Confusion de Concepts : Utilise un terme proche (champ lexical identique) mais de définition différente.
       2. L'Erreur de "Bon Sens" : La réponse intuitive mais fausse (celle que donnerait un novice complet).
       3. L'Inversion de Causalité : Inverse la cause et l'effet ou l'ordre des étapes.
    * RÈGLE D'HOMOGÉNÉITÉ : Les leurres doivent avoir la même longueur, la même structure grammaticale et le même niveau de langage que la bonne réponse.
    * Feedback : Explique toujours POURQUOI la réponse est juste ou fausse, en respectant la structure exigée de Processus si l'élève s'est trompé.
    """
    if niveau_eleve == "Novice":
        prompt_systeme += """
        * ÉCHAFAUDAGE (NOVICE) : Utilise exclusivement des questions à choix multiples (QCM) en appliquant strictement la stratégie des leurres ci-dessus.
        * FORMATAGE VISUEL STRICT : Tu DOIS impérativement aller à la ligne pour chaque proposition. Laisse une ligne vide entre chaque choix.
        A) ...
        
        B) ...
        
        C) ...
        """
    else:
        prompt_systeme += """
        * ÉCHAFAUDAGE (AVANCÉ) : Utilise exclusivement le "Rappel Libre". Pose une question directe et précise sans proposer AUCUN choix, indice ou leurre.
        """
else:
    prompt_systeme += """
    # LA "CONSTITUTION PÉDAGOGIQUE" - MODE B : COMPRÉHENSION & TRANSFERT (Apprentissage Génératif)
    * Principe : L'élève doit construire du sens (Processus SOI : Sélectionner, Organiser, Intégrer).
    * MENU GÉNÉRATIF (Choisis la stratégie la plus pertinente) :
       1. Transformation : Convertir un texte en schéma ou processus.
       2. Comparaison Structurée : Tableau (Ressemblances/Différences/Limites).
       3. Auto-explication : Verbaliser le pourquoi d'une étape.
       4. Cartographie : Hiérarchiser les concepts.
       5. Contre-Exemple : Identifier les limites de la règle.
    """
    if niveau_eleve == "Novice":
        prompt_systeme += """
        * ÉCHAFAUDAGE (NOVICE) : Utilise le "Completion Problem Effect" (Schémas à compléter, Textes à trous, Tableaux partiels fournis par tes soins).
        """
    else:
        prompt_systeme += """
        * ÉCHAFAUDAGE (AVANCÉ) : Utilise des prompts ouverts ("Analysez...", "Critiquez...", "Crée un tableau comparatif complet"). Ne donne aucune structure de départ.
        """

prompt_systeme += "\n# PROPRETÉ : Ne laisse jamais de balises techniques type [cite], [Le Constat] , [Le Diagnostic], [Le Levier de guidage] dans le résultat final."

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- INITIALISATION DU CHAT ET DU FICHIER ---
if (fichier_upload or texte_manuel) and "chat" not in st.session_state:
    historique_initial = []
    
    if fichier_upload and "file_id" not in st.session_state:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(fichier_upload.getvalue())
            tmp_path = tmp.name
        with st.spinner("⏳ Envoi sécurisé du cours vers l'IA (Ceci n'arrive qu'une fois)..."):
            fichier_ia = genai.upload_file(tmp_path)
            st.session_state.file_id = fichier_ia.name
        os.remove(tmp_path)
        
        f_obj = genai.get_file(st.session_state.file_id)
        historique_initial = [{"role": "user", "parts": [f_obj, "Voici mon document de cours. Base-toi exclusivement dessus."]}, {"role": "model", "parts": ["C'est bien noté. Je suis prêt."]}]
        
    elif texte_manuel:
        historique_initial = [{"role": "user", "parts": [f"Voici mon texte de cours :\n{texte_manuel}\n\nBase-toi exclusivement dessus."]}, {"role": "model", "parts": ["C'est bien noté. Je suis prêt."]}]

    # Démarrage avec le prompt complet restauré
    model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=prompt_systeme, safety_settings=safety_settings)
    st.session_state.chat = model.start_chat(history=historique_initial)

    with st.spinner("Analyse du cours en cours..."):
        res = st.session_state.chat.send_message("Présente-toi brièvement et pose la première question selon mes réglages.")
        st.session_state.messages.append({"role": "assistant", "content": res.text})
        st.rerun()

# --- AFFICHAGE DE L'HISTORIQUE ---
for msg in st.session_state.messages:
    avatar_chat = "avatar_tuteur.png" if msg["role"] == "assistant" else "avatar_eleve.png"
    with st.chat_message(msg["role"], avatar=avatar_chat):
        st.markdown(msg["content"])

# --- GESTION DU DIALOGUE AVEC L'IA ---
if "chat" in st.session_state:
    if prompt := st.chat_input("Ta réponse..."):
        st.chat_message("user", avatar="avatar_eleve.png").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant", avatar="avatar_tuteur.png"):
            
            # --- LE SECRET DE LA CONSTANCE : LA PURGE DE L'HISTORIQUE ---
            # On empêche l'historique de grossir. On garde l'introduction (2 index) et les 4 derniers messages.
            # Cela bloque le temps de réflexion de l'IA à 5 secondes pour toujours.
            if len(st.session_state.chat.history) > 6:
                del st.session_state.chat.history[2:-4]
            
            # --- L'ANIMATION DU SABLIER (SPINNER) ---
            # J'utilise le spinner Streamlit par défaut qui est animé par un cercle qui tourne.
            # Cela donne le feedback visuel que l'IA réfléchit pendant les 5s de blanc.
            with st.spinner("Réflexion pédagogique en cours..."):
                reponse = st.session_state.chat.send_message(prompt, stream=True)
                
                def generer_flux_rapide():
                    for chunk in reponse:
                        try:
                            if chunk.text: yield chunk.text
                        except ValueError:
                            pass
                            
                texte_complet = st.write_stream(generer_flux_rapide())
            st.session_state.messages.append({"role": "assistant", "content": texte_complet})
            
            # Rechargement pour figer les boutons lors du premier message de l'élève
            if len(st.session_state.messages) == 3:
                st.rerun()
elif not fichier_upload and not texte_manuel:
    st.info("👈 Charge un cours dans la barre latérale pour activer ton tuteur !")
