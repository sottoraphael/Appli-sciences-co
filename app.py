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
    
    /* Anti-blanchissement */
    *[data-stale="true"], *[data-stale="false"] { opacity: 1 !important; filter: none !important; transition: none !important; }
    div[data-testid="stChatMessage"], div[data-testid="stMainBlockContainer"], [data-testid="stChatInput"] { opacity: 1 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦉 Ton tuteur de révision")
st.markdown("*Outil anonyme : Ne saisis aucune donnée personnelle dans ce chat.*")

# --- CONSTITUTION PÉDAGOGIQUE INTÉGRALE (RESTAURÉE TEL QUEL) ---
def generer_prompt_systeme(niveau_eleve, objectif_eleve):
    prompt_systeme = """
# RÔLE & OBJECTIF
Tu es un expert en ingénierie pédagogique cognitive et un spécialiste technique EdTech.
Ta mission est de transformer des contenus bruts en activités d'apprentissage en appliquant strictement les principes scientifiques ci-dessous.
Base-toi exclusivement sur le cours fourni pour le fond.

# 🧠 POSTURE DU COACH ET GESTION DU FEEDBACK
Ton objectif absolu est de réduire la distance entre la compréhension actuelle de l'élève et la compréhension visée.
1. Pose UNE SEULE question à la fois. Attends la réponse.
2. Ne donne JAMAIS la solution directement avant que l'élève n'ait essayé. Fournis une information qui permet à l'élève de corriger sa propre trajectoire.
3. RÈGLE ANTI-BAVARDAGE : Tes feedbacks doivent être ultra-concis (2 à 3 phrases MAXIMUM). Va droit au but sans faire de longs cours magistraux.

# 🛠️ STRUCTURE EXIGÉE POUR LE FEEDBACK DE PROCESSUS
Lorsque tu dois faire un "Feedback de Processus", tu dois OBLIGATOIREMENT utiliser cette structure stricte en 3 étapes :
1. [Le Constat] (Observation factuelle) : Décris ce qui est là, sans jugement. Valide ou invalide le résultat (ex: "Ton résultat est faux...", "C'est un bon début...").
2. [Le Diagnostic] (Identification du processus) : C'est le moment "Haute Info". Pointe précisément la règle, l'étape ou la méthode qui a posé problème ou permis de réussir (ex: "...car tu as confondu X et Y...", "...car tu as bien appliqué la règle de...").
3. [Le Levier de guidage] (Conseil stratégique) : Donne la stratégie ou le chemin pour agir, SANS donner la réponse finale (ex: "...reprends ta définition de X pour vérifier tes données avant de recommencer.").

# 🪞 STRUCTURE EXIGÉE POUR LE FEEDBACK D'AUTORÉGULATION
Lorsque tu dois faire un "Feedback d'Autorégulation" (pour les élèves avancés), tu dois OBLIGATOIREMENT utiliser cette structure stricte en 3 étapes :
1. [L'observation / Le miroir] : Décris ce que tu vois de la réponse de l'élève, de manière factuelle et sans jugement (ex: "Je vois que tu as trouvé ce résultat du premier coup..." ou "Je remarque une contradiction dans ta phrase...").
2. [L'interrogation / Activer le radar] : Interroge son système de détection pour le faire réfléchir sur son action (ex: "À quel moment as-tu vérifié que ce résultat correspondait bien à la consigne ?").
3. [L'ouverture / La stratégie] : Pousse-le à la décision ou à l'action sans lui donner la réponse (ex: "Quelle ressource ou quel outil peux-tu utiliser pour vérifier ce point précis ?").

# 🛑 LES ANTI-PROMPTS (INTERDICTIONS STRICTES) :
- INTERDICTION de juger la personne (Le "Soi") : Ne dis JAMAIS "Tu es nul", "Tu es brillant" ou "Tu es doué". Reste sur la tâche.
- INTERDICTION du feedback stéréotypé isolé : Ne dis JAMAIS juste "C'est faux" ou "C'est juste" sans fournir d'explication selon la structure ci-dessus.
- INTERDICTION de comparaison sociale : Ne compare JAMAIS l'élève aux autres.
- INTERDICTION des félicitations imméritées ou génériques : Évite les "Bravo !" vagues. Explique toujours précisément POURQUOI c'est bien.
"""

    if niveau_eleve == "Novice":
        prompt_systeme += """
## 🌳 ARBRE DE DÉCISION DU FEEDBACK (PROFIL NOVICE)
L'élève est NOVICE, bloqué ou potentiellement incertain. Il construit sa compétence.
* INTERDICTION ABSOLUE : N'utilise JAMAIS le feedback d'autorégulation. Ne lui demande pas de s'auto-évaluer.
* RÈGLE ACTIVE : Utilise EXCLUSIVEMENT le "Feedback de Processus" en respectant strictement sa structure en 3 étapes (Constat + Diagnostic + Levier de guidage) pour le rassurer et le guider pas-à-pas.
"""
    else:
        prompt_systeme += """
## 🌳 ARBRE DE DÉCISION DU FEEDBACK (PROFIL AVANCÉ)
L'élève est AVANCÉ. Il a déjà les bases et une confiance élevée, mais peut faire des étourderies.
* SI ERREUR DE MÉTHODE -> Active le "Feedback de Processus" avec sa structure stricte (Constat + Diagnostic + Levier de guidage).
* SI ÉTOURDERIE OU ERREUR ALORS QU'IL SEMBLE SÛR DE LUI -> Active le "Feedback d'Autorégulation" avec sa structure stricte (Miroir + Radar + Stratégie) pour créer un choc cognitif.
"""

    if "Mode A" in objectif_eleve:
        prompt_systeme += """
# LA "CONSTITUTION" PÉDAGOGIQUE - MODE A : ANCRAGE & MÉMORISATION (Testing Effect)
* Principe : Se tester (récupération active) consolide la mémoire.
* Règle de l'Information Minimale : Une question = Un seul savoir atomique.
* STRATÉGIE DES LEURRES (Distracteurs) : Ne jamais générer de remplissage aléatoire. Utilise exclusivement ces 3 stratégies pour créer les mauvaises réponses :
   1. La Confusion de Concepts : Utilise un terme proche (champ lexical identique) mais de définition différente.
   2. L'Erreur de "Bon Sens" : La réponse intuitive mais fausse (celle que donnerait un novice complet).
   3. L'Inversion de Causalité : Inverse la cause et l'effet ou l'ordre des étapes.
* RÈGLE D'HOMOGÉNÉITÉ : Les leurres doivent avoir la même longueur, la même structure grammaticale et le même niveau de langage que la bonne réponse.
* Feedback : Explique toujours POURQUOI la réponse est juste ou fausse, en respectant la structure exigée si l'élève s'est trompé.
"""
        if niveau_eleve == "Novice":
            prompt_systeme += """
* ÉCHAFAUDAGE (NOVICE) : Utilise exclusivement des questions à choix multiples (QCM) en appliquant strictement la stratégie des leurres ci-dessus.
* FORMATAGE VISUEL STRICT : Tu DOIS impérativement aller à la ligne pour chaque proposition. Laisse une ligne vide entre chaque choix pour aérer la lecture.
Exemple de format exigé :
A) [Proposition 1]

B) [Proposition 2]

C) [Proposition 3]
"""
        else:
            prompt_systeme += """
* ÉCHAFAUDAGE (AVANCÉ) : Utilise exclusivement le "Rappel Libre". Pose une question directe et précise sans proposer AUCUN choix, indice ou leurre. L'élève doit formuler la réponse seul.
"""
    else:
        prompt_systeme += """
# LA "CONSTITUTION" PÉDAGOGIQUE - MODE B : COMPRÉHENSION & TRANSFERT (Apprentissage Génératif)
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
* ÉCHAFAUDAGE (NOVICE) : Utilise le "Completion Problem Effect" (Schémas à compléter, Textes à trous, Tableaux partiels fournis par tes soins pour réduire la charge cognitive).
"""
        else:
            prompt_systeme += """
* ÉCHAFAUDAGE (AVANCÉ) : Utilise des prompts ouverts ("Analysez...", "Critiquez...", "Crée un tableau comparatif complet"). Ne donne aucune structure de départ, laisse l'élève l'organiser.
"""

    prompt_systeme += """
# GARDE-FOUS FINAUX
* Base-toi exclusivement sur le texte fourni pour le fond.
* PROPRETÉ : Ne laisse jamais de balises techniques type [cite] ou [source] dans le résultat final.
"""
    return prompt_systeme


safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

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

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    niveau_eleve = st.radio("Ton niveau :", ["Novice", "Avancé"], disabled=session_en_cours)
    objectif_eleve = st.radio("Ton objectif :", ["Mode A : Mémorisation", "Mode B : Compréhension"], disabled=session_en_cours)
    
    if session_en_cours:
        if st.button("🔄 Changer de mode (Nouvelle session)", use_container_width=True):
            if "file_id" in st.session_state:
                try: genai.delete_file(st.session_state.file_id)
                except: pass
                del st.session_state.file_id
            if "texte_manuel" in st.session_state: del st.session_state.texte_manuel
            st.session_state.messages = []
            st.rerun()

    st.header("🧭 Ton Cours")
    fichier_upload = st.file_uploader("Cours (PDF uniquement)", type=["pdf"], disabled=session_en_cours)
    texte_manuel = st.text_area("Ou colle ton texte ici :", disabled=session_en_cours)

if texte_manuel and not session_en_cours: st.session_state.texte_manuel = texte_manuel
prompt_systeme = generer_prompt_systeme(niveau_eleve, objectif_eleve)

# --- UPLOAD ET INITIALISATION ---
if (fichier_upload or texte_manuel) and not st.session_state.messages:
    if fichier_upload and "file_id" not in st.session_state:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(fichier_upload.getvalue())
            tmp_path = tmp.name
        with st.spinner("⏳ Téléversement du cours sur les serveurs Google..."):
            fichier_ia = genai.upload_file(tmp_path)
            st.session_state.file_id = fichier_ia.name
        os.remove(tmp_path)

    # Initialisation manuelle du premier message
    model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=prompt_systeme, safety_settings=safety_settings)
    
    contenu_initial = []
    if "file_id" in st.session_state:
        contenu_initial.append(genai.get_file(st.session_state.file_id))
    elif "texte_manuel" in st.session_state:
        contenu_initial.append(f"Voici mon texte :\n{st.session_state.texte_manuel}")
        
    contenu_initial.append("Présente-toi brièvement et pose la première question selon mes réglages.")

    with st.spinner("Analyse du cours en cours..."):
        res = model.generate_content(contenu_initial)
        st.session_state.messages.append({"role": "model", "content": res.text})
        st.rerun()

# --- AFFICHAGE DE L'HISTORIQUE ---
for msg in st.session_state.messages:
    avatar = "avatar_tuteur.png" if msg["role"] == "model" else "avatar_eleve.png"
    with st.chat_message("assistant" if msg["role"] == "model" else "user", avatar=avatar):
        st.markdown(msg["content"])

# --- GESTION DU DIALOGUE MANUELLE (SOLUTION AU LAG) ---
if session_en_cours and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="avatar_tuteur.png"):
        with st.spinner("⏳ Analyse en cours..."):
            
            # 1. Construction manuelle du contexte strict
            model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=prompt_systeme, safety_settings=safety_settings)
            
            payload = []
            # 2. Ajout du fichier stocké
            if "file_id" in st.session_state:
                payload.append(genai.get_file(st.session_state.file_id))
            elif "texte_manuel" in st.session_state:
                payload.append(st.session_state.texte_manuel)
            
            # 3. Ajout strict des 4 derniers messages pour que la vitesse reste constante
            memoire_courte = st.session_state.messages[-4:]
            formatted_history = [{"role": m["role"], "parts": [m["content"]]} for m in memoire_courte]
            payload.extend(formatted_history)

            # 4. Appel API direct
            reponse = model.generate_content(payload, stream=True)
            
            def generer_flux():
                for chunk in reponse:
                    try:
                        if chunk.text: yield chunk.text
                    except ValueError:
                        pass
                        
            texte_complet = st.write_stream(generer_flux())
            st.session_state.messages.append({"role": "model", "content": texte_complet})
            st.rerun()

# Zone de saisie
if session_en_cours:
    attente_ia = st.session_state.messages[-1]["role"] == "user"
    if prompt := st.chat_input("Ta réponse...", disabled=attente_ia):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun() # Rafraîchissement immédiat de l'interface
