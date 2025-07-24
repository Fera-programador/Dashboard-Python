import os
from datetime import datetime
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd

# ------------------------------------------------------------------
# 1. Configuração Inicial
# ------------------------------------------------------------------
df_full = px.data.gapminder()

# Tema escuro do Bootstrap + CSS personalizado
app = dash.Dash(
    __name__,
    title="Dashboard em Python",
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    meta_tags=[{
        'name': 'viewport',
        'content': 'width=device-width, initial-scale=1.0'
    }]
)
server = app.server

# ------------------------------------------------------------------
# 2. Layout - Design Escuro Moderno
# ------------------------------------------------------------------
app.layout = dbc.Container(fluid=True, style={
    "padding": "20px",
    "backgroundColor": "#0d1117",  # Preto azulado
    "color": "#e6edf3",
    "minHeight": "100vh",
    "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
}, children=[

    # Cabeçalho com ícone
    dbc.Row([
        dbc.Col(
            html.Div([
                html.Div([
                    html.I(className="fas fa-globe-americas fa-2x", 
                          style={"marginRight": "15px", "color": "#58a6ff"}),
                    html.H1("Gapminder Analytics", style={"marginBottom": "0"})
                ], style={"display": "flex", "alignItems": "center", "justifyContent": "center"}),
                html.P("Dados socioeconômicos mundiais (1952-2007)", 
                      style={"color": "#8b949e", "textAlign": "center"})
            ], style={
                "backgroundColor": "#161b22",
                "padding": "25px",
                "borderRadius": "10px",
                "borderLeft": "4px solid #58a6ff",
                "marginBottom": "30px",
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"
            }),
            width=12
        )
    ]),

    # Área de Controles
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filtros", style={
                    "backgroundColor": "#1a1f27",
                    "color": "#c9d1d9",
                    "fontWeight": "600",
                    "borderBottom": "1px solid #30363d"
                }),
                dbc.CardBody([
                    html.Label("Selecione o Ano:", style={"color": "#c9d1d9", "marginTop": "10px"}),
                    dcc.Slider(
                        id="year-slider",
                        min=df_full["year"].min(),
                        max=df_full["year"].max(),
                        step=5,
                        value=2007,
                        marks={str(y): {"label": str(y), "style": {"color": "#e6edf3"}} 
                               for y in df_full["year"].unique() if y % 10 == 0},
                        tooltip={"placement": "bottom", "always_visible": True},
                        updatemode='drag',
                        className="mb-4"
                    ),

                    dbc.Row([
                        dbc.Col([
                            html.Label("Continente:", style={"color": "#c9d1d9"}),
                            dcc.Dropdown(
                                id="continent-dropdown",
                                options=[{"label": "Todos", "value": "all"}] +
                                        [{"label": cont, "value": cont} for cont in df_full["continent"].unique()],
                                value="all",
                                clearable=False,
                                className="dropdown-dark",
                                style={"backgroundColor": "#161b22", "color": "#e6edf3"}
                            )
                        ], md=6),
                        
                        dbc.Col([
                            html.Label("Tamanho do Gráfico:", style={"color": "#c9d1d9"}),
                            dbc.RadioItems(
                                id="graph-size-radio",
                                options=[
                                    {"label": "Pequeno", "value": "small"},
                                    {"label": "Médio", "value": "medium"},
                                    {"label": "Grande", "value": "large"}
                                ],
                                value="medium",
                                inline=True,
                                className="btn-group",
                                inputClassName="btn-check",
                                labelClassName="btn btn-outline-primary",
                                labelCheckedClassName="active",
                            )
                        ], md=6)
                    ], className="mt-3"),

                    html.Div([
                        html.Label("Escala do Eixo X:", style={"color": "#c9d1d9", "marginRight": "10px"}),
                        dbc.Switch(
                            id="log-x-radio",
                            label="Logarítmica",
                            value=True,
                            style={"display": "inline-block"}
                        )
                    ], style={"marginTop": "15px"})
                ], style={"backgroundColor": "#0d1117"})
            ], className="mb-4", style={
                "border": "1px solid #30363d",
                "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.2)"
            })
        ], width=12)
    ]),

    # Linha 1 de Gráficos
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Expectativa de Vida vs. PIB per Capita", 
                              style={"backgroundColor": "#1a1f27", "color": "#c9d1d9"}),
                dbc.CardBody(dcc.Graph(id="scatter-plot"))
            ], style={
                "border": "1px solid #30363d",
                "height": "100%"
            }),
            md=6, xs=12, className="mb-4"
        ),
        
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Top 10 Países por PIB per Capita", 
                              style={"backgroundColor": "#1a1f27", "color": "#c9d1d9"}),
                dbc.CardBody(dcc.Graph(id="bar-chart"))
            ], style={
                "border": "1px solid #30363d",
                "height": "100%"
            }),
            md=6, xs=12, className="mb-4"
        )
    ]),

    # Linha 2 de Gráficos
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Evolução da Expectativa de Vida", 
                              style={"backgroundColor": "#1a1f27", "color": "#c9d1d9"}),
                dbc.CardBody(dcc.Graph(id="line-chart"))
            ], style={
                "border": "1px solid #30363d",
                "height": "100%"
            }),
            md=6, xs=12, className="mb-4"
        ),
        
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Distribuição Populacional", 
                              style={"backgroundColor": "#1a1f27", "color": "#c9d1d9"}),
                dbc.CardBody(dcc.Graph(id="pie-chart"))
            ], style={
                "border": "1px solid #30363d",
                "height": "100%"
            }),
            md=6, xs=12, className="mb-4"
        )
    ]),

    # Rodapé
    dbc.Row([
        dbc.Col(
            html.Div([
                html.P([
                    f"Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    html.Br(),
                    "© 2023 Gapminder Dashboard | ",
                    html.A("Código Fonte", 
                          href="https://github.com/Fera-programador/Dashboard-Python",
                          style={"color": "#58a6ff"})
                ], style={
                    "fontSize": "12px", 
                    "color": "#8b949e", 
                    "textAlign": "center",
                    "padding": "15px"
                })
            ], style={
                "backgroundColor": "#161b22",
                "borderRadius": "5px",
                "marginTop": "20px"
            }),
            width=12
        )
    ])
])

# ------------------------------------------------------------------
# 3. Callbacks - Interatividade
# ------------------------------------------------------------------
@callback(
    Output("scatter-plot", "figure"),
    Output("bar-chart", "figure"),
    Output("line-chart", "figure"),
    Output("pie-chart", "figure"),
    Input("year-slider", "value"),
    Input("continent-dropdown", "value"),
    Input("graph-size-radio", "value"),
    Input("log-x-radio", "value")
)
def update_graphs(selected_year, selected_continent, graph_size, log_x):
    # Filtro dos dados
    filtered_df = df_full[df_full["year"] == selected_year]
    if selected_continent != "all":
        filtered_df = filtered_df[filtered_df["continent"] == selected_continent]
    
    # Tamanho dos gráficos
    size_map = {"small": 400, "medium": 500, "large": 650}
    graph_height = size_map[graph_size]
    
    # Configuração de tema escuro personalizado
    dark_template = {
        'layout': {
            'paper_bgcolor': '#0d1117',
            'plot_bgcolor': '#0d1117',
            'font': {'color': '#e6edf3'},
            'xaxis': {
                'gridcolor': '#30363d',
                'linecolor': '#30363d',
                'zerolinecolor': '#30363d'
            },
            'yaxis': {
                'gridcolor': '#30363d',
                'linecolor': '#30363d',
                'zerolinecolor': '#30363d'
            },
            'hoverlabel': {
                'bgcolor': '#161b22',
                'font': {'color': '#e6edf3'}
            },
            'colorway': ['#58a6ff', '#f78166', '#56d364', '#d2a8ff', '#79c0ff']
        }
    }

    # 1. Scatter Plot
    scatter_fig = px.scatter(
        filtered_df,
        x="gdpPercap", y="lifeExp",
        size="pop", color="continent",
        hover_name="country",
        log_x=log_x,
        title=f"{selected_year}",
        labels={
            "gdpPercap": "PIB per Capita (USD)",
            "lifeExp": "Expectativa de Vida (anos)",
            "continent": "Continente"
        },
        height=graph_height,
        template=dark_template
    )
    scatter_fig.update_layout(
        margin={"t": 30, "b": 40},
        hovermode="closest",
        legend_title_text=None
    )

    # 2. Bar Chart
    bar_fig = px.bar(
        filtered_df.nlargest(10, "gdpPercap"),
        x="country", y="gdpPercap", color="continent",
        title=f"{selected_year}",
        labels={
            "gdpPercap": "PIB per Capita (USD)",
            "country": "País",
            "continent": "Continente"
        },
        height=graph_height,
        template=dark_template
    )
    bar_fig.update_layout(
        margin={"t": 30, "b": 40},
        xaxis_tickangle=-45,
        legend_title_text=None
    )

    # 3. Line Chart
    if selected_continent == "all":
        line_df = df_full.groupby(["year", "continent"]).agg({"lifeExp": "mean"}).reset_index()
        line_fig = px.line(
            line_df, x="year", y="lifeExp", color="continent",
            title="Evolução Temporal",
            labels={
                "year": "Ano",
                "lifeExp": "Expectativa de Vida (anos)",
                "continent": "Continente"
            },
            height=graph_height,
            template=dark_template
        )
    else:
        line_df = df_full[df_full["continent"] == selected_continent]
        line_df = line_df.groupby("year").agg({"lifeExp": "mean"}).reset_index()
        line_fig = px.line(
            line_df, x="year", y="lifeExp",
            title=f"Evolução na {selected_continent}",
            labels={
                "year": "Ano",
                "lifeExp": "Expectativa de Vida (anos)"
            },
            height=graph_height,
            template=dark_template
        )
    line_fig.update_layout(
        margin={"t": 30, "b": 40},
        legend_title_text=None
    )

    # 4. Pie Chart
    if selected_continent == "all":
        pie_df = filtered_df.groupby("continent").agg({"pop": "sum"}).reset_index()
        pie_fig = px.pie(
            pie_df, names="continent", values="pop",
            title="Distribuição por Continente",
            height=graph_height,
            template=dark_template,
            hole=0.4
        )
    else:
        pie_df = filtered_df.nlargest(10, "pop")
        pie_fig = px.pie(
            pie_df, names="country", values="pop",
            title=f"Top 10 na {selected_continent}",
            height=graph_height,
            template=dark_template,
            hole=0.4
        )
    pie_fig.update_layout(
        margin={"t": 30, "b": 40},
        legend_title_text=None,
        showlegend=False
    )
    pie_fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#0d1117', width=1))
    )

    return scatter_fig, bar_fig, line_fig, pie_fig


# ------------------------------------------------------------------
# 4. Execução
# ------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))     # Railway usa a variável PORT
    app.run(host="0.0.0.0", port=port, debug=False)