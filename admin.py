# admin.py
# ============================================================
# EduReco — Admin Dashboard (version claire blanc + bleu)
# Déploiement friendly pour Render
# ============================================================

import os
import dash
from dash import html, dcc, dash_table, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import requests

# ─────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://127.0.0.1:5001")

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server
app.title = "EduReco — Admin"

# Palette claire
COLORS = {
    "bg": "#f5f8fc",
    "card": "#ffffff",
    "primary": "#3f6df6",
    "primary_dark": "#2954d4",
    "secondary": "#eaf2ff",
    "text": "#1f2d3d",
    "muted": "#6b7a90",
    "border": "#dbe6f3",
    "success": "#2e8b57",
    "warning": "#f0ad4e",
    "danger": "#dc3545",
    "info": "#5bc0de",
}

# ─────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────
GLOBAL_STYLE = {
    "backgroundColor": COLORS["bg"],
    "minHeight": "100vh",
    "paddingBottom": "30px"
}

CARD_STYLE = {
    "backgroundColor": COLORS["card"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "16px",
    "boxShadow": "0 4px 14px rgba(31, 45, 61, 0.08)"
}

KPI_CARD_STYLE = {
    **CARD_STYLE,
    "padding": "6px"
}

SECTION_TITLE_STYLE = {
    "color": COLORS["text"],
    "fontWeight": "700",
    "marginBottom": "18px"
}

# ─────────────────────────────────────────────────────────
# APPELS API
# ─────────────────────────────────────────────────────────
def fetch_stats():
    try:
        r = requests.get(f"{API_URL}/api/admin/stats", timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("stats", {}) if data.get("succes") else {}
    except Exception:
        return {}


def fetch_users():
    try:
        r = requests.get(f"{API_URL}/api/admin/users", timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("users", []) if data.get("succes") else []
    except Exception:
        return []


def fetch_recos():
    try:
        r = requests.get(f"{API_URL}/api/admin/recommendations", timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("recommendations", []) if data.get("succes") else []
    except Exception:
        return []


# ─────────────────────────────────────────────────────────
# COMPOSANTS
# ─────────────────────────────────────────────────────────
def kpi_card(titre, valeur, icone, couleur):
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div(icone, style={"fontSize": "2rem"}),
                ], width=3),
                dbc.Col([
                    html.H3(
                        str(valeur),
                        className="mb-1 fw-bold",
                        style={"color": couleur}
                    ),
                    html.P(
                        titre,
                        className="mb-0",
                        style={"color": COLORS["muted"], "fontSize": "0.95rem"}
                    )
                ], width=9)
            ], align="center")
        ]),
        style=KPI_CARD_STYLE,
        className="h-100"
    )


def alerte_api_down():
    return dbc.Alert(
        [
            html.Strong("API inaccessible. "),
            "Vérifie que api.py tourne correctement ou que API_URL est bien configuré."
        ],
        color="danger",
        style={"borderRadius": "12px"}
    )


def top_banner():
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H2(
                        "Bonjour Admin 👋",
                        className="fw-bold mb-2",
                        style={"color": "#26435f"}
                    ),
                    html.P(
                        "Supervision de la plateforme EduReco, suivi des utilisateurs et des recommandations.",
                        className="mb-0",
                        style={"color": "#55708b", "fontSize": "1rem"}
                    )
                ], width=8),
                dbc.Col([
                    dbc.Button(
                        "🔄 Actualiser",
                        id="btn-refresh-top",
                        color="light",
                        outline=False,
                        style={
                            "borderRadius": "10px",
                            "fontWeight": "600",
                            "color": COLORS["primary"]
                        }
                    )
                ], width=4, className="d-flex justify-content-end align-items-start")
            ])
        ]),
        style={
            "backgroundColor": "#e8f4fb",
            "border": "1px solid #d6ebf7",
            "borderRadius": "16px",
            "boxShadow": "0 2px 10px rgba(63,109,246,0.06)"
        },
        className="mb-4"
    )


# ─────────────────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────────────────
def page_dashboard():
    stats = fetch_stats()

    if not stats:
        return alerte_api_down()

    kpis = dbc.Row([
        dbc.Col(kpi_card("Utilisateurs inscrits", stats.get("total_users", 0), "👤", COLORS["primary"]), md=3, className="mb-3"),
        dbc.Col(kpi_card("Recommendations générées", stats.get("total_recos", 0), "🤖", "#22a06b"), md=3, className="mb-3"),
        dbc.Col(kpi_card("Formations recommandées", stats.get("nb_formations_reco", 0), "🎓", "#1f9bd1"), md=3, className="mb-3"),
        dbc.Col(kpi_card("Bourses recommandées", stats.get("nb_bourses_reco", 0), "💰", "#e0a100"), md=3, className="mb-3"),
    ], className="mb-2")

    par_domaine = stats.get("par_domaine", {})
    fig_domaine = px.pie(
        names=list(par_domaine.keys()),
        values=list(par_domaine.values()),
        title="Répartition par domaine",
        hole=0.45,
        color_discrete_sequence=["#3f6df6", "#6ea8fe", "#9ec5fe", "#bfd7ff", "#dbeafe"]
    )
    fig_domaine.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color=COLORS["text"],
        title_font_color=COLORS["text"],
        legend=dict(orientation="v"),
        margin=dict(l=20, r=20, t=50, b=20)
    )

    par_niveau = stats.get("par_niveau", {})
    fig_niveau = px.bar(
        x=list(par_niveau.keys()),
        y=list(par_niveau.values()),
        title="Répartition par niveau d'études",
        labels={"x": "Niveau", "y": "Nb utilisateurs"},
        color=list(par_niveau.values()),
        color_continuous_scale=["#dbeafe", "#93c5fd", "#60a5fa", "#3b82f6"]
    )
    fig_niveau.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color=COLORS["text"],
        title_font_color=COLORS["text"],
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    par_pays = stats.get("par_pays", {})
    fig_pays = px.bar(
        x=list(par_pays.values()),
        y=list(par_pays.keys()),
        orientation="h",
        title="Répartition par pays",
        labels={"x": "Nb utilisateurs", "y": "Pays"},
        color=list(par_pays.values()),
        color_continuous_scale=["#dbeafe", "#93c5fd", "#60a5fa", "#3b82f6"]
    )
    fig_pays.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color=COLORS["text"],
        title_font_color=COLORS["text"],
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    score_moyen = stats.get("score_moyen", 0)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_moyen,
        title={"text": "Score NLP moyen (%)", "font": {"color": COLORS["text"]}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": COLORS["text"]},
            "bar": {"color": COLORS["primary"]},
            "steps": [
                {"range": [0, 40], "color": "#e9eef5"},
                {"range": [40, 70], "color": "#d9e7ff"},
                {"range": [70, 100], "color": "#bfd7ff"},
            ],
            "threshold": {
                "line": {"color": COLORS["danger"], "width": 4},
                "thickness": 0.75,
                "value": 70
            }
        },
        number={"suffix": "%", "font": {"color": COLORS["text"]}}
    ))
    fig_gauge.update_layout(
        paper_bgcolor="white",
        font_color=COLORS["text"],
        height=260,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return html.Div([
        html.H4("📊 Tableau de bord", style=SECTION_TITLE_STYLE),
        kpis,
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig_domaine)), style=CARD_STYLE), md=5, className="mb-4"),
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig_niveau)), style=CARD_STYLE), md=4, className="mb-4"),
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig_gauge)), style=CARD_STYLE), md=3, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig_pays)), style=CARD_STYLE), md=6, className="mb-4"),
        ])
    ])


def page_utilisateurs():
    users = fetch_users()

    if not users:
        return alerte_api_down()

    colonnes = [
        {"name": "ID", "id": "id"},
        {"name": "Nom", "id": "nom"},
        {"name": "Prénom", "id": "prenom"},
        {"name": "Email", "id": "email"},
        {"name": "Pays", "id": "pays"},
        {"name": "Niveau", "id": "niveau_etudes"},
        {"name": "Domaine", "id": "domaine"},
        {"name": "Objectif", "id": "objectif"},
        {"name": "Créé le", "id": "created_at"},
    ]

    return html.Div([
        html.H4(f"👤 Utilisateurs — {len(users)} inscrits", style=SECTION_TITLE_STYLE),
        dbc.Card(
            dbc.CardBody([
                dash_table.DataTable(
                    data=users,
                    columns=colonnes,
                    page_size=15,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "textAlign": "left",
                        "padding": "12px",
                        "fontFamily": "Arial",
                        "fontSize": "14px",
                        "border": "none",
                        "backgroundColor": "white",
                        "color": COLORS["text"]
                    },
                    style_header={
                        "backgroundColor": "#edf4ff",
                        "color": COLORS["primary_dark"],
                        "fontWeight": "bold",
                        "borderBottom": f"1px solid {COLORS['border']}"
                    },
                    style_data={
                        "backgroundColor": "white",
                        "color": COLORS["text"],
                        "borderBottom": "1px solid #eef3f8"
                    },
                    style_data_conditional=[
                        {"if": {"row_index": "odd"}, "backgroundColor": "#f9fbfe"}
                    ],
                    style_filter={
                        "backgroundColor": "#f3f8ff",
                        "color": COLORS["text"],
                        "border": "1px solid #d9e7ff"
                    }
                )
            ]),
            style=CARD_STYLE
        )
    ])


def page_recommendations():
    recos = fetch_recos()

    if not recos:
        return alerte_api_down()

    nb_formations = sum(1 for r in recos if r.get("type_item") == "formation")
    nb_bourses = sum(1 for r in recos if r.get("type_item") == "bourse")

    colonnes = [
        {"name": "ID", "id": "id"},
        {"name": "User ID", "id": "user_id"},
        {"name": "Type", "id": "type_item"},
        {"name": "Item ID", "id": "item_id"},
        {"name": "Score (%)", "id": "score"},
        {"name": "Raison", "id": "raisons"},
    ]

    return html.Div([
        html.H4(f"🤖 Recommendations — {len(recos)} générées", style=SECTION_TITLE_STYLE),

        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5(str(nb_formations), className="fw-bold mb-1", style={"color": COLORS["primary"]}),
                        html.Div("🎓 Formations", style={"color": COLORS["muted"]})
                    ]),
                    style={**CARD_STYLE, "backgroundColor": "#f2f7ff"}
                ),
                md=3, className="mb-3"
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5(str(nb_bourses), className="fw-bold mb-1", style={"color": "#d4a017"}),
                        html.Div("💰 Bourses", style={"color": COLORS["muted"]})
                    ]),
                    style={**CARD_STYLE, "backgroundColor": "#fffaf0"}
                ),
                md=3, className="mb-3"
            ),
        ]),

        dbc.Card(
            dbc.CardBody([
                dash_table.DataTable(
                    data=recos,
                    columns=colonnes,
                    page_size=20,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "textAlign": "left",
                        "padding": "12px",
                        "fontFamily": "Arial",
                        "fontSize": "14px",
                        "border": "none",
                        "backgroundColor": "white",
                        "color": COLORS["text"],
                        "whiteSpace": "normal",
                        "height": "auto",
                    },
                    style_header={
                        "backgroundColor": "#edf4ff",
                        "color": COLORS["primary_dark"],
                        "fontWeight": "bold",
                        "borderBottom": f"1px solid {COLORS['border']}"
                    },
                    style_data={
                        "backgroundColor": "white",
                        "color": COLORS["text"],
                        "borderBottom": "1px solid #eef3f8"
                    },
                    style_data_conditional=[
                        {"if": {"row_index": "odd"}, "backgroundColor": "#f9fbfe"},
                        {
                            "if": {
                                "filter_query": "{type_item} = 'formation'",
                                "column_id": "type_item"
                            },
                            "color": "#1f73d8",
                            "fontWeight": "bold"
                        },
                        {
                            "if": {
                                "filter_query": "{type_item} = 'bourse'",
                                "column_id": "type_item"
                            },
                            "color": "#c69214",
                            "fontWeight": "bold"
                        },
                    ],
                    style_filter={
                        "backgroundColor": "#f3f8ff",
                        "color": COLORS["text"],
                        "border": "1px solid #d9e7ff"
                    }
                )
            ]),
            style=CARD_STYLE
        )
    ])


# ─────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────
app.layout = html.Div([
    dbc.Navbar(
        dbc.Container([
            html.Div(
                "🎓 EduReco — Administration",
                style={
                    "color": "white",
                    "fontWeight": "700",
                    "fontSize": "1.35rem"
                }
            )
        ], fluid=True),
        style={
            "background": "linear-gradient(90deg, #3f6df6 0%, #5485ff 100%)",
            "paddingTop": "14px",
            "paddingBottom": "14px",
            "marginBottom": "25px",
            "boxShadow": "0 4px 12px rgba(63,109,246,0.22)"
        },
        dark=True
    ),

    dbc.Container([
        top_banner(),

        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button(
                        "📊 Tableau de bord",
                        id="btn-dashboard",
                        color="primary",
                        n_clicks=0,
                        style={"fontWeight": "600", "borderRadius": "10px"}
                    ),
                    dbc.Button(
                        "👤 Utilisateurs",
                        id="btn-users",
                        color="primary",
                        outline=True,
                        n_clicks=0,
                        style={"fontWeight": "600", "borderRadius": "10px"}
                    ),
                    dbc.Button(
                        "🤖 Recommendations",
                        id="btn-recos",
                        color="primary",
                        outline=True,
                        n_clicks=0,
                        style={"fontWeight": "600", "borderRadius": "10px"}
                    ),
                    dbc.Button(
                        "🔄 Rafraîchir",
                        id="btn-refresh",
                        color="secondary",
                        n_clicks=0,
                        style={
                            "fontWeight": "600",
                            "borderRadius": "10px",
                            "backgroundColor": "#eef4ff",
                            "border": "1px solid #dbe6f3",
                            "color": COLORS["primary_dark"]
                        }
                    ),
                ], className="flex-wrap")
            ])
        ], className="mb-4"),

        html.Div(id="admin-contenu", children=page_dashboard())
    ], fluid=True)
], style=GLOBAL_STYLE)


# ─────────────────────────────────────────────────────────
# CALLBACK
# ─────────────────────────────────────────────────────────
@app.callback(
    Output("admin-contenu", "children"),
    [
        Input("btn-dashboard", "n_clicks"),
        Input("btn-users", "n_clicks"),
        Input("btn-recos", "n_clicks"),
        Input("btn-refresh", "n_clicks"),
        Input("btn-refresh-top", "n_clicks"),
    ],
    prevent_initial_call=True
)
def changer_page(n_dashboard, n_users, n_recos, n_refresh, n_refresh_top):
    ctx = dash.callback_context
    if not ctx.triggered:
        return page_dashboard()

    bouton_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if bouton_id == "btn-users":
        return page_utilisateurs()
    elif bouton_id == "btn-recos":
        return page_recommendations()
    else:
        return page_dashboard()


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    print("=" * 50)
    print(" EduReco — Admin Dashboard")
    print("=" * 50)
    print(f" Admin → http://127.0.0.1:{port}")
    print(f" API   → {API_URL}")
    print("=" * 50)
    app.run(debug=False, host="0.0.0.0", port=port)