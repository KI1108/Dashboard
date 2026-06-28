import os
import time
import requests
import dash
from dash import html, dcc, dash_table, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

API_URL = os.getenv("API_URL", "").rstrip("/")
REQUEST_TIMEOUT = 20
CACHE_TTL_SECONDS = 60

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=False,
)
server = app.server
app.title = "EduReco — Admin"

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


def api_down_message(details=""):
    base = "API inaccessible."
    if API_URL:
        base += f" API utilisée : {API_URL}"
    else:
        base += " API_URL non configurée dans les variables du Space."
    if details:
        base += f" | Détail : {details}"
    return dbc.Alert(
        [html.Strong(base)],
        color="danger",
        style={"borderRadius": "12px"}
    )


def build_url(path: str) -> str:
    return f"{API_URL}{path}"


def safe_get_json(url, timeout=REQUEST_TIMEOUT, retries=2):
    last_error = None
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 429:
                retry_after = r.headers.get("Retry-After")
                wait_seconds = int(retry_after) if retry_after and retry_after.isdigit() else min(2 ** attempt, 8)
                time.sleep(wait_seconds)
                last_error = requests.HTTPError(f"429 Too Many Requests for url: {url}")
                continue
            r.raise_for_status()
            try:
                return r.json()
            except ValueError:
                # La réponse n'est pas du JSON (ex: page d'erreur HTML du proxy / Space en veille)
                extrait = r.text[:200].replace("\n", " ")
                raise requests.HTTPError(
                    f"Réponse non-JSON reçue de {url} (content-type={r.headers.get('content-type')}) : {extrait}"
                )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            last_error = e
            if attempt < retries:
                time.sleep(min(2 ** attempt, 4))
                continue
            raise
    raise last_error


def normalize_api_response(data, key):
    """
    Tolère plusieurs formats d'API :
      - {"succes": true, "stats": {...}}
      - {"success": true, "stats": {...}}
      - {"stats": {...}}                       (sans flag de succès)
      - {"success": true, "data": {...}}       (payload sous "data"/"result")
      - {"succes": true, "total_utilisateurs": ..., "repartition_domaine": {...}}
        (payload à plat, directement aux côtés du flag de succès)
      - {"succes": true, "utilisateurs": [...]} (une seule liste à côté du flag)
    """
    if not isinstance(data, dict):
        print(f"[normalize_api_response] Réponse inattendue (pas un dict) pour '{key}': {data!r}")
        return None

    flags_succes = ("succes", "success", "ok")
    flag_present = next((f for f in flags_succes if f in data), None)

    # 1) Flag de succès explicite qui vaudrait False -> on arrête là (erreur API)
    if flag_present is not None:
        valeur = data.get(flag_present)
        est_ok = valeur is True or (isinstance(valeur, str) and valeur.lower() in ("ok", "true", "success", "succes"))
        if not est_ok:
            print(f"[normalize_api_response] Flag '{flag_present}' négatif pour '{key}': {data!r}")
            return None

    # 2) La clé attendue est présente directement
    if key in data:
        return data.get(key)

    # 3) Le payload est rangé sous data / result / payload
    for alt in ("data", "result", "payload"):
        if isinstance(data.get(alt), dict) and key in data[alt]:
            return data[alt][key]
        if alt in data and isinstance(data.get(alt), (dict, list)):
            return data[alt]

    # 4) Pas d'enveloppe reconnue : le payload est à plat dans le dict
    #    (on retire juste le flag de succès / message d'erreur éventuel)
    reste = {k: v for k, v in data.items() if k not in flags_succes and k not in ("erreur", "error", "message")}
    if reste:
        # S'il ne reste qu'une seule clé contenant une liste -> c'est elle qu'on veut
        if len(reste) == 1:
            seule_valeur = next(iter(reste.values()))
            if isinstance(seule_valeur, list):
                return seule_valeur
        # Sinon, si on cherche un dict de stats, le reste à plat EST le payload
        return reste

    print(f"[normalize_api_response] Aucun format reconnu pour '{key}'. Clés reçues: {list(data.keys())}")
    return None


def extract_error_message(data):
    if not isinstance(data, dict):
        return "Réponse API invalide"
    for champ in ("erreur", "error", "message", "detail"):
        if data.get(champ):
            return str(data[champ])
    # Aide au diagnostic : montre les clés reçues si aucun message d'erreur explicite
    return f"Réponse API invalide (clés reçues : {list(data.keys())})"


def pick(d, *keys, default=None):
    """Renvoie la première clé présente (et non-None) parmi plusieurs noms possibles."""
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            return d.get(k)
    return default


def fetch_stats():
    if not API_URL:
        return None, "API_URL manquante"
    try:
        data = safe_get_json(build_url("/api/admin/stats"))
        stats = normalize_api_response(data, "stats")
        if stats is not None:
            return stats, None
        return None, extract_error_message(data)
    except requests.exceptions.Timeout:
        return None, "Timeout API"
    except Exception as e:
        return None, str(e)


def fetch_users():
    if not API_URL:
        return None, "API_URL manquante"
    try:
        data = safe_get_json(build_url("/api/admin/users"))
        users = normalize_api_response(data, "users")
        if users is not None:
            return users, None
        return None, extract_error_message(data)
    except requests.exceptions.Timeout:
        return None, "Timeout API"
    except Exception as e:
        return None, str(e)


def fetch_recos():
    if not API_URL:
        return None, "API_URL manquante"
    try:
        data = safe_get_json(build_url("/api/admin/recommendations"))
        recos = normalize_api_response(data, "recommendations")
        if recos is not None:
            return recos, None
        return None, extract_error_message(data)
    except requests.exceptions.Timeout:
        return None, "Timeout API"
    except Exception as e:
        return None, str(e)


def kpi_card(titre, valeur, icone, couleur):
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([html.Div(icone, style={"fontSize": "2rem"})], width=3),
                dbc.Col([
                    html.H3(str(valeur), className="mb-1 fw-bold", style={"color": couleur}),
                    html.P(titre, className="mb-0", style={"color": COLORS["muted"], "fontSize": "0.95rem"})
                ], width=9)
            ], align="center")
        ]),
        style=KPI_CARD_STYLE,
        className="h-100"
    )


def top_banner():
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H2("Bonjour Admin 👋", className="fw-bold mb-2", style={"color": "#26435f"}),
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
                        style={"borderRadius": "10px", "fontWeight": "600", "color": COLORS["primary"]}
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


def make_empty_figure(title, annotation="Aucune donnée"):
    fig = go.Figure()
    fig.add_annotation(
        text=annotation,
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 16, "color": COLORS["muted"]}
    )
    fig.update_layout(
        title=title,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color=COLORS["text"],
        height=320,
        xaxis={"visible": False},
        yaxis={"visible": False},
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def fig_pie_from_dict(data_dict, title):
    if not data_dict:
        return make_empty_figure(title)
    labels = list(data_dict.keys())
    values = list(data_dict.values())
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker=dict(colors=["#3f6df6", "#6ea8fe", "#9ec5fe", "#bfd7ff", "#dbeafe", "#eaf2ff"])
    )])
    fig.update_layout(
        title=title,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color=COLORS["text"],
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def fig_bar_vertical(data_dict, title, x_label, y_label):
    if not data_dict:
        return make_empty_figure(title)
    x_vals = list(data_dict.keys())
    y_vals = list(data_dict.values())
    fig = go.Figure(data=[go.Bar(
        x=x_vals,
        y=y_vals,
        marker_color="#3f6df6"
    )])
    fig.update_layout(
        title=title,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color=COLORS["text"],
        showlegend=False,
        xaxis_title=x_label,
        yaxis_title=y_label,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def fig_bar_horizontal(data_dict, title, x_label, y_label):
    if not data_dict:
        return make_empty_figure(title)
    x_vals = list(data_dict.values())
    y_vals = list(data_dict.keys())
    fig = go.Figure(data=[go.Bar(
        x=x_vals,
        y=y_vals,
        orientation="h",
        marker_color="#60a5fa"
    )])
    fig.update_layout(
        title=title,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color=COLORS["text"],
        showlegend=False,
        xaxis_title=x_label,
        yaxis_title=y_label,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def fig_gauge(score_moyen):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(score_moyen or 0),
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
    fig.update_layout(
        paper_bgcolor="white",
        font_color=COLORS["text"],
        height=260,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig


def dashboard_layout_shell():
    return html.Div([
        html.H4("📊 Tableau de bord", style=SECTION_TITLE_STYLE),
        html.Div(id="dashboard-alert"),
        html.Div(id="dashboard-kpis"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-domaine")), style=CARD_STYLE), md=5, className="mb-4"),
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-niveau")), style=CARD_STYLE), md=4, className="mb-4"),
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-gauge")), style=CARD_STYLE), md=3, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-pays")), style=CARD_STYLE), md=6, className="mb-4"),
        ])
    ])


def users_layout_shell():
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
        html.H4(id="users-title", children="👤 Utilisateurs", style=SECTION_TITLE_STYLE),
        html.Div(id="users-alert"),
        dbc.Card(
            dbc.CardBody([
                dash_table.DataTable(
                    id="users-table",
                    data=[],
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


def recos_layout_shell():
    colonnes = [
        {"name": "ID", "id": "id"},
        {"name": "User ID", "id": "user_id"},
        {"name": "Type", "id": "type_item"},
        {"name": "Item ID", "id": "item_id"},
        {"name": "Score (%)", "id": "score"},
        {"name": "Raison", "id": "raisons"},
    ]
    return html.Div([
        html.H4(id="recos-title", children="🤖 Recommendations", style=SECTION_TITLE_STYLE),
        html.Div(id="recos-alert"),
        dbc.Row([
            dbc.Col(html.Div(id="recos-formations-card"), md=3, className="mb-3"),
            dbc.Col(html.Div(id="recos-bourses-card"), md=3, className="mb-3"),
        ]),
        dbc.Card(
            dbc.CardBody([
                dash_table.DataTable(
                    id="recos-table",
                    data=[],
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
                            "if": {"filter_query": "{type_item} = 'formation'", "column_id": "type_item"},
                            "color": "#1f73d8",
                            "fontWeight": "bold"
                        },
                        {
                            "if": {"filter_query": "{type_item} = 'bourse'", "column_id": "type_item"},
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


def loading_shell():
    return dcc.Loading(
        type="default",
        children=html.Div(
            "Chargement des données...",
            style={
                "padding": "24px",
                "backgroundColor": "white",
                "border": f"1px solid {COLORS['border']}",
                "borderRadius": "16px",
                "color": COLORS["muted"]
            }
        )
    )


app.layout = html.Div([
    dcc.Store(id="current-page", data="dashboard"),
    dcc.Store(id="stats-store"),
    dcc.Store(id="users-store"),
    dcc.Store(id="recos-store"),
    dcc.Store(id="error-store"),
    dcc.Store(id="meta-store", data={"last_refresh": 0}),
    dcc.Interval(id="startup-trigger", interval=400, n_intervals=0, max_intervals=1),

    dbc.Navbar(
        dbc.Container([
            html.Div(
                "🎓 EduReco — Administration",
                style={"color": "white", "fontWeight": "700", "fontSize": "1.35rem"}
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
                    dbc.Button("📊 Tableau de bord", id="btn-dashboard", color="primary", n_clicks=0, style={"fontWeight": "600", "borderRadius": "10px"}),
                    dbc.Button("👤 Utilisateurs", id="btn-users", color="primary", outline=True, n_clicks=0, style={"fontWeight": "600", "borderRadius": "10px"}),
                    dbc.Button("🤖 Recommendations", id="btn-recos", color="primary", outline=True, n_clicks=0, style={"fontWeight": "600", "borderRadius": "10px"}),
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

        html.Div(id="admin-contenu", children=loading_shell())
    ], fluid=True)
], style=GLOBAL_STYLE)


@app.callback(
    Output("current-page", "data"),
    Input("btn-dashboard", "n_clicks"),
    Input("btn-users", "n_clicks"),
    Input("btn-recos", "n_clicks"),
    prevent_initial_call=True
)
def set_current_page(n_dashboard, n_users, n_recos):
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update
    bouton_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if bouton_id == "btn-users":
        return "users"
    if bouton_id == "btn-recos":
        return "recos"
    return "dashboard"


@app.callback(
    Output("admin-contenu", "children"),
    Input("current-page", "data"),
)
def render_page(page):
    if page == "users":
        return users_layout_shell()
    if page == "recos":
        return recos_layout_shell()
    return dashboard_layout_shell()


@app.callback(
    Output("stats-store", "data"),
    Output("users-store", "data"),
    Output("recos-store", "data"),
    Output("error-store", "data"),
    Output("meta-store", "data"),
    Input("startup-trigger", "n_intervals"),
    Input("btn-refresh", "n_clicks"),
    Input("btn-refresh-top", "n_clicks"),
    State("meta-store", "data"),
    prevent_initial_call=False
)
def load_all_data(n_startup, n_refresh, n_refresh_top, meta):
    now = int(time.time())
    meta = meta or {"last_refresh": 0}
    last_refresh = int(meta.get("last_refresh", 0))

    if now - last_refresh < CACHE_TTL_SECONDS and last_refresh != 0:
        return no_update, no_update, no_update, no_update, no_update

    stats, err_stats = fetch_stats()
    users, err_users = fetch_users()
    recos, err_recos = fetch_recos()

    errors = {
        "stats": err_stats,
        "users": err_users,
        "recos": err_recos
    }

    return stats, users, recos, errors, {"last_refresh": now}


@app.callback(
    Output("dashboard-alert", "children"),
    Output("dashboard-kpis", "children"),
    Output("fig-domaine", "figure"),
    Output("fig-niveau", "figure"),
    Output("fig-pays", "figure"),
    Output("fig-gauge", "figure"),
    Input("stats-store", "data"),
    Input("error-store", "data"),
)
def update_dashboard(stats, errors):
    err = (errors or {}).get("stats")
    if not stats:
        return (
            api_down_message(err or "Aucune donnée de statistiques."),
            html.Div(),
            make_empty_figure("Répartition par domaine"),
            make_empty_figure("Répartition par niveau d'études"),
            make_empty_figure("Répartition par pays"),
            fig_gauge(0),
        )

    kpis = dbc.Row([
        dbc.Col(kpi_card("Utilisateurs inscrits", pick(stats, "total_users", "total_utilisateurs", default=0), "👤", COLORS["primary"]), md=3, className="mb-3"),
        dbc.Col(kpi_card("Recommendations générées", pick(stats, "total_recos", "total_recommendations", default=0), "🤖", "#22a06b"), md=3, className="mb-3"),
        dbc.Col(kpi_card("Formations recommandées", pick(stats, "nb_formations_reco", "total_formations_recommandees", default=0), "🎓", "#1f9bd1"), md=3, className="mb-3"),
        dbc.Col(kpi_card("Bourses recommandées", pick(stats, "nb_bourses_reco", "total_bourses_recommandees", default=0), "💰", "#e0a100"), md=3, className="mb-3"),
    ], className="mb-2")

    return (
        html.Div(),
        kpis,
        fig_pie_from_dict(pick(stats, "par_domaine", "repartition_domaine", default={}), "Répartition par domaine"),
        fig_bar_vertical(pick(stats, "par_niveau", "repartition_niveau", default={}), "Répartition par niveau d'études", "Niveau", "Nb utilisateurs"),
        fig_bar_horizontal(pick(stats, "par_pays", "repartition_pays", default={}), "Répartition par pays", "Nb utilisateurs", "Pays"),
        fig_gauge(pick(stats, "score_moyen", "score_nlp_moyen", default=0)),
    )


@app.callback(
    Output("users-title", "children"),
    Output("users-alert", "children"),
    Output("users-table", "data"),
    Input("users-store", "data"),
    Input("error-store", "data"),
)
def update_users(users, errors):
    err = (errors or {}).get("users")
    if users is None:
        return "👤 Utilisateurs", api_down_message(err or "Aucune donnée utilisateur."), []
    return f"👤 Utilisateurs — {len(users)} inscrits", html.Div(), users


@app.callback(
    Output("recos-title", "children"),
    Output("recos-alert", "children"),
    Output("recos-formations-card", "children"),
    Output("recos-bourses-card", "children"),
    Output("recos-table", "data"),
    Input("recos-store", "data"),
    Input("error-store", "data"),
)
def update_recos(recos, errors):
    err = (errors or {}).get("recos")
    if recos is None:
        empty_card_1 = dbc.Card(dbc.CardBody([html.H5("0", className="fw-bold mb-1"), html.Div("🎓 Formations")]), style={**CARD_STYLE, "backgroundColor": "#f2f7ff"})
        empty_card_2 = dbc.Card(dbc.CardBody([html.H5("0", className="fw-bold mb-1"), html.Div("💰 Bourses")]), style={**CARD_STYLE, "backgroundColor": "#fffaf0"})
        return "🤖 Recommendations", api_down_message(err or "Aucune donnée de recommandations."), empty_card_1, empty_card_2, []

    nb_formations = sum(1 for r in recos if r.get("type_item") == "formation")
    nb_bourses = sum(1 for r in recos if r.get("type_item") == "bourse")

    formation_card = dbc.Card(
        dbc.CardBody([
            html.H5(str(nb_formations), className="fw-bold mb-1", style={"color": COLORS["primary"]}),
            html.Div("🎓 Formations", style={"color": COLORS["muted"]})
        ]),
        style={**CARD_STYLE, "backgroundColor": "#f2f7ff"}
    )
    bourse_card = dbc.Card(
        dbc.CardBody([
            html.H5(str(nb_bourses), className="fw-bold mb-1", style={"color": "#d4a017"}),
            html.Div("💰 Bourses", style={"color": COLORS["muted"]})
        ]),
        style={**CARD_STYLE, "backgroundColor": "#fffaf0"}
    )

    return f"🤖 Recommendations — {len(recos)} générées", html.Div(), formation_card, bourse_card, recos


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print("=" * 50)
    print(" EduReco — Admin Dashboard")
    print("=" * 50)
    print(f" API   → {API_URL or 'NON CONFIGURÉE'}")
    print(f" Admin → http://0.0.0.0:{port}")
    print("=" * 50)
    app.run(debug=False, host="0.0.0.0", port=port)
