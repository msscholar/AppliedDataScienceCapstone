# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Build a list of launch-site options for the dropdown
launch_sites = spacex_df['Launch Site'].unique().tolist()
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in launch_sites
]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center',
                   'color': '#503D36',
                   'fontSize': 40}),
    
    # ----------  TASK 1 : Launch-site dropdown  ----------
    dcc.Dropdown(id='site-dropdown',
                 options=site_options,
                 value='ALL',                       # default
                 placeholder='Select a Launch Site here',
                 searchable=True),
    
    html.Br(),

    # ----------  TASK 2 : Pie chart  ----------
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # ----------  TASK 3 : Payload slider  ----------
    dcc.RangeSlider(id='payload-slider',
                    min=0,
                    max=10000,
                    step=1000,
                    marks={0: '0',
                           2500: '2 500',
                           5000: '5 000',
                           7500: '7 500',
                           10000: '10 000'},
                    value=[min_payload, max_payload]),

    # ----------  TASK 4 : Scatter chart  ----------
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# --------------------------------------------------------
#  TASK 2 : callback → pie chart
# --------------------------------------------------------
@app.callback(Output('success-pie-chart', 'figure'),
              Input('site-dropdown', 'value'))
def render_pie_chart(selected_site):
    """Return a pie chart of launch successes."""
    if selected_site == 'ALL':
        # Total successes for each site
        fig = px.pie(spacex_df,
                     names='Launch Site',
                     values='class',
                     title='Total Success Launches by Site')
    else:
        # Success vs-failure for the chosen site
        site_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(site_df,
                     names='class',
                     values='class',
                     title=f'Total Success vs Failure for {selected_site}')
        fig.update_traces(labels=['Failure (0)', 'Success (1)'])
    return fig

# --------------------------------------------------------
#  TASK 4 : callback → scatter chart
# --------------------------------------------------------
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input('site-dropdown', 'value'),
               Input('payload-slider', 'value')])
def render_scatter(selected_site, payload_range):
    """Return a scatter plot of payload mass vs success."""
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & \
           (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    title_site = 'all Sites' if selected_site == 'ALL' else selected_site
    fig = px.scatter(filtered_df,
                     x='Payload Mass (kg)',
                     y='class',
                     color='Booster Version Category',
                     title=f'Correlation between Payload and Success for {title_site}',
                     hover_data=['Mission Outcome'] if 'Mission Outcome' in filtered_df.columns else None)
    return fig

# Run the app
if __name__ == '__main__':
    # debug=False keeps stdout clean when you grab screenshots
    app.run(debug=False)