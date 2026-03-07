import streamlit as st
import google.generativeai as genai
import tempfile
import time
import os
import csv
import datetime

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
if "texte_manuel" not in st.session_state:
    st.session_state.texte_manuel = ""
if "tutoriel_vu" not in st.session_state:
    st.session_state.tutoriel_vu = False
# Variables pour la gestion fluide de la modale de fin
if "bilan_genere" not in st.session_state:
    st.session_state.bilan_genere = None
if "eval_en_cours" not in st.session_state:
    st.session_state.eval_en_cours = False

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
# --- GESTION DES DONNÉES D'ÉVALUATION ---
# ==========================================
def sauvegarder_donnees_locales(donnees):
    """Sauvegarde factuelle des données dans un fichier CSV local pour analyse ultérieure."""
    fichier_csv = 'donnees_impact_cognitif.csv'
    fichier_existe = os.path.isfile(fichier_csv)
    
    with open(fichier_csv, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=donnees.keys())
        if not fichier_existe:
            writer.writeheader()
        writer.writerow(donnees)

def afficher_questionnaire_evaluation():
    """Affiche le formulaire à l'intérieur de la modale active sans utiliser @st.dialog"""
    st.write("Aide-nous à améliorer cette application. Tes réponses sont anonymes.")
    
    with st.form("form_evaluation"):
        # --- 1. Stratégies ---
        st.markdown("**1. Comment as-tu travaillé aujourd'hui ?**")
        mode_a = st.checkbox("Mode Révision Rapide (J'ai fait appel à ma mémoire)")
        mode_b = st.checkbox("Mode Réflexion (J'ai pris le temps d'expliquer et de comprendre)")
        
        st.caption("Si tu as utilisé le Mode Réflexion, précise :")
        col1, col2 = st.columns(2)
        with col1:
            strat_sacha = st.checkbox("J'ai expliqué à Sacha")
        with col2:
            strat_auto = st.checkbox("J'ai résumé avec mes mots")
            
        st.divider()

        # --- 2. Expérience Utilisateur (UX) ---
        st.markdown("**2. Ton avis sur l'application**")
        ux_interface = st.slider(
            "Facilité d'utilisation (1 = Très compliqué, 5 = Très simple)",
            min_value=1, max_value=5, value=3
        )
        ux_consignes = st.slider(
            "Clarté des explications de l'IA (1 = Incompréhensible, 5 = Très clair)",
            min_value=1, max_value=5, value=3
        )
        
        st.divider()

        # --- 3. Métacognition & Charge Cognitive ---
        st.markdown("**3. Ton apprentissage**")
        sentiment_maitrise = st.slider(
            "As-tu l'impression de mieux connaître ton cours ? (1 = Pas du tout, 5 = Tout à fait)",
            min_value=1, max_value=5, value=3
        )
        capacite_explication = st.slider(
            "Serais-tu capable d'expliquer cette leçon demain ? (1 = Pas du tout, 5 = Tout à fait)",
            min_value=1, max_value=5, value=3
        )
        effort_cognitif = st.slider(
            "Effort mental fourni (1 = Très facile / Passif, 5 = Très fatigant / Difficile)",
            min_value=1, max_value=5, value=3
        )
        
        st.divider()

        # --- 4. Qualitatif ---
        commentaire = st.text_area("Un mot à ajouter ? (Ce qui t'a aidé ou bloqué)", placeholder="Facultatif...")
        consentement = st.checkbox("J'accepte d'envoyer ces réponses anonymes pour améliorer l'application.", value=False)

        soumis = st.form_submit_button("Envoyer mon bilan", type="primary")
        
        if soumis:
            if not consentement:
                st.error("Tu dois cocher la case de consentement pour envoyer tes réponses.")
            else:
                sauvegarder_donnees_locales({
                    "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Mode_A": mode_a,
                    "Mode_B": mode_b,
                    "Strat_Sacha": strat_sacha,
                    "Strat_AutoExp": strat_auto,
                    "UX_Interface": ux_interface,
                    "UX_Consignes": ux_consignes,
                    "Maitrise": sentiment_maitrise,
                    "Transfert": capacite_explication,
                    "Effort_Cognitif": effort_cognitif,
                    "Commentaire": commentaire.replace('\n', ' ')
                })
                st.success("✅ Merci ! Tes réponses ont été enregistrées.")
                time.sleep(1.5)
                # Réinitialisation complète des variables d'état
                st.session_state.session_active = False
                st.session_state.messages = []
                st.session_state.texte_manuel = ""
                st.session_state.bilan_genere = None
                st.session_state.eval_en_cours = False
                st.rerun()

# ==========================================
# --- DIALOGUE BILAN FINAL ---
# ==========================================
@st.dialog("📈 Ton Bilan de Révision", width="large")
def afficher_bilan():
    if len(st.session_state.messages) > 1:
        
        # Phase 1 : Génération (mise en cache pour éviter les appels API multiples)
        if st.session_state.bilan_genere is None:
            with st.spinner("Analyse métacognitive en cours..."):
                historique_complet = []
                
                # Gestion de la source (PDF ou Texte)
                if st.session_state.gemini_file_name:
                    g_file = genai.get_file(st.session_state.gemini_file_name)
                    historique_complet.extend([{"role": "user", "parts": [g_file, "Voici mon document de cours."]}, {"role": "model", "parts": ["Compris."]}])
                elif st.session_state.texte_manuel:
                    historique_complet.extend([{"role": "user", "parts": [f"Voici mon texte de cours :\n{st.session_state.texte_manuel}"]}, {"role": "model", "parts": ["Compris."]}])
                
                for msg in st.session_state.messages:
                    role = "user" if msg["role"] == "user" else "model"
                    historique_complet.append({"role": role, "parts": [msg["content"]]})
                    
                instruction_metacognitive = """
                Tu es un coach pédagogique. Fais un bilan métacognitif factuel, ultra-concis et encourageant. Adresse-toi à l'élève avec 'Tu'. Ne pose plus de question.
                
                CONTRAINTE STRICTE : Ton bilan doit être extrêmement bref, visuel et direct. Utilise des listes à puces et limite-toi à 1 ou 2 phrases maximum par point. Pas de longs paragraphes.
                
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
                    st.session_state.bilan_genere = reponse.text
                except Exception as e:
                    st.error(f"Impossible de générer le bilan pour le moment : {e}")
                    return # Stoppe l'exécution si l'API échoue

        # Affichage du bilan
        st.success(st.session_state.bilan_genere)
        st.divider()

        # Phase 2 : Routage intra-modale (Boutons ou Formulaire)
        if not st.session_state.eval_en_cours:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Quitter sans évaluer"):
                    st.session_state.session_active = False
                    st.session_state.messages = []
                    st.session_state.texte_manuel = ""
                    st.session_state.bilan_genere = None
                    st.rerun()
            with col2:
                if st.button("📊 Évaluer l'outil (1 min)", type="primary"):
                    st.session_state.eval_en_cours = True
                    st.rerun() # Recharge la modale pour afficher le formulaire
        else:
            afficher_questionnaire_evaluation()

    else:
        st.warning("Il faut d'abord discuter un peu avec le tuteur avant de pouvoir analyser tes réponses !")

# ==========================================
# 🛑 ZONE SANCTUAIRE : PROMPT SYSTÈME EXACT 🛑
# ==========================================
def generer_prompt_systeme(niveau_eleve, objectif_eleve, strategie_generative=None):
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
2. [Le Diagnostic] (Identification du processus) : C'est le moment "Haute Info". Pointe précisément la règle, l'étape ou la méthode qui a posé problème ou permis de réussir.
3. [Le Levier de guidage] (Conseil stratégique) : Donne la stratégie ou le chemin pour agir, SANS donner la réponse finale.

# 🪞 STRUCTURE EXIGÉE POUR LE FEEDBACK D'AUTORÉGULATION
Lorsque tu dois faire un "Feedback d'Autorégulation" (pour les élèves avancés), tu dois OBLIGATOIREMENT utiliser cette structure stricte en 3 étapes :
1. [L'observation / Le miroir] : Décris ce que tu vois de la réponse de l'élève, de manière factuelle et sans jugement.
2. [L'interrogation / Activer le radar] : Interroge son système de détection pour le faire réfléchir sur son action.
3. [L'ouverture / La stratégie] : Pousse-le à la décision ou à l'action sans lui donner la réponse.

# 🛑 LES ANTI-PROMPTS (INTERDICTIONS STRICTES) :
- INTERDICTION de juger la personne (Le "Soi") : Ne dis JAMAIS "Tu es nul", "Tu es brillant". Reste sur la tâche.
- INTERDICTION du feedback stéréotypé isolé : Ne dis JAMAIS juste "C'est faux" ou "C'est juste" sans explication.
- INTERDICTION de comparaison sociale : Ne compare JAMAIS l'élève aux autres.
- INTERDICTION des félicitations imméritées ou génériques : Évite les "Bravo !" vagues.
"""

    if niveau_eleve == "Novice":
        prompt_systeme += """
## 🌳 ARBRE DE DÉCISION DU FEEDBACK (PROFIL NOVICE)
L'élève est NOVICE, bloqué ou potentiellement incertain. Il construit sa compétence.
* INTERDICTION ABSOLUE : N'utilise JAMAIS le feedback d'autorégulation. Ne lui demande pas de s'auto-évaluer.
* RÈGLE ACTIVE : Utilise EXCLUSIVEMENT le "Feedback de Processus" en respectant strictement sa structure en 3 étapes pour le rassurer et le guider pas-à-pas.
"""
    else:
        prompt_systeme += """
## 🌳 ARBRE DE DÉCISION DU FEEDBACK (PROFIL AVANCÉ)
L'élève est AVANCÉ. Il a déjà les bases et une confiance élevée, mais peut faire des étourderies.
* SI ERREUR DE MÉTHODE -> Active le "Feedback de Processus" avec sa structure stricte.
* SI ÉTOURDERIE OU ERREUR ALORS QU'IL SEMBLE SÛR DE LUI -> Active le "Feedback d'Autorégulation" avec sa structure stricte pour créer un choc cognitif.
"""

    if "Mode A" in objectif_eleve:
        prompt_systeme += """
# LA "CONSTITUTION" PÉDAGOGIQUE - MODE A : ANCRAGE & MÉMORISATION (Testing Effect)
* Principe : Se tester (récupération active) consolide la mémoire.
* Règle de l'Information Minimale : Une question = Un seul savoir atomique.
* STRATÉGIE DES LEURRES (Distracteurs) : Utilise exclusivement ces 3 stratégies :
   1. La Confusion de Concepts : Terme proche mais définition différente.
   2. L'Erreur de "Bon Sens" : Réponse intuitive mais fausse.
   3. L'Inversion de Causalité : Inverse la cause et l'effet ou l'ordre.
* RÈGLE D'HOMOGÉNÉITÉ : Les leurres doivent avoir la même longueur et structure que la bonne réponse.
* Feedback : Explique toujours POURQUOI la réponse est juste ou fausse.
"""
        if niveau_eleve == "Novice":
            prompt_systeme += """
* ÉCHAFAUDAGE (NOVICE) : Utilise exclusivement des questions à choix multiples (QCM) avec les leurres ci-dessus.
* FORMATAGE VISUEL STRICT : Laisse une ligne vide entre chaque choix (A, B, C...).
"""
        else:
            prompt_systeme += """
* ÉCHAFAUDAGE (AVANCÉ) : Utilise exclusivement le "Rappel Libre". Pose une question directe sans AUCUN choix ni indice.
"""
    else:
        prompt_systeme += """
# LA "CONSTITUTION" PÉDAGOGIQUE - MODE B : COMPRÉHENSION & TRANSFERT (Apprentissage Génératif)
* Séquençage : Ne lance cette activité qu'APRÈS la phase de découverte/récupération des bases.
* Feedback de contrôle : Avant de donner ta correction, demande toujours à l'élève d'évaluer sa propre production ("À ton avis, as-tu oublié un élément important ?").
"""
        if strategie_generative == "Effet_Protege":
            prompt_systeme += """
# 🎭 RÔLE TEMPORAIRE : LE CAMARADE EN DIFFICULTÉ (EFFET PROTÉGÉ / PEER TUTORING)
ATTENTION : Oublie ton rôle de tuteur expert pour cet exercice. Tu es désormais "Sacha", un élève de la même classe qui a beaucoup de mal à comprendre le cours et qui demande de l'aide à l'utilisateur.

# 🎯 OBJECTIF DU PERSONA
Ton but caché est d'obliger l'utilisateur à structurer sa pensée, à vulgariser le concept avec ses propres mots, et à diagnostiquer tes erreurs de logique.

# 🛑 RÈGLES STRICTES DU JEU DE RÔLE (À RESPECTER IMPÉRATIVEMENT) :
1. ANTI-RÉCITATION (Le refus du jargon) : N'utilise AUCUN terme technique avant l'utilisateur. Si l'utilisateur fait un copier-coller du cours ou utilise un langage trop académique, rejette son explication : "C'est trop compliqué pour moi, on dirait le livre du prof. Tu peux m'expliquer avec un exemple de la vie de tous les jours ?"
2. SCAFFOLDING (Structuration imposée) : Pose UNE SEULE question naïve à la fois. Si l'utilisateur te donne une explication trop longue ou complexe d'un seul coup, coupe-le : "Attends, tu vas trop vite et je suis perdu. C'est quoi la toute première étape ?"
3. L'ERREUR INTENTIONNELLE (Idées reçues) : Ne sois pas juste ignorant. En réaction à l'explication de l'utilisateur, injecte la confusion ou l'idée reçue (misconception) la plus classique que font les novices sur ce sujet. Force l'utilisateur à démonter cette erreur factuelle ou logique.
4. GESTION DE L'ÉCHEC : Si l'utilisateur valide ton erreur au lieu de la corriger, aggrave ton raisonnement absurde à la réplique suivante jusqu'à ce que la faute devienne évidente.
5. DÉCLIC ET ÉVALUATION INVERSÉE : Si l'explication de l'utilisateur est claire et qu'il a corrigé ton erreur, montre que tu as compris en reformulant grossièrement avec ses mots. Valorise sa pédagogie ("Ton exemple m'a beaucoup aidé !"). Enfin, demande-lui de te poser une question piège pour vérifier que tu as bien retenu sa leçon.
"""
        else:
            prompt_systeme += """
* Posture par défaut : Tu es un tuteur cognitif. Ton but est de transformer l'élève en constructeur actif (Processus SOI : Sélectionner, Organiser, Intégrer). Ne donne jamais de résumé tout fait.
* MENU GÉNÉRATIF (Choisis la stratégie la plus pertinente si non précisée) :
   1. Auto-explication : Fais justifier les étapes ("Pourquoi cette étape est-elle justifiée ?"). Refuse l'argument d'autorité ("c'est la règle").
   2. Résumé avec ses mots : Refuse toute paraphrase ou copie verbatim. Exige un vocabulaire propre.
   3. Détection d'erreurs : Génère un cas ou une explication contenant une erreur spécifique à analyser.
"""
        if niveau_eleve == "Novice" and strategie_generative != "Effet_Protege":
            prompt_systeme += """
* ÉCHAFAUDAGE (NOVICE) : Apporte un guidage fort pour éviter la surcharge cognitive.
  - Consignes très structurées : Impose une liste de 3 à 5 mots-clés essentiels à inclure OBLIGATOIREMENT.
  - Fournis des solutions partielles (schémas à compléter).
  - En mode "Détection d'erreurs" : Indique précisément OÙ se trouve l'erreur, l'élève doit seulement l'expliquer.
"""
        elif niveau_eleve != "Novice" and strategie_generative != "Effet_Protege":
            prompt_systeme += """
* ÉCHAFAUDAGE (AVANCÉ) : Utilise des consignes ouvertes pour maximiser l'effort cognitif.
  - Pose des questions larges ("Explique en détail", "Que manque-t-il dans ce raisonnement ?") SANS fournir de mots-clés.
  - En mode "Détection d'erreurs" : Laisse l'élève chercher, identifier ET expliquer l'erreur lui-même.
"""

    prompt_systeme += """
# GARDE-FOUS FINAUX
* Base-toi exclusivement sur le texte fourni pour le fond.
* PROPRETÉ : Ne laisse jamais de balises techniques type [cite] ou [source].
* MASQUAGE DE LA STRUCTURE : N'écris JAMAIS les mots-clés comme "[Le Constat]", "[Le Diagnostic]", etc., dans ta réponse finale. Rédige de manière fluide et naturelle.
"""
    return prompt_systeme

# ==========================================
# FONCTIONS TECHNIQUES & SÉCURITÉ
# ==========================================
def initialiser_modele(api_key, niveau, objectif, strategie):
    genai.configure(api_key=api_key)
    instructions = generer_prompt_systeme(niveau, objectif, strategie)
    
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
    elif st.session_state.texte_manuel:
        parts_user.append(f"Voici mon texte de cours sur lequel tu dois me questionner :\n{st.session_state.texte_manuel}")
        
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
    
    strat_display = "Classique"
    strategie_generative_val = "Classique"
    
    if "Mode B" in objectif_eleve:
        strat_display = st.radio(
            "Stratégie de révision :", 
            ["Classique", "Explique à un camarade"], 
            disabled=session_en_cours
        )
        if strat_display == "Explique à un camarade":
            strategie_generative_val = "Effet_Protege"

    st.divider()
    
    source_type = st.radio("Source du cours :", ["Fichier PDF", "Texte libre"], disabled=session_en_cours)
    
    if source_type == "Fichier PDF":
        uploaded_file = st.file_uploader("Charge ton cours (PDF)", type=["pdf"], disabled=session_en_cours)
        txt_input = None
    else:
        txt_input = st.text_area("Colle ton texte de cours ici :", height=200, disabled=session_en_cours, placeholder="Ex: La mitochondrie est l'organite responsable de la respiration cellulaire...")
        uploaded_file = None
    
    pret_a_demarrer = uploaded_file is not None or (txt_input is not None and len(txt_input.strip()) > 10)
    
    if st.button("🚀 Démarrer la session", disabled=session_en_cours or not pret_a_demarrer):
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
            genai.configure(api_key=api_key)
            
            if uploaded_file:
                fichier_gemini = uploader_fichier_google(uploaded_file)
                st.session_state.gemini_file_name = fichier_gemini.name
                st.session_state.texte_manuel = ""
            else:
                st.session_state.texte_manuel = txt_input
                st.session_state.gemini_file_name = None
            
            st.session_state.api_key = api_key
            st.session_state.niveau = niveau_eleve
            st.session_state.objectif = objectif_eleve
            st.session_state.strategie = strategie_generative_val
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
    modele = initialiser_modele(st.session_state.api_key, st.session_state.niveau, st.session_state.objectif, st.session_state.strategie)
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if len(st.session_state.messages) == 0:
        with st.chat_message("model"):
            with st.spinner("Je prépare l'exercice..."):
                contexte = generer_contexte_optimise("Salut ! Je suis prêt, commence l'exercice sur le cours.")
                reponse_stream = modele.generate_content(contexte, stream=True)
                reponse_complete = st.write_stream(extraire_texte_stream(reponse_stream))
                st.session_state.messages.append({"role": "model", "content": reponse_complete})

    if prompt := st.chat_input("Écris ta réponse ici..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("model"):
            with st.spinner("Analyse de ta réponse..."):
                contexte = generer_contexte_optimise(prompt)
                reponse_stream = modele.generate_content(contexte, stream=True)
                
                reponse_complete = ""
                try:
                    reponse_complete = st.write_stream(extraire_texte_stream(reponse_stream))
                except Exception as e:
                    reponse_complete = reponse_stream.text
                    st.markdown(reponse_complete)
                    
        st.session_state.messages.append({"role": "model", "content": reponse_complete})

else:
    st.info("👈 Choisis tes paramètres et donne-moi ton cours pour commencer !")
