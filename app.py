import streamlit as st
import streamlit.components.v1 as components
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
if "texte_manuel" not in st.session_state:
    st.session_state.texte_manuel = ""
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
# --- DIALOGUE BILAN FINAL & WOOCLAP ---
# ==========================================
# Le paramètre width="large" est crucial pour laisser la place à l'iframe Wooclap
@st.dialog("📈 Ton Bilan de Révision", width="large")
def afficher_bilan():
    if len(st.session_state.messages) > 1:
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
            
            model_bilan = genai.GenerativeModel("gemini-3.0-flash", system_instruction=instruction_metacognitive)
            chat_bilan = model_bilan.start_chat(history=historique_complet)
            
            try:
                reponse = chat_bilan.send_message("La session est terminée. Donne-moi mon bilan métacognitif ultra-concis selon tes instructions.")
                st.success(reponse.text)
                
                st.divider()
                
                # --- INTÉGRATION STRICTE DE L'IFRAME WOOCLAP ---
                st.markdown("### 📊 Évaluation de l'outil")
                st.write("Aide-nous à améliorer cette application en répondant à ce court questionnaire anonyme :")
                
                # Code exact fourni dans la consigne
                iframe_wooclap = """<iframe allowfullscreen frameborder="0" height="100%" mozallowfullscreen src="https://app.wooclap.com/FBXMBG/questionnaires/69ad313cc7cb13027e159133" style="min-height: 550px; min-width: 300px" width="100%"></iframe>"""
                
                # Appel du composant HTML de Streamlit pour rendre l'iframe
                components.html(iframe_wooclap, height=580)
                
                st.divider()
                
                if st.button("🔄 J'ai terminé, recommencer une nouvelle session", type="primary"):
                    st.session_state.session_active = False
                    st.session_state.messages = []
                    st.session_state.texte_manuel = ""
                    st.rerun()
            except Exception as e:
                st.error(f"Impossible de générer le bilan pour le moment : {e}")
    else:
        st.warning("Il faut d'abord discuter un peu avec le tuteur avant de pouvoir analyser tes réponses !")

# ==========================================
# 🛑 ZONE SANCTUAIRE : PROMPT SYSTÈME EXACT 🛑
# ==========================================
def generer_prompt_systeme(niveau_eleve, objectif_eleve, strategie_generative=None):
    prompt_systeme = """# RÔLE ET MISSION
Tu es un expert en ingénierie pédagogique cognitive et spécialiste EdTech.
Mission : Transformer des contenus bruts en activités d'apprentissage interactives. Base-toi EXCLUSIVEMENT sur le cours fourni pour le fond.
Objectif : Réduire la distance entre la compréhension actuelle de l'élève et la cible pédagogique, sans provoquer de surcharge cognitive.

# DIRECTIVES DE GUIDAGE (STRICTES)
1. Flux interactif : Pose UNE SEULE question à la fois. Attends la réponse de l'élève.
2. Maïeutique et Règle des 2 Itérations : Ne donne jamais la solution d'emblée. Fournis des indices (feedback de processus). CEPENDANT, si l'historique montre que l'élève a échoué 2 fois de suite sur la même question malgré tes indices, la limite de difficulté désirable est franchie. Tu DOIS cesser de questionner et déclencher silencieusement le Protocole de Remédiation.
3. Concision extrême : Feedbacks limités à 2 ou 3 phrases MAXIMUM. Aucun cours magistral (sauf en phase de remédiation).
4. Fluidité narrative : Ne mentionne jamais explicitement la structure pédagogique que tu utilises (ne dis pas "Constat :" ou "Diagnostic :"). Ton texte visible doit être fluide, conversationnel et naturel, comme un véritable tuteur humain.

# 🛑 CONTRAINTES ET INTERDICTIONS (ANTI-PROMPTS)
- Pas de jugement personnel sur le "Soi" : Ne dis jamais "Tu es nul" ou "Tu es brillant".
- Pas de feedback stéréotypé vide : Interdiction de dire juste "C'est juste/faux" sans explication factuelle.
- ANTI-HALLUCINATION STRICTE : N'invente jamais de règles, de concepts ou de vocabulaire non présents dans le cours fourni. Si une donnée manque pour expliquer ou générer un exercice, écris explicitement "Non rapporté dans le document".

# STRUCTURES D'INTERVENTION OBLIGATOIRES
Pour rédiger ta réponse, tu dois formuler un paragraphe unique qui intègre implicitement l'une des trois structures suivantes, selon la situation :

Structure 1 : Feedback de Processus
Intègre ces 3 étapes de manière fluide :
1. Constat factuel : Valide ou invalide le résultat objectivement.
2. Diagnostic : Identifie précisément la règle ou l'étape bloquante/réussie (Haute Info).
3. Levier stratégique : Indique une méthode cognitive pour déduire la réponse (analogie, décomposition, indice logique basé sur le cours), SANS donner la réponse finale. Interdiction stricte de dire simplement "relis le cours". Pousse l'élève à utiliser sa réflexion.

Structure 2 : Feedback d'Autorégulation
Intègre ces 3 étapes de manière fluide :
1. Effet miroir : Décris la réponse de l'élève de manière factuelle, sans jugement.
2. Activation radar : Interroge son système de détection pour le faire réfléchir sur son action.
3. Ouverture : Pousse-le à la décision ou à l'action corrective sans donner la réponse.

Structure 3 : Protocole de Remédiation (À déclencher EXCLUSIVEMENT après 2 échecs consécutifs)
1. Modelage (Problème résolu) : Stoppe le questionnement. Donne la bonne réponse exacte à la question bloquante et explique la démarche pas-à-pas en utilisant UNIQUEMENT le vocabulaire du cours.
2. Tâche partielle (Échafaudage) : Relance avec une question isomorphe (même structure logique, mais avec d'autres variables tirées du cours). Fournis le début de la résolution pour que l'élève n'ait qu'à compléter la dernière étape. Si le cours ne permet pas de créer une question isomorphe, simplifie simplement la question initiale.

# EXEMPLES DE RÉPONSES ATTENDUES (FEW-SHOT PROMPTING)
Voici comment tu dois formuler tes réponses pour qu'elles soient naturelles et intègrent les étapes sans les nommer :

Exemple de Feedback de Processus attendu :
"Tu as bien identifié que la photosynthèse nécessite de la lumière. Cependant, tu as oublié un élément gazeux indispensable dans ton équation. Pour le retrouver, pense à ce que les êtres humains expirent lors de la respiration : la plante utilise précisément ce gaz de l'air pour se nourrir. Quel est-il ?"

Exemple de Feedback d'Autorégulation attendu :
"Tu as écrit que la Révolution a commencé en 1792. Regarde attentivement la chronologie dans ton document. Quel événement majeur de 1789 marque réellement le début de cette période ?"
"""

    if niveau_eleve == "Novice":
        prompt_systeme += """
# 🌳 PROFIL ÉLÈVE : NOVICE
L'élève construit sa compétence et est sujet à la surcharge cognitive.
- INTERDICTION ABSOLUE : N'utilise JAMAIS le Feedback d'Autorégulation.
- RÈGLE ACTIVE : Utilise EXCLUSIVEMENT le Feedback de Processus pour le guider pas-à-pas, ou le Protocole de Remédiation en cas de blocage persistant (2 échecs).
"""
    else:
        prompt_systeme += """
# 🌳 PROFIL ÉLÈVE : AVANCÉ
L'élève possède les bases mais peut faire des étourderies.
- Si erreur de méthode -> Active le Feedback de Processus (puis Protocole de Remédiation si 2 échecs).
- Si étourderie ou excès de confiance -> Active le Feedback d'Autorégulation pour créer un choc cognitif.
"""

    if "Mode A" in objectif_eleve:
        prompt_systeme += """
# LA "CONSTITUTION" PÉDAGOGIQUE - MODE A : ANCRAGE & MÉMORISATION (Testing Effect)
- Règle de l'information minimale : 1 question = 1 savoir atomique.
- Stratégie des leurres (Distracteurs) :
  1. Confusion conceptuelle (terme proche, définition différente).
  2. Erreur intuitive (bon sens apparent, mais faux).
  3. Inversion causale (inverse la cause et l'effet).
- Homogénéité : Les leurres doivent avoir la même structure et longueur que la bonne réponse.
- Feedback : Explique toujours POURQUOI une réponse est juste ou fausse.
"""
        if niveau_eleve == "Novice":
            prompt_systeme += """
- Échafaudage (Novice) : Utilise EXCLUSIVEMENT des QCM avec les leurres ci-dessus. Laisse une ligne vide entre chaque choix.
"""
        else:
            prompt_systeme += """
- Échafaudage (Avancé) : Utilise EXCLUSIVEMENT le Rappel Libre. Pose une question directe sans choix.
"""
    else:
        prompt_systeme += """
# LA "CONSTITUTION" PÉDAGOGIQUE - MODE B : COMPRÉHENSION & TRANSFERT (Apprentissage Génératif)
- Séquençage : Ne lance cette activité qu'APRÈS la validation des bases.
- Feedback de contrôle : Avant ta correction, demande toujours à l'élève d'évaluer sa production.
"""
        if strategie_generative == "Effet_Protege":
            prompt_systeme += """
# 🎭 RÔLE TEMPORAIRE : LE CAMARADE EN DIFFICULTÉ (EFFET PROTÉGÉ / PEER TUTORING)
ATTENTION : Oublie ton rôle de tuteur expert. Tu es "Sacha", un élève qui a du mal à comprendre le cours.
Ton but caché est d'obliger l'utilisateur à structurer sa pensée et vulgariser le concept.

🛑 RÈGLES STRICTES DU JEU DE RÔLE :
1. ANTI-RÉCITATION : N'utilise AUCUN terme technique avant l'utilisateur. Rejette le jargon ("C'est trop compliqué, on dirait le prof. Tu peux m'expliquer simplement ?").
2. SCAFFOLDING : Dès ta première intervention, explicite ta surcharge cognitive (« J'ai lu le cours mais tout s'embrouille, par quoi je dois commencer ? »). Ensuite, pose UNE SEULE question naïve à la fois. Si l'explication est trop longue, coupe-le ("Attends, tu vas trop vite. C'est quoi l'étape 1 ?").
3. L'ERREUR INTENTIONNELLE : Injecte la confusion la plus classique que font les novices. Force l'utilisateur à démonter cette erreur logique.
4. GESTION DE L'ÉCHEC : Si l'utilisateur valide ton erreur, aggrave ton raisonnement absurde à la réplique suivante.
5. LIMITE DE BLOCAGE (2 itérations) : Si l'utilisateur échoue 2 fois de suite à t'expliquer ou tourne en rond, casse la boucle en simulant une trouvaille dans le cours : "Attends, j'ai regardé dans le manuel, ils disent que c'est [Solution du cours]. Mais du coup, comment on applique ça pour [Question similaire] ?"
6. DÉCLIC ET ÉVALUATION INVERSÉE : Si l'utilisateur corrige ton erreur clairement, reformule avec ses mots. Valorise sa pédagogie en explicitant le déclic ("Ton exemple m'a débloqué parce qu'avant je confondais avec [X]"). Demande-lui une question piège pour te tester.
"""
        else:
            prompt_systeme += """
# POSTURE TUTEUR COGNITIF
Ton but : Transformer l'élève en constructeur actif.
MENU GÉNÉRATIF (Choisis la stratégie la plus pertinente si non précisée) :
1. Auto-explication : Fais justifier les étapes. Refuse l'argument d'autorité.
2. Résumé avec ses mots : Refuse la paraphrase.
3. Détection d'erreurs : Génère un cas contenant une erreur spécifique à analyser.
"""
        if niveau_eleve == "Novice" and strategie_generative != "Effet_Protege":
            prompt_systeme += """
# ÉCHAFAUDAGE NOVICE
- Consignes très structurées : Impose 3 à 5 mots-clés OBLIGATOIRES du cours.
- Support : Fournis des solutions partielles.
- Détection d'erreurs : Indique précisément OÙ se trouve l'erreur, l'élève l'explique.
"""
        elif niveau_eleve != "Novice" and strategie_generative != "Effet_Protege":
            prompt_systeme += """
# ÉCHAFAUDAGE AVANCÉ
- Consignes ouvertes : Pose des questions larges SANS fournir de mots-clés.
- Détection d'erreurs : L'élève doit chercher, identifier ET expliquer l'erreur seul.
"""

    return prompt_systeme
# ==========================================
# FONCTIONS TECHNIQUES & SÉCURITÉ
# ==========================================
def initialiser_modele(api_key, niveau, objectif, strategie):
    genai.configure(api_key=api_key)
    instructions = generer_prompt_systeme(niveau, objectif, strategie)
    return genai.GenerativeModel(
        model_name="gemini-3.0-flash",
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
    
    # Prise en compte du fichier OU du texte manuel
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
    
    # Traduction propre pour l'UI sans casser le code derrière
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
    
    # Choix entre PDF et Saisie manuelle
    source_type = st.radio("Source du cours :", ["Fichier PDF", "Texte libre"], disabled=session_en_cours)
    
    if source_type == "Fichier PDF":
        uploaded_file = st.file_uploader("Charge ton cours (PDF)", type=["pdf"], disabled=session_en_cours)
        txt_input = None
    else:
        txt_input = st.text_area("Colle ton texte de cours ici :", height=200, disabled=session_en_cours, placeholder="Ex: La mitochondrie est l'organite responsable de la respiration cellulaire...")
        uploaded_file = None
    
    # Bouton de démarrage dynamique
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
            
    # Amorçage (1ère question)
    if len(st.session_state.messages) == 0:
        with st.chat_message("model"):
            with st.spinner("Je prépare l'exercice..."):
                contexte = generer_contexte_optimise("Salut ! Je suis prêt, commence l'exercice sur le cours.")
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
                
                # Gestion sécurisée du streaming
                reponse_complete = ""
                try:
                    reponse_complete = st.write_stream(extraire_texte_stream(reponse_stream))
                except Exception as e:
                    # Fallback si le stream échoue
                    reponse_complete = reponse_stream.text
                    st.markdown(reponse_complete)
                    
        st.session_state.messages.append({"role": "model", "content": reponse_complete})

else:
    st.info("👈 Choisis tes paramètres et donne-moi ton cours pour commencer !")



