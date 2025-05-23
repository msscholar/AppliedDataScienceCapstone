import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize app
app = dash.Dash(__name__)
server = app.server

# Generate dropdown options
site_options = [{'label': 'All Sites', 'value': 'All Sites'}] + \
               [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),

    dcc.Dropdown(id='site_dropdown',
                 options=site_options,
                 placeholder='Select a Launch Site here',
                 searchable=True,
                 value='All Sites'),

    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    dcc.RangeSlider(id='payload_slider',
                    min=0,
                    max=10000,
                    step=1000,
                    marks={i: f'{i} kg' for i in range(0, 10001, 1000)},
                    value=[min_payload, max_payload]),

    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Pie chart callback
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site_dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'All Sites':
        df_filtered = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(df_filtered, names='Launch Site', hole=.3,
                     title='Total Success Launches by All Sites')
    else:
        df_filtered = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(df_filtered, names='class', hole=.3,
                     title=f'Total Success Launches for Site {selected_site}')
    return fig

# Scatter chart callback
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site_dropdown', 'value'),
     Input('payload_slider', 'value')]
)
def update_scatter_plot(selected_site, payload_range):
    low, high = payload_range
    df_filtered = spacex_df if selected_site == 'All Sites' else spacex_df[spacex_df['Launch Site'] == selected_site]
    mask = (df_filtered['Payload Mass (kg)'] > low) & (df_filtered['Payload Mass (kg)'] < high)
    fig = px.scatter(df_filtered[mask], x="Payload Mass (kg)", y="class",
                     color="Booster Version", size='Payload Mass (kg)',
                     hover_data=['Payload Mass (kg)'])
    return fig

# Run app
if __name__ == '__main__':
    app.run_server(debug=False)