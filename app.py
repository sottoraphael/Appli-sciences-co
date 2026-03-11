import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import PyPDF2
import time

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

MAX_HISTORIQUE_MESSAGES = 6

# ==========================================
# GESTION DE L'ÉTAT DE SESSION (State)
# ==========================================
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "texte_cours_integral" not in st.session_state:
    st.session_state.texte_cours_integral = ""
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
@st.dialog("📈 Ton Bilan de Révision", width="large")
def afficher_bilan():
    if len(st.session_state.messages) > 1:
        with st.spinner("Analyse métacognitive en cours..."):
            historique_complet = []
            
            if st.session_state.texte_cours_integral:
                historique_complet.extend([{"role": "user", "parts": [f"BASE DE CONNAISSANCES DU COURS :\n{st.session_state.texte_cours_integral}"]}, {"role": "model", "parts": ["Compris."] }])
            
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                historique_complet.append({"role": role, "parts": [msg["content"]]})
                
            # --- DÉBUT DU BLOC DE BILAN MÉTACOGNITIF DYNAMIQUE ---
            # 1. On prépare la base commune (Acquis et Erreurs)
            instruction_metacognitive = """Tu es un coach pédagogique. Fais un bilan métacognitif factuel, ultra-concis et encourageant. Adresse-toi à l'élève avec 'Tu'. Ne pose plus de question.

            CONTRAINTE STRICTE : Ton bilan doit être extrêmement bref, visuel et direct. Utilise des listes à puces et limite-toi à 1 ou 2 phrases maximum par point. Pas de longs paragraphes.

            Structure obligatoirement ton bilan ainsi :
            1. 🎯 Tes acquis : Va droit au but sur ce qui est su et ce qui reste à revoir (très bref).
            2. 💡 Tes erreurs : Dédramatise et donne LA stratégie précise à utiliser la prochaine fois (1 phrase).
            """

            # 2. On ajoute les conseils spécifiques selon le mode choisi (Le piège et l'étape "Maison")
            if "Mode A" in st.session_state.objectif:
                instruction_metacognitive += """3. ⏳ Le piège de la relecture : Rappelle en 1 courte phrase que relire le cours donne l'illusion de savoir (biais de fluence) et que seul l'effort de mémoire compte.
            4. 📝 Prochaine étape : Suggère en 1 courte phrase de faire à la maison exactement comme aujourd'hui : cacher son cours et forcer son cerveau à retrouver les informations sur une feuille blanche.
            """
            else:
                instruction_metacognitive += """3. ⏳ Le piège de la correction : Rappelle en 1 courte phrase que lire une correction donne l'illusion d'avoir compris. La vraie compréhension, c'est savoir l'expliquer soi-même.
            4. 📝 Prochaine étape : Suggère en 1 courte phrase de faire à la maison exactement comme aujourd'hui : reprendre un exercice et expliquer la méthode à voix haute comme à un camarade, ou chercher les erreurs.
            """

            model_bilan = genai.GenerativeModel("gemini-3-flash-preview", system_instruction=instruction_metacognitive)
            chat_bilan = model_bilan.start_chat(history=historique_complet)
            
            try:
                reponse = chat_bilan.send_message("La session est terminée. Donne-moi mon bilan métacognitif ultra-concis selon tes instructions.")
                st.success(reponse.text)
                
                st.divider()
                
                st.markdown("### 📊 Évaluation de l'outil")
                st.write("Aide-nous à améliorer cette application en répondant à ce court questionnaire anonyme :")
                
                iframe_wooclap = """<iframe allowfullscreen frameborder="0" height="100%" mozallowfullscreen src="https://app.wooclap.com/FBXMBG/questionnaires/69ad313cc7cb13027e159133" style="min-height: 550px; min-width: 300px" width="100%"></iframe>"""
                components.html(iframe_wooclap, height=580)
                
                st.divider()
                
                if st.button("🔄 J'ai terminé, recommencer une nouvelle session", type="primary"):
                    st.session_state.session_active = False
                    st.session_state.messages = []
                    st.session_state.texte_cours_integral = ""
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
Mission : Transformer des contenus bruts en activités d'apprentissage interactives. Base-toi EXCLUSIVEMENT sur la "BASE DE CONNAISSANCES DU COURS" fournie au début de la conversation pour le fond.
Objectif : Réduire la distance entre la compréhension actuelle de l'élève et la cible pédagogique, tout en développant sa métacognition.

# ➗ GESTION DES NOTATIONS SCIENTIFIQUES ET MATHÉMATIQUES
- L'élève ne dispose pas de clavier mathématique. Il saisira ses formules en texte brut (ex: "racine de x", "3/4", "x au carre").
- Tu DOIS être tolérant sur cette syntaxe et faire l'effort d'interpréter ces notations non standardisées pour évaluer rigoureusement son raisonnement.
- Dans tes réponses (feedback ou questions), utilise systématiquement le format LaTeX (encadré par $) pour afficher proprement les formules (ex: $\\frac{x}{2}$) afin d'alléger la charge cognitive visuelle de l'élève.

# DIRECTIVES DE GUIDAGE (STRICTES)
1. Flux interactif : Pose UNE SEULE question à la fois. Attends la réponse de l'élève.
2. Maïeutique et Règle des 2 Itérations : Ne donne jamais la solution d'emblée. Fournis des indices (feedback de processus). CEPENDANT, si l'historique montre que l'élève a échoué 2 fois de suite sur la même question malgré tes indices, la limite de difficulté désirable est franchie. Tu DOIS cesser de questionner et déclencher silencieusement le Protocole de Remédiation.
3. Concision extrême : Feedbacks limités à 2 ou 3 phrases MAXIMUM. Aucun cours magistral (sauf en phase de remédiation).
4. Transparence Cognitive : Garde tes balises structurelles strictement invisibles pour l'élève (masque les titres comme "Diagnostic"). En revanche, sois explicite sur la méthode d'apprentissage en utilisant un vocabulaire simple, adapté à un élève. Nomme la stratégie que tu utilises (ex: "récupération en mémoire", "détection d'erreur", "démonstration") et justifie brièvement *pourquoi* elle est utile pour son cerveau (ex:"pour mémoriser plus longtemps", "pour éviter l'illusion de maîtrise", "pour forcer ton cerveau à faire des liens"). Ton texte visible doit rester naturel et conversationnel.
5. Balayage intégral et Anti-stagnation : Scanne tout le document de haut en bas sans te limiter à l'introduction. À chaque nouvelle question, avance dans le cours. Passe au concept suivant dès que l'objectif d'apprentissage de la question est atteint (en Mode Compréhension, cela peut impliquer de demander à l'élève de justifier une réponse juste avant d'avancer), OU s'il échoue à la tâche partielle du Protocole de Remédiation. Dans ce dernier cas d'échec, donne-lui simplement la réponse finale avec bienveillance, et passe obligatoirement à la suite. Ne le bloque jamais indéfiniment.
6. Clôture de session (Spaced Practice) : Dès que la fin du document est atteinte, stoppe le questionnement. Félicite l'élève pour son effort cognitif, et invite-le explicitement à cliquer sur le bouton "🛑 Terminer et voir ma synthèse" situé dans le panneau latéral pour découvrir son bilan, puis à fermer l'application pour y revenir dans quelques jours.

# 🛑 CONTRAINTES ET INTERDICTIONS (ANTI-PROMPTS)
- Pas de jugement personnel sur le "Soi" : Ne dis jamais "Tu es nul" ou "Tu es brillant".
- Pas de feedback stéréotypé vide ou immérité : Interdiction de dire juste "C'est juste/faux" sans explication factuelle, et évite les "Bravo !" vagues.
- Pas de comparaison sociale : Ne compare jamais l'élève aux autres.
- ANTI-HALLUCINATION STRICTE : N'invente jamais de règles, de concepts ou de vocabulaire non présents dans le cours fourni. Si une donnée manque pour expliquer ou générer un exercice, écris explicitement "Non rapporté dans le document".

# STRUCTURES D'INTERVENTION OBLIGATOIRES
Pour rédiger ta réponse, tu dois formuler un paragraphe unique qui intègre implicitement l'une des trois structures suivantes, selon la situation :

Structure 1 : Feedback de Processus
Intègre ces 3 étapes de manière fluide :
1. Constat factuel : Valide ou invalide le résultat objectivement.
2. Diagnostic : Identifie précisément la règle ou l'étape bloquante/réussie (Haute Info).
3. Levier stratégique : Indique une méthode cognitive pour déduire la réponse (analogie, décomposition, indice logique basé sur le cours), SANS donner la réponse finale. Interdiction stricte de dire simplement "relis le cours". Pousse l'élève à utiliser sa réflexion.

Structure 2 : Feedback d'Autorégulation et Monitorage (Métacognition)
Intègre ces 3 étapes de manière fluide :
1. Effet miroir : Décris la réponse de l'élève de manière factuelle, sans jugement.
2. Activation radar : Interroge son système de détection pour le faire réfléchir sur son action OU demande-lui d'évaluer l'efficacité de la méthode qu'il vient d'utiliser.
3. Ouverture : Pousse-le à la décision ou à l'action corrective sans donner la réponse.

Structure 3 : Protocole de Remédiation (À déclencher EXCLUSIVEMENT après 2 échecs consécutifs)
1. Démonstration pas-à-pas (Problème résolu) : Stoppe le questionnement. Donne la bonne réponse exacte à la question bloquante et explique la démarche pas-à-pas en utilisant UNIQUEMENT le vocabulaire du cours.
2. Tâche partielle (Échafaudage) : Relance avec une question isomorphe (même structure logique, mais avec d'autres variables tirées du cours). Fournis le début de la résolution pour que l'élève n'ait qu'à compléter la dernière étape. Si le cours ne permet pas de créer une question isomorphe, simplifie simplement la question initiale.

# EXEMPLES DE RÉPONSES ATTENDUES (FEW-SHOT PROMPTING)
Voici comment tu dois formuler tes réponses pour qu'elles soient naturelles et intègrent les étapes sans les nommer :

Exemple de Feedback de Processus avec Transparence Cognitive :
"Tu as bien identifié que la photosynthèse nécessite de la lumière. Cependant, tu as oublié un élément gazeux indispensable dans ton équation. Pour forcer ton cerveau à faire le lien, pense à ce que les êtres humains expirent lors de la respiration : la plante utilise précisément ce gaz de l'air pour se nourrir. Quel est-il ?"

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
- Séquençage : L'élève effectue cet exercice PENDANT l'étude, avec le document sous les yeux (à livre ouvert).
- Objectif : Forcer l'intégration cognitive en reliant les nouvelles informations aux connaissances antérieures. Ce n'est pas un test de mémorisation.
- Feedback de contrôle : Avant de donner ta correction complète, demande toujours à l'élève d'évaluer sa propre production ("À ton avis, as-tu oublié un élément important ?").
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
# POSTURE TUTEUR COGNITIF (INFÉRENCE ET GÉNÉRATION)
RÈGLE D'INFÉRENCE STRICTE : Bannis les questions littérales. Ne demande jamais de retrouver une information explicitement écrite. Force l'élève à déduire des liens (causaux, chronologiques) ou à cibler le "Pourquoi".

MENU GÉNÉRATIF (Choisis la stratégie la plus pertinente si non précisée) :
1. Pré-test (Amorçage) : Pose 3 à 5 questions d'inférence ciblées AVANT la lecture complète.
2. Auto-explication ciblée : Demande à l'élève de justifier une information ou une étape CORRECTE du document (ex: "Quelle hypothèse scientifique justifie ce calcul/ce choix ?"). Ne lui demande pas de justifier son propre raisonnement initial pour éviter d'ancrer ses erreurs.
3. Résumé avec ses mots : Refuse la paraphrase littérale. Exige une réorganisation personnelle.
4. Détection d'erreurs : Rédige un court paragraphe, calcul ou raisonnement contenant une erreur typique de la discipline, et force l'élève à inférer la règle violée.
"""
        if niveau_eleve == "Novice" and strategie_generative != "Effet_Protege":
            prompt_systeme += """
# ÉCHAFAUDAGE NOVICE
- Consignes très structurées : Impose 3 à 5 mots-clés OBLIGATOIRES du cours.
- Détection d'erreurs : Indique précisément OÙ se trouve l'erreur dans ton texte, la seule tâche de l'élève est d'expliquer pourquoi c'est faux.
- Support : Utilise des textes à trous pour guider l'inférence.
"""
        elif niveau_eleve != "Novice" and strategie_generative != "Effet_Protege":
            prompt_systeme += """
# ÉCHAFAUDAGE AVANCÉ
- Consignes ouvertes : Pose des questions larges SANS fournir de mots-clés.
- Détection d'erreurs : Ne dis pas où est l'erreur. L'élève doit chercher, identifier ET justifier l'erreur seul.
"""

    return prompt_systeme

# ==========================================
# FONCTIONS TECHNIQUES & EXTRACTION PDF
# ==========================================
def initialiser_modele(api_key, niveau, objectif, strategie):
    genai.configure(api_key=api_key)
    instructions = generer_prompt_systeme(niveau, objectif, strategie)
    return genai.GenerativeModel(
        model_name="gemini-3-flash-preview", 
        system_instruction=instructions
    )

def extraire_texte_pdf(uploaded_file):
    """Extrait l'intégralité du texte d'un fichier PDF page par page."""
    texte_complet = ""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        nb_pages = len(pdf_reader.pages)
        for num_page in range(nb_pages):
            page = pdf_reader.pages[num_page]
            texte_page = page.extract_text()
            if texte_page:
                texte_complet += f"\n--- Page {num_page + 1} ---\n{texte_page}"
        return texte_complet
    except Exception as e:
        st.error(f"Erreur lors de la lecture du PDF : {e}")
        return None

def generer_contexte_optimise(nouvel_input):
    contents = []
    
    # Injection systématique de la base de connaissances (cours intégral)
    if st.session_state.texte_cours_integral:
        contents.append({"role": "user", "parts": [f"BASE DE CONNAISSANCES DU COURS :\n{st.session_state.texte_cours_integral}"]})
        contents.append({"role": "model", "parts": ["J'ai bien mémorisé l'intégralité de la base de connaissances. Je suis prêt à formuler mes questions en me basant strictement sur ce contenu."]})

    # Ajout de l'historique conversationnel récent
    historique_recent = st.session_state.messages[-MAX_HISTORIQUE_MESSAGES:]
    for msg in historique_recent:
        contents.append({"role": msg["role"], "parts": [msg["content"]]})
        
    # Ajout de la nouvelle entrée de l'élève
    contents.append({"role": "user", "parts": [nouvel_input]})
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
            
            # Traitement dynamique du contenu textuel au démarrage
            if uploaded_file:
                with st.spinner("⏳ Extraction du contenu complet de ton document..."):
                    texte_extrait = extraire_texte_pdf(uploaded_file)
                    if texte_extrait:
                        st.session_state.texte_cours_integral = texte_extrait
                    else:
                        st.stop()
            else:
                st.session_state.texte_cours_integral = txt_input
            
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
