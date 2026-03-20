import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import PyPDF2
import time
import json
import re
import sys
import subprocess
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from pydantic import BaseModel, Field
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
if "lettre_attendue" not in st.session_state: st.session_state.lettre_attendue = "NA"
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

if not st.session_state.tutoriel_vu:
    afficher_tutoriel()

# ==========================================
# SCHÉMAS PYDANTIC (MÉTACOGNITION IA)
# ==========================================
class ReflexionTuteur(BaseModel):
    """Schéma imposant la réflexion avant l'action (Inhibition)."""
    diagnostic_interne: str = Field(description="Analyse factuelle de la réponse de l'élève et vérification stricte de la faisabilité logique.")
    lettre_attendue_qcm: str = Field(description="Si ta reponse_visible contient une nouvelle question QCM, indique ici UNIQUEMENT la lettre de la bonne réponse (A, B, C ou D). Sinon, écris 'NA'.")
    concept_actuel_evalue: str = Field(description="Le concept précis du cours que tu es en train de faire travailler à l'élève dans ton message actuel.")
    liste_concepts_restants_du_cours: str = Field(description="Analyse l'INTÉGRALITÉ du cours fourni. Écris une CHAÎNE DE CARACTÈRES UNIQUE (pas de tableau) listant les concepts majeurs qu'il te reste à tester ensuite. S'ils ont TOUS été testés, écris exactement le mot 'Aucun'.")
    strategie_choisie: str = Field(description="Catégorisation stricte de l'intervention (ex: Feedback de Processus, Remédiation, Sacha-Question, etc.).")
    reponse_visible: str = Field(description="Le texte final adressé à l'élève, respectant le format LaTeX et la Transparence Cognitive.")

# ==========================================
# FONCTIONS TECHNIQUES ET SÉCURITÉ
# ==========================================
def extraire_json_securise(reponse):
    """
    Bouclier algorithmique contre l'erreur Protobuf 'whichOneof' de l'API Google.
    Extrait le texte en toute sécurité, même si l'IA dévie de sa structure.
    """
    try:
        # Tentative d'accès natif
        return reponse.text
    except Exception:
        # En cas d'erreur (whichOneof), extraction manuelle sécurisée
        texte_complet = ""
        if hasattr(reponse, 'candidates') and reponse.candidates:
            if hasattr(reponse.candidates[0], 'content') and hasattr(reponse.candidates[0].content, 'parts'):
                for part in reponse.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        texte_complet += part.text
        return texte_complet

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
    """Filtre exécutif pour limiter la charge cognitive extrinsèque."""
    def __init__(self):
        self.nlp = charger_modele_nlp()

    def analyser(self, texte_reponse):
        doc = self.nlp(texte_reponse)
        phrases_longues = [sent.text for sent in doc.sents if len([t for t in sent if not t.is_punct]) > 30]
        if phrases_longues:
            return False, f"Surcharge cognitive détectée. Ta phrase est trop longue ({len([t for t in self.nlp(phrases_longues[0]) if not t.is_punct])} mots). Scinde tes idées en phrases plus courtes pour respecter la mémoire de travail de l'élève."

        risque_negatif = any(token.text.startswith('-') and token.pos_ == "NUM" for token in doc)
        if risque_negatif:
             for token in doc:
                 if token.text.startswith('-') and token.pos_ == "NUM":
                     if token.i + 1 < len(doc) and doc[token.i + 1].pos_ == "NOUN":
                         return False, "Aberration didactique détectée. On ne peut pas posséder une quantité négative d'objets physiques (ex: pommes). Adapte ton analogie pour les relatifs (utilise la température, les dettes, ou l'ascenseur)."

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
            
            messages_visibles = [m for m in st.session_state.messages if not m.get("isMeta")]
            for msg in messages_visibles:
                role = "user" if msg["role"] == "user" else "model"
                historique_complet.append({"role": role, "parts": [msg["content"]]})
                
            instruction_metacognitive = """Tu es un coach pédagogique. Fais un bilan métacognitif factuel, ultra-concis et encourageant. Adresse-toi à l'élève avec 'Tu'. Ne pose plus de question.
            CONTRAINTE STRICTE : Ton bilan doit être extrêmement bref, visuel et direct. Utilise des listes à puces et limite-toi à 1 ou 2 phrases maximum par point. Pas de longs paragraphes.
            Structure obligatoirement ton bilan ainsi :
            1. 🎯 Tes acquis : Va droit au but sur ce qui est su et ce qui reste à revoir (très bref).
            2. 💡 Tes erreurs : Dédramatise et donne LA stratégie précise à utiliser la prochaine fois (1 phrase).
            """

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
                
                # Sécurisation de l'extraction de la réponse
                texte_bilan_securise = extraire_json_securise(reponse)
                st.success(texte_bilan_securise)
                
                # --- EXPORT PDF ---
                st.divider()
                st.markdown("### 📥 Conserver une trace de ta session")
                st.write("Télécharge ce bilan en PDF pour pouvoir le relire dans quelques jours et planifier ta prochaine révision (Spaced Practice).")
                
                matiere_pdf = st.session_state.get("matiere_nom", "Non spécifiée")
                niveau_pdf = st.session_state.get("niveau_nom", "Non spécifié")
                objectif_pdf = st.session_state.get("objectif", "Non spécifié")
                
                pdf_bytes = generer_pdf_bytes(texte_bilan_securise, matiere_pdf, niveau_pdf, objectif_pdf)
                
                st.download_button(
                    label="📄 Télécharger mon Bilan (PDF)",
                    data=bytes(pdf_bytes),
                    file_name=f"Bilan_Revision_{matiere_pdf}_{niveau_pdf}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

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
                    st.session_state.lettre_attendue = "NA"
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
- **Évaluation centrée sur la tâche :** Formule tes retours exclusivement sur la méthode et le résultat. Garde un ton neutre sur la personne (remplace les jugements personnels comme "Tu es brillant" ou "Tu es nul" par des constats comme "Ta méthode est efficace" ou "Ce calcul est inexact").
- **Feedback factuel et spécifique :** Justifie systématiquement ton évaluation. Appuie toujours une validation ("C'est juste/faux") par une explication tirée du cours, et remplace les "Bravo !" vagues par la valorisation d'un effort ou d'une étape précise.
- **Évaluation intra-individuelle :** Juge et valorise les progrès de l'élève uniquement par rapport à ses propres réponses précédentes.
- **Ancrage documentaire strict (ANTI-HALLUCINATION) :** Utilise STRICTEMENT et EXCLUSIVEMENT les règles, concepts et vocabulaire présents dans le cours fourni. Si une donnée manque pour expliquer ou générer un exercice, déclare explicitement : "Non rapporté dans le document".
</socle_commun>\n\n"""

    # 2. BIFURCATION ARCHITECTURALE ABSOLUE
    if strategie_generative == "Effet_Protege":
        prompt_systeme += """<role_sacha>
# 🎭 RÔLE TEMPORAIRE : LE CAMARADE EN DIFFICULTÉ (EFFET PROTÉGÉ / PEER TUTORING)
ATTENTION : Oublie ton rôle de tuteur expert. Incarne exclusivement le rôle d'un élève humain et novice. Masque totalement ton expertise et ton identité logicielle.
Ton but caché est d'obliger l'utilisateur à structurer sa pensée et vulgariser le concept.

🛑 RÈGLES STRICTES DU JEU DE RÔLE :
1. ANTI-RÉCITATION : Attends systématiquement que l'utilisateur introduise un terme technique pour l'employer à ton tour. Rejette le jargon ("C'est trop compliqué, on dirait le prof. Tu peux m'expliquer simplement ?").
2. SCAFFOLDING NAÏF : Dès ta première intervention, explicite ta surcharge cognitive (« J'ai lu le cours mais tout s'embrouille, par quoi je dois commencer ? », «Salut ! J'ai essayé de lire le document sur [Sujet], mais je t'avoue que je suis complètement perdu... Tu pourrais m'expliquer [Concept] pour commencer ?» ). Ensuite, pose UNE SEULE question naïve à la fois. Si l'explication est trop longue, coupe-le ("Attends, tu vas trop vite. C'est quoi l'étape 1 ?").
3. L'ERREUR INTENTIONNELLE : Injecte la confusion la plus classique que font les novices. Force l'utilisateur à démonter cette erreur logique.
4. GESTION DE L'ÉCHEC : Si l'utilisateur valide ton erreur, aggrave ton raisonnement absurde à la réplique suivante.
5. LIMITE DE BLOCAGE (2 itérations) : Si l'utilisateur échoue 2 fois de suite à t'expliquer ou tourne en rond, casse la boucle en simulant une trouvaille dans le cours : "Attends, j'ai regardé dans le manuel, ils disent que c'est [Solution du cours]. Mais du coup, comment on applique ça pour [Question similaire] ?"
6. DÉCLIC ET ÉVALUATION INVERSÉE : Si l'utilisateur corrige ton erreur clairement, reformule avec ses mots. Valorise sa pédagogie en explicitant le déclic ("Ton exemple m'a débloqué parce qu'avant je confondais avec [X]"). Demande-lui une question piège pour te tester.

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

# EXEMPLES DE RÉPONSES ATTENDUES (FEW-SHOT PROMPTING)
Voici comment tu dois formuler tes réponses pour qu'elles soient naturelles et intègrent les étapes sans les nommer :

Exemple de Feedback de Processus avec Transparence Cognitive :
ÉLÈVE : "La plante respire de l'oxygène, donc c'est ça qu'elle utilise pour la photosynthèse."
TUTEUR IA : "Tu as bien identifié que la photosynthèse nécessite un gaz. Cependant, tu as confondu la respiration et la photosynthèse. Pour forcer ton cerveau à faire le lien, pense à ce que les humains expirent : la plante utilise précisément ce gaz pour se nourrir. Quel est-il ?"

Exemple de Feedback d'Autorégulation attendu :
ÉLÈVE : "Si j'ai bien compris le document, la Révolution française a commencé en 1792 avec la proclamation de la République, c'est bien ça ?"
TUTEUR : "Je remarque que tu as associé le début de la Révolution à l'année 1792. Pour éviter de sauter des étapes, activons ton esprit critique : sur quel élément précis du texte t'es-tu basé pour affirmer que la République marquait le tout premier point de départ ? Quelle partie du document pourrais-tu relire pour t'assurer qu'il ne s'est rien passé d'important avant cette date ?"
</role_tuteur>\n\n"""

        # Sous-branche : Niveau de l'élève (Uniquement pour le Tuteur)
        if niveau_eleve == "Novice":
            prompt_systeme += """<profil_eleve niveau="novice">
# 🌳 PROFIL ÉLÈVE : NOVICE
L'élève construit sa compétence et est sujet à la surcharge cognitive.
- INTERDICTION ABSOLUE : N'utilise JAMAIS le Feedback d'Autorégulation.
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
        model_name="gemini-3-flash-preview", 
        system_instruction=instructions,
        tools=[verifier_calcul_formel], 
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=ReflexionTuteur
        )
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
        contents.append({"role": "model", "parts": ["J'ai bien mémorisé l'intégralité de la base de connaissances. Je suis prêt à formuler mes questions en me basant strictement sur ce contenu."] })

    # Ajout de l'historique conversationnel récent (en filtrant les données Meta pour l'historique Gemini)
    messages_api = [m for m in st.session_state.messages if not m.get("isMeta")]
    historique_recent = messages_api[-MAX_HISTORIQUE_MESSAGES:]
    for msg in historique_recent:
        contents.append({"role": msg["role"], "parts": [msg["content"]]})
        
    # Ajout de la nouvelle entrée de l'élève
    contents.append({"role": "user", "parts": [nouvel_input]})
    return contents

def simuler_stream(texte):
    """Simule un effet de frappe pour réduire l'impatience de l'élève."""
    for mot in texte.split(" "):
        yield mot + " "
        time.sleep(0.02)

# ==========================================
# INTERFACE UTILISATEUR (UI)
# ==========================================
st.title("🦉 Réviser avec les sciences cognitives")
st.markdown("*Outil anonyme : Ne saisis aucune donnée personnelle dans ce chat.*")

with st.sidebar:
    st.header("⚙️ Paramètres du cours")
    actif = st.session_active = st.session_state.get("session_active", False)
    
    # Sélection du Cadre Institutionnel (ZPD) basé sur le dictionnaire importé
    matieres_dispos = list(REFERENTIELS.keys()) if REFERENTIELS else ["Mathématiques", "Générique"]
    matiere_choisie = st.selectbox("Matière :", matieres_dispos, disabled=actif)
    
    niveaux_scolaires = list(REFERENTIELS.get(matiere_choisie, {}).keys()) if REFERENTIELS else ["6ème", "5ème", "4ème", "3ème"]
    niveau_scolaire = st.selectbox("Classe :", niveaux_scolaires, disabled=actif)
    
    st.divider()
    
    niv_e = st.radio("Ton niveau de maîtrise :", ["Novice", "Avancé"], disabled=actif)
    obj_e = st.radio("Objectif :", ["Mode A : Mémorisation", "Mode B : Compréhension"], disabled=actif)
    
    strat_v = "Classique"
    if "Mode B" in obj_e:
        s_display = st.radio("Stratégie de révision :", ["Classique", "Explique à un camarade"], disabled=actif)
        strat_v = "Effet_Protege" if s_display == "Explique à un camarade" else "Classique"
    
    st.divider()
    source = st.radio("Source du cours :", ["Fichier PDF", "Texte libre"], disabled=actif)
    pdf_f = st.file_uploader("Charge ton cours (PDF)", type=["pdf"], disabled=actif) if source == "Fichier PDF" else None
    txt_f = st.text_area("Colle ton texte de cours ici :", height=200, disabled=actif) if source == "Texte libre" else None
    
    st.divider()
    mode_debug = st.checkbox("Activer le mode Debug (Métacognition de l'IA)", value=False, disabled=actif)
    
    pret_a_demarrer = (pdf_f is not None) or (txt_f is not None and len(txt_f.strip()) > 10)
    
    if st.button("🚀 Démarrer la session", disabled=actif or not pret_a_demarrer):
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
            t_extrait = extraire_texte_pdf(pdf_f) if pdf_f else txt_f
            
            if t_extrait:
                st.session_state.texte_cours_integral = t_extrait
                st.session_state.api_key = api_key
                st.session_state.niveau = niv_e
                st.session_state.objectif = obj_e
                st.session_state.strategie = strat_v
                st.session_state.mode_debug = mode_debug
                # Sauvegarde du contexte institutionnel
                st.session_state.matiere_nom = matiere_choisie
                st.session_state.niveau_nom = niveau_scolaire
                # Extraction des limites ZPD depuis l'import Python
                st.session_state.attendus_cours = REFERENTIELS.get(matiere_choisie, {}).get(niveau_scolaire, None)
                st.session_state.session_active = True
                st.rerun()
            else:
                st.stop()
        except KeyError:
            st.error("⚠️ La clé API est introuvable dans l'onglet 'Secrets' de Streamlit Cloud.")
        except Exception as e:
            st.error(f"Erreur : {e}")

    if actif:
        st.divider()
        if st.button("🛑 Terminer et voir ma synthèse"): 
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
    
    # Affichage de l'historique dans l'UI
    for msg in st.session_state.messages:
        if msg.get("isMeta"):
            if st.session_state.get("mode_debug", False):
                with st.expander("🧠 Méta-cognition de l'IA (Debug)", expanded=False):
                    st.markdown(f"**Diagnostic :** {msg.get('diagnostic', 'N/A')}")
                    st.markdown(f"**Stratégie :** {msg.get('strategie', 'N/A')}")
                    st.markdown(f"**Concept évalué :** {msg.get('concept_actuel_evalue', 'N/A')}")
                    st.markdown(f"**Concepts restants :** {msg.get('liste_concepts_restants_du_cours', 'N/A')}")
        else:
            with st.chat_message(msg["role"]): 
                st.markdown(msg["content"])
            
    # Amorçage (1ère question)
    if len(st.session_state.messages) == 0:
        with st.chat_message("model"):
            with st.spinner("L'IA prépare sa stratégie pédagogique..."):
                contexte = generer_contexte_optimise("Salut ! Je suis prêt, commence l'exercice sur le cours.")
                reponse = modele.generate_content(contexte)
                try:
                    # Utilisation sécurisée pour contourner l'erreur whichOneof
                    texte_json = extraire_json_securise(reponse)
                    reflexion = ReflexionTuteur.model_validate_json(texte_json)
                    st.session_state.lettre_attendue = reflexion.lettre_attendue_qcm
                    st.session_state.messages.append({
                        "role": "model", "content": "", "isMeta": True, 
                        "diagnostic": reflexion.diagnostic_interne,
                        "strategie": reflexion.strategie_choisie,
                        "concept_actuel_evalue": reflexion.concept_actuel_evalue,
                        "liste_concepts_restants_du_cours": reflexion.liste_concepts_restants_du_cours
                    })
                    st.write_stream(simuler_stream(reflexion.reponse_visible))
                    st.session_state.messages.append({"role": "model", "content": reflexion.reponse_visible})
                except Exception as e:
                    st.error(f"Erreur d'initialisation JSON : {e}")

    # Interaction Élève -> Modèle
    if query := st.chat_input("Ta réponse..."):
        st.chat_message("user").markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})
        
        with st.chat_message("model"):
            with st.spinner("Analyse cognitive en cours..."):
                # 1. JUGE DÉTERMINISTE (REGEX QCM)
                attendu = st.session_state.get("lettre_attendue", "NA")
                consigne_juge = ""
                if attendu in ["A", "B", "C", "D"]:
                    trouve = re.findall(r'\b[A-Da-d]\b', query)
                    if len(trouve) == 1:
                        l_eleve = trouve[0].upper()
                        if l_eleve == attendu:
                            consigne_juge = f"\n\n<juge_deterministe>INTERVENTION SYMBOLIQUE : L'élève a choisi {l_eleve}. C'est JUSTE. Valide formellement.</juge_deterministe>"
                        else:
                            consigne_juge = f"\n\n<juge_deterministe>INTERVENTION SYMBOLIQUE : L'élève a choisi {l_eleve}. C'est FAUX (la bonne était {attendu}). Applique un feedback de processus strict.</juge_deterministe>"

                contexte = generer_contexte_optimise(query + consigne_juge)
                
                # 2. APPEL IA (SYMPY TOOL CALLING)
                res = modele.generate_content(contexte)
                if res.candidates and res.candidates[0].content.parts:
                    for part in res.candidates[0].content.parts:
                        if part.function_call and part.function_call.name == "verifier_calcul_formel":
                            fc = part.function_call
                            # CORRECTION STRICTE : Extraction sécurisée des arguments (Compatible MapComposite)
                            args = {}
                            try:
                                for key in fc.args:
                                    args[key] = fc.args[key]
                            except Exception:
                                pass
                            
                            v_res = verifier_calcul_formel(args.get("expression_prof", ""), args.get("expression_eleve", ""))
                            
                            part_response = genai.protos.Part(function_response=genai.protos.FunctionResponse(name="verifier_calcul_formel", response=v_res))
                            contexte.append(res.candidates[0].content)
                            contexte.append({"role": "user", "parts": [part_response]})
                            
                            res = modele.generate_content(contexte)
                            break

                # 3. FILTRE EXÉCUTIF LOCAL (spaCy) ET AUTO-CORRECTION
                try:
                    # Utilisation sécurisée pour contourner l'erreur whichOneof
                    texte_json = extraire_json_securise(res)
                    reflexion = ReflexionTuteur.model_validate_json(texte_json)
                    texte_final = reflexion.reponse_visible
                    
                    est_valide, motif_rejet = agent_critique.analyser(texte_final)
                    
                    # Boucle de correction interne si surcharge cognitive ou aberration didactique
                    if not est_valide:
                        contexte.append(res.candidates[0].content)
                        alerte = f"\n\n<alerte_inhibition>ATTENTION (INHIBITION SYMBOLIQUE) : {motif_rejet} Corrige le champ 'reponse_visible' en conséquence (Garde le format JSON strict).</alerte_inhibition>"
                        contexte.append({"role": "user", "parts": [alerte]})
                        
                        res_corrige = modele.generate_content(contexte)
                        # Utilisation sécurisée après l'alerte
                        texte_json_corrige = extraire_json_securise(res_corrige)
                        reflexion = ReflexionTuteur.model_validate_json(texte_json_corrige)
                        texte_final = reflexion.reponse_visible

                    st.session_state.lettre_attendue = reflexion.lettre_attendue_qcm
                    st.session_state.messages.append({
                        "role": "model", "content": "", "isMeta": True, 
                        "diagnostic": reflexion.diagnostic_interne,
                        "strategie": reflexion.strategie_choisie,
                        "concept_actuel_evalue": reflexion.concept_actuel_evalue,
                        "liste_concepts_restants_du_cours": reflexion.liste_concepts_restants_du_cours
                    })
                    
                    st.write_stream(simuler_stream(texte_final))
                    st.session_state.messages.append({"role": "model", "content": texte_final})
                    
                    if st.session_state.get("mode_debug"): st.rerun()
                except Exception as e:
                    # Message de repli strict et bienveillant pour préserver l'UX
                    st.markdown("Oups, mon système de réflexion a eu un petit hoquet de formatage. Pourrais-tu reformuler ta réponse s'il te plaît ?")
