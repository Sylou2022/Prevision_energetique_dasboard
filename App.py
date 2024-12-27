from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import numpy as np

# Initialisation de l'application Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Tableau de Bord Énergétique"
server = app.server

# Données synthétiques (inchangées)
regions = ["Île-de-France", "PACA", "Occitanie", "Auvergne-Rhône-Alpes", "Nouvelle-Aquitaine"]
coordinates = {
    "Île-de-France": [48.8566, 2.3522],
    "PACA": [43.9352, 6.0679],
    "Occitanie": [43.7000, 1.6163],
    "Auvergne-Rhône-Alpes": [45.7640, 4.8357],
    "Nouvelle-Aquitaine": [44.8378, -0.5792]
}
consumption_by_region = [500, 300, 250, 400, 320]

sectors = ["Industrie", "Transport", "Ménages", "Agriculture", "Services"]
sector_consumption = [300, 200, 400, 50, 150]

# Données temporelles
dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
real_consumption = np.random.randint(400, 600, size=len(dates))
forecast_consumption = real_consumption + np.random.randint(-50, 50, size=len(dates))

# Layout de la page d'accueil (inchangé)
homepage_layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Tableau de Bord Énergétique", className="text-center", style={"color": "#003366", "font-weight": "bold"}),
            html.P("Avec analyses et prévisions", className="text-center", style={"color": "#555555", "font-size": "18px"})
        ], style={"padding": "20px", "background-color": "#EAF2F8"}),

        html.Div([
            html.Div([
                html.Img(src="/assets/energie.jpg", style={"width": "300px", "margin": "auto", "display": "block"}),
                html.H2("Suivez la consommation énergétique", className="text-center", style={"color": "#003366"}),
                html.P("Explorez les données régionales, les prévisions et les indicateurs clés de manière interactive.",
                       className="text-center", style={"color": "#333333"}),
            ], style={"margin-bottom": "30px"}),

            html.Div([
                dbc.Button("Accéder au Tableau de Bord", id="dashboard-button", color="primary", 
                          style={'width': '100%'}, n_clicks=0)
            ], style={"text-align": "center", "margin": "20px auto", "max-width": "300px"})
        ], style={"padding": "40px"})
    ], style={"background-color": "#F8F9F9", "min-height": "100vh"})
])

# Layout modifié du dashboard avec nouvelles tailles
dashboard_layout = html.Div([
    html.Div([
        dbc.Button("Retour à l'Accueil", id="back-home", color="secondary", href="/", 
                  style={"font-size": "18px"})
    ], style={"margin": "20px"}),

    dbc.Container([
        # Contrôles de date et KPIs
        dbc.Row([
            dbc.Col([
                html.Div([
                    # Ajout d'un sélecteur de période
                    dbc.Select(
                        id="period-selector",
                        options=[
                            {"label": "Dernier mois", "value": "1M"},
                            {"label": "Derniers 3 mois", "value": "3M"},
                            {"label": "Derniers 6 mois", "value": "6M"},
                            {"label": "Dernière année", "value": "1Y"},
                            {"label": "Personnalisé", "value": "custom"}
                        ],
                        value="1M",
                        style={"width": "200px", "margin-right": "20px"}
                    ),
                    # Le DatePickerRange ne sera visible que si "Personnalisé" est sélectionné
                    html.Div([
                        dcc.DatePickerRange(
                            id="date-picker",
                            display_format="YYYY-MM-DD",
                            style={"display": "none"}
                        ),
                    ], id="custom-date-container"),
                    html.Div(id="date-validation", style={"color": "red", "margin": "10px 0"}),
                ], style={"display": "flex", "align-items": "center", "margin-bottom": "20px"})
            ], width=12)
        ]),

        # KPIs
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div(id="selected-dates"),
                    html.Div(id="kpi-cost"),
                    html.Div(id="kpi-co2"),
                    html.Div(id="kpi-alerts")
                ], style={"text-align": "center", "margin-bottom": "20px"})
            ])
        ]),

        # Graphiques principaux
        dbc.Row([
            # Première ligne : carte (plus petite) et graphique ARIMA (plus grand)
            dbc.Col(dcc.Graph(id="regional-consumption-map"), width=3),
            dbc.Col(dcc.Graph(id="arima-forecast-graph"), width=9),
        ], style={"margin-bottom": "20px"}),

        # Deuxième ligne : graphique en barres (plus petit) et comparaison (plus grand)
        dbc.Row([
            dbc.Col(dcc.Graph(id="sector-bar-chart"), width=3),
            dbc.Col(dcc.Graph(id="comparison-graph"), width=9),
        ])
    ], fluid=True)
], style={"background-color": "#FFFFFF", "min-height": "100vh"})

# Layout initial
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

# Callbacks de navigation (inchangés)
@app.callback(
    Output("url", "pathname"),
    [Input("dashboard-button", "n_clicks")]
)
def go_to_dashboard(n_clicks):
    if n_clicks:
        return "/dashboard"
    return "/"

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/dashboard":
        return dashboard_layout
    return homepage_layout

# Nouveau callback pour gérer l'affichage du sélecteur de dates personnalisé
@app.callback(
    Output("custom-date-container", "style"),
    Input("period-selector", "value")
)
def toggle_date_picker(selected_period):
    if selected_period == "custom":
        return {"display": "block"}
    return {"display": "none"}

# Callback pour calculer les dates en fonction de la période sélectionnée
@app.callback(
    [Output("date-picker", "start_date"),
     Output("date-picker", "end_date")],
    Input("period-selector", "value")
)
def update_date_range(selected_period):
    end_date = pd.Timestamp.now()
    
    if selected_period == "1M":
        start_date = end_date - pd.Timedelta(days=30)
    elif selected_period == "3M":
        start_date = end_date - pd.Timedelta(days=90)
    elif selected_period == "6M":
        start_date = end_date - pd.Timedelta(days=180)
    elif selected_period == "1Y":
        start_date = end_date - pd.Timedelta(days=365)
    else:  # custom
        return dates.min(), dates.max()
    
    return start_date, end_date

# Callback principal modifié pour prendre en compte la période sélectionnée
@app.callback(
    [Output("date-validation", "children"),
     Output("kpi-cost", "children"),
     Output("kpi-co2", "children"),
     Output("kpi-alerts", "children"),
     Output("selected-dates", "children"),
     Output("sector-bar-chart", "figure"),
     Output("regional-consumption-map", "figure"),
     Output("comparison-graph", "figure"),
     Output("arima-forecast-graph", "figure")],
    [Input("period-selector", "value"),
     Input("date-picker", "start_date"),
     Input("date-picker", "end_date")]
)
def update_dashboard(selected_period, start_date, end_date):
    # Validation de la période
    if start_date is None or end_date is None:
        return ["Veuillez sélectionner une période valide"] + [None] * 8

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # Filtrage des données selon la période sélectionnée
    selected_dates = (dates >= start) & (dates <= end)
    selected_real_consumption = real_consumption[selected_dates]
    selected_forecast_consumption = forecast_consumption[selected_dates]

    # Période d'analyse
    period_text = f"Période d'analyse: {start.strftime('%Y-%m-%d')} à {end.strftime('%Y-%m-%d')}"

    # Calcul des KPI
    total_cost = f"Coût Total: {selected_real_consumption.sum() * 0.15:,.2f} €"
    total_co2 = f"Émissions de CO₂: {selected_real_consumption.sum() * 0.0001:,.2f} t"

    # Détection des alertes
    next_10_days = pd.date_range(start=end, periods=10, freq="D")
    arima_forecast = np.random.randint(450, 550, size=len(next_10_days))
    alerts = sum(1 for val in arima_forecast if val > 520)
    total_alerts = f"Alertes: {alerts}"

    # Graphiques avec tailles ajustées
    # Graphique des secteurs (plus petit)
    sector_fig = px.bar(
        x=sectors,
        y=sector_consumption,
        labels={"x": "Secteur", "y": "Consommation (MWh)"},
        title=f"Consommation par Secteur\n{period_text}",
        template="plotly_dark",
        color_discrete_sequence=["#FFA15A"]
    )
    sector_fig.update_layout(
        height=300,  # Hauteur réduite
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="#003366"
    )

    # Carte (plus petite)
    regional_fig = px.scatter_mapbox(
        lat=[coordinates[region][0] for region in regions],
        lon=[coordinates[region][1] for region in regions],
        size=consumption_by_region,
        color=consumption_by_region,
        size_max=30,  # Taille réduite des marqueurs
        zoom=4.5,
        mapbox_style="carto-positron",
        title=f"Consommation Régionale\n{period_text}"
    )
    regional_fig.update_layout(
        height=300,  # Hauteur réduite
        margin={"r": 0, "t": 30, "l": 0, "b": 0}
    )

    # Graphique de comparaison (plus grand)
    comparison_df = pd.DataFrame({
        "Date": dates[selected_dates],
        "Consommation Réelle": selected_real_consumption,
        "Prévisions": selected_forecast_consumption
    })
    comparison_fig = px.line(
        comparison_df,
        x="Date",
        y=["Consommation Réelle", "Prévisions"],
        labels={"value": "Consommation (MWh)", "variable": "Type"},
        title=f"Comparaison : Réel vs Prévisions\n{period_text}",
        template="plotly_dark"
    )
    comparison_fig.update_layout(
        height=400,  # Hauteur augmentée
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="#003366"
    )

    # Graphique ARIMA (plus grand)
    arima_fig = px.line(
        x=next_10_days,
        y=arima_forecast,
        labels={"x": "Date", "y": "Consommation (MWh)"},
        title=f"Prévisions ARIMA\n{period_text}",
        template="plotly_dark"
    )
    arima_fig.update_traces(marker=dict(color="red"))
    arima_fig.update_layout(
        height=400,  # Hauteur augmentée
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="#003366"
    )

    return ["", total_cost, total_co2, total_alerts, period_text,
            sector_fig, regional_fig, comparison_fig, arima_fig]

if __name__ == "__main__":
    app.run_server(debug=True)