
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
import plotly.express as px
import json
import numpy as np
import os
from shapely.geometry import Point
from shapely import wkt
from datetime import date
# Process the 'reeds_ba_list' column to expand the sets into individual rows, keeping 'state' intact
from ast import literal_eval
# Get the current directory where your script is running
current_directory = os.getcwd()

# Construct the path to your resources folder dynamically
data_path = os.path.join(current_directory, 'web_page_data')


# Define file paths for saving
gdf_country_path = os.path.join(data_path, 'gdf_country.gpkg')
gdf_state_path = os.path.join(data_path, 'gdf_state.gpkg')
gdf_subregion_path = os.path.join(data_path, 'gdf_subregion.gpkg')

# Define paths for the GeoJSON files
country_geojson_path = os.path.join(data_path, 'country_centroids.csv')
state_geojson_path = os.path.join(data_path, 'state_centroids.csv')
rb_geojson_path = os.path.join(data_path, 'rb_centroids.csv')


# Function to read GeoJSON from a file
def read_geojson(file_path):
    with open(file_path) as f:
        return json.load(f)


# Read the GeoDataFrames
gdf_country = gpd.read_file(gdf_country_path)
gdf_state = gpd.read_file(gdf_state_path)
gdf_subregion = gpd.read_file(gdf_subregion_path)

gdf_country = gdf_country.to_crs(epsg=4326)
gdf_state = gdf_state.to_crs(epsg=4326)
gdf_subregion = gdf_subregion.to_crs(epsg=4326)

geojson_country = gdf_country.__geo_interface__
geojson_state = gdf_state.__geo_interface__
geojson_subregion = gdf_subregion.__geo_interface__


# Use pandas to read the CSV files
country_centroids_df = pd.read_csv(country_geojson_path)
state_centroids_df = pd.read_csv(state_geojson_path)
rb_centroids_df = pd.read_csv(rb_geojson_path)

# Function to convert a DataFrame with 'lon' and 'lat' columns to a GeoDataFrame
def df_to_gdf(df):
    # Create a GeoSeries from the 'lon' and 'lat' columns
    geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf

# Convert the DataFrames to GeoDataFrames
gdf_country_centroids = df_to_gdf(country_centroids_df)
gdf_state_centroids = df_to_gdf(state_centroids_df)
gdf_rb_centroids = df_to_gdf(rb_centroids_df)


# Initialize the Dash app
app = dash.Dash(__name__)
server=app.server

app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='usa-map', 
            config={'scrollZoom': False,'modeBarButtonsToRemove': ['zoom', 'zoomIn', 'zoomOut', 'pan']},
            style={'display': 'inline-block', 'width': '80%'}
        ),
        html.Div([
            html.H4("Select Breakdown:", style={'marginBottom': -20, 'marginTop': 0}), 
            dcc.RadioItems(
                id='map-toggle',
                options=[
                    {'label': 'Whole Country', 'value': 'country'},
                    {'label': 'By State', 'value': 'state'},
                    {'label': 'By Subregion', 'value': 'subregion'},
                ],
                value='country',  # Default value
                style={'padding': 20},
                inline=True
            ),
            html.H4("Select Scenario:", style={'marginBottom': -20, 'marginTop': 0}),
            dcc.RadioItems(
                id='scenario-toggle',
                options=[
                    {'label': 'Most extreme', 'value': 'rcp85hotter'},
                    {'label': 'Extreme', 'value': 'rcp85cooler'},
                    {'label': 'Mini extreme', 'value': 'rcp45hotter'},
                    {'label': 'Least extreme', 'value': 'rcp45cooler'},
                    {'label': 'Stable(unimplement)','value': 'stable'}
                ],
                value='rcp85hotter',  # Default value
                style={'padding': 20},
                inline=True
            ),
            html.H4("Select Time for the map:", style={'marginBottom': 0, 'marginTop': 0}),
            html.Div([
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=date(2020, 1, 1),
                max_date_allowed=date(2100, 12, 31),
                start_date=date(2020, 1, 1),
                end_date=date(2100, 12, 31)
            )
            ]),
            html.H4("Choose region to inspect:", style={'marginBottom': 0, 'marginTop': 0}), 
            html.Div([dcc.Dropdown(id='graph-toggle',value='USA',  multi=False)]),
        ], style={'display': 'inline-block', 'width': '20%', 'verticalAlign': 'top'}),
    ]),
    html.Div([
        dcc.Graph(id='line-graph'),  # Placeholder for the line graph
    ], style={'paddingTop': 20})
])

@app.callback(
    Output('usa-map', 'figure'),
    [
        Input('scenario-toggle', 'value'),
        Input('map-toggle', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ]
)


def update_map(scenario_value,toggle_value,start_date,end_date):
    # Choose the correct DataFrame and title based on toggle_value
    if toggle_value == 'country':
        data = gdf_country
        geojson = geojson_country
        color_column = 'country'
        df_centroids=gdf_country_centroids
        # Define the columns to read from the CSV file
        columns_to_read = ['time', 'USA']
    elif toggle_value == 'state':
        data = gdf_state
        geojson = geojson_state
        color_column = 'state'
        df_centroids=gdf_state_centroids
        columns_to_read = ['time', 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
          'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
          'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
          'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
          'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
    else:  # Assuming 'subregion'
        data = gdf_subregion
        geojson = geojson_subregion
        color_column = 'rb'
        df_centroids=gdf_rb_centroids
        columns_to_read = ['time'] + [f'p{i}' for i in range(1, 135)]
    resources_path=os.path.join(current_directory, 'resources')
    file_path = os.path.join(resources_path, f'mock_{scenario_value}.csv')
    
    
    # Read only the selected columns from the CSV file
    df = pd.read_csv(file_path, usecols=columns_to_read)
    
    # Ensure 'time' column is datetime type for proper plotting
    df['time'] = pd.to_datetime(df['time'])
    
    
    # Filter the data based on the selected date range
    mask = (df['time'] >= start_date) & (df['time'] <= end_date)
    df = df.loc[mask]
    # Sum df vertically by column
    df_summed = df.drop('time', axis=1).sum().reset_index()
    df_summed.columns = ['region', 'demand']

    # Create a mapping from region to demand
    demand_mapping = df_summed.set_index('region')['demand'].to_dict()

    # Apply the mapping to create a new 'demand' column in 'data'
    data['demand'] = data[color_column].map(demand_mapping)
    # Use Plotly Express to create the choropleth map with a Mapbox base map
    fig = px.choropleth_mapbox(data, geojson=geojson, 
                               locations=data.index, 
                               color='demand',
                               mapbox_style="carto-positron",
                               hover_data=[color_column,'demand'],
                               zoom=3, center={"lat": 37.0902, "lon": -95.7129},
                               opacity=0.5)

    # Update layout to fix the map view (disable zoom and pan)
    fig.update_layout(
        mapbox=dict(
            center={"lat": 37.0902, "lon": -95.7129},
            zoom=3,
            style="carto-positron"
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        title=f"Map by {toggle_value.title()}",
    )
    fig.add_trace(go.Scattergeo(
        lon=data["geometry"].centroid.x,
        lat=data["geometry"].centroid.y,
        mode='text',
        text=df_centroids[color_column].str.title(),
        textfont={'color': 'Green'},
        name='',
    ))

    return fig

@app.callback(
    [Output('graph-toggle', 'options'),
     Output('graph-toggle', 'value')],
    [Input('map-toggle', 'value')]
)
def set_graph_toggle_options(selected_map_view):
    #print(f"Selected map view: {selected_map_view}")
    if selected_map_view == 'country':
        # Explicitly return 'USA' as the option
        options = [{'label': 'USA', 'value': 'USA'}]
        value='USA'
    elif selected_map_view == 'state':
        # Example state list; replace with your actual data or method to retrieve states
        options =[{'label': i, 'value': i} for i in state_centroids_df['state'].unique()]
        value='New York'
    elif selected_map_view == 'subregion':
        # Generate subregion options from 'p1' to 'p134'
        options = [{'label': f'p{i}', 'value': f'p{i}'} for i in range(1, 135)]
        value='p1'

    return options,value

@app.callback(
    Output('line-graph', 'figure'),
    [
        Input('scenario-toggle', 'value'),
        Input('graph-toggle', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ]
)
def update_line_graph(scenario_value, graph_value, start_date, end_date):
    # Construct the file path for the selected scenario
    resources_path=os.path.join(current_directory, 'resources')
    file_path = os.path.join(resources_path, f'mock_{scenario_value}.csv')
    
    # Define the columns to read from the CSV file
    columns_to_read = ['time', graph_value]
    
    # Read only the selected columns from the CSV file
    df = pd.read_csv(file_path, usecols=columns_to_read)
    
    # Ensure 'time' column is datetime type for proper plotting
    df['time'] = pd.to_datetime(df['time'])
    
    
    # Filter the data based on the selected date range
    mask = (df['time'] >= start_date) & (df['time'] <= end_date)
    filtered_df = df.loc[mask]
    
    # Extract the data for plotting
    x_data = filtered_df['time']
    y_data = filtered_df[graph_value]
    
    # Create the figure
    fig = go.Figure()
    
    # Add the line trace
    fig.add_trace(go.Scatter(x=x_data, y=y_data, mode='lines'))
    
    # Dynamically set the title based on the toggle selections
    title_text = f"Scenario: {scenario_value}, Graph: {graph_value}"
    fig.update_layout(title=title_text)
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)