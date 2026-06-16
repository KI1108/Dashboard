# dashboard.py
# ============================================================
# EduReco — Dashboard utilisateur Dash
# Version corrigée pour déploiement local + Render
# ============================================================

import os
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import requests

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

API_URL = os.getenv("API_URL", "http://127.0.0.1:5001").rstrip("/")


# ─────────────────────────────────────────────────────────
# HELPERS API
# ─────────────────────────────────────────────────────────
def api_get(path, timeout=30):
    url = f"{API_URL}{path}"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()


def api_post(path, payload, timeout=30):
    url = f"{API_URL}{path}"
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def api_put(path, payload, timeout=30):
    url = f"{API_URL}{path}"
    r = requests.put(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def erreur_api_message(err):
    if isinstance(err, requests.exceptions.ConnectionError):
        return dbc.Alert(
            f"❌ Impossible de joindre l'API distante : {API_URL}",
            color="danger"
        )
    if isinstance(err, requests.exceptions.Timeout):
        return dbc.Alert(
            f"⏱️ L'API ne répond pas à temps : {API_URL}",
            color="warning"
        )
    if isinstance(err, requests.exceptions.HTTPError):
        return dbc.Alert(
            f"❌ Erreur HTTP API : {err}",
            color="danger"
        )
    return dbc.Alert(
        f"❌ Erreur inattendue : {err}",
        color="danger"
    )


# ═════════════════════════════════════════════════════════
# DONNÉES PARTAGÉES
# ═════════════════════════════════════════════════════════
PAYS_OPTIONS = [
    {"label": "Sénégal", "value": "Senegal"},
    {"label": "Guinée", "value": "Guinea"},
    {"label": "Mali", "value": "Mali"},
    {"label": "Côte d'Ivoire", "value": "Cote d'Ivoire"},
    {"label": "Burkina Faso", "value": "Burkina Faso"},
    {"label": "Cameroun", "value": "Cameroun"},
    {"label": "Maroc", "value": "Maroc"},
    {"label": "France", "value": "France"},
    {"label": "Autre", "value": "Autre"},
]

NIVEAU_OPTIONS = [
    {"label": "Lycée / Bac", "value": "lycee"},
    {"label": "Licence", "value": "licence"},
    {"label": "Master", "value": "master"},
    {"label": "Doctorat", "value": "doctorat"},
]

DOMAINE_OPTIONS = [
    {"label": "Informatique / Data Science", "value": "informatique"},
    {"label": "Ingénierie", "value": "ingenierie"},
    {"label": "Économie / Finance", "value": "economie"},
    {"label": "Droit", "value": "droit"},
    {"label": "Médecine / Santé", "value": "medecine"},
    {"label": "Sciences", "value": "science"},
    {"label": "Éducation", "value": "education"},
    {"label": "Arts / Lettres", "value": "arts"},
]

OBJECTIF_OPTIONS = [
    {"label": "Trouver un emploi", "value": "emploi"},
    {"label": "Faire de la recherche", "value": "recherche"},
    {"label": "Créer une entreprise", "value": "entrepreneuriat"},
    {"label": "Formation continue", "value": "continue"},
]

LANGUE_OPTIONS = [
    {"label": "Français", "value": "francais"},
    {"label": "Anglais", "value": "anglais"},
    {"label": "Arabe", "value": "arabe"},
]


# ═════════════════════════════════════════════════════════
# PAGES
# ═════════════════════════════════════════════════════════
def page_accueil():
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2("🎓 EduReco", className="text-center mb-2"),
                    html.P(
                        "Trouvez les formations et bourses qui correspondent à votre profil grâce à l'intelligence artificielle.",
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
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H4("Créer mon profil")),
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
                        className="mb-3"
                    ),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Niveau d'études *"),
                            dbc.Select(
                                id="inp-niveau",
                                options=NIVEAU_OPTIONS
                            )
                        ]),
                        dbc.Col([
                            dbc.Label("Domaine *"),
                            dbc.Select(
                                id="inp-domaine",
                                options=DOMAINE_OPTIONS
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


def carte_formation(f):
    pct = f.get("pct", 0)
    if pct >= 40:
        couleur = "success"
    elif pct >= 25:
        couleur = "warning"
    else:
        couleur = "secondary"

    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5(f.get("titre", ""), className="card-title"),
                    html.P([
                        dbc.Badge(f.get("domaine", ""), color="primary", className="me-1"),
                        dbc.Badge(f.get("niveau_requis", ""), color="info", className="me-1"),
                        dbc.Badge(
                            "Gratuit" if f.get("est_gratuit") else "Payant",
                            color="success" if f.get("est_gratuit") else "secondary",
                            className="me-1"
                        ),
                    ]),
                    html.P(f.get("organisme", ""), className="text-muted small")
                ], width=9),
                dbc.Col([
                    html.H3(
                        f"{pct}%",
                        className=f"text-{couleur} text-center fw-bold"
                    ),
                    html.P("Correspondance", className="text-center small text-muted")
                ], width=3)
            ]),
            html.A(
                "Voir la formation →",
                href=f.get("lien", "#"),
                target="_blank",
                rel="noopener noreferrer",
                role="button",
                className="btn btn-outline-primary btn-sm mt-1"
            ) if f.get("lien") else html.Span()
        ])
    ], className="mb-3 shadow-sm")


def carte_bourse(b):
    pct = b.get("pct", 0)
    if pct >= 40:
        couleur = "success"
    elif pct >= 25:
        couleur = "warning"
    else:
        couleur = "secondary"

    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5(b.get("titre", ""), className="card-title"),
                    html.P([
                        dbc.Badge(b.get("organisme", ""), color="danger", className="me-1"),
                        dbc.Badge(b.get("niveau_requis", ""), color="info", className="me-1"),
                        dbc.Badge(b.get("pays_eligible", "Tous pays"), color="warning", className="me-1"),
                    ]),
                    html.P(b.get("montant", ""), className="text-success fw-bold")
                ], width=9),
                dbc.Col([
                    html.H3(
                        f"{pct}%",
                        className=f"text-{couleur} text-center fw-bold"
                    ),
                    html.P("Correspondance", className="text-center small text-muted")
                ], width=3)
            ]),
            html.A(
                "Voir la bourse →",
                href=b.get("lien", "#"),
                target="_blank",
                rel="noopener noreferrer",
                role="button",
                className="btn btn-outline-danger btn-sm mt-1"
            ) if b.get("lien") else html.Span()
        ])
    ], className="mb-3 shadow-sm")


def page_resultats(user, formations, bourses, texte_profil):
    return html.Div([
        dbc.Alert([
            dbc.Row([
                dbc.Col([
                    html.H4(f"Bonjour {user.get('prenom', '')} {user.get('nom', '')} 👋"),
                    html.P([
                        html.Strong("Profil analysé : "),
                        html.Em(texte_profil or "")
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
                ], width=3, className="text-end")
            ], className="align-items-center")
        ], color="info"),

        dcc.Store(id="store-user", data=user),
        html.Hr(),

        dbc.Row([
            dbc.Col([
                html.H4(f"🎓 Formations recommandées ({len(formations)})"),
                html.Div(
                    [carte_formation(f) for f in formations]
                    if formations else [dbc.Alert("Aucune formation trouvée.", color="warning")]
                )
            ], width=6),

            dbc.Col([
                html.H4(f"💵 Bourses recommandées ({len(bourses)})"),
                html.Div(
                    [carte_bourse(b) for b in bourses]
                    if bourses else [dbc.Alert("Aucune bourse trouvée.", color="warning")]
                )
            ], width=6),
        ])
    ])


def page_modifier_profil(user):
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
                            className="text-end"
                        )
                    ])
                ]),
                dbc.CardBody([
                    dbc.Alert([
                        html.Strong("Email (non modifiable) : "),
                        html.Span(user.get("email", ""))
                    ], color="light", className="mb-3"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Nom"),
                            dbc.Input(id="mod-nom", value=user.get("nom", ""))
                        ]),
                        dbc.Col([
                            dbc.Label("Prénom"),
                            dbc.Input(id="mod-prenom", value=user.get("prenom", ""))
                        ])
                    ], className="mb-3"),

                    dbc.Label("Pays"),
                    dbc.Select(
                        id="mod-pays",
                        value=user.get("pays", ""),
                        options=PAYS_OPTIONS,
                        className="mb-3"
                    ),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Niveau d'études"),
                            dbc.Select(
                                id="mod-niveau",
                                value=user.get("niveau_etudes", ""),
                                options=NIVEAU_OPTIONS
                            )
                        ]),
                        dbc.Col([
                            dbc.Label("Domaine"),
                            dbc.Select(
                                id="mod-domaine",
                                value=user.get("domaine", ""),
                                options=DOMAINE_OPTIONS
                            )
                        ])
                    ], className="mb-3"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Objectif"),
                            dbc.Select(
                                id="mod-objectif",
                                value=user.get("objectif", "emploi"),
                                options=OBJECTIF_OPTIONS
                            )
                        ]),
                        dbc.Col([
                            dbc.Label("Langue"),
                            dbc.Select(
                                id="mod-langue",
                                value=user.get("langue", "francais"),
                                options=LANGUE_OPTIONS
                            )
                        ])
                    ], className="mb-4"),

                    dcc.Store(id="mod-user-id", data=user.get("id")),

                    dbc.Button(
                        "💾 Sauvegarder et voir mes nouvelles recommandations",
                        id="btn-sauvegarder-profil",
                        color="success",
                        size="lg",
                        className="w-100"
                    ),

                    html.Div(id="msg-modification", className="mt-3")
                ])
            ], className="shadow")
        ], width=8, className="mx-auto mt-3")
    ])


# ═════════════════════════════════════════════════════════
# LAYOUT
# ═════════════════════════════════════════════════════════
app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="🎓 EduReco",
        color="primary",
        dark=True,
        className="mb-4"
    ),
    html.Div(id="contenu-principal", children=page_accueil())
], fluid=True)


# ═════════════════════════════════════════════════════════
# CALLBACKS NAVIGATION
# ═════════════════════════════════════════════════════════
@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-vers-inscription", "n_clicks"),
    prevent_initial_call=True
)
def aller_inscription(n):
    return page_inscription() if n else dash.no_update


@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-vers-connexion", "n_clicks"),
    prevent_initial_call=True
)
def aller_connexion(n):
    return page_connexion() if n else dash.no_update


@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-retour-accueil-inscription", "n_clicks"),
    prevent_initial_call=True
)
def retour_depuis_inscription(n):
    return page_accueil() if n else dash.no_update


@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-retour-accueil-connexion", "n_clicks"),
    prevent_initial_call=True
)
def retour_depuis_connexion(n):
    return page_accueil() if n else dash.no_update


@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-retour-accueil-resultats", "n_clicks"),
    prevent_initial_call=True
)
def retour_depuis_resultats(n):
    return page_accueil() if n else dash.no_update


@app.callback(
    Output("contenu-principal", "children", allow_duplicate=True),
    Input("btn-retour-accueil-modif", "n_clicks"),
    prevent_initial_call=True
)
def retour_depuis_modif(n):
    return page_accueil() if n else dash.no_update


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
# INSCRIPTION
# ═════════════════════════════════════════════════════════
@app.callback(
    [
        Output("msg-inscription", "children"),
        Output("contenu-principal", "children", allow_duplicate=True)
    ],
    Input("btn-soumettre-inscription", "n_clicks"),
    [
        State("inp-nom", "value"),
        State("inp-prenom", "value"),
        State("inp-email", "value"),
        State("inp-pays", "value"),
        State("inp-niveau", "value"),
        State("inp-domaine", "value"),
        State("inp-objectif", "value"),
        State("inp-langue", "value"),
    ],
    prevent_initial_call=True
)
def soumettre_inscription(n, nom, prenom, email, pays, niveau, domaine, objectif, langue):
    if not n:
        return "", dash.no_update

    champs = {
        "Nom": nom,
        "Prénom": prenom,
        "Email": email,
        "Pays": pays,
        "Niveau": niveau,
        "Domaine": domaine
    }
    for label, val in champs.items():
        if not val:
            return dbc.Alert(f"⚠️ Le champ '{label}' est obligatoire.", color="danger"), dash.no_update

    try:
        data = api_post("/api/users", {
            "nom": nom,
            "prenom": prenom,
            "email": email.strip().lower(),
            "pays": pays,
            "niveau_etudes": niveau,
            "domaine": domaine,
            "objectif": objectif or "emploi",
            "langue": langue or "francais",
        })

        if not data.get("succes"):
            return dbc.Alert(f"❌ {data.get('erreur', 'Erreur inconnue')}", color="danger"), dash.no_update

        user_id = data["utilisateur"]["id"]

        data_reco = api_get(f"/api/recommendations/{user_id}")

        if not data_reco.get("succes"):
            return dbc.Alert("Profil créé mais erreur lors des recommandations.", color="warning"), dash.no_update

        return "", page_resultats(
            data_reco["utilisateur"],
            data_reco["formations"],
            data_reco["bourses"],
            data_reco["texte_profil"]
        )

    except Exception as e:
        return erreur_api_message(e), dash.no_update


# ═════════════════════════════════════════════════════════
# CONNEXION
# ═════════════════════════════════════════════════════════
@app.callback(
    [
        Output("msg-connexion", "children"),
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
        data = api_post("/api/users/connexion", {
            "email": email.strip().lower()
        })

        if not data.get("succes"):
            return dbc.Alert(f"❌ {data.get('erreur', 'Erreur inconnue')}", color="danger"), dash.no_update

        user_id = data["utilisateur"]["id"]
        data_reco = api_get(f"/api/recommendations/{user_id}")

        if not data_reco.get("succes"):
            return dbc.Alert("Erreur lors du chargement des recommandations.", color="warning"), dash.no_update

        return "", page_resultats(
            data_reco["utilisateur"],
            data_reco["formations"],
            data_reco["bourses"],
            data_reco["texte_profil"]
        )

    except Exception as e:
        return erreur_api_message(e), dash.no_update


# ═════════════════════════════════════════════════════════
# MODIFICATION PROFIL
# ═════════════════════════════════════════════════════════
@app.callback(
    [
        Output("msg-modification", "children"),
        Output("contenu-principal", "children", allow_duplicate=True)
    ],
    Input("btn-sauvegarder-profil", "n_clicks"),
    [
        State("mod-user-id", "data"),
        State("mod-nom", "value"),
        State("mod-prenom", "value"),
        State("mod-pays", "value"),
        State("mod-niveau", "value"),
        State("mod-domaine", "value"),
        State("mod-objectif", "value"),
        State("mod-langue", "value"),
    ],
    prevent_initial_call=True
)
def sauvegarder_modification(n, user_id, nom, prenom, pays, niveau, domaine, objectif, langue):
    if not n:
        return "", dash.no_update

    if not all([nom, prenom, pays, niveau, domaine]):
        return dbc.Alert("⚠️ Tous les champs sont requis.", color="danger"), dash.no_update

    try:
        data = api_put(f"/api/users/{user_id}", {
            "nom": nom,
            "prenom": prenom,
            "pays": pays,
            "niveau_etudes": niveau,
            "domaine": domaine,
            "objectif": objectif,
            "langue": langue,
        })

        if not data.get("succes"):
            return dbc.Alert(f"❌ {data.get('erreur', 'Erreur inconnue')}", color="danger"), dash.no_update

        data_reco = api_get(f"/api/recommendations/{user_id}")

        if not data_reco.get("succes"):
            return dbc.Alert("Erreur lors de la mise à jour des recommandations.", color="warning"), dash.no_update

        return "", page_resultats(
            data_reco["utilisateur"],
            data_reco["formations"],
            data_reco["bourses"],
            data_reco["texte_profil"]
        )

    except Exception as e:
        return erreur_api_message(e), dash.no_update


# ═════════════════════════════════════════════════════════
# DÉMARRAGE
# ═════════════════════════════════════════════════════════
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("=" * 50)
    print(" EduReco — Dashboard Dash")
    print("=" * 50)
    print(f" Dashboard → http://127.0.0.1:{port}")
    print(f" API       → {API_URL}")
    print("=" * 50)
    app.run(debug=False, host="0.0.0.0", port=port)