import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import folium
from folium.plugins import HeatMap

# Load data
df4 = pd.read_csv('WIND.1.csv')
DF = pd.read_csv('Energy.csv')
df_e_s = pd.read_csv("Energy_Source_2021.csv")
df_e_s = df_e_s.groupby(['State','Source'],as_index=False)[['Consumption']].sum()

# Create Plotly density map
figure = px.density_mapbox(df4, lat='Lat', lon='Lon', z='WindSpeed', radius=20,
                           center=dict(lat=df4['Lat'].mean(), lon=df4['Lon'].mean()), zoom=4,
                           mapbox_style='open-street-map', height=900)

barchart = px.bar(
data_frame=df_e_s,
x="State",
y="Consumption",
color="Source",
opacity=0.9,
orientation="v",
color_continuous_scale=px.colors.diverging.Picnic,
barmode='overlay',
title='Energy Consumption',
)

df_top = pd.read_csv("top.csv")
dfg = df_top.groupby(['State','Consumption']).size().to_frame().sort_values([0], ascending = True).head(10).reset_index()

top10 = px.histogram(dfg, y='State', x='Consumption')
top10.layout.yaxis.title.text = 'Energy Consumption'

# Pie Chart Source Distribution
df_pie = pd.read_csv("ECS.csv")

pie = px.pie(df_pie, names='Source', values='Consumption Billions BTU', hole=0.5)
pie.update_traces(textinfo='percent + value')
pie.update_layout(title_text='Energy Consumption by Source - 2021', title_x=0.5)

df6 = pd.read_csv("Line.csv")

line = px.line(df6, x='Year', y=' MBTU',markers=True,template='plotly_dark')
line.update_layout(title_text='Renewable Energy Consumption Evolution', title_x=0.5)

# Create Folium HeatMap
def hMap():
    m = folium.Map(location=[df4['Lat'].mean(), df4['Lon'].mean()], zoom_start=5, control_scale=True)
    map_values = df4[['Lat', 'Lon', 'WindSpeed']]
    data = map_values.values.tolist()
    hm = HeatMap(data, min_opacity=0.01, max_opacity=0.9, radius=50).add_to(m)
    return m

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define app layout
app.layout = dbc.Container([
dbc.Row([
dbc.Col([
html.H1("Wind Energy Analisys", style={'textAlign': 'center'})
], width=12)
]),

dbc.Row([
dbc.Col([
dcc.Graph(id='Energy Consumption', figure=barchart)
], width=6),
dbc.Col([
dcc.Graph(id='Top10', figure=top10)
], width=6)
]),

dbc.Row([
dbc.Col([
dcc.Graph(id='Energy Consumption2', figure=pie)
], width=6),
dbc.Col([
dcc.Graph(id='Energy Consumption3', figure=line)
], width=6),
]),
dcc.Graph(id='density-map', figure=figure),
    dcc.Graph(id='bar-graph'),
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Option 1', 'value': 'option1'},
            {'label': 'Option 2', 'value': 'option2'}
        ],
        value='option1' 
    )
])

@app.callback(
    Output('bar-graph', 'figure'),
    [Input('dropdown', 'value')]
)
def update_graph(selected_value):
    fig = px.bar(DF, x='Consumption per Capita, Million Btu', y='State', title='State Energy Consumption')
    return fig

if __name__ == '__main__':
    app.run_server()