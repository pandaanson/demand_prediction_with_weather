
# # Get the current directory where your script is running
# current_directory = os.getcwd()

# # Construct the path to your resources folder dynamically
# data_path = os.path.join(current_directory, 'web_page_data')


# # Define paths for the GeoJSON files
# country_geojson_path = os.path.join(data_path, 'country_centroids.csv')
# state_geojson_path = os.path.join(data_path, 'state_centroids.csv')
# rb_geojson_path = os.path.join(data_path, 'rb_centroids.csv')


# # Use pandas to read the CSV files
# country_centroids_df = pd.read_csv(country_geojson_path)
# state_centroids_df = pd.read_csv(state_geojson_path)
# rb_centroids_df = pd.read_csv(rb_geojson_path)

# # Function to convert a DataFrame with 'lon' and 'lat' columns to a GeoDataFrame
# def df_to_gdf(df):
#     # Create a GeoSeries from the 'lon' and 'lat' columns
#     geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
#     gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
#     return gdf

# # Convert the DataFrames to GeoDataFrames
# gdf_country_centroids = df_to_gdf(country_centroids_df)
# gdf_state_centroids = df_to_gdf(state_centroids_df)
# gdf_rb_centroids = df_to_gdf(rb_centroids_df)
# # Read geometries and centroids GeoJSON files using GeoPandas
# # Paths to the CSV files
# country_geometry_path = os.path.join(data_path, 'country.csv')
# state_geometry_path = os.path.join(data_path, 'state.csv')
# rb_geometry_path = os.path.join(data_path, 'rb.csv')

# # Read CSV files
# df_country = pd.read_csv(country_geometry_path)
# df_state = pd.read_csv(state_geometry_path)
# df_rb = pd.read_csv(rb_geometry_path)

# # # Convert WKT strings to geometrical objects
# # df_country['geometry'] = df_country['geometry'].apply(wkt.loads)
# # df_state['geometry'] = df_state['geometry'].apply(wkt.loads)
# # df_rb['geometry'] = df_rb['geometry'].apply(wkt.loads)

# # Transform DataFrames into GeoDataFrames
# gdf_country = gpd.GeoDataFrame(df_country, geometry=gpd.GeoSeries.from_wkt(df_country['WKT'])).reset_index()
# gdf_state  = gpd.GeoDataFrame(df_state , geometry=gpd.GeoSeries.from_wkt(df_state['WKT'])).reset_index()
# gdf_subregion  = gpd.GeoDataFrame(df_rb , geometry=gpd.GeoSeries.from_wkt(df_rb['WKT'])).drop_duplicates()


# # Convert each GeoDataFrame to GeoJSON for use in Plotly
# geojson_country = json.loads(gdf_country.to_json())
# geojson_state = json.loads(gdf_state.to_json())
# geojson_subregion = json.loads(gdf_subregion.to_json())
# # Initialize the Dash app
# app = dash.Dash(__name__)
# server=app.server

# app.layout = html.Div([
#     html.Div([
#         dcc.Graph(id='usa-map', style={'display': 'inline-block', 'width': '70%'}),
#         html.Div([
#             dcc.RadioItems(
#                 id='map-toggle',
#                 options=[
#                     {'label': 'Whole Country', 'value': 'country'},
#                     {'label': 'By State', 'value': 'state'},
#                     {'label': 'By Subregion', 'value': 'subregion'},
#                 ],
#                 value='country',  # Default value
#                 style={'padding': 20}
#             ),
#             dcc.Dropdown(id='graph-toggle',value='USA',  multi=True)
#         ], style={'display': 'inline-block', 'width': '30%', 'verticalAlign': 'top'}),
#     ]),
#     html.Div([
#         dcc.Graph(id='line-graph'),  # Placeholder for the line graph
#     ], style={'paddingTop': 20})
# ])

# @app.callback(
#     Output('usa-map', 'figure'),
#     Input('map-toggle', 'value')
# )


# def update_map(toggle_value):
#     # Choose the correct DataFrame and title based on toggle_value
#     if toggle_value == 'country':
#         data = gdf_country
#         geojson = geojson_country
#         color_column = 'country'
#     elif toggle_value == 'state':
#         data = gdf_state
#         geojson = geojson_state
#         color_column = 'state'
#     else:  # Assuming 'subregion'
#         data = gdf_subregion
#         geojson = geojson_subregion
#         color_column = 'rb'

#     # Use Plotly Express to create the choropleth map with a Mapbox base map
#     fig = px.choropleth_mapbox(data, geojson=geojson, 
#                                locations=data.index, 
#                                color=color_column,
#                                mapbox_style="white-bg",
#                                zoom=3, center={"lat": 37.0902, "lon": -95.7129},
#                                opacity=0.5)
#     # Calculate centroids of geometries


#     # if toggle_value == 'country':
#     #     annotations_data = country_centroids_df
#     # elif toggle_value == 'state':
#     #     annotations_data = state_centroids_df
#     # else:  # Assuming 'subregion'
#     #     annotations_data = rb_centroids_df

#     # Use Plotly Express to create the choropleth map
#     fig = px.choropleth_mapbox(data, geojson=data.geometry.__geo_interface__, 
#                                locations=data.index, 
#                                color=color_column,
#                                mapbox_style="white-bg",
#                                zoom=3, center={"lat": 37.0902, "lon": -95.7129},
#                                opacity=0.5)
    
#     # Dynamically add annotations using centroids

#     # annotations = []
#     # for _, row in annotations_data:
#     #     annotations.append(go.layout.Annotation(
#     #         x=row['lon'],
#     #         y=row['lat'],
#     #         text=str(row['region']),  # Ensure text is a string
#     #         showarrow=False,
#     #         bgcolor="white",
#     #         font=dict(color="black"),
#     #     ))

#     fig.update_layout(
#         margin={"r":0,"t":0,"l":0,"b":0}, 
#         title=f"Map by {toggle_value.title()}"
#     )
#     #,annotations=annotations  # Ensure annotations are correctly added to the layout
#     return fig
# @app.callback(
#     [Output('graph-toggle', 'options'),
#      Output('graph-toggle', 'value')],
#     [Input('map-toggle', 'value')]
# )
# def set_graph_toggle_options(selected_map_view):
#     #print(f"Selected map view: {selected_map_view}")
#     if selected_map_view == 'country':
#         # Explicitly return 'USA' as the option
#         options = [{'label': 'USA', 'value': 'USA'}]
#         value='USA'
#     elif selected_map_view == 'state':
#         # Example state list; replace with your actual data or method to retrieve states
#         state_list = ['California', 'New York', 'Texas', 'Florida', 'Illinois']
#         options = [{'label': state, 'value': state} for state in state_list]
#         value='New York'
#     elif selected_map_view == 'subregion':
#         # Generate subregion options from 'p1' to 'p134'
#         options = [{'label': f'p{i}', 'value': f'p{i}'} for i in range(1, 135)]
#         value='p1'

#     return options,value

# if __name__ == '__main__':
#     app.run_server(debug=True)


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
# Process the 'reeds_ba_list' column to expand the sets into individual rows, keeping 'state' intact
from ast import literal_eval
# Get the current directory where your script is running
current_directory = os.getcwd()

# Construct the path to your resources folder dynamically
data_path = os.path.join(current_directory, 'web_page_data')

geojson_country_path = os.path.join(data_path, 'geojson_country.json')
geojson_state_path = os.path.join(data_path, 'geojson_state.json')
geojson_subregion_path = os.path.join(data_path, 'geojson_subregion.json')

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

# Read the GeoJSON data
geojson_country = read_geojson(geojson_country_path)
geojson_state = read_geojson(geojson_state_path)
geojson_subregion = read_geojson(geojson_subregion_path)

# Read the GeoDataFrames
gdf_country = gpd.read_file(gdf_country_path)
gdf_state = gpd.read_file(gdf_state_path)
gdf_subregion = gpd.read_file(gdf_subregion_path)


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
# Read geometries and centroids GeoJSON files using GeoPandas
# Paths to the CSV files




# Initialize the Dash app
app = dash.Dash(__name__)
server=app.server

app.layout = html.Div([
    html.Div([
        dcc.Graph(id='usa-map', style={'display': 'inline-block', 'width': '70%'}),
        html.Div([
            dcc.RadioItems(
                id='map-toggle',
                options=[
                    {'label': 'Whole Country', 'value': 'country'},
                    {'label': 'By State', 'value': 'state'},
                    {'label': 'By Subregion', 'value': 'subregion'},
                ],
                value='country',  # Default value
                style={'padding': 20}
            ),
            dcc.Dropdown(id='graph-toggle',value='USA',  multi=True)
        ], style={'display': 'inline-block', 'width': '30%', 'verticalAlign': 'top'}),
    ]),
    html.Div([
        dcc.Graph(id='line-graph'),  # Placeholder for the line graph
    ], style={'paddingTop': 20})
])

@app.callback(
    Output('usa-map', 'figure'),
    Input('map-toggle', 'value')
)


def update_map(toggle_value):
    # Choose the correct DataFrame and title based on toggle_value
    if toggle_value == 'country':
        data = gdf_country
        geojson = geojson_country
        color_column = 'country'
    elif toggle_value == 'state':
        data = gdf_state
        geojson = geojson_state
        color_column = 'state'
    else:  # Assuming 'subregion'
        data = gdf_subregion
        geojson = geojson_subregion
        color_column = 'rb'

    # Use Plotly Express to create the choropleth map with a Mapbox base map
    fig = px.choropleth_mapbox(data, geojson=geojson, 
                               locations=data.index, 
                               color=color_column,
                               mapbox_style="white-bg",
                               zoom=3, center={"lat": 37.0902, "lon": -95.7129},
                               opacity=0.5)

    # # Add USGS Imagery base map
    # fig.update_layout(
    #     mapbox_layers=[
    #         {
    #             "below": 'traces',
    #             "sourcetype": "raster",
    #             "source": [
    #                 "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
    #             ]
    #         }
    #     ]
    # )

    # Update layout for no margin and title
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, title=f"Map by {toggle_value.title()}")

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
        state_list = ['California', 'New York', 'Texas', 'Florida', 'Illinois']
        options = [{'label': state, 'value': state} for state in state_list]
        value='New York'
    elif selected_map_view == 'subregion':
        # Generate subregion options from 'p1' to 'p134'
        options = [{'label': f'p{i}', 'value': f'p{i}'} for i in range(1, 135)]
        value='p1'

    return options,value

if __name__ == '__main__':
    app.run_server(debug=True)