# Ce fichier centralise les programmes officiels extraits d'Eduscol.
# Il sert de "Loi" (Grounding) pour brider les hallucinations du modèle Albert.
# Il permet de garantir que l'IA reste dans la Zone Proximale de Développement (ZPD) de l'élève.

REFERENTIEL_COLLEGE = {
    "Mathématiques": {
        "6ème": {
            "notions_cles": [
                "Utiliser et représenter les grands nombres entiers",
                "Comprendre et utiliser des fractions simples et des nombres décimaux",
                "Mettre en œuvre les quatre opérations et le calcul mental dans des situations variées",
                "Résoudre des problèmes en mobilisant nombres, calcul et organisation de données",
                "Mesurer et comparer des grandeurs (longueur, masse, durée, aire, volume)",
                "Décrire et reconnaître des figures planes et des solides usuels",
                "Se repérer sur une droite graduée et dans le plan",
                "Utiliser tableaux, graphiques et diagrammes pour organiser des données"
            ],
            "vocabulaire_exigible": [
                "nombre entier", "fraction simple", "nombre décimal",
                "addition, soustraction, multiplication, division", "calcul mental",
                "droite graduée", "segment, longueur, périmètre", "aire, volume",
                "tableau, graphique, diagramme"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "5ème": {
            "notions_cles": [
                "Nombres décimaux relatifs et opérations sur les nombres",
                "Fractions, nombres rationnels et calcul fractionnaire",
                "Puissances et notation scientifique",
                "Divisibilité, nombres premiers et décomposition en facteurs premiers",
                "Calcul littéral, expressions, distributivité et premières équations du premier degré",
                "Organisation et gestion de données, indicateurs (moyenne, médiane, étendue)",
                "Premières notions de probabilités et modélisation simple du hasard",
                "Grandeurs et mesures : aires, volumes, grandeurs produit et quotient, conversions",
                "Espace et géométrie : figures usuelles, codages et transformations simples",
                "Algorithmique et programmation par blocs pour des programmes de calcul ou de tracé"
            ],
            "vocabulaire_exigible": [
                "nombre relatif", "fraction, nombre rationnel", "puissance, notation scientifique",
                "multiple, diviseur, nombre premier", "expression littérale, distributivité",
                "équation du premier degré", "moyenne, médiane, étendue",
                "probabilité, expérience aléatoire, événement", "aire, volume, grandeur produit, grandeur quotient"
            ],
            "limites_zpd": [
                "Pas d'attendu sur les propriétés algébriques générales des racines carrées (manipulations symboliques avancées)",
                "Pas d'attendu sur les formules générales de produits et quotients de puissances (la mise en œuvre des calculs repose sur la définition des puissances)",
                "La notion d'arbre de probabilités n'est pas au programme (les dénombrements s'appuient sur des tableaux à double entrée)",
                "Les définitions ponctuelles formelles des translations, rotations et homothéties ne figurent pas au programme",
                "Aucune virtuosité calculatoire n'est attendue dans les développements et factorisations",
                "L’usage systématique de la double distributivité et la résolution d’équations produits au-delà du premier degré ne sont pas prioritaires"
            ]
        },
        "4ème": {
            "notions_cles": [
                "Consolider le calcul avec nombres décimaux relatifs et nombres rationnels",
                "Approfondir calcul fractionnaire, fractions irréductibles et décomposition en facteurs premiers",
                "Approfondir puissances (exposants positifs et négatifs) et notation scientifique",
                "Développer le calcul littéral (développement, factorisation, simplification d’expressions)",
                "Mettre en équation des problèmes et résoudre des équations du premier degré",
                "Approfondir statistiques (tableaux, diagrammes, histogrammes, moyenne, médiane, étendue)",
                "Probabilités simples, fréquences et modélisation de situations aléatoires élémentaires",
                "Grandeurs et mesures : formules d’aires et de volumes, grandeurs composées",
                "Espace et géométrie : parallélogrammes, triangles, symétries, translations",
                "Initiation aux fonctions (tableaux de valeurs, premiers graphiques)"
            ],
            "vocabulaire_exigible": [
                "fraction irréductible", "décomposition en facteurs premiers", "racine carrée (usage numérique)",
                "puissance de 10", "développement, factorisation", "équation, solution",
                "fréquence, histogramme", "coefficient de proportionnalité", "fonction (tableau de valeurs, graphique)",
                "parallélogramme, symétrie centrale, translation"
            ],
            "limites_zpd": [
                "Pas d'attendu sur les propriétés algébriques générales des racines carrées (manipulations symboliques avancées)",
                "Pas d'attendu sur les formules générales de produits et quotients de puissances (la mise en œuvre des calculs repose sur la définition des puissances)",
                "La notion d'arbre de probabilités n'est pas au programme (les dénombrements s'appuient sur des tableaux à double entrée)",
                "Les définitions ponctuelles formelles des translations, rotations et homothéties ne figurent pas au programme",
                "Aucune virtuosité calculatoire n'est attendue dans les développements et factorisations",
                "L’usage systématique de la double distributivité et la résolution d’équations produits au-delà du premier degré ne sont pas prioritaires"
            ]
        },
        "3ème": {
            "notions_cles": [
                "Maîtriser les opérations sur nombres relatifs et rationnels (y compris puissances usuelles)",
                "Utiliser la notation scientifique et estimer des ordres de grandeur",
                "Maîtriser le calcul littéral pour transformer des expressions et résoudre des équations du premier degré",
                "Utiliser racine carrée et théorème de Pythagore dans des problèmes de géométrie",
                "Utiliser proportionnalité, pourcentages et coefficients multiplicateurs dans des situations variées",
                "Étudier des fonctions linéaires et affines, leurs expressions et représentations graphiques",
                "Approfondir statistiques (moyenne, médiane, étendue, histogrammes) et probabilités simples",
                "Calculer avec des grandeurs composées et vérifier la cohérence des unités",
                "Mettre en œuvre Thalès, triangles semblables et transformations pour résoudre des problèmes",
                "Écrire, mettre au point et exécuter des programmes simples en algorithmique (boucles, tests, variables)"
            ],
            "vocabulaire_exigible": [
                "racine carrée (usage numérique lié à Pythagore)", "notation scientifique, ordre de grandeur",
                "identité, expression littérale", "équation du premier degré, équation-produit (cas simples)",
                "coefficient multiplicateur, taux d’évolution", "fonction linéaire, fonction affine, image, antécédent",
                "médiane, étendue, histogramme", "théorème de Pythagore, théorème de Thalès",
                "triangles semblables", "boucle, instruction conditionnelle, variable (en programmation par blocs)"
            ],
            "limites_zpd": [
                "Pas d'attendu sur les propriétés algébriques générales des racines carrées (manipulations symboliques avancées)",
                "Pas d'attendu sur les formules générales de produits et quotients de puissances (la mise en œuvre des calculs repose sur la définition des puissances)",
                "La notion d'arbre de probabilités n'est pas au programme (les dénombrements s'appuient sur des tableaux à double entrée)",
                "Les définitions ponctuelles formelles des translations, rotations et homothéties ne figurent pas au programme",
                "Aucune virtuosité calculatoire n'est attendue dans les développements et factorisations",
                "L’usage systématique de la double distributivité et la résolution d’équations produits au-delà du premier degré ne sont pas prioritaires"
            ]
        }
    },
    "Français": {
        "6ème": {
            "notions_cles": [
                "Comprendre et s’exprimer à l’oral dans des situations variées",
                "Lire avec fluidité et comprendre des textes littéraires et documentaires",
                "Écrire régulièrement des textes variés (récits, descriptions, comptes rendus)",
                "Étudier le fonctionnement de la langue (grammaire, orthographe, lexique)",
                "Construire une première culture littéraire et artistique commune",
                "Utiliser le langage oral pour débattre, expliquer, raconter",
                "Recourir à l’écriture pour réfléchir et pour apprendre"
            ],
            "vocabulaire_exigible": [
                "langage oral, échange, débat", "texte narratif, descriptif",
                "phrase simple, phrase complexe", "orthographe lexicale, orthographe grammaticale",
                "verbe, sujet, complément (terminologie de base)", "temps du récit (passé, présent, futur)",
                "lexique, champ lexical", "texte littéraire, œuvre intégrale", "lecture à voix haute, récitation"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "5ème": {
            "notions_cles": [
                "Comprendre et interpréter des messages et discours oraux complexes",
                "Lire et interpréter des textes littéraires de genres variés",
                "Rédiger des écrits organisés en tenant compte du destinataire et de l’intention",
                "Approfondir l’étude de la langue (phrase complexe, classes et fonctions essentielles)",
                "Enrichir sa culture littéraire et artistique (repères d’histoire littéraire et culturelle)",
                "Initier une argumentation plus maîtrisée à l’oral et à l’écrit"
            ],
            "vocabulaire_exigible": [
                "narrateur, point de vue", "implicite, inférence", "paragraphe, connecteur logique",
                "classes de mots majeures (nom, verbe, adjectif, adverbe)",
                "complément de phrase, complément du verbe (terminologie usuelle du programme)",
                "discours direct, discours indirect", "argument, exemple, thèse",
                "genre narratif, poésie, théâtre"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "4ème": {
            "notions_cles": [
                "Contrôler sa compréhension et devenir lecteur autonome de textes complexes",
                "Produire des écrits argumentatifs, explicatifs ou narratifs structurés",
                "Analyser le fonctionnement de la phrase complexe et des subordonnées",
                "Approfondir l’orthographe grammaticale et lexicale dans les écrits",
                "Consolider une culture littéraire et artistique (dialogue des œuvres et des époques)",
                "Pratiquer l’oral long (exposé, restitution, lecture expressive)"
            ],
            "vocabulaire_exigible": [
                "proposition subordonnée relative, complétive, circonstancielle (terminologie de base du programme)",
                "valeurs des temps (imparfait, passé simple, plus-que-parfait, etc.)",
                "registre de langue", "figure de style simple (comparaison, métaphore, hyperbole)",
                "cohésion textuelle, anaphore", "paragraphe argumentatif",
                "champ lexical, connotation", "point de vue critique sur une œuvre"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "3ème": {
            "notions_cles": [
                "Comprendre et interpréter des textes et documents complexes, y compris argumentatifs",
                "Rédiger des textes argumentatifs organisés pour préparer les épreuves du DNB",
                "Maîtriser les principales notions de grammaire de phrase et de texte",
                "Stabiliser l’orthographe lexicale et grammaticale dans les écrits scolaires",
                "Structurer une culture littéraire et artistique de référence pour la fin du collège",
                "S’exprimer à l’oral de façon maîtrisée (présentation, débat, argumentation)"
            ],
            "vocabulaire_exigible": [
                "thèse, argument, exemple, connecteur logique",
                "proposition indépendante, coordonnée, subordonnée",
                "voix active, voix passive", "valeurs modales et temporelles des temps de l’indicatif",
                "registres (comique, tragique, pathétique, etc. au sens du programme)",
                "narrateur, focalisation", "discours rapporté",
                "dossier de lecture, carnet de lecteur (outils de lecture suivie)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        }
    },
    "Histoire-Géographie & EMC": {
        "6ème": {
            "notions_cles": [
                "Se repérer dans le temps : premiers repères historiques et distinction entre histoire et fiction",
                "Se repérer dans l’espace : passer d’une représentation personnelle aux premiers repères géographiques",
                "Comprendre la démarche historique pour répondre à des interrogations sur le passé",
                "Comprendre la relation entre individus, sociétés et espaces à différentes échelles",
                "Découvrir les enjeux du développement durable dans l’étude des milieux et des activités humaines",
                "EMC : compréhension de la règle, du droit et de la vie collective à l’école et au collège"
            ],
            "vocabulaire_exigible": [
                "chronologie, repère historique", "frise chronologique (terme d’usage scolaire standard)",
                "carte, légende, échelle", "territoire, paysage", "société, individu",
                "règle, droit, citoyen, laïcité (terminologie EMC de base)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "5ème": {
            "notions_cles": [
                "Thèmes d’histoire : Chrétientés et islam (VIe–XIIIe siècles), mondes en contact",
                "Thèmes d’histoire : Société, Église et pouvoir politique dans l’Occident féodal",
                "Thèmes d’histoire : Transformations de l’Europe et ouverture sur le monde aux XVIe et XVIIe siècles",
                "Thèmes de géographie : question démographique et inégal développement",
                "Thèmes de géographie : ressources limitées, à gérer et à renouveler",
                "Compétences : se repérer dans le temps et l’espace, raisonner, analyser des documents, pratiquer différents langages",
                "EMC : principes et symboles de la République, vivre ensemble et respect d’autrui"
            ],
            "vocabulaire_exigible": [
                "Moyen Âge, féodalité", "Chrétienté, islam", "croissance démographique, inégalités de développement",
                "ressource, contrainte, risque", "carte thématique, croquis", "République, symbole, devise",
                "liberté, égalité, fraternité, laïcité"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "4ème": {
            "notions_cles": [
                "Thèmes d’histoire : Le XVIIIe siècle – expansions, Lumières et révolutions",
                "Thèmes d’histoire : L’Europe et le monde au XIXe siècle",
                "Thèmes d’histoire : Société, culture et politique dans la France du XIXe siècle",
                "Thèmes de géographie : urbanisation du monde",
                "Thèmes de géographie : mobilités humaines transnationales",
                "Thèmes de géographie : espaces transformés par la mondialisation",
                "Compétences : analyser et comprendre des documents, écrire et pratiquer l’oral en histoire-géographie",
                "EMC : droits et devoirs, exercice de la citoyenneté, débat argumenté"
            ],
            "vocabulaire_exigible": [
                "Lumières, Révolution", "industrialisation, bourgeoisie, prolétariat (en lien avec les thèmes officiels)",
                "mondialisation, métropole, mégalopole", "flux migratoires, mobilité",
                "espace urbain, périurbain", "citoyenneté, droit, devoir", "argumentation, débat"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "3ème": {
            "notions_cles": [
                "Thèmes d’histoire : L’Europe, théâtre majeur des guerres totales (1914–1945)",
                "Thèmes d’histoire : Le monde depuis 1945",
                "Thèmes d’histoire : Françaises et Français dans une République repensée",
                "Thèmes de géographie : dynamiques territoriales de la France contemporaine",
                "Thèmes de géographie : aménagement du territoire et développement durable",
                "Thèmes de géographie : la France et l’Union européenne",
                "Compétences : pratiquer différents langages (cartographiques, graphiques, écrits, oraux)",
                "EMC : valeurs et principes de la République, pluralisme, engagement et responsabilité"
            ],
            "vocabulaire_exigible": [
                "guerre totale, génocide", "guerre froide, décolonisation", "Ve République, Constitution",
                "aménagement du territoire, acteur, échelle", "Union européenne, organisation internationale",
                "développement durable", "valeurs républicaines, engagement, responsabilité"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        }
    },
    "Sciences de la Vie et de la Terre (SVT)": {
        "6ème": {
            "notions_cles": [
                "Non rapporté"
            ],
            "vocabulaire_exigible": [
                "Non rapporté"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "5ème": {
            "notions_cles": [
                "La planète Terre, l’environnement et l’action humaine (phénomènes géologiques, météorologie, climat)",
                "Risque volcanique et risques liés à l’activité interne de la Terre",
                "Impacts des actions humaines sur les écosystèmes et les ressources naturelles",
                "Fonctionnement du corps humain (systèmes de transport, digestion, respiration) et santé",
                "Rôle des micro-organismes dans la digestion et l’alimentation",
                "Reproduction des êtres vivants et dynamique des populations"
            ],
            "vocabulaire_exigible": [
                "lithosphère, asthénosphère", "tectonique des plaques, aléa, risque",
                "écosystème, biodiversité", "population, dynamique des populations",
                "microorganisme, microbiote", "tube digestif, besoins nutritionnels",
                "reproduction sexuée, reproduction asexuée"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "4ème": {
            "notions_cles": [
                "Approfondissement des phénomènes géologiques (activité interne, séismes, volcanisme, risques)",
                "Étude des impacts différenciés des activités humaines sur les écosystèmes",
                "Régulation du fonctionnement de l’organisme humain (systèmes de transport, rôle des micro-organismes)",
                "Lien entre alimentation, microbiote et santé",
                "Reproduction, cycles de vie et évolution des populations",
                "Mobilisation de démarches expérimentales et de modélisation en SVT"
            ],
            "vocabulaire_exigible": [
                "aléa naturel, risque anthropique", "prévention, protection, adaptation",
                "biodiversité, perturbation, résilience", "système de transport (circulatoire, respiratoire, etc.)",
                "microbiote intestinal", "sélection, reproduction, fécondation"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "3ème": {
            "notions_cles": [
                "Synthèse sur la planète Terre, l’environnement et l’action humaine (enjeux globaux)",
                "Analyse d’exemples d’actions humaines et de leurs effets sur les écosystèmes (déforestation, pollution, etc.)",
                "Approfondissement du lien entre comportements, hygiène de vie et santé",
                "Lien entre reproduction, héritage, diversité du vivant et évolution",
                "Mobilisation de données scientifiques pour argumenter des choix de gestion environnementale",
                "Usage critique de modèles scientifiques en SVT"
            ],
            "vocabulaire_exigible": [
                "enjeu environnemental global", "pollution, ressource renouvelable / non renouvelable",
                "prévention, risque sanitaire", "génération, population, dynamique",
                "argumentation scientifique (données, hypothèses, conclusion)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        }
    },
    "Physique-Chimie": {
        "6ème": {
            "notions_cles": [
                "Non rapporté"
            ],
            "vocabulaire_exigible": [
                "Non rapporté"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "5ème": {
            "notions_cles": [
                "Organisation et transformations de la matière",
                "Mouvements et interactions (description simple des mouvements et actions)",
                "L’énergie et ses conversions dans des situations usuelles",
                "Ondes et signaux pour observer et communiquer",
                "Démarche expérimentale en physique-chimie (observer, mesurer, interpréter)"
            ],
            "vocabulaire_exigible": [
                "organisation de la matière (solide, liquide, gaz)", "transformation physique, transformation chimique",
                "mouvement, trajectoire (terminologie générale du programme)", "interaction (contact, à distance)",
                "énergie, transfert, conversion", "onde, signal"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "4ème": {
            "notions_cles": [
                "Approfondissement de l’organisation et des transformations de la matière (changements d’état, réactions simples)",
                "Étude de mouvements et d’interactions dans différents contextes (quotidiens, techniques)",
                "Analyse de chaînes de conversions d’énergie dans des systèmes simples",
                "Étude d’ondes et de signaux (lumière, son) pour observer et communiquer",
                "Pratique de la modélisation et du raisonnement expérimental"
            ],
            "vocabulaire_exigible": [
                "modèle de la matière (échelle usuelle du programme)", "changements d’état",
                "interaction, force (termes usuels d’introduction)",
                "énergie mécanique, électrique, thermique (catégories usuelles du cycle 4)",
                "signal lumineux, signal sonore"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "3ème": {
            "notions_cles": [
                "Synthèse sur organisation et transformations de la matière (modèles simples)",
                "Analyse de situations de mouvements et interactions pour prévoir ou interpréter un comportement",
                "Bilans énergétiques simples et rendement dans des systèmes techniques usuels",
                "Utilisation de signaux pour transmettre une information (exemples courants)",
                "Démarche scientifique complète : questionnement, hypothèse, expérimentation, modélisation, conclusion"
            ],
            "vocabulaire_exigible": [
                "modèle (en physique-chimie)", "bilan d’énergie (formulation qualitative au niveau du programme)",
                "rendement (sens qualitatif et calcul simple)", "signal numérique / analogique (terminologie du programme)",
                "grandeur mesurée, unité (terminologie générale)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        }
    },
    "Technologie": {
        "6ème": {
            "notions_cles": [
                "Non rapporté"
            ],
            "vocabulaire_exigible": [
                "Non rapporté"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "5ème": {
            "notions_cles": [
                "Découvrir des objets et systèmes techniques répondant à des besoins",
                "Identifier fonctions et solutions techniques simples dans des objets usuels",
                "Comprendre la place de l’informatique et de la programmation dans les systèmes techniques",
                "Premières démarches de conception et de réalisation d’objets ou prototypes simples",
                "Prendre en compte l’environnement et les usages dans l’étude d’un objet"
            ],
            "vocabulaire_exigible": [
                "objet technique, système technique", "fonction d’usage, fonction d’estime (terminologie d’usage en technologie collège)",
                "schéma fonctionnel simple", "prototype, maquette", "informations, données (en lien avec l’informatique)",
                "algorithme simple, programme"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "4ème": {
            "notions_cles": [
                "Analyser le fonctionnement d’objets et systèmes techniques (flux de matière, d’énergie et d’information)",
                "Comprendre l’organisation fonctionnelle d’un système et ses composants",
                "Concevoir et réaliser des objets ou systèmes simples intégrant capteurs et actionneurs",
                "Utiliser la programmation pour piloter un système technique simple",
                "Prendre en compte des critères de développement durable et d’impact environnemental"
            ],
            "vocabulaire_exigible": [
                "chaîne d’énergie (alimentation, distribution, conversion, action)",
                "chaîne d’information (acquérir, traiter, communiquer)",
                "capteur, actionneur", "diagramme fonctionnel",
                "protocole (échanges de données dans un réseau simple)", "prototype, cahier des charges"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "3ème": {
            "notions_cles": [
                "Approfondir l’analyse de systèmes techniques complexes (organisation, flux, contraintes)",
                "Mener un projet de conception–réalisation en équipe (de l’idée au prototype)",
                "Mobiliser la programmation pour automatiser un comportement ou un traitement d’information",
                "Étudier le cycle de vie d’un produit et ses impacts (ressources, énergie, recyclage)",
                "Relier innovation technologique, besoins sociaux et enjeux de développement durable"
            ],
            "vocabulaire_exigible": [
                "cycle de vie d’un produit", "contrainte, critère de choix",
                "innovation, obsolescence (terminologie usuelle du programme)",
                "système automatisé", "capteur, actionneur, interface de commande", "impact environnemental"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        }
    },
    "Langues Vivantes (Anglais - LVA)": {
        "6ème": {
            "notions_cles": [
                "Poursuivre l’apprentissage d’une langue vivante étrangère commencé au cycle 2",
                "Développer de manière équilibrée les cinq activités langagières (écouter, lire, parler en continu, écrire, réagir et dialoguer)",
                "Comprendre des messages oraux simples en lien avec l’environnement proche",
                "Comprendre des textes courts et simples (supports scolaires, vie quotidienne)",
                "Produire des énoncés oraux et écrits très guidés sur soi et son environnement",
                "Découvrir des repères culturels des pays anglophones"
            ],
            "vocabulaire_exigible": [
                "activités langagières (écouter, lire, parler, écrire, interagir)",
                "salutations, présentation de soi", "vocabulaire du quotidien (famille, école, loisirs, lieux de vie)",
                "lexique des consignes de classe", "alphabet, nombres usuels", "formulations simples de questions et réponses"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "5ème": {
            "notions_cles": [
                "Approfondir la compréhension orale et écrite de documents simples à légèrement complexes",
                "Produire des énoncés oraux plus développés (description, récit simple)",
                "Écrire de courts textes structurés sur des expériences personnelles",
                "Mobiliser des connaissances lexicales, grammaticales et culturelles dans des situations de communication variées",
                "Ancrer les apprentissages dans des situations culturelles authentiques de l’aire anglophone"
            ],
            "vocabulaire_exigible": [
                "formules pour parler de goûts et préférences", "lexique des activités, métiers, lieux de la ville",
                "structures de base du présent et du passé proche (niveau A1+/A2)",
                "connecteurs simples (and, but, because, then)", "lexique pour se repérer dans un document (title, picture, paragraph, etc.)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "4ème": {
            "notions_cles": [
                "Atteindre au moins le niveau A2 dans les cinq activités langagières pour la LV1 en fin de cycle (avec possibilité de B1 dans plusieurs activités)",
                "Comprendre des documents oraux et écrits plus longs et plus denses",
                "Produire des prises de parole continues plus structurées (raconter, décrire, expliquer)",
                "Écrire des textes organisés (lettre, message, récit bref, description, opinion simple)",
                "Mobiliser des stratégies de compréhension (repérage d’indices, répétitions, structures récurrentes)",
                "Percevoir les spécificités culturelles du monde anglophone dans des situations variées"
            ],
            "vocabulaire_exigible": [
                "lexique de l’environnement proche (ville, activités, métiers, etc.)",
                "expressions pour localiser dans le temps et l’espace",
                "formes verbales de base au présent, passé, futur simple (au niveau du CECRL visé)",
                "tournures fréquentes pour exprimer l’opinion et la justification",
                "vocabulaire élémentaire de la vie culturelle et médiatique (films, musiques, réseaux, etc.)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "3ème": {
            "notions_cles": [
                "Consolider au moins le niveau A2 et viser B1 dans plusieurs activités langagières pour la LV1",
                "Comprendre des documents authentiques simples, oraux et écrits, avec appuis",
                "S’exprimer à l’oral avec plus d’aisance sur des sujets familiers et scolaires",
                "Écrire des textes plus complets (récit, description, prise de position simple)",
                "Utiliser des repères culturels de l’aire anglophone pour interpréter des documents",
                "Mettre en œuvre des stratégies d’auto-correction et de reformulation"
            ],
            "vocabulaire_exigible": [
                "lexique plus étendu de la vie quotidienne, scolaire et sociale",
                "expressions de liaison plus variées (however, in my opinion, first, then, finally, etc.)",
                "formes verbales correspondantes au profil A2/B1 dans le CECRL (temps simples et principaux modaux usuels)",
                "lexique de base pour commenter des documents (character, setting, main idea, opinion)",
                "références culturelles simples (fêtes, institutions, modes de vie)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        }
    },
    "Éducation Physique et Sportive (EPS)": {
        "6ème": {
            "notions_cles": [
                "Développer sa motricité et apprendre à s’exprimer en utilisant son corps",
                "Explorer différents jeux et activités physiques et sportives",
                "Apprendre à partager des règles et assumer des rôles et responsabilités",
                "Découvrir les liens entre activité physique, santé et hygiène de vie",
                "Commencer à s’approprier une culture physique, sportive et artistique"
            ],
            "vocabulaire_exigible": [
                "motricité, action motrice", "règle, rôle (joueur, arbitre, observateur)",
                "effort, récupération", "sécurité, fair-play",
                "activité physique, performance (au sens scolaire)", "échauffement"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "5ème": {
            "notions_cles": [
                "Produire une performance optimale mesurable à une échéance donnée",
                "S’approprier des méthodes et outils par la pratique physique (s’échauffer, répéter, réguler son effort)",
                "Partager des règles, assumer des rôles et des responsabilités dans des activités collectives",
                "Apprendre à entretenir sa santé par une activité physique régulière",
                "S’approprier une culture physique, sportive et artistique (diversité des APSA)"
            ],
            "vocabulaire_exigible": [
                "performance mesurable (distance, temps, score)", "répétition, entraînement",
                "intensité de l’effort (qualificatifs usuels du programme)",
                "rôle social (capitaine, arbitre, juge)", "activité physique, santé"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "4ème": {
            "notions_cles": [
                "Affiner ses habiletés motrices pour améliorer la performance dans différents champs d’apprentissage",
                "Adapter son engagement et gérer l’effort en fonction de la tâche et de ses ressources",
                "Coopérer et s’opposer individuellement et collectivement dans des jeux sportifs variés",
                "Construire des repères pour entretenir sa santé (charge d’entraînement, récupération)",
                "Approfondir sa culture des pratiques physiques, sportives et artistiques"
            ],
            "vocabulaire_exigible": [
                "habileté, coordination", "stratégie, projet d’action", "gestion de l’effort (rythme, allure)",
                "récupération, étirement (termes usuels scolaires)", "chorégraphie, prestation (pour les activités à visée artistique)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "3ème": {
            "notions_cles": [
                "Stabiliser et transférer ses compétences dans les différents champs d’apprentissage",
                "Gérer son engagement moteur et émotionnel en situation d’opposition et de coopération",
                "Construire un projet personnel d’activité physique pour la santé",
                "Assumer pleinement des rôles sociaux dans les activités (organisation, arbitrage, aide à l’entraînement)",
                "Situer les pratiques physiques et sportives dans une culture commune"
            ],
            "vocabulaire_exigible": [
                "projet d’entraînement personnel", "gestion du risque dans l’activité",
                "rôle d’arbitre ou de juge", "comportement citoyen en EPS",
                "culture sportive (référence aux grandes familles d’APSA du programme)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        }
    },
    "Arts Plastiques": {
        "6ème": {
            "notions_cles": [
                "Expérimenter, produire, créer en manipulant des matériaux et outils variés",
                "Découvrir la représentation, les images, la relation réalité / fiction",
                "Observer la matérialité de l’œuvre, l’objet et l’œuvre",
                "Commencer à se repérer dans les domaines liés aux arts plastiques",
                "Exprimer et décrire simplement sa pratique et celle des autres"
            ],
            "vocabulaire_exigible": [
                "forme, couleur, matière (terminologie de base)", "support, format",
                "geste, trace", "image, représentation", "œuvre, auteur, spectateur"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "5ème": {
            "notions_cles": [
                "Expérimenter et choisir des langages plastiques pour traduire des intentions",
                "Mettre en œuvre un projet plastique simple (de l’intention à la réalisation)",
                "Interroger la relation entre œuvre, espace, auteur, spectateur",
                "Développer un regard critique sur sa production et celle des autres",
                "Approfondir les repères dans l’histoire des arts"
            ],
            "vocabulaire_exigible": [
                "composition", "point de vue", "plan (avant-plan, arrière-plan, sens usuel des programmes)",
                "contraste, nuance", "installation (sens usuel arts plastiques)", "référence, citation (d’une œuvre)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "4ème": {
            "notions_cles": [
                "Concevoir et réaliser des projets plastiques plus complexes et contextualisés",
                "Explorer la matérialité de l’œuvre (support, techniques, procédés)",
                "Mettre en relation des œuvres de domaines et d’époques variés",
                "Analyser plus finement la relation œuvre–espace–public",
                "Mobiliser une culture artistique pour nourrir ses productions"
            ],
            "vocabulaire_exigible": [
                "cadrage, hors-champ", "texture, empâtement (terminologie usuelle du programme)",
                "installation, dispositif", "espace d’exposition", "réception, interprétation"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "3ème": {
            "notions_cles": [
                "Mener un projet plastique personnel ou collectif de la conception à la présentation",
                "Articuler intention, choix plastiques et discours sur l’œuvre",
                "Situer ses productions dans une histoire des formes et des pratiques artistiques",
                "Questionner la place de l’œuvre dans la société et dans l’espace public",
                "Préparer la transition vers le lycée en consolidant les compétences d’analyse et de création"
            ],
            "vocabulaire_exigible": [
                "démarche de projet", "intention plastique", "dispositif de presentation",
                "contextualisation d’une œuvre", "références croisées (arts, périodes, cultures)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        }
    },
    "Éducation Musicale": {
        "6ème": {
            "notions_cles": [
                "Réaliser des projets musicaux d’interprétation (chant) ou de création simples",
                "Écouter, comparer et construire une première culture musicale commune",
                "Explorer sa voix parlée et chantée",
                "Découvrir des organisations musicales simples (répétition, contraste)",
                "Échanger autour de ce que l’on entend et produit"
            ],
            "vocabulaire_exigible": [
                "voix parlée, voix chantée", "rythme, tempo", "intensité (forte, douce – terminologie scolaire)",
                "timbre (voix, instruments)", "refrain, couplet"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "5ème": {
            "notions_cles": [
                "Réaliser des projets musicaux plus structurés (interprétation ou création collective)",
                "Identifier, décrire et comparer des organisations musicales plus complexes",
                "Explorer des liens entre musique et autres arts ou contextes culturels",
                "Échanger, argumenter et débattre autour d’écoutes",
                "Utiliser la voix et éventuellement des instruments scolaires pour interpréter un répertoire"
            ],
            "vocabulaire_exigible": [
                "pulsation, rythme", "phrase musicale, motif", "nuance (piano, forte, crescendo, etc.)",
                "texture simple (solo, chœur, accompagnement)", "répertoire, interprétation"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "4ème": {
            "notions_cles": [
                "Concevoir, créer et réaliser des pièces musicales en lien avec des projets artistiques",
                "Identifier et décrire des organisations musicales complexes",
                "Situer et comparer des musiques de styles proches ou éloignés",
                "Prendre en compte les droits d’auteur et les sources dans les projets musicaux",
                "Articuler écoute, pratique et culture musicale"
            ],
            "vocabulaire_exigible": [
                "structure musicale (introduction, développement, coda, etc.)",
                "style musical (au sens scolaire du programme)", "arrangement, orchestration simple",
                "source, droit d’auteur", "enregistrement, mixage (terminologie d’usage scolaire)"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        },
        "3ème": {
            "notions_cles": [
                "Mener des projets musicaux aboutis (création, interprétation, restitution publique scolaire)",
                "Analyser et commenter des œuvres musicales à partir de critères construits au collège",
                "Mettre en relation musiques et contextes historiques, sociaux et culturels",
                "Mobiliser la culture musicale acquise pour élaborer un jugement argumenté",
                "Préparer la transition vers le lycée par une pratique musicale autonome"
            ],
            "vocabulaire_exigible": [
                "analyse musicale (critères simples : forme, timbres, dynamiques)",
                "répertoire de référence (œuvres étudiées)", "critère esthétique (notion scolaire)",
                "projet musical, restitution", "interprétation, intention"
            ],
            "limites_zpd": [
                "Non rapporté"
            ]
        }
    }
}

def obtenir_attendus(matiere, niveau):
    """
    Récupère les données sécurisées (Noyau de compétences) pour un binôme matière/niveau.
    Retourne un dictionnaire contenant : notions_cles, vocabulaire_exigible, limites_zpd
    """
    try:
        return REFERENTIEL_COLLEGE.get(matiere, {}).get(niveau, None)
    except Exception:
        return None
