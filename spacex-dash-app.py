import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

app = dash.Dash(__name__)
server = app.server

uniquelaunchsites = spacex_df['Launch Site'].unique().tolist()
lsites = [{'label': 'All Sites', 'value': 'All Sites'}]
for site in uniquelaunchsites:
    lsites.append({'label': site, 'value': site})

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    dcc.Dropdown(
        id='site_dropdown',
        options=lsites,
        placeholder='Select a Launch Site here',
        searchable=True,
        value='All Sites'
    ),
    html.Br(),

    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    dcc.RangeSlider(
        id='payload_slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i} kg' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site_dropdown', 'value')
)
def update_pie(site):
    if site == 'All Sites':
        df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(df, names='Launch Site', hole=.3,
                     title='Total Successful Launches by All Sites')
    else:
        df = spacex_df[spacex_df['Launch Site'] == site]
        fig = px.pie(df, names='class', hole=.3,
                     title=f'Success vs Failure for {site}')
    return fig

@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site_dropdown', 'value'),
     Input('payload_slider', 'value')]
)
def update_scatter(site, payload):
    low, high = payload
    df = spacex_df
    if site != 'All Sites':
        df = df[df['Launch Site'] == site]

    df = df[(df['Payload Mass (kg)'] >= low) & (df['Payload Mass (kg)'] <= high)]

    fig = px.scatter(df, 
                     x="Payload Mass (kg)", y="class",
                     color="Booster Version",
                     size="Payload Mass (kg)",
                     hover_data=['Payload Mass (kg)'],
                     title='Payload vs Launch Outcome')
    return fig

if __name__ == '__main__':
    app.run(debug=False)
