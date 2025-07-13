import os
from datetime import datetime
from dotenv import load_dotenv
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd   # já vem com Dash, mas mantido aqui por clareza

# ------------------------------------------------------------------
# 1. Configuração inicial
# ------------------------------------------------------------------
load_dotenv()                               # carrega .env se houver
df_full = px.data.gapminder()               # base completa (1952-2007)

# Escolhi o tema BOOTSTRAP MINTY.  Troque por outro se preferir:
external_stylesheets = [dbc.themes.MINTY]

app = dash.Dash(__name__,
                title="Dashboard em Python",
                external_stylesheets=external_stylesheets)

# ------------------------------------------------------------------
# 2. Layout – 100 % responsivo usando o grid do Bootstrap
# ------------------------------------------------------------------
app.layout = dbc.Container(fluid=True, style={"padding": "20px"}, children=[

    # Cabeçalho
    dbc.Row([
        dbc.Col(
            html.Div([
                html.H1("Dashboard Gapminder – Análise Global"),
                html.P("Visualização interativa de dados socioeconômicos mundiais (1952-2007)")
            ], style={
                "backgroundColor": "#f8f9fa",
                "padding": "20px",
                "borderRadius": "5px",
                "textAlign": "center"
            }),
            width=12
        )
    ]),

    # Área de controles / filtros
    dbc.Row([
        dbc.Col([
            html.Label("Selecione o Ano:"),
            dcc.Slider(
                id="year-slider",
                min=df_full["year"].min(),
                max=df_full["year"].max(),
                step=5,
                value=2007,
                marks={str(y): str(y) for y in df_full["year"].unique() if y % 10 == 0},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            html.Br(),

            html.Label("Selecione o Continente:"),
            dcc.Dropdown(
                id="continent-dropdown",
                options=[{"label": "Todos", "value": "all"}] +
                        [{"label": cont, "value": cont} for cont in df_full["continent"].unique()],
                value="all",
                clearable=False
            ),
            html.Br(),

            html.Label("Tamanho do Gráfico:"),
            dcc.RadioItems(
                id="graph-size-radio",
                options=[
                    {"label": "Pequeno", "value": "small"},
                    {"label": "Médio",   "value": "medium"},
                    {"label": "Grande",  "value": "large"}
                ],
                value="medium",
                inline=True
            ),
            html.Br(),

            html.Label("Escala do Eixo X:"),
            dcc.RadioItems(
                id="log-x-radio",
                options=[
                    {"label": "Linear",       "value": False},
                    {"label": "Logarítmica",  "value": True}
                ],
                value=True,
                inline=True
            ),
        ], width=12, style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "borderRadius": "5px",
            "marginBottom": "20px"
        })
    ]),

    # Linha 1 de gráficos (Scatter + Bar)
    dbc.Row([
        dbc.Col(dcc.Graph(id="scatter-plot"), md=6, xs=12, style={"marginBottom": "20px"}),
        dbc.Col(dcc.Graph(id="bar-chart"),    md=6, xs=12, style={"marginBottom": "20px"})
    ]),

    # Linha 2 de gráficos (Line + Pie)
    dbc.Row([
        dbc.Col(dcc.Graph(id="line-chart"), md=6, xs=12, style={"marginBottom": "20px"}),
        dbc.Col(dcc.Graph(id="pie-chart"),  md=6, xs=12, style={"marginBottom": "20px"})
    ]),

    # Rodapé
    dbc.Row([
        dbc.Col(
            html.P(
                f"Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                style={"fontSize": "12px", "color": "#6c757d", "textAlign": "right"}
            ), width=12
        )
    ])
])

# ------------------------------------------------------------------
# 3. Callbacks – interatividade
# ------------------------------------------------------------------
@callback(
    Output("scatter-plot", "figure"),
    Output("bar-chart",    "figure"),
    Output("line-chart",   "figure"),
    Output("pie-chart",    "figure"),
    Input("year-slider",       "value"),
    Input("continent-dropdown","value"),
    Input("graph-size-radio",  "value"),
    Input("log-x-radio",       "value")
)
def update_graphs(selected_year: int,
                  selected_continent: str,
                  graph_size: str,
                  log_x: bool):

    # ---- Filtro básico
    filtered_df = df_full[df_full["year"] == selected_year]
    if selected_continent != "all":
        filtered_df = filtered_df[filtered_df["continent"] == selected_continent]

    # ---- Dimensão dos gráficos
    size_map = {"small": 400, "medium": 600, "large": 800}
    graph_height = size_map[graph_size]

    # 1. Scatter – Expectativa de Vida vs. PIB per capita
    scatter_fig = px.scatter(
        filtered_df,
        x="gdpPercap", y="lifeExp",
        size="pop", color="continent",
        hover_name="country",
        log_x=log_x,
        title=f"Expectativa de Vida vs. PIB per Capita ({selected_year})",
        labels={"gdpPercap": "PIB per Capita", "lifeExp": "Expectativa de Vida"},
        height=graph_height
    )
    scatter_fig.update_layout(transition_duration=500)

    # 2. Barras – Top 10 por PIB per capita
    bar_fig = px.bar(
        filtered_df.nlargest(10, "gdpPercap"),
        x="country", y="gdpPercap", color="continent",
        title=f"Top 10 Países por PIB per Capita ({selected_year})",
        labels={"gdpPercap": "PIB per Capita", "country": "País"},
        height=graph_height
    )

    # 3. Linha – Evolução da expectativa de vida
    if selected_continent == "all":
        line_df = (df_full
                   .groupby(["year", "continent"])
                   .agg({"lifeExp": "mean"})
                   .reset_index())
        line_fig = px.line(
            line_df, x="year", y="lifeExp", color="continent",
            title="Evolução da Expectativa de Vida por Continente",
            labels={"year": "Ano", "lifeExp": "Expectativa de Vida"},
            height=graph_height
        )
    else:
        line_df = (df_full[df_full["continent"] == selected_continent]
                   .groupby("year")
                   .agg({"lifeExp": "mean"})
                   .reset_index())
        line_fig = px.line(
            line_df, x="year", y="lifeExp",
            title=f"Evolução da Expectativa de Vida na {selected_continent}",
            labels={"year": "Ano", "lifeExp": "Expectativa de Vida"},
            height=graph_height
        )

    # 4. Pizza – Distribuição populacional
    if selected_continent == "all":
        pie_df = (filtered_df
                  .groupby("continent")
                  .agg({"pop": "sum"})
                  .reset_index())
        pie_fig = px.pie(
            pie_df, names="continent", values="pop",
            title=f"Distribuição Populacional por Continente ({selected_year})",
            height=graph_height
        )
    else:
        pie_df = filtered_df.nlargest(10, "pop")
        pie_fig = px.pie(
            pie_df, names="country", values="pop",
            title=f"Top 10 Países mais Populosos – {selected_continent} ({selected_year})",
            height=graph_height
        )

    return scatter_fig, bar_fig, line_fig, pie_fig

# ------------------------------------------------------------------
# 4. Execução
# ------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))     # Railway usa a variável PORT
    app.run(host="0.0.0.0", port=port, debug=False)