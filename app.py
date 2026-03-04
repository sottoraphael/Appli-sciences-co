import streamlit as st
import google.generativeai as genai
import tempfile
import time
import os

# ==========================================
# CONFIGURATION DE LA PAGE & CSS
# ==========================================
st.set_page_config(page_title="Réviser avec les sciences cognitives", page_icon="🦉", layout="centered")

st.markdown("""
    <style>
    .stApp { transition: all 0.1s ease-in-out; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton>button { width: 100%; border-radius: 15px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

MAX_HISTORIQUE_MESSAGES = 4 

# ==========================================
# GESTION DE L'ÉTAT DE SESSION (State)
# ==========================================
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gemini_file_name" not in st.session_state:
    st.session_state.gemini_file_name = None
if "tutoriel_vu" not in st.session_state:
    st.session_state.tutoriel_vu = False

# ==========================================
# --- TUTORIEL D'ACCUEIL ---
# ==========================================
@st.dialog("👋 Bienvenue dans cette application de révision")
def afficher_tutoriel():
    st.markdown("""
        <style>
        .big-font { font-size: 1.25rem !important; line-height: 1.7 !important; color: #2D3748; }
        .step-title { font-weight: bold; color: #5B9BD5; font-size: 1.35rem; display: block; margin-top: 15px; }
        .mode-box { background-color: #F0F4F8; padding: 15px; border-radius: 12px; margin: 15px 0; border-left: 6px solid #5B9BD5; }
        </style>
        <div class="big-font">
        Cette application utilise les principes issus des <b>sciences cognitives</b> pour t'aider à réviser efficacement.<br>
        <div class="mode-box">
        <b>💡 Quel mode choisir ?</b><br><br>
        • <b>Mémorisation :</b> Pour retenir les définitions et les concepts "par cœur".<br><br>
        • <b>Compréhension :</b> Pour maîtriser ton cours en profondeur en l'expliquant avec tes propres mots.
        </div>
        <b>Comment l'utiliser en 3 étapes :</b><br>
        <span class="step-title">1. ⚙️ Règle l'application</span> Choisis ton mode et ton niveau.<br>
        <span class="step-title">2. 🧭 Donne-lui ton cours</span> Charge ton PDF ou colle ton texte.<br>
        <span class="step-title">3. 💬 Discute</span> Réponds aux questions dans le chat, et demande ton bilan à la fin !
        </div><br>
    """, unsafe_allow_html=True)
    if st.button("🚀 J'ai compris, c'est parti !", use_container_width=True):
        st.session_state.tutoriel_vu = True
        st.rerun()

# ==========================================
# --- DIALOGUE BILAN FINAL (VERSION CONCISE) ---
# ==========================================
@st.dialog("📈 Ton Bilan de Révision")
def afficher_bilan():
    if len(st.session_state.messages) > 1:
        with st.spinner("Analyse métacognitive en cours..."):
            historique_complet = []
            
            # Intégration du document de cours via l'API File
            if st.session_state.gemini_file_name:
                g_file = genai.get_file(st.session_state.gemini_file_name)
                historique_complet.extend([{"role": "user", "parts": [g_file, "Voici mon document de cours."]}, {"role": "model", "parts": ["Compris."]}])
            
            # Intégration de la conversation
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                historique_complet.append({"role": role, "parts": [msg["content"]]})
                
            # Prompt injecté avec contrainte d'hyper-concision
            instruction_metacognitive = """
            Tu es un coach pédagogique. Fais un bilan métacognitif factuel, ultra-concis et encourageant. Adresse-toi à l'élève avec 'Tu'. Ne pose plus de question.
            
            CONTRAINTE STRICTE : Ton bilan doit être extrêmement bref, visuel et direct pour s'adapter à l'attention d'un collégien fatigué. Utilise des listes à puces et limite-toi à 1 ou 2 phrases maximum par point. Pas de longs paragraphes.
            
            Structure obligatoirement ton bilan ainsi :
            1. 🎯 Tes acquis : Va droit au but sur ce qui est su et ce qui reste à revoir (très bref).
            2. 💡 Tes erreurs : Dédramatise et donne LA stratégie précise à utiliser la prochaine fois (1 phrase).
            3. ⏳ Le piège de la relecture : Rappelle en 1 courte phrase que relire donne l'illusion de savoir (biais de fluence) et qu'il faut attendre un peu avant de se retester.
            4. 📝 Prochaine étape : Suggère en 1 courte phrase de noter ces points dans son carnet de progrès.
            """
            
            model_bilan = genai.GenerativeModel("gemini-2.5-flash", system_instruction=instruction_metacognitive)
            chat_bilan = model_bilan.start_chat(history=historique_complet)
            
            try:
                reponse = chat_bilan.send_message("La session est terminée. Donne-moi mon bilan métacognitif ultra-concis selon tes instructions.")
                st.success(reponse.text)
                
                st.divider()
                if st.button("🔄 Fermer et recommencer une nouvelle session"):
                    st.session_state.session_active = False
                    st.session_state.messages = []
                    st.rerun()
            except Exception as e:
                st.error(f"Impossible de générer le bilan pour le moment : {e}")
    else:
        st.warning("Il faut d'abord discuter un peu avec le tuteur avant de pouvoir analyser tes réponses !")

# ==========================================
# 🛑 ZONE SANCTUAIRE : PROMPT SYSTÈME 🛑
# ==========================================
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
   2. Auto-explication : Verbaliser le pourquoi d'une étape.
   3. Cartographie : Hiérarchiser les concepts.
   4. Contre-Exemple : Identifier les limites de la règle.
"""
        if niveau_eleve == "Novice":
            prompt_systeme += """
* ÉCHAFAUDAGE (NOVICE) : Utilise le "Completion Problem Effect" (Schémas à compléter, Dire quel schéma est faux parmis deux proposés).
"""
        else:
            prompt_systeme += """
* ÉCHAFAUDAGE (AVANCÉ) : Utilise des prompts ouverts ("Analysez...", "Critiquez...", "Explquez l'erreur dans l'exemple suivant ..."). Ne donne aucune structure de départ, laisse l'élève l'organiser.
"""

    prompt_systeme += """
# GARDE-FOUS FINAUX
* Base-toi exclusivement sur le texte fourni pour le fond.
* PROPRETÉ : Ne laisse jamais de balises techniques type [cite] ou [source] dans le résultat final.
* MASQUAGE DE LA STRUCTURE (IMPORTANT) : N'écris JAMAIS les mots-clés ou balises comme "[Le Constat]", "[Le Diagnostic]", "[Le Levier de guidage]", "[L'observation / Le miroir]", "[L'interrogation / Activer le radar]" ou "[L'ouverture / La stratégie]" dans ta réponse finale à l'élève. Rédige ton feedback de manière fluide et naturelle. Ces balises ne servent qu'à structurer ta pensée en interne.
"""
    return prompt_systeme

# ==========================================
# FONCTIONS TECHNIQUES & SÉCURITÉ
# ==========================================
def initialiser_modele(api_key, niveau, objectif):
    genai.configure(api_key=api_key)
    instructions = generer_prompt_systeme(niveau, objectif)
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=instructions
    )

def uploader_fichier_google(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    with st.spinner("⏳ Je lis ton cours pour préparer les questions..."):
        g_file = genai.upload_file(tmp_path)
        while g_file.state.name == "PROCESSING":
            time.sleep(1)
            g_file = genai.get_file(g_file.name)
            
    os.remove(tmp_path)
    return g_file

def generer_contexte_optimise(nouvel_input):
    contents = []
    historique_recent = st.session_state.messages[-MAX_HISTORIQUE_MESSAGES:]
    for msg in historique_recent:
        contents.append({"role": msg["role"], "parts": [msg["content"]]})
        
    parts_user = []
    if st.session_state.gemini_file_name:
        parts_user.append(genai.get_file(st.session_state.gemini_file_name))
        
    parts_user.append(nouvel_input)
    contents.append({"role": "user", "parts": parts_user})
    return contents

def extraire_texte_stream(reponse):
    for chunk in reponse:
        try:
            if chunk.text:
                yield chunk.text
        except Exception:
            pass

# ==========================================
# INTERFACE UTILISATEUR (UI)
# ==========================================
st.title("🦉 Réviser avec les sciences cognitives")
st.markdown("*Outil anonyme : Ne saisis aucune donnée personnelle dans ce chat.*")

if not st.session_state.tutoriel_vu:
    afficher_tutoriel()

# --- PANNEAU LATÉRAL ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    session_en_cours = st.session_state.session_active
    
    niveau_eleve = st.radio("Ton niveau :", ["Novice", "Avancé"], disabled=session_en_cours)
    objectif_eleve = st.radio("Ton objectif :", ["Mode A : Mémorisation", "Mode B : Compréhension"], disabled=session_en_cours)
    uploaded_file = st.file_uploader("Charge ton cours (PDF/TXT)", type=["pdf", "txt"], disabled=session_en_cours)
    
    if st.button("🚀 Démarrer la session", disabled=session_en_cours or not uploaded_file):
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
            genai.configure(api_key=api_key)
            fichier_gemini = uploader_fichier_google(uploaded_file)
            st.session_state.gemini_file_name = fichier_gemini.name
            
            st.session_state.api_key = api_key
            st.session_state.niveau = niveau_eleve
            st.session_state.objectif = objectif_eleve
            st.session_state.session_active = True
            st.rerun()
        except KeyError:
            st.error("⚠️ La clé API est introuvable dans l'onglet 'Secrets' de Streamlit Cloud.")
        except Exception as e:
            st.error(f"Erreur : {e}")

    if st.session_state.session_active:
        st.divider()
        if st.button("🛑 Terminer et voir ma synthèse"):
            afficher_bilan()

# --- ZONE DE DISCUSSION ---
if st.session_state.session_active:
    modele = initialiser_modele(st.session_state.api_key, st.session_state.niveau, st.session_state.objectif)
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Amorçage (1ère question)
    if len(st.session_state.messages) == 0:
        with st.chat_message("model"):
            with st.spinner("Je prépare ta première question..."):
                contexte = generer_contexte_optimise("Salut ! Pose-moi la première question sur le cours pour démarrer.")
                reponse_stream = modele.generate_content(contexte, stream=True)
                reponse_complete = st.write_stream(extraire_texte_stream(reponse_stream))
                st.session_state.messages.append({"role": "model", "content": reponse_complete})

    # Boucle d'interaction
    if prompt := st.chat_input("Écris ta réponse ici..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("model"):
            with st.spinner("Analyse de ta réponse..."):
                contexte = generer_contexte_optimise(prompt)
                reponse_stream = modele.generate_content(contexte, stream=True)
                reponse_complete = st.write_stream(extraire_texte_stream(reponse_stream))
        st.session_state.messages.append({"role": "model", "content": reponse_complete})

else:
    st.info("👈 Remplis les paramètres à gauche et charge ton cours pour commencer à réviser !")
