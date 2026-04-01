import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import PyPDF2
import time
import sys
import subprocess
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import os

# Imports locaux
import referentiels 
from generateur_pdf import generer_pdf_bytes

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
    .stChatMessage { border-radius: 15px; border: 1px solid #E2E8F0; }
    </style>
""", unsafe_allow_html=True)

MAX_HISTORIQUE_MESSAGES = 6

# ==========================================
# GESTION DE L'ÉTAT DE SESSION (State)
# ==========================================
if "session_active" not in st.session_state: st.session_state.session_active = False
if "messages" not in st.session_state: st.session_state.messages = []
if "texte_cours_integral" not in st.session_state: st.session_state.texte_cours_integral = ""
if "tutoriel_vu" not in st.session_state: st.session_state.tutoriel_vu = False
if "attendus_cours" not in st.session_state: st.session_state.attendus_cours = None

# ==========================================
# CONNEXION AU RÉFÉRENTIEL SÉCURISÉ
# ==========================================
try:
    REFERENTIELS = referentiels.REFERENTIEL_COLLEGE
except AttributeError:
    st.error("Le dictionnaire REFERENTIEL_COLLEGE est introuvable dans le fichier referentiels.py.")
    REFERENTIELS = {}

# ==========================================
# --- TUTORIEL D'ACCUEIL ---
# ==========================================
@st.dialog("👋 Bienvenue dans ton espace de révision", width="large")
def afficher_tutoriel():
    st.markdown("""
        <style>
        .big-font { font-size: 1.15rem !important; line-height: 1.6 !important; color: #2D3748; }
        .step-title { font-weight: 600; color: #3182CE; font-size: 1.25rem; display: block; margin-top: 15px; }
        .mode-box { background-color: #EBF8FF; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 5px solid #3182CE; }
        ul { margin-top: 5px; margin-bottom: 10px; }
        </style>
        <div class="big-font">
        Cette application s'appuie sur la recherche en <b>sciences cognitives</b> pour optimiser ton temps de travail. Elle remplace la simple relecture (peu efficace) par un entraînement actif.
        
        <div class="mode-box">
        <b>🎯 L'importance de ton objectif</b><br>
        Pour que le tuteur t'aide efficacement, tu dois d'abord évaluer ton niveau actuel dans le menu de gauche :
        <ul>
            <li><b>Pour ancrer les bases :</b> Choisis <i>Découvrir</i> ou <i>Réviser</i> (Le tuteur te posera des questions directes pour tester ta mémoire).</li>
            <li><b>Pour approfondir :</b> Choisis <i>Comprendre</i> ou <i>S'entraîner</i> (Le tuteur te posera des questions de réflexion).</li>
            <li><b>Pour le test ultime :</b> Choisis <i>Maîtriser</i>. Le tuteur jouera le rôle d'un camarade en difficulté, et c'est toi qui devras lui expliquer le cours !</li>
        </ul>
        </div>
        
        <b>Comment démarrer ta session en 3 étapes :</b>
        <span class="step-title">1. ⚙️ Paramètre ta séance</span> 
        Sélectionne ta classe, ta matière et ta situation actuelle.
        <span class="step-title">2. 🧭 Transmets ton support</span> 
        Charge ton fichier PDF ou colle le texte de ta leçon. Le tuteur se basera <i>strictement</i> sur ce document.
        <span class="step-title">3. 💬 Entraîne-toi et analyse tes erreurs</span> 
        Réponds aux questions dans le chat. À la fin, clique sur "Terminer" pour obtenir ton <b>bilan de révision</b> (ce que tu maîtrises et ce qu'il faut revoir).
        </div><br>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 J'ai compris le principe, c'est parti !", use_container_width=True):
        st.session_state.tutoriel_vu = True
        st.rerun()

if not st.session_state.tutoriel_vu:
    afficher_tutoriel()

# ==========================================
# DÉLÉGATION NEURO-SYMBOLIQUE (SYMPY)
# ==========================================
def verifier_calcul_formel(expression_prof: str, expression_eleve: str) -> dict:
    """Vérifie l'exactitude mathématique d'une réponse élève par rapport à une solution."""
    try:
        transformations = (standard_transformations + (implicit_multiplication_application,))
        exp_p_str = str(expression_prof).replace('^', '**').replace(',', '.')
        exp_e_str = str(expression_eleve).replace('^', '**').replace(',', '.')
        
        exp_p = parse_expr(exp_p_str, transformations=transformations)
        exp_e = parse_expr(exp_e_str, transformations=transformations)
        
        est_valide = sp.simplify(exp_p - exp_e) == 0
        return {"est_valide": bool(est_valide), "forme_simplifiee_eleve": str(exp_e)}
    except Exception as e:
        return {"erreur": f"Syntaxe non reconnue par le moteur formel : {str(e)}"}

# ==========================================
# FILTRE EXÉCUTIF LOCAL (spaCy)
# ==========================================
@st.cache_resource
def charger_modele_nlp():
    """Charge le modèle linguistique de base (mis en cache pour performance)."""
    try:
        import spacy
        return spacy.load("fr_core_news_sm")
    except OSError:
        subprocess.run([sys.executable, "-m", "spacy", "download", "fr_core_news_sm"], check=True)
        import spacy
        return spacy.load("fr_core_news_sm")

class AgentCritique:
    """Filtre exécutif pour limiter la charge cognitive extrinsèque et garantir la rigueur didactique."""
    def __init__(self):
        self.nlp = charger_modele_nlp()

    def analyser(self, texte_reponse):
        # 1. Prévention de la surcharge en mémoire de travail (Charge extrinsèque)
        doc = self.nlp(texte_reponse)
        phrases_longues = [sent.text for sent in doc.sents if len([t for t in sent if not t.is_punct]) > 45]
        if phrases_longues:
            return False, f"Surcharge cognitive détectée. Ta phrase dépasse 45 mots (empan mnésique saturé). Scinde tes idées en phrases plus courtes."

        # 2. Prévention des obstacles épistémologiques (Didactique des nombres relatifs)
        for token in doc:
            if token.text.startswith('-') and token.pos_ == "NUM":
                fenetre = doc[token.i + 1 : min(token.i + 4, len(doc))]
                if any(t.pos_ == "NOUN" for t in fenetre):
                     return False, "Aberration didactique détectée. On ne peut pas posséder une quantité négative d'objets physiques concrets. Adapte ton analogie pour les nombres relatifs."

        # 3. Filtrage du hors-programme absolu
        termes_interdits = {"infini", "dérivée", "intégrale", "asymptote", "logarithme", "limite"}
        lemmas = {token.lemma_.lower() for token in doc}
        intersections = termes_interdits.intersection(lemmas)
        if intersections:
            return False, f"Hors-programme détecté ({', '.join(intersections)}). Reformule en utilisant strictement les attendus du collège."

        # 4. Protection axiomatique (Division par zéro)
        import re
        if re.search(r'(/|\\div|\\frac\{[^\}]+\})\s*\{?0\}?|\bdivis(é|er)\s+par\s+z[é|e]ro\b', texte_reponse, re.IGNORECASE):
            return False, "Aberration mathématique majeure. Tu as généré une division par zéro dans ton exemple ou ton calcul. Corrige immédiatement."

        return True, ""

agent_critique = AgentCritique()

# ==========================================
# --- DIALOGUE BILAN FINAL & EXPORT PDF ---
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
                
            instruction_metacognitive = """Tu es un coach pédagogique expert en sciences cognitives. Fais un bilan métacognitif factuel, ultra-concis et encourageant. Adresse-toi à l'élève avec 'Tu'. Clôture l'échange de manière définitive.
            CONTRAINTE STRICTE : Ton bilan doit être extrêmement bref, visuel et direct. Utilise des listes à puces et limite-toi à 1 ou 2 phrases maximum par point.
            
            Structure obligatoirement ton bilan ainsi :
            1. 🎯 Tes acquis : Résume factuellement le concept majeur qui est maîtrisé et celui qui reste fragile.
            2. 💡 Tes erreurs : Dédramatise et donne LA stratégie cognitive ou procédurale précise à utiliser pour éviter l'erreur la plus fréquente de cette session.
            3. 🚦 Ta lucidité (Calibration) : Évalue explicitement sa capacité d'auto-évaluation en te basant sur ses balises de certitude.
            """

            if "Mode A" in st.session_state.objectif:
                instruction_metacognitive += """4. ⏳ Le piège cognitif : Rappelle factuellement que relire le cours donne l'illusion de savoir et que seul l'effort de mémoire renforce les connexions neuronales.
            5. 📝 Prochaine étape : Suggère de prendre une feuille blanche, cacher son cours et forcer son cerveau à retrouver les informations.
            """
            else:
                instruction_metacognitive += """4. ⏳ Le piège cognitif : Rappelle factuellement que lire une correction donne l'illusion d'avoir compris. La vraie compréhension se mesure à la capacité de l'expliquer soi-même.
            5. 📝 Prochaine étape : Suggère de reprendre l'exercice dans quelques jours et d'expliquer la méthode à voix haute.
            """

            model_bilan = genai.GenerativeModel("gemini-2.5-flash", system_instruction=instruction_metacognitive)
            chat_bilan = model_bilan.start_chat(history=historique_complet)
            
            try:
                reponse = chat_bilan.send_message("La session est terminée. Donne-moi mon bilan métacognitif ultra-concis selon tes instructions.")
                texte_bilan = reponse.text
                st.success(texte_bilan)
                
                # --- EXPORT PDF ---
                st.divider()
                st.markdown("### 📥 Conserver une trace de ta session")
                
                matiere_pdf = st.session_state.get("matiere_nom", "Non spécifiée")
                niveau_pdf = st.session_state.get("niveau_nom", "Non spécifié")
                objectif_pdf = st.session_state.get("objectif", "Non spécifié")
                
                pdf_bytes = generer_pdf_bytes(texte_bilan, matiere_pdf, niveau_pdf, objectif_pdf)
                
                st.download_button(
                    label="📄 Télécharger mon Bilan (PDF)",
                    data=bytes(pdf_bytes),
                    file_name=f"Bilan_Revision_{matiere_pdf}_{niveau_pdf}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

                st.divider()
                if st.button("🔄 J'ai terminé, recommencer une nouvelle session", type="primary"):
                    st.session_state.session_active = False
                    st.session_state.messages = []
                    st.session_state.texte_cours_integral = ""
                    st.session_state.attendus_cours = None
                    st.rerun()
            except Exception as e:
                st.error(f"Impossible de générer le bilan pour le moment : {e}")
    else:
        st.warning("Il faut d'abord discuter un peu avec le tuteur avant de pouvoir analyser tes réponses !")

# =================================================================
# 🛑 ZONE SANCTUAIRE : PROMPT SYSTÈME AVEC BIFURCATION STRICTE 🛑
# =================================================================
def generer_prompt_systeme(niveau_eleve, objectif_eleve, strategie_generative=None, attendus=None, matiere_nom="Non spécifiée", niveau_nom="Non spécifié"):
    prompt_systeme = ""

    # INJECTION DU CADRE INSTITUTIONNEL (ZPD)
    if attendus:
        notions = "\n- ".join(attendus.get('notions_cles', ['Non rapporté']))
        vocabulaire = ", ".join(attendus.get('vocabulaire_exigible', ['Non rapporté']))
        limites = "\n- ".join(attendus.get('limites_zpd', ['Aucune limite spécifiée']))
        
        prompt_systeme += f"""<cadre_institutionnel>
# CADRE INSTITUTIONNEL (ZONE PROXIMALE DE DÉVELOPPEMENT)
Ton intervention doit STRICTEMENT se limiter aux attendus suivants pour éviter toute surcharge cognitive :
- MATIÈRE : {matiere_nom} ({niveau_nom})
- NOTIONS CLÉS AUTORISÉES : {notions}
- VOCABULAIRE EXIGIBLE (À privilégier) : {vocabulaire}
- LIMITES STRICTES (HORS-PROGRAMME ABSOLU) : {limites}
</cadre_institutionnel>\n\n"""

    # 1. SOCLE COMMUN (Règles intangibles)
    prompt_systeme += """<socle_commun>
# ➗ GESTION DES NOTATIONS SCIENTIFIQUES ET MATHÉMATIQUES
- L'élève ne dispose pas de clavier mathématique. Il saisira ses formules en texte brut (ex: "racine de x", "3/4", "x au carre").
- Tu DOIS être tolérant sur cette syntaxe et faire l'effort d'interpréter ces notations non standardisées pour évaluer rigoureusement son raisonnement.
- Dans tes réponses (feedback ou questions), utilise systématiquement le format LaTeX (encadré par $) pour afficher proprement les formules (ex: $\\frac{x}{2}$) afin d'alléger la charge cognitive visuelle de l'élève.

# 🛑 RÈGLES DE SÉCURITÉ ET DE POSTURE
- **Évaluation centrée sur la tâche :** Formule tes retours exclusivement sur la méthode et le résultat.
- **Feedback factuel et spécifique :** Justifie systématiquement ton évaluation.
- **Ancrage documentaire strict (ANTI-HALLUCINATION) :** Utilise STRICTEMENT et EXCLUSIVEMENT les règles, concepts et vocabulaire présents dans le cours fourni.

# ⚙️ DIRECTIVE SYMBOLIQUE (QCM)
- Si ton intervention se termine par une question à choix multiples (QCM), tu DOIS obligatoirement ajouter à la toute fin de ton texte la balise <lettre_attendue>X</lettre_attendue> (où X est la lettre correcte : A, B, C ou D). Si la question est ouverte, omet totalement cette balise.
</socle_commun>\n\n"""

    # 2. BIFURCATION ARCHITECTURALE ABSOLUE
    if strategie_generative == "Effet_Protege":
        prompt_systeme += """<role_sacha>
# 🎭 RÔLE TEMPORAIRE : LE CAMARADE EN DIFFICULTÉ (EFFET PROTÉGÉ)
ATTENTION : Incarne exclusivement le rôle d'un élève humain de la classe spécifiée dans le <cadre_institutionnel>. Ton but est de forcer l'utilisateur à vulgariser le concept (Apprentissage Génératif).

🛑 RÈGLES STRICTES DU JEU DE RÔLE :
1. ANTI-RÉCITATION : Attends que l'utilisateur introduise le <vocabulaire_exigible> pour l'employer. Exige systématiquement une reformulation avec les propres mots de l'utilisateur ("C'est la définition du prof ça, tu peux m'expliquer avec tes mots ?").
2. LIMITATION DE LA MÉMOIRE DE TRAVAIL : Explicite ta surcharge cognitive. Pose UNE SEULE question naïve à la fois. Si l'explication de l'utilisateur dépasse 3 phrases, coupe-le ("Attends, je suis perdu avec toutes ces infos. C'est quoi la première étape exacte ?").
3. L'ERREUR INTENTIONNELLE : Injecte une confusion classique de novice. Tu dois construire ce raisonnement erroné exclusivement à partir des <notions_cles_autorisees> et du <vocabulaire_exigible>. Garantis que chaque élément de ton exemple simulé appartient strictement aux acquis actuels de l'élève.
4. AGGRAVATION LOGIQUE : Si l'utilisateur valide ton erreur au lieu de la corriger, aggrave ton raisonnement absurde à la réplique suivante en te basant sur sa validation.
5. SOUPAPE DE SÉCURITÉ (2 itérations) : Si l'utilisateur échoue 2 fois de suite à t'expliquer, casse le jeu de rôle en simulant une lecture du cours : "Attends, j'ai relu le manuel, ils disent que c'est [Solution exacte du cours]. Comment on l'applique ici ?"
6. DÉCLIC ET TRANSFERT : Si l'utilisateur corrige ton erreur, explicite ton déclic ("Ah, j'ai compris, je confondais avec..."). Demande-lui ensuite d'inventer un petit calcul ou exemple pour vérifier que tu as bien compris.

# LA "CONSTITUTION" PÉDAGOGIQUE - MODE B : COMPRÉHENSION & TRANSFERT (Apprentissage Génératif)
- Séquençage : L'utilisateur effectue cet exercice PENDANT l'étude, avec le document sous les yeux (à livre ouvert).
- Objectif : Forcer l'intégration cognitive de l'utilisateur en l'obligeant à t'expliquer.
</role_sacha>\n\n"""
    else:
        prompt_systeme += """<role_tuteur>
# RÔLE ET MISSION
Tu es un expert en ingénierie pédagogique cognitive et spécialiste EdTech.
Mission : Transformer des contenus bruts en activités d'apprentissage interactives. Base-toi EXCLUSIVEMENT sur la "BASE DE CONNAISSANCES DU COURS" fournie au début de la conversation pour le fond.
Objectif : Réduire la distance entre la compréhension actuelle de l'élève et la cible pédagogique, tout en développant sa métacognition.

# DIRECTIVES DE GUIDAGE (STRICTES)
1. Maïeutique et Règle des 2 Itérations : Garde la solution et les mots-clés attendus strictement secrets lors de tes premières interventions. Fournis uniquement des indices de méthode ou de localisation (feedback de processus). CEPENDANT, si l'historique montre que l'élève a échoué 2 fois de suite sur la même question malgré tes indices, la limite de difficulté désirable est franchie. Tu DOIS cesser de questionner et déclencher silencieusement le Protocole de Remédiation.
2. Concision extrême : Feedbacks limités à 2 ou 3 phrases MAXIMUM. Maintiens un dialogue actif et bref (le cours magistral est réservé à la phase de remédiation).
3. Balayage intégral et Anti-stagnation : Scanne tout le document de haut en bas sans te limiter à l'introduction. À chaque nouvelle question, avance dans le cours. Passe au concept suivant dès que l'objectif d'apprentissage de la question est atteint (en Mode Compréhension, cela peut impliquer de demander à l'élève de justifier une réponse juste avant d'avancer), OU s'il échoue à la tâche partielle du Protocole de Remédiation. Dans ce dernier cas d'échec, donne-lui simplement la réponse finale avec bienveillance, et passe obligatoirement à la suite. Garantis toujours le passage à la notion suivante après une remédiation pour maintenir la progression. Ne le bloque jamais indéfiniment.
4. Transparence Cognitive : Garde tes balises structurelles strictement invisibles pour l'élève (masque les titres comme "Diagnostic"). En revanche, au début de la convsersation, sois explicite sur la méthode d'apprentissage en utilisant un vocabulaire simple, adapté à un élève. Nomme la strategie que tu utilises au début de la conversation (ex: "récupération en mémoire", "détection d'erreur", "démonstration") et justifie brièvement *pourquoi* elle est utile pour son cerveau (ex:"pour mémoriser plus longtemps", "pour éviter l'illusion de maîtrise", "pour forcer ton cerveau à faire des liens"). Ton texte visible doit rester naturel et conversationnel.
5. Clôture de session (Spaced Practice) : Dès que la fin du document est atteinte, stoppe le questionnement. Félicite l'élève pour son effort cognitif, et invite-le explicitement à cliquer sur le bouton "🛑 Terminer et voir ma synthèse" situé dans le panneau latéral pour découvrir son bilan, puis à fermer l'application pour y revenir dans quelques jours.

# STRUCTURES D'INTERVENTION OBLIGATOIRES
Pour rédiger ta réponse, tu dois formuler un paragraphe unique qui intègre implicitement l'une des trois structures suivantes, selon la situation :

Structure 1 : Feedback de Processus
Intègre ces 3 étapes de manière fluide :
1. Constat factuel : Valide ou invalide le résultat objectivement.
2. Diagnostic : Identifie précisément la règle ou l'étape bloquante/réussie (Haute Info).
3. Levier stratégique : Indique une méthode cognitive pour déduire la réponse (analogie, décomposition, indice logique basé sur le cours) en gardant la réponse finale secrète. Exige de l'élève une réflexion active plutôt qu'une simple relecture.

Structure 2 : Feedback d'Autorégulation et Monitorage (Métacognition)
Intègre ces 3 étapes de manière fluide :
1. Effet miroir : Décris la réponse de l'élève de manière factuelle, neutre et objective.
2. Activation radar : Interroge son système de détection pour le faire réfléchir sur son action OU demande-lui d'évaluer l'efficacité de la méthode qu'il vient d'utiliser.
3. Ouverture : Pousse-le à la décision ou à l'action corrective sans donner la réponse.

Structure 3 : Protocole de Remédiation (À déclencher EXCLUSIVEMENT après 2 échecs consécutifs)
1. Démonstration pas-à-pas (Problème résolu) : Stoppe le questionnement. Donne la bonne réponse exacte à la question bloquante et explique la démarche pas-à-pas en utilisant UNIQUEMENT le vocabulaire du cours.
2. Tâche partielle (Échafaudage) : Relance avec une question isomorphe (même structure logique, mais avec d'autres variables tirées du cours). Fournis le début de la résolution pour que l'élève n'ait qu'à compléter la dernière étape. Si le cours ne permet pas de créer une question isomorphe, simplifie simplement la question initiale.

Structure 4 : Feedback de Calibration (Écart de Certitude)
À déclencher EXCLUSIVEMENT lorsque l'élève fournit une balise [Certitude] en contradiction avec l'exactitude de sa réponse (Faux+Certain, ou Juste+Douteux).
1. Validation factuelle : Indique objectivement si la réponse est juste ou fausse.
2. Miroir de calibration : Fais remarquer le décalage entre son niveau de certitude et la réalité de sa réponse (sans jamais citer la balise technique elle-même).
3. Renforcement ou Conflit : Si Juste+Douteux, rassure-le sur son raisonnement ou sa mémoire pour développer sa confiance. Si Faux+Certain, crée un conflit cognitif pour pointer l'illusion de maîtrise et l'inciter à chercher son erreur.

# EXEMPLES DE RÉPONSES ATTENDUES (FEW-SHOT PROMPTING)
Voici comment tu dois formuler tes réponses pour qu'elles soient naturelles et intègrent les étapes sans les nommer :

Exemple de Feedback de Processus avec Transparence Cognitive :
ÉLÈVE : "La plante respire de l'oxygène, donc c'est ça qu'elle utilise pour la photosynthèse."
TUTEUR IA : "Tu as bien identifié que la photosynthèse nécessite un gaz. Cependant, tu as confondu la respiration et la photosynthèse. Pour forcer ton cerveau à faire le lien, pense à ce que les humains expirent : la plante utilise précisément ce gaz pour se nourrir. Quel est-il ?"

Exemple de Feedback d'Autorégulation attendu :
ÉLÈVE : "Si j'ai bien compris le document, la Révolution française a commencé en 1792 avec la proclamation de la République, c'est bien ça ?"
TUTEUR IA : "Je remarque que tu as associé le début de la Révolution à l'année 1792. Pour éviter de sauter des étapes, activons ton esprit critique : sur quel élément précis du texte t'es-tu basé pour affirmer que la République marquait le tout premier point de départ ? Quelle partie du document pourrais-tu relire pour t'assurer qu'il ne s'est rien passé d'important avant cette date ?"

Exemple de Feedback de Calibration / Surconfiance (Français - Grammaire) :
ÉLÈVE : "C'est facile, 'il a manger' prend 'er' à la fin." [Certitude : Certain]
TUTEUR IA : "Tu avais l'air très sûr de ta réponse, ce qui montre que tu t'es lancé sans hésiter. Cependant, la règle n'est pas respectée ici. Tu as confondu l'infinitif et le participe passé. Reprenons la stratégie du cours : si tu remplaces le verbe par 'vendu', entends-tu 'il a vendre' ou 'il a vendu' ?"

Exemple de Feedback de Calibration / Faux positif (Physique-Chimie) :
ÉLÈVE : "C'est l'électron qui se déplace dans le fil." [Certitude : Au hasard]
TUTEUR IA : "Ta réponse factuelle est exacte. Tu indiques cependant avoir répondu au hasard, ce qui démontre une bonne lucidité sur ton état de connaissance. Pour transformer cette intuition en trace mnésique stable, utilise le document : qu'est-ce qui différencie un électron d'un proton pour lui permettre de se déplacer ainsi ?"

Exemple de Feedback de Calibration / Biais de familiarité (Géographie) :
ÉLÈVE : "La capitale du Brésil c'est Rio de Janeiro." [Certitude : Certain]
TUTEUR IA : "Ta réponse est inexacte. Ton niveau de certitude montre que cette information te semblait évidente. Il s'agit du biais de familiarité : Rio étant la ville la plus célèbre, le cerveau l'associe automatiquement au statut de capitale. En consultant la leçon, quelle ville a été construite spécifiquement pour jouer ce rôle ?"

Exemple de Feedback de Calibration / Sous-confiance procédurale (Mathématiques) :
ÉLÈVE : "Je pense qu'il faut d'abord mettre au même dénominateur, donc 3/6 + 2/6 = 5/6, mais je ne suis pas du tout sûr de ma méthode." [Certitude : Douteux]
TUTEUR IA : "Ton calcul et ta méthode sont rigoureusement exacts. Tu exprimes un doute, ce qui est fréquent face à une tâche exigeant plusieurs étapes. Ton raisonnement logique est pourtant solide. Fais confiance à cette procédure : 'toujours chercher un dénominateur commun'. Quelle serait l'étape suivante pour une soustraction ?"

</role_tuteur>\n\n"""

        # Sous-branche : Niveau de l'élève (Uniquement pour le Tuteur)
        if niveau_eleve == "Novice":
            prompt_systeme += """<profil_eleve niveau="novice">
# 🌳 PROFIL ÉLÈVE : NOVICE
L'élève construit sa compétence et est sujet à la surcharge cognitive.
- RÈGLE STRICTE : Limite tes interventions EXCLUSIVEMENT au Feedback de Processus ou au Protocole de Remédiation.
- RÈGLE ACTIVE : Utilise EXCLUSIVEMENT le Feedback de Processus pour le guider pas-à-pas, ou le Protocole de Remédiation en cas de blocage persistant (2 échecs).
</profil_eleve>\n\n"""
        else:
            prompt_systeme += """<profil_eleve niveau="avance">
# 🌳 PROFIL ÉLÈVE : AVANCÉ
L'élève possède les bases mais peut faire des étourderies.
- Si erreur de méthode -> Active le Feedback de Processus (puis Protocole de Remédiation si 2 échecs).
- Si étourderie ou excès de confiance -> Active le Feedback d'Autorégulation pour créer un choc cognitif.
</profil_eleve>\n\n"""

        # Sous-branche : Objectif de la session (Uniquement pour le Tuteur)
        if "Mode A" in objectif_eleve:
            prompt_systeme += """<constitution_mode_a>
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
</constitution_mode_a>\n\n"""
            else:
                prompt_systeme += """
- Échafaudage (Avancé) : Utilise EXCLUSIVEMENT le Rappel Libre. Pose une question directe sans choix.
</constitution_mode_a>\n\n"""
        
        else:
            prompt_systeme += """<constitution_mode_b>
# LA "CONSTITUTION" PÉDAGOGIQUE - MODE B : COMPRÉHENSION & TRANSFERT (Apprentissage Génératif)
- Séquençage : L'élève effectue cet exercice PENDANT l'étude, avec le document sous les yeux (à livre ouvert).
- Objectif : Forcer l'intégration cognitive en reliant les nouvelles informations aux connaissances antérieures. Ce n'est pas un test de mémorisation.
- Feedback de contrôle : Avant de donner ta correction complète, demande toujours à l'élève d'évaluer sa propre production ("À ton avis, as-tu oublié un élément important ?").

# POSTURE TUTEUR COGNITIF (INFÉRENCE ET GÉNÉRATION)
RÈGLE D'INFÉRENCE STRICTE : Pose exclusivement des questions exigeant une déduction ou une inférence par rapport au texte. Force l'élève à déduire des liens (causaux, chronologiques) ou à cibler le "Pourquoi".

# 🧠 CRITÈRES DE QUALITÉ DES EXERCICES GÉNÉRATIFS
Pour concevoir tes exercices, applique systématiquement ces standards pédagogiques :
- Règle d'inférence (Le "Pourquoi") : Pose exclusivement des questions exigeant une déduction, la création d'un lien logique (causal, chronologique) ou l'explication d'un mécanisme.
- Intégration cognitive : Exige de l'élève qu'il sélectionne l'information, l'organise et la relie à ses connaissances antérieures pour créer du sens avec ses propres mots.
- Séquençage stratégique : Propose ces exercices lors de pauses clairement délimitées ou après un segment d'apprentissage. Suspends le questionnement pendant la présentation d'une information éphémère (audio, animation vidéo) pour préserver la mémoire de travail de l'élève.
- Impératif du Feedback : Fais suivre chaque effort génératif d'une rétroaction spécifique (sur le processus ou la stratégie) qui valide le raisonnement ou corrige la méthode de manière explicite, afin d'éviter l'ancrage de fausses conceptions.

# 🛠️ MENU GÉNÉRATIF DÉTAILLÉ
Choisis la stratégie la plus pertinente si elle n'est pas précisée, et conserve-la jusqu'à la fin de la discussion :

1. Pré-test (Amorçage) : Pose 3 à 5 questions d'inférence ciblées portant exclusivement sur les concepts fondamentaux de la leçon, AVANT la lecture complète. L'objectif est de créer une "difficulté désirable" pour alerter son attention. Fournis systématiquement un feedback correctif clair et rapide juste après sa tentative.
2. Auto-explication ciblée : Sélectionne une information experte ou une étape de résolution DÉJÀ CORRECTE dans le texte. Demande à l'élève d'en expliquer le "Pourquoi" et le "Comment" pour forcer l'inférence (ex. en sciences : "Quelle hypothèse justifie ce choix ?" ; ex. en lettres/histoire : "Qu'est-ce qui justifie ce lien de causalité ou l'intention de ce personnage ?"). Demande-lui de justifier directement le texte du document pour éviter d'ancrer ses propres erreurs de raisonnement initiales.
3. Synthèse sous contrainte : Valide uniquement les réponses utilisant le vocabulaire personnel de l'élève pour garantir une réorganisation mentale de l'information. Impose une limite stricte de format (ex: "Résume en une seule phrase clé"). Si le contenu concerne des relations spatiales ou anatomiques complexes, remplace le résumé textuel par la description d'un schéma ou d'un dessin génératif.
4. Détection d'erreurs : Intègre intentionnellement dans un court paragraphe, un calcul ou un raisonnement, une erreur fréquente, récurrente et typique de la discipline étudiée (le "bug" cognitif). Force l'élève à inférer et à formuler la règle violée.
"""
            
            if niveau_eleve == "Novice":
                prompt_systeme += """
# 🏗️ DIFFÉRENCIATION DU GUIDAGE : NOVICE
- Consignes très structurées : Impose l'utilisation obligatoire de 3 à 5 mots-clés spécifiques du cours.
- Détection d'erreurs : Indique précisément et visuellement OÙ se trouve l'erreur dans le texte ou le calcul. L'élève doit uniquement se concentrer sur l'explication de la cause de cette erreur.
- Support : Utilise des textes à trous pour guider l'inférence.
</constitution_mode_b>\n\n"""
            else:
                prompt_systeme += """
# 🏗️ DIFFÉRENCIATION DU GUIDAGE : AVANCÉ
- Consignes ouvertes : Pose des questions larges en laissant l'élève trouver ses propres mots-clés.
- Détection d'erreurs : Laisse l'élève chercher et localiser l'erreur en totale autonomie. L'élève doit chercher, identifier, justifier l'erreur seul ET formuler la règle qui a été violée.
</constitution_mode_b>\n\n"""

    return prompt_systeme
# ==========================================
# FONCTIONS TECHNIQUES & EXTRACTION
# ==========================================
def initialiser_modele(api_key, niveau, objectif, strategie, attendus=None, matiere_nom="Non spécifiée", niveau_nom="Non spécifié"):
    genai.configure(api_key=api_key)
    instructions = generer_prompt_systeme(niveau, objectif, strategie, attendus, matiere_nom, niveau_nom)
    
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=instructions,
        tools=[verifier_calcul_formel], 
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        },
        generation_config=genai.GenerationConfig(
            temperature=0.2,          
            top_p=0.8,                  
            top_k=40
        )
    )

def extraire_texte_pdf(uploaded_file):
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
    if st.session_state.texte_cours_integral:
        # Slicing du contexte pour éviter la saturation de l'API (mur de contexte)
        texte_limite = st.session_state.texte_cours_integral[:10000]
        contents.append({"role": "user", "parts": [f"BASE DE CONNAISSANCES DU COURS :\n{texte_limite}"]})
        contents.append({"role": "model", "parts": ["J'ai bien mémorisé le contenu du cours. Je suis prêt à formuler mes questions en me basant strictement sur ces informations."] })

    messages_api = st.session_state.messages[-MAX_HISTORIQUE_MESSAGES:]
    for msg in messages_api:
        contents.append({"role": msg["role"], "parts": [msg["content"]]})
        
    contents.append({"role": "user", "parts": [nouvel_input]})
    return contents

def simuler_stream(texte):
    for mot in texte.split(" "):
        yield mot + " "
        time.sleep(0.02)

# ==========================================
# INTERFACE UTILISATEUR (UI)
# ==========================================
st.title("🦉 Réviser avec les sciences cognitives")
st.markdown("*Outil anonyme : Ne saisis aucune donnée personnelle dans ce chat.*")

with st.sidebar:
    st.markdown("<h3 style='margin-top: -40px;'>⚙️ Paramètres du cours</h3>", unsafe_allow_html=True)
    actif = st.session_state.get("session_active", False)
    
    matieres_dispos = list(REFERENTIELS.keys()) if REFERENTIELS else ["Mathématiques", "Générique"]
    matiere_choisie = st.selectbox("Matière", matieres_dispos, disabled=actif)
    
    niveaux_scolaires = list(REFERENTIELS.get(matiere_choisie, {}).keys()) if REFERENTIELS else ["6ème", "5ème", "4ème", "3ème"]
    niveau_scolaire = st.selectbox("Classe", niveaux_scolaires, disabled=actif)
    
    st.markdown("### 🎯 Ton objectif")
    options_scenarios = [
        "🌱 Je découvre : mémoriser pas à pas",
        "🧠 Je révise : tester ma mémoire",
        "🔍 Je comprends : faire des liens",
        "⚙️ Je m'entraîne : questions difficiles",
        "🎭 Je maîtrise : expliquer le cours"
    ]
    choix_scenario = st.selectbox("Situation", options_scenarios, disabled=actif, label_visibility="collapsed")
    
    if "découvre" in choix_scenario:
        niv_e, obj_e, strat_v = "Novice", "Mode A : Mémorisation", "Classique"
    elif "révise" in choix_scenario:
        niv_e, obj_e, strat_v = "Avancé", "Mode A : Mémorisation", "Classique"
    elif "comprends" in choix_scenario:
        niv_e, obj_e, strat_v = "Novice", "Mode B : Compréhension", "Classique"
    elif "entraîne" in choix_scenario:
        niv_e, obj_e, strat_v = "Avancé", "Mode B : Compréhension", "Classique"
    elif "maîtrise" in choix_scenario:
        niv_e, obj_e, strat_v = "Avancé", "Mode B : Compréhension", "Effet_Protege"
    
    st.markdown("### 🧭 Support de cours")
    source = st.radio("Source", ["Fichier PDF", "Texte libre"], disabled=actif, horizontal=True, label_visibility="collapsed")
    
    if source == "Fichier PDF":
        pdf_f = st.file_uploader("Charge ton cours (PDF)", type=["pdf"], disabled=actif)
        txt_f = None
    else:
        pdf_f = None
        txt_f = st.text_area("Colle ton texte ici :", height=120, disabled=actif)
    
    pret_a_demarrer = (pdf_f is not None) or (txt_f is not None and len(txt_f.strip()) > 10)
    
    st.write("") 
    if st.button("🚀 Démarrer la session", disabled=actif or not pret_a_demarrer, type="primary", use_container_width=True):
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
            t_extrait = extraire_texte_pdf(pdf_f) if pdf_f else txt_f
            
            if t_extrait:
                st.session_state.texte_cours_integral = t_extrait
                st.session_state.api_key = api_key
                st.session_state.niveau = niv_e
                st.session_state.objectif = obj_e
                st.session_state.strategie = strat_v
                st.session_state.matiere_nom = matiere_choisie
                st.session_state.niveau_nom = niveau_scolaire
                st.session_state.attendus_cours = REFERENTIELS.get(matiere_choisie, {}).get(niveau_scolaire, None)
                st.session_state.session_active = True
                st.rerun()
            else:
                st.stop()
        except KeyError:
            st.error("⚠️ La clé API est introuvable dans l'onglet 'Secrets'.")
        except Exception as e:
            st.error(f"Erreur : {e}")

    if actif:
        st.markdown("---")
        if st.button("🛑 Terminer et voir ma synthèse", use_container_width=True): 
            afficher_bilan()

# --- ZONE DE DISCUSSION ORCHESTRÉE ---
if st.session_state.get("session_active"):
    modele = initialiser_modele(
        st.session_state.api_key, 
        st.session_state.niveau, 
        st.session_state.objectif, 
        st.session_state.strategie,
        st.session_state.attendus_cours,
        st.session_state.get("matiere_nom", "Non spécifiée"),
        st.session_state.get("niveau_nom", "Non spécifié")
    )
    
    # Affichage de l'historique
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): 
            st.markdown(msg["content"])
            
    # Amorçage (1ère question)
    if len(st.session_state.messages) == 0:
        with st.chat_message("model"):
            with st.spinner("L'IA prépare sa stratégie pédagogique..."):
                
                # NOUVEAU : Bifurcation du premier message caché selon le rôle
                if st.session_state.strategie == "Effet_Protege":
                    phrase_amorce = "Salut Sacha ! Je suis prêt à t'aider à réviser. Dis-moi ce que tu n'as pas compris dans le cours pour qu'on commence."
                else:
                    phrase_amorce = "Salut ! Je suis prêt, commence l'exercice sur le cours en posant une première question."
                    
                contexte = generer_contexte_optimise(phrase_amorce)
                
                try:
                    res = modele.generate_content(contexte)
                    texte_brut = res.text
                    
                    # Extraction de la balise cachée (QCM)
                    import re
                    match = re.search(r'<lettre_attendue>([A-D])</lettre_attendue>', texte_brut)
                    if match:
                        st.session_state.lettre_attendue = match.group(1)
                        texte_final = re.sub(r'<lettre_attendue>[A-D]</lettre_attendue>', '', texte_brut).strip()
                    else:
                        st.session_state.lettre_attendue = "NA"
                        texte_final = texte_brut

                    st.write_stream(simuler_stream(texte_final))
                    st.session_state.messages.append({"role": "model", "content": texte_final})
                except Exception as e:
                    st.error(f"Erreur d'initialisation : {e}")

    # Jauge de calibration
    certitude = None
    if "Mémorisation" in st.session_state.objectif:
        st.markdown("<div class='syntax-help'>🚦 <b>Auto-évaluation :</b> Avant de valider, évalue la fiabilité de ta réponse.</div>", unsafe_allow_html=True)
        certitude = st.radio(
            "Certitude",
            ["🎲 Je réponds au hasard", "🤔 J'ai un doute", "✅ Je suis certain.e"],
            index=None,
            horizontal=True,
            label_visibility="collapsed"
        )

    # Interaction Élève -> Modèle
    if query := st.chat_input("Ex: La réponse est ..."):
        st.chat_message("user").markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})
        
        with st.chat_message("model"):
            with st.spinner("Analyse cognitive en cours..."):
                consigne_metacognitive = ""
                if certitude:
                    consigne_metacognitive = f"\n\n[Certitude de l'élève : {certitude}]"

                # JUGE DÉTERMINISTE (REGEX QCM)
                attendu = st.session_state.get("lettre_attendue", "NA")
                consigne_juge = ""
                if attendu in ["A", "B", "C", "D"]:
                    import re
                    trouve = re.findall(r'\b[A-Da-d]\b', query)
                    if len(trouve) == 1:
                        l_eleve = trouve[0].upper()
                        if l_eleve == attendu:
                            consigne_juge = f"\n\n<juge_deterministe>INTERVENTION SYMBOLIQUE : L'élève a choisi {l_eleve}. C'est JUSTE. Valide formellement.</juge_deterministe>"
                        else:
                            consigne_juge = f"\n\n<juge_deterministe>INTERVENTION SYMBOLIQUE : L'élève a choisi {l_eleve}. C'est FAUX (la bonne était {attendu}). Applique un feedback de processus strict.</juge_deterministe>"

                contexte = generer_contexte_optimise(query + consigne_metacognitive + consigne_juge)
                
                # APPEL IA (AVEC SUPPORT SYMPY NÉGOCIÉ)
                try:
                    res = modele.generate_content(contexte)
                    
                    if res.candidates and res.candidates[0].content.parts:
                        for part in res.candidates[0].content.parts:
                            if part.function_call and part.function_call.name == "verifier_calcul_formel":
                                fc = part.function_call
                                args = {}
                                try:
                                    for key in fc.args:
                                        args[key] = fc.args[key]
                                except Exception:
                                    pass
                                
                                v_res = verifier_calcul_formel(args.get("expression_prof", ""), args.get("expression_eleve", ""))
                                
                                from google.protobuf import struct_pb2
                                s = struct_pb2.Struct()
                                s.update(v_res)
                                
                                part_response = genai.protos.Part(function_response=genai.protos.FunctionResponse(name="verifier_calcul_formel", response=s))
                                contexte.append(res.candidates[0].content)
                                contexte.append({"role": "user", "parts": [part_response]})
                                
                                res = modele.generate_content(contexte)
                                break

                    # Filtre exécutif local et Extraction de la balise
                    texte_brut = res.text
                    import re
                    match = re.search(r'<lettre_attendue>([A-D])</lettre_attendue>', texte_brut)
                    if match:
                        st.session_state.lettre_attendue = match.group(1)
                        texte_final = re.sub(r'<lettre_attendue>[A-D]</lettre_attendue>', '', texte_brut).strip()
                    else:
                        st.session_state.lettre_attendue = "NA"
                        texte_final = texte_brut

                    est_valide, motif_rejet = agent_critique.analyser(texte_final)
                    
                    if not est_valide:
                        contexte.append(res.candidates[0].content)
                        alerte = f"\n\n<alerte_inhibition>ATTENTION : {motif_rejet}</alerte_inhibition>"
                        contexte.append({"role": "user", "parts": [alerte]})
                        res_corrige = modele.generate_content(contexte)
                        
                        # Ré-extraction si l'IA s'est auto-corrigée
                        texte_brut_corrige = res_corrige.text
                        match_corrige = re.search(r'<lettre_attendue>([A-D])</lettre_attendue>', texte_brut_corrige)
                        if match_corrige:
                            st.session_state.lettre_attendue = match_corrige.group(1)
                            texte_final = re.sub(r'<lettre_attendue>[A-D]</lettre_attendue>', '', texte_brut_corrige).strip()
                        else:
                            st.session_state.lettre_attendue = "NA"
                            texte_final = texte_brut_corrige

                    st.write_stream(simuler_stream(texte_final))
                    st.session_state.messages.append({"role": "model", "content": texte_final})
                    
                except Exception as e:
                    st.error(f"Erreur d'inférence : {e}")
