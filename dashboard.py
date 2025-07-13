import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
from datetime import datetime

# Carrega todos os dados do gapminder (não apenas 2007)
df_full = px.data.gapminder()

# Inicializar app
app = dash.Dash(__name__, title='Dashboard em Python')

# Estilos CSS
styles = {
    'container': {
        'margin': '20px',
        'fontFamily': 'Arial, sans-serif'
    },
    'header': {
        'backgroundColor': '#f8f9fa',
        'padding': '20px',
        'borderRadius': '5px',
        'marginBottom': '20px',
        'textAlign': 'center'
    },
    'controls': {
        'backgroundColor': '#e9ecef',
        'padding': '15px',
        'borderRadius': '5px',
        'marginBottom': '20px'
    },
    'graph-container': {
        'display': 'flex',
        'flexDirection': 'row',
        'flexWrap': 'wrap',
        'justifyContent': 'space-between'
    },
    'graph-box': {
        'width': '48%',
        'marginBottom': '20px',
        'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
        'borderRadius': '5px',
        'padding': '10px'
    }
}

# Layout do Dashboard
app.layout = html.Div(style=styles['container'], children=[
    html.Div(style=styles['header'], children=[
        html.H1("Dashboard Gapminder - Análise Global"),
        html.P("Visualização interativa de dados socioeconômicos mundiais (1952-2007)")
    ]),
    
    html.Div(style=styles['controls'], children=[
        html.Div([
            html.Label("Selecione o Ano:", style={'marginRight': '10px'}),
            dcc.Slider(
                id='year-slider',
                min=df_full['year'].min(),
                max=df_full['year'].max(),
                step=5,
                value=2007,
                marks={str(year): str(year) for year in df_full['year'].unique() if year % 10 == 0},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'marginBottom': '15px'}),
        
        html.Div([
            html.Label("Selecione o Continente:", style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='continent-dropdown',
                options=[{'label': 'Todos', 'value': 'all'}] + 
                        [{'label': cont, 'value': cont} for cont in df_full['continent'].unique()],
                value='all',
                clearable=False,
                style={'width': '50%'}
            )
        ], style={'marginBottom': '15px'}),
        
        html.Div([
            html.Label("Tamanho do Gráfico:", style={'marginRight': '10px'}),
            dcc.RadioItems(
                id='graph-size-radio',
                options=[
                    {'label': 'Pequeno', 'value': 'small'},
                    {'label': 'Médio', 'value': 'medium'},
                    {'label': 'Grande', 'value': 'large'}
                ],
                value='medium',
                inline=True,
                style={'marginRight': '20px'}
            ),
            
            html.Label("Escala do Eixo X:", style={'marginRight': '10px'}),
            dcc.RadioItems(
                id='log-x-radio',
                options=[
                    {'label': 'Linear', 'value': False},
                    {'label': 'Logarítmica', 'value': True}
                ],
                value=True,
                inline=True
            )
        ])
    ]),
    
    html.Div(style=styles['graph-container'], children=[
        html.Div(style=styles['graph-box'], children=[
            dcc.Graph(id='scatter-plot')
        ]),
        
        html.Div(style=styles['graph-box'], children=[
            dcc.Graph(id='bar-chart')
        ]),
        
        html.Div(style=styles['graph-box'], children=[
            dcc.Graph(id='line-chart')
        ]),
        
        html.Div(style=styles['graph-box'], children=[
            dcc.Graph(id='pie-chart')
        ])
    ]),
    
    html.Div([
        html.P(f"Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
              style={'fontSize': '12px', 'color': '#6c757d', 'textAlign': 'right'})
    ])
])

# Callbacks para interatividade
@callback(
    [Output('scatter-plot', 'figure'),
     Output('bar-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output('pie-chart', 'figure')],
    [Input('year-slider', 'value'),
     Input('continent-dropdown', 'value'),
     Input('graph-size-radio', 'value'),
     Input('log-x-radio', 'value')]
)
def update_graphs(selected_year, selected_continent, graph_size, log_x):
    # Filtra os dados baseado nos inputs
    filtered_df = df_full[df_full['year'] == selected_year]
    
    if selected_continent != 'all':
        filtered_df = filtered_df[filtered_df['continent'] == selected_continent]
    
    # Define o tamanho do gráfico baseado na seleção
    size_map = {'small': 400, 'medium': 600, 'large': 800}
    graph_height = size_map[graph_size]
    
    # 1. Gráfico de Dispersão
    scatter_fig = px.scatter(
        filtered_df, 
        x="gdpPercap", 
        y="lifeExp", 
        size="pop",
        color="continent",
        hover_name="country",
        log_x=log_x,
        title=f"Expectativa de Vida vs. PIB per Capita ({selected_year})",
        labels={"gdpPercap": "PIB per Capita", "lifeExp": "Expectativa de Vida"},
        height=graph_height
    )
    scatter_fig.update_layout(transition_duration=500)
    
    # 2. Gráfico de Barras (Top 10 países por PIB per capita)
    top_countries = filtered_df.nlargest(10, 'gdpPercap')
    bar_fig = px.bar(
        top_countries,
        x='country',
        y='gdpPercap',
        color='continent',
        title=f"Top 10 Países por PIB per Capita ({selected_year})",
        labels={"gdpPercap": "PIB per Capita", "country": "País"},
        height=graph_height
    )
    
    # 3. Gráfico de Linha (Evolução temporal para o continente selecionado)
    if selected_continent == 'all':
        line_df = df_full.groupby(['year', 'continent']).agg({'lifeExp': 'mean'}).reset_index()
    else:
        line_df = df_full[df_full['continent'] == selected_continent].groupby('year').agg({'lifeExp': 'mean'}).reset_index()
    
    line_fig = px.line(
        line_df,
        x='year',
        y='lifeExp',
        color='continent' if selected_continent == 'all' else None,
        title=f"Evolução da Expectativa de Vida {'por Continente' if selected_continent == 'all' else 'no ' + selected_continent}",
        labels={"year": "Ano", "lifeExp": "Expectativa de Vida"},
        height=graph_height
    )
    
    # 4. Gráfico de Pizza (Distribuição populacional por continente)
    if selected_continent == 'all':
        pie_df = filtered_df.groupby('continent').agg({'pop': 'sum'}).reset_index()
        pie_fig = px.pie(
            pie_df,
            names='continent',
            values='pop',
            title=f"Distribuição Populacional por Continente ({selected_year})",
            height=graph_height
        )
    else:
        pie_df = filtered_df.nlargest(10, 'pop')
        pie_fig = px.pie(
            pie_df,
            names='country',
            values='pop',
            title=f"Top 10 Países mais Populosos na {selected_continent} ({selected_year})",
            height=graph_height
        )
    
    return scatter_fig, bar_fig, line_fig, pie_fig

# Rodar servidor local
if __name__ == '__main__':
    app.run(debug=True)