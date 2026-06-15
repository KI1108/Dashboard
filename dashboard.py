




# dashboard.py
# ============================================================
# RÔLE : Interface utilisateur — 100% Python avec Dash
#
# Pages :
#   - Accueil        → choix créer ou se connecter
#   - Inscription    → formulaire création profil
#   - Connexion      → connexion par email
#   - Résultats      → formations + bourses recommandées
#   - Modifier profil → mise à jour du profil
#
# ⚠️  L'API doit tourner en parallèle :
#      python api.py  (port 5001)
#
# LANCER : python dashboard.py
# ACCÈS  : http://127.0.0.1:5000
#
# Dépendances :
#   pip install dash dash-bootstrap-components requests
# ============================================================

import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import requests
import os 
# ─────────────────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
app.title = "EduReco — Formations & Bourses"
server = app.server 
# for local
# API_URL = "http://127.0.0.1:5001" 


# for production
API_URL = os.getenv("API_URL", "http://127.0.0.1:5001")


# ═════════════════════════════════════════════════════════
# DONNÉES PARTAGÉES
# ═════════════════════════════════════════════════════════

PAYS_OPTIONS = [
    {"label": "Sénégal",       "value": "Senegal"},
    {"label": "Guinée",        "value": "Guinea"},
    {"label": "Mali",          "value": "Mali"},
    {"label": "Côte d'Ivoire", "value": "Cote d'Ivoire"},
    {"label": "Burkina Faso",  "value": "Burkina Faso"},
    {"label": "Cameroun",      "value": "Cameroun"},
    {"label": "Maroc",         "value": "Maroc"},
    {"label": "France",        "value": "France"},
    {"label": "Autre",         "value": "Autre"},
]

NIVEAU_OPTIONS = [
    {"label": "Lycée / Bac", "value": "lycee"},
    {"label": "Licence",     "value": "licence"},
    {"label": "Master",      "value": "master"},
    {"label": "Doctorat",    "value": "doctorat"},
]

DOMAINE_OPTIONS = [
    {"label": "Informatique / Data Science", "value": "informatique"},
    {"label": "Ingénierie",                  "value": "ingenierie"},
    {"label": "Économie / Finance",          "value": "economie"},
    {"label": "Droit",                       "value": "droit"},
    {"label": "Médecine / Santé",            "value": "medecine"},
    {"label": "Sciences",                    "value": "science"},
    {"label": "Éducation",                   "value": "education"},
    {"label": "Arts / Lettres",              "value": "arts"},
]

OBJECTIF_OPTIONS = [
    {"label": "Trouver un emploi",     "value": "emploi"},
    {"label": "Faire de la recherche", "value": "recherche"},
    {"label": "Créer une entreprise",  "value": "entrepreneuriat"},
    {"label": "Formation continue",    "value": "continue"},
]

LANGUE_OPTIONS = [
    {"label": "Français", "value": "francais"},
    {"label": "Anglais",  "value": "anglais"},
    {"label": "Arabe",    "value": "arabe"},
]


# ═════════════════════════════════════════════════════════
# FONCTIONS DE PAGE
# ═════════════════════════════════════════════════════════

def page_accueil():
    """Page d'accueil — choix entre créer un profil ou se connecter."""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2("🎓 EduReco", className="text-center mb-2"),
                    html.P(
                        "Trouvez les formations et bourses qui correspondent "
                        "à votre profil grâce à l'intelligence artificielle.",
                        className="text-center text-muted mb-4"
                    ),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "✨ Créer mon profil",
                                id="btn-vers-inscription",
                                color="primary",
                                size="lg",
                                className="w-100"
                            )
                        ]),
                        dbc.Col([
                            dbc.Button(
                                "🔑 J'ai déjà un compte",
                                id="btn-vers-connexion",
                                color="outline-primary",
                                size="lg",
                                className="w-100"
                            )
                        ])
                    ])
                ])
            ], className="shadow mt-5")
        ], width=6, className="mx-auto")
    ])


def page_inscription():
    """Formulaire de création de profil."""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H4(" Créer mon profil")),
                        dbc.Col(
                            dbc.Button(
                                "← Accueil",
                                id="btn-retour-accueil-inscription",
                                color="outline-secondary",
                                size="sm"
                            ),
                            className="text-end"
                        )
                    ])
                ]),
                dbc.CardBody([

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Nom *"),
                            dbc.Input(id="inp-nom", placeholder="Ex: Diallo")
                        ]),
                        dbc.Col([
                            dbc.Label("Prénom *"),
                            dbc.Input(id="inp-prenom", placeholder="Ex: Mamadou")
                        ])
                    ], className="mb-3"),

                    dbc.Label("Email *"),
                    dbc.Input(
                        id="inp-email",
                        type="email",
                        placeholder="vous@example.com",
                        className="mb-3"
                    ),

                    dbc.Label("Pays *"),
                    dbc.Select(
                        id="inp-pays",
                        options=PAYS_OPTIONS,
                        placeholder="Choisir un pays",
                        className="mb-3"
                    ),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Niveau d'études *"),
                            dbc.Select(
                                id="inp-niveau",
                                options=NIVEAU_OPTIONS,
                                placeholder="Choisir un niveau"
                            )
                        ]),
                        dbc.Col([
                            dbc.Label("Domaine *"),
                            dbc.Select(
                                id="inp-domaine",
                                options=DOMAINE_OPTIONS,
                                placeholder="Choisir un domaine"
                            )
                        ])
                    ], className="mb-3"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Objectif"),
                            dbc.Select(
                                id="inp-objectif",
                                options=OBJECTIF_OPTIONS,
                                value="emploi"
                            )
                        ]),
                        dbc.Col([
                            dbc.Label("Langue préférée"),
                            dbc.Select(
                                id="inp-langue",
                                options=LANGUE_OPTIONS,
                                value="francais"
                            )
                        ])
                    ], className="mb-4"),

                    dbc.Button(
                        "Créer mon profil et voir mes recommandations →",
                        id="btn-soumettre-inscription",
                        color="primary",
                        size="lg",
                        className="w-100"
                    ),

                    html.Div(id="msg-inscription", className="mt-3")

                ])
            ], className="shadow")
        ], width=8, className="mx-auto mt-3")
    ])


def page_connexion():
    """Formulaire de connexion par email."""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H4("🔑 Me connecter")),
                        dbc.Col(
                            dbc.Button(
                                "← Accueil",
                                id="btn-retour-accueil-connexion",
                                color="outline-secondary",
                                size="sm"
                            ),
                            className="text-end"
                        )
                    ])
                ]),
                dbc.CardBody([
                    dbc.Label("Mon email"),
                    dbc.Input(
                        id="inp-email-connexion",
                        type="email",
                        placeholder="vous@example.com",
                        className="mb-3"
                    ),
                    dbc.Button(
                        "Se connecter →",
                        id="btn-soumettre-connexion",
                        color="primary",
                        size="lg",
                        className="w-100"
                    ),
                    html.Div(id="msg-connexion", className="mt-3")
                ])
            ], className="shadow")
        ], width=5, className="mx-auto mt-5")
    ])


# ═════════════════════════════════════════════════════════
# CARTES
# ═════════════════════════════════════════════════════════

def carte_formation(f):
    """Carte d'affichage d'une formation recommandée."""
    # Couleur selon le score de correspondance
    if f['pct'] >= 40:
        couleur = "success"
    elif f['pct'] >= 25:
        couleur = "warning"
    else:
        couleur = "secondary"

    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5(f['titre'], className="card-title"),
                    html.P([
                        dbc.Badge(
                            f.get('domaine', ''),
                            color="primary",
                            className="me-1"
                        ),
                        dbc.Badge(
                            f.get('niveau_requis', ''),
                            color="info",
                            className="me-1"
                        ),
                        dbc.Badge(
                            "Gratuit" if f.get('est_gratuit') else "Payant",
                            
                            color="success" if f.get('est_gratuit') else "secondary",
                            className="me-1"
                        ),
                    ]),
                    html.P(f.get('organisme', ''), className="text-muted small")
                ], width=9),

                # Score de correspondance NLP
                dbc.Col([
                    html.H3(
                        f"{f['pct']}%",
                        className=f"text-{couleur} text-center fw-bold"
                    ),
                  
                    html.P(
                        "Correspondance",
                        className="text-center small text-muted"
                    )
                ], width=3)
            ]),
            # Lien vers la formation
            html.A(
                "Voir la formation →",
                href=f.get('lien', '#'),
                target="_blank",
                role="button",
                className="btn btn-outline-primary btn-sm mt-1"
            ) if f.get('lien') else html.Span()
        ])
   
    ], className="mb-3 shadow-sm")


def carte_bourse(b):
    """Carte d'affichage d'une bourse recommandée."""
    # Couleur selon le score de correspondance
    if b['pct'] >= 40:
        couleur = "success"
    elif b['pct'] >= 25:
        couleur = "warning"
    else:
        couleur = "secondary"

    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5(b['titre'], className="card-title"),
                    html.P([
                        dbc.Badge(
                            b.get('organisme', ''),
                            color="danger",
                            className="me-1"
                        ),
                        dbc.Badge(
                            b.get('niveau_requis', ''),
                            color="info",
                          
                            className="me-1"
                        ),
                        dbc.Badge(
                            b.get('pays_eligible', 'Tous pays'),
                            color="warning",
                         
                            className="me-1"
                        ),
                    ]),
                    html.P(b.get('montant', ''), className="text-success fw-bold")
                ], width=9),

                # Score de correspondance NLP
                dbc.Col([
                    html.H3(
                        f"{b['pct']}%",
                        className=f"text-{couleur} text-center fw-bold"
                    ),
                    
                    html.P(
                        "Correspondance",
                        className="text-center small text-muted"
                    )
                ], width=3)
            ]),
            # Lien vers la bourse
            html.A(
                "Voir la bourse →",
                href=b.get('lien', '#'),
                target="_blank",
                role="button",
                className="btn btn-outline-danger btn-sm mt-1"
            ) if b.get('lien') else html.Span()
        ])
    
    ], className="mb-3 shadow-sm")

# ***************************************************************************************************
# ═════════════════════════════════════════════════════════
# PAGE RÉSULTATS
# ═════════════════════════════════════════════════════════

def page_resultats(user, formations, bourses, texte_profil):
    """Page d'affichage des recommandations NLP."""
    return html.Div([

        # Bandeau de bienvenue avec infos profil
        dbc.Alert([
            dbc.Row([
                dbc.Col([
                    html.H4(f"Bonjour {user['prenom']} {user['nom']} 👋"),
                    html.P([
                        html.Strong("Profil analysé : "),
                        html.Em(texte_profil)
                    ], className="mb-0")   
                ], width=9),
                dbc.Col([
                    dbc.Button(
                        "✏️ Modifier profil",
                        id="btn-modifier-profil",
                        color="light",
                        size="sm",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Accueil",
                        id="btn-retour-accueil-resultats",
                        color="outline-light",
                        size="sm"
                    )
                ], width=3),
          
            ], className="d-flex align-items-center justify-content-end")
        ], color="info"),

        # ✅ CORRIGÉ : dcc.store → dcc.Store  |  i= → id=
        dcc.Store(id="store-user", data=user),
        html.Hr(),

       
        dbc.Row([
            dbc.Col([
                html.H4(f"🎓 Formations recommandées ({len(formations)})"),
                html.Div([
                    carte_formation(f) for f in formations
                ] if formations else [
                    dbc.Alert("Aucune formation trouvée.", color="warning")
                ])
            ], width=6),

            dbc.Col([
                html.H4(f"💵 Bourses recommandées ({len(bourses)})"),
                html.Div([
                    carte_bourse(b) for b in bourses
            
                ] if bourses else [
                    dbc.Alert("Aucune bourse trouvée.", color="warning")
                ])
            ], width=6),
        ])

  
    ])

# *******************************************************************************************
# Modification fonction
# *******************************************************************************************
def page_modifier_profil(user):
    """Formulaire de modofication du profil de user"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H4("✏️ Modifier mon profil")),
                        dbc.Col(
                            dbc.Button(
                                "↩ Accueil",
                                id="btn-retour-accueil-modif",
                                color="outline-secondary",
                                size="sm"
                            ),
                            class_name="text-end"
                        )
                    ])
                ]),
                dbc.CardBody([
                    # Email non modifiable-afficher en lecteur seule
                    dbc.Alert([
                        html.Strong("Email(non modifiable) :"),
                        html.Span((user.get('email', '')))
                    ], color="light", class_name="mb-3"),

                    dbc.Row([
                        dbc.Col([
                        dbc.Label("nom"),
                        dbc.Input(id="mod-nom", value=user.get('nom', ''))
                        ]),

                        dbc.Col([
                            dbc.Label("prenom"),
                            dbc.Input(id="mod-prenom", value=user.get('prenom', ''))
                        ]) 
                    ],class_name="mb-3"),

                    dbc.Label("Pays"),
                    dbc.Select(
                        id="mod-pays",
                        value=user.get('pays', ''),
                        options=PAYS_OPTIONS,
                        class_name="mb-3"
                    ),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Niveau d'études"),
                            dbc.Select(
                                id="mod-niveau",
                                value=user.get('niveau_etudes', ''),
                                options=NIVEAU_OPTIONS
                            )
                        ]),

                        dbc.Col([
                            dbc.Label("Domaine"),
                            dbc.Select(
                                id="mod-domaine",
                                value=user.get('domaine', ''),
                                options=DOMAINE_OPTIONS
                            )

                        ])
                    ],class_name="mb-3"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Objectif"),
                            dbc.Select(
                                id="mod-objectif",
                                value=user.get('objectif', 'emploi'),
                                options=OBJECTIF_OPTIONS
                            )
                        ]),
                        dbc.Col([
                            dbc.Label("Langue"),
                            dbc.Select(
                                id="mod-langue",
                                value=user.get('langue', 'français'),
                                options=LANGUE_OPTIONS
                            )
                        ])
                    ], class_name="mb-4"),

                    # stocker l'ID pour le callback de sauvegarde
                    dcc.Store(id="mod-user-id", data=user.get('id')),

                    dbc.Button(
                    "💾 Sauvegarder et voir mes nouvelles recommendations ",
                    id="btn-sauvegarder-profil",
                    color="success",
                    size="lg",
                    className="w-100"
                    ),

                    html.Div(id="msg-modification", className="mt-3")
                    
                ])
            ], class_name="shadow")
        ], width=8, class_name="mx-auto mt-3")
    ])





# ═════════════════════════════════════════════════════════
# LAYOUT PRINCIPAL
# ═════════════════════════════════════════════════════════
app.layout = dbc.Container([

    dbc.NavbarSimple(
        brand="🎓 EduReco",
        color="primary",
        dark=True,
        className="mb-4"
    ),

    html.Div(id="contenu-principal", children=page_accueil()),

], fluid=True)

# # Les call back

# ═════════════════════════════════════════════════════════
# CALLBACKS DE NAVIGATION
# ═════════════════════════════════════════════════════════

@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-vers-inscription", "n_clicks"),
    prevent_initial_call=True
)
def aller_inscription(n):
    if n:
        return page_inscription()
    return dash.no_update


@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-vers-connexion", "n_clicks"),
    prevent_initial_call=True
)
def aller_connexion(n):
    if n:
        return page_connexion()
    return dash.no_update


@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-retour-accueil-inscription", "n_clicks"),
    prevent_initial_call=True
)
def retour_depuis_inscription(n):
    if n:
        return page_accueil()
    return dash.no_update


@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-retour-accueil-connexion", "n_clicks"),
    prevent_initial_call=True
)
def retour_depuis_connexion(n):
    if n:
        return page_accueil()
    return dash.no_update


@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-retour-accueil-resultats", "n_clicks"),
    prevent_initial_call=True
)
def retour_depuis_resultats(n):
    if n:
        return page_accueil()
    return dash.no_update


@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-retour-accueil-modif", "n_clicks"),
    prevent_initial_call=True
)
def retour_depuis_modif(n):
    if n:
        return page_accueil()
    return dash.no_update


@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-modifier-profil", "n_clicks"),
    State("store-user", "data"),
    prevent_initial_call=True
)
def aller_modifier(n, user):
    if n and user:
        return page_modifier_profil(user)
    return dash.no_update


# ═════════════════════════════════════════════════════════
# CALLBACK INSCRIPTION
# 1. Valider les champs obligatoires
# 2. POST /api/users → créer le profil
# 3. GET /api/recommendations/{id} → générer les reco NLP
# 4. Afficher la page résultats
# ═════════════════════════════════════════════════════════

@app.callback(
    [
        Output("msg-inscription",   "children"),
        Output("contenu-principal", "children", allow_duplicate=True)
    ],
    Input("btn-soumettre-inscription", "n_clicks"),
    [
        State("inp-nom",      "value"),
        State("inp-prenom",   "value"),
        State("inp-email",    "value"),
        State("inp-pays",     "value"),
        State("inp-niveau",   "value"),
        State("inp-domaine",  "value"),
        State("inp-objectif", "value"),
        State("inp-langue",   "value"),
    ],
    prevent_initial_call=True
)
def soumettre_inscription(n, nom, prenom, email,
                          pays, niveau, domaine, objectif, langue):
    if not n:
        return "", dash.no_update

    # Validation des champs obligatoires
    champs = {"Nom": nom, "Prénom": prenom, "Email": email,
              "Pays": pays, "Niveau": niveau, "Domaine": domaine}
    for label, val in champs.items():
        if not val:
            return dbc.Alert(
                f"⚠️ Le champ '{label}' est obligatoire.",
                color="danger"
            ), dash.no_update

    try:
        # Étape 1 : créer l'utilisateur
        rep = requests.post(
            f"{API_URL}/api/users",
            json={
                "nom":           nom,
                "prenom":        prenom,
                "email":         email,
                "pays":          pays,
                "niveau_etudes": niveau,
                "domaine":       domaine,
                "objectif":      objectif or "emploi",
                "langue":        langue   or "francais",
            },
            timeout=30
        )
        data = rep.json()

        if not data['succes']:
            return dbc.Alert(f"❌ {data['erreur']}", color="danger"), dash.no_update

        user_id = data['utilisateur']['id']

        # Étape 2 : générer les recommendations NLP
        rep_reco = requests.get(
            f"{API_URL}/api/recommendations/{user_id}",
            timeout=30
        )
        data_reco = rep_reco.json()

        if not data_reco['succes']:
            return dbc.Alert(
                "Profil créé mais erreur lors des recommendations.",
                color="warning"
            ), dash.no_update

        # Étape 3 : afficher la page résultats
        return "", page_resultats(
            data_reco['utilisateur'],
            data_reco['formations'],
            data_reco['bourses'],
            data_reco['texte_profil']
        )

    except requests.exceptions.ConnectionError:
        return dbc.Alert(
            "❌ Impossible de joindre l'API. "
            "Vérifiez que api.py tourne sur le port 5001.",
            color="danger"
        ), dash.no_update

    except requests.exceptions.Timeout:
        return dbc.Alert(
            "⏱️ L'API met trop de temps à répondre. Réessayez.",
            color="warning"
        ), dash.no_update

    except Exception as e:
        return dbc.Alert(f"Erreur : {str(e)}", color="danger"), dash.no_update


# ═════════════════════════════════════════════════════════
# CALLBACK CONNEXION
# 1. POST /api/users/connexion → vérifier l'email
# 2. GET /api/recommendations/{id} → charger les reco
# 3. Afficher la page résultats
# ═════════════════════════════════════════════════════════

@app.callback(
    [
        Output("msg-connexion",     "children"),
        Output("contenu-principal", "children", allow_duplicate=True)
    ],
    Input("btn-soumettre-connexion", "n_clicks"),
    State("inp-email-connexion", "value"),
    prevent_initial_call=True
)
def soumettre_connexion(n, email):
    if not n:
        return "", dash.no_update

    if not email or not email.strip():
        return dbc.Alert("⚠️ Entrez votre email.", color="warning"), dash.no_update

    try:
        # Étape 1 : connexion
        rep = requests.post(
            f"{API_URL}/api/users/connexion",
            json={"email": email.strip().lower()},
            timeout=30
        )
        data = rep.json()

        if not data['succes']:
            return dbc.Alert(f"❌ {data['erreur']}", color="danger"), dash.no_update

        user_id = data['utilisateur']['id']

        # Étape 2 : recommendations
        rep_reco = requests.get(
            f"{API_URL}/api/recommendations/{user_id}",
            timeout=30
        )
        data_reco = rep_reco.json()

        # Étape 3 : afficher les résultats
        return "", page_resultats(
            data_reco['utilisateur'],
            data_reco['formations'],
            data_reco['bourses'],
            data_reco['texte_profil']
        )

    except requests.exceptions.ConnectionError:
        return dbc.Alert(
            "❌ Impossible de joindre l'API. "
            "Vérifiez que api.py tourne sur le port 5001.",
            color="danger"
        ), dash.no_update

    except requests.exceptions.Timeout:
        return dbc.Alert(
            "⏱️ L'API met trop de temps à répondre. Réessayez.",
            color="warning"
        ), dash.no_update

    except Exception as e:
        return dbc.Alert(f"Erreur : {str(e)}", color="danger"), dash.no_update


# ═════════════════════════════════════════════════════════
# CALLBACK MODIFICATION PROFIL
# 1. PUT /api/users/{id} → mettre à jour le profil
# 2. GET /api/recommendations/{id} → nouvelles reco NLP
# 3. Afficher la page résultats mise à jour
# ═════════════════════════════════════════════════════════

@app.callback(
    [
        Output("msg-modification",  "children"),
        Output("contenu-principal", "children", allow_duplicate=True)
    ],
    Input("btn-sauvegarder-profil", "n_clicks"),
    [
        State("mod-user-id",  "data"),
        State("mod-nom",      "value"),
        State("mod-prenom",   "value"),
        State("mod-pays",     "value"),
        State("mod-niveau",   "value"),
        State("mod-domaine",  "value"),
        State("mod-objectif", "value"),
        State("mod-langue",   "value"),
    ],
    prevent_initial_call=True
)
def sauvegarder_modification(n, user_id, nom, prenom,
                              pays, niveau, domaine, objectif, langue):
    if not n:
        return "", dash.no_update

    if not all([nom, prenom, pays, niveau, domaine]):
        return dbc.Alert(
            "⚠️ Tous les champs sont requis.",
            color="danger"
        ), dash.no_update

    try:
        # Étape 1 : modifier le profil
        rep = requests.put(
            f"{API_URL}/api/users/{user_id}",
            json={
                "nom":           nom,
                "prenom":        prenom,
                "pays":          pays,
                "niveau_etudes": niveau,
                "domaine":       domaine,
                "objectif":      objectif,
                "langue":        langue,
            },
            timeout=30
        )
        data = rep.json()

        if not data['succes']:
            return dbc.Alert(f"❌ {data['erreur']}", color="danger"), dash.no_update

        # Étape 2 : nouvelles recommendations avec le profil modifié
        rep_reco = requests.get(
            f"{API_URL}/api/recommendations/{user_id}",
            timeout=30
        )
        data_reco = rep_reco.json()

        # Étape 3 : afficher les résultats
        return "", page_resultats(
            data_reco['utilisateur'],
            data_reco['formations'],
            data_reco['bourses'],
            data_reco['texte_profil']
        )

    except requests.exceptions.ConnectionError:
        return dbc.Alert(
            "❌ Impossible de joindre l'API. "
            "Vérifiez que api.py tourne sur le port 5001.",
            color="danger"
        ), dash.no_update

    except Exception as e:
        return dbc.Alert(f"Erreur : {str(e)}", color="danger"), dash.no_update


# ═════════════════════════════════════════════════════════
# DÉMARRAGE
# ═════════════════════════════════════════════════════════
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)